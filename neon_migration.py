"""Safely copy JobSwipe application data from local PostgreSQL to Neon.

Run from the JobSwipe project root with DATABASE_URL pointing to Neon and
DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT pointing to local PostgreSQL.
This imports records through Django ORM and does not alter schema/migrations.
"""
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

if os.getenv("MIGRATE_TO_NEON") != "YES":
    sys.exit(
        "STOPPED: Set MIGRATE_TO_NEON=YES only after DATABASE_URL points to Neon."
    )
if not os.getenv("DATABASE_URL"):
    sys.exit("STOPPED: DATABASE_URL is missing (it must point to Neon).")

import django
django.setup()

from django.conf import settings
from django.db import connections, transaction
from django.contrib.auth import get_user_model
from accounts.models import Profile, JobPreference
from jobs.models import (
    Company, Job, JobSwipe, JobBookmark, CompanyMembership, Conversation, Message,
)

# Define the source database from the local .env DB_* settings. Do not print secrets.
source_db = settings.DATABASES["default"].copy()

source_db.update({
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.getenv("DB_NAME", "job_swipe"),
    "USER": os.getenv("DB_USER", "job_swipe_user"),
    "PASSWORD": os.getenv("DB_PASSWORD", "jobsearch"),
    "HOST": os.getenv("DB_HOST", "127.0.0.1"),
    "PORT": os.getenv("DB_PORT", "5432"),
    "CONN_MAX_AGE": 0,
    "OPTIONS": {},
})

settings.DATABASES["source"] = source_db

SRC = "source"
DST = "default"
User = get_user_model()
counts = {}
notes = []

# Fail early if either database is not accessible or target migrations/schema are missing.
try:
    with connections[SRC].cursor() as cur:
        cur.execute("SELECT 1")
    with connections[DST].cursor() as cur:
        cur.execute("SELECT 1")
    User.objects.using(SRC).count()
    User.objects.using(DST).count()
except Exception as exc:
    sys.exit(f"STOPPED: Could not connect or required tables are missing ({type(exc).__name__}: {exc}). No data was imported.")


def model_values(obj, fields):
    return {field: getattr(obj, field) for field in fields}


def run_migration():
    user_map = {}
    company_map = {}
    job_map = {}
    swipe_map = {}
    conversation_map = {}

    with transaction.atomic(using=DST):
        # Users: match by normalized email. Existing Neon accounts are never overwritten.
        user_fields = [
            "password", "last_login", "is_superuser", "first_name", "last_name",
            "is_staff", "is_active", "date_joined", "email", "full_name", "role",
        ]
        for src_user in User.objects.using(SRC).order_by("pk"):
            email = src_user.email.strip().lower()
            dst_user = User.objects.using(DST).filter(email__iexact=email).first()
            if dst_user:
                user_map[src_user.pk] = dst_user.pk
                counts["users_matched_existing"] = counts.get("users_matched_existing", 0) + 1
                if src_user.role != dst_user.role:
                    notes.append(f"Role differs for a matched account (local user ID {src_user.pk}); existing Neon role preserved.")
                if src_user.is_superuser and not dst_user.is_superuser:
                    notes.append(f"Local superuser matched an existing non-superuser account (local user ID {src_user.pk}); Neon privileges preserved for safety.")
            else:
                values = model_values(src_user, user_fields)
                values["email"] = email
                dst_user = User.objects.using(DST).create(**values)
                user_map[src_user.pk] = dst_user.pk
                counts["users_imported"] = counts.get("users_imported", 0) + 1

        # Companies: unique name is the stable natural key.
        company_fields = ["name", "website", "description", "headquarters", "logo_url", "is_verified", "created_at", "updated_at"]
        for src_obj in Company.objects.using(SRC).order_by("pk"):
            dst_obj = Company.objects.using(DST).filter(name=src_obj.name).first()
            if not dst_obj:
                dst_obj = Company.objects.using(DST).create(**model_values(src_obj, company_fields))
                counts["companies_imported"] = counts.get("companies_imported", 0) + 1
            else:
                counts["companies_matched_existing"] = counts.get("companies_matched_existing", 0) + 1
            company_map[src_obj.pk] = dst_obj.pk

        # Jobs: match by company + title; existing cloud rows are preserved.
        job_fields = ["title", "description", "responsibilities", "required_skills", "location", "work_mode", "employment_type", "experience_level", "minimum_salary", "maximum_salary", "application_url", "posted_at", "closing_date", "is_active", "created_at", "updated_at"]
        for src_obj in Job.objects.using(SRC).order_by("pk"):
            company_id = company_map[src_obj.company_id]
            dst_obj = Job.objects.using(DST).filter(company_id=company_id, title=src_obj.title).first()
            if not dst_obj:
                values = model_values(src_obj, job_fields)
                values["company_id"] = company_id
                dst_obj = Job.objects.using(DST).create(**values)
                counts["jobs_imported"] = counts.get("jobs_imported", 0) + 1
            else:
                counts["jobs_matched_existing"] = counts.get("jobs_matched_existing", 0) + 1
            job_map[src_obj.pk] = dst_obj.pk

        # Candidate profile and preferences; resume files themselves are not stored in the DB.
        for src_obj in Profile.objects.using(SRC).order_by("pk"):
            uid = user_map[src_obj.user_id]
            values = {
                "qualification": src_obj.qualification,
                "skills": src_obj.skills,
                "experience_years": src_obj.experience_years,
                "resume": "",  # media files must be transferred separately
                "created_at": src_obj.created_at,
                "updated_at": src_obj.updated_at,
            }
            _, created = Profile.objects.using(DST).get_or_create(user_id=uid, defaults=values)
            counts["profiles_imported"] = counts.get("profiles_imported", 0) + int(created)

        pref_fields = ["preferred_roles", "preferred_locations", "minimum_salary", "maximum_salary", "work_mode", "employment_type", "experience_level", "willing_to_relocate", "updated_at"]
        for src_obj in JobPreference.objects.using(SRC).order_by("pk"):
            uid = user_map[src_obj.user_id]
            _, created = JobPreference.objects.using(DST).get_or_create(user_id=uid, defaults=model_values(src_obj, pref_fields))
            counts["preferences_imported"] = counts.get("preferences_imported", 0) + int(created)

        # Swipes/applications.
        for src_obj in JobSwipe.objects.using(SRC).order_by("pk"):
            uid, jid = user_map[src_obj.user_id], job_map[src_obj.job_id]
            reviewed_by_id = user_map.get(src_obj.reviewed_by_id) if src_obj.reviewed_by_id else None
            dst_obj = JobSwipe.objects.using(DST).filter(user_id=uid, job_id=jid).first()
            if not dst_obj:
                dst_obj = JobSwipe.objects.using(DST).create(
                    user_id=uid, job_id=jid, direction=src_obj.direction,
                    interest_status=src_obj.interest_status, reviewed_at=src_obj.reviewed_at,
                    reviewed_by_id=reviewed_by_id, created_at=src_obj.created_at,
                    updated_at=src_obj.updated_at,
                )
                counts["swipes_imported"] = counts.get("swipes_imported", 0) + 1
            else:
                counts["swipes_matched_existing"] = counts.get("swipes_matched_existing", 0) + 1
            swipe_map[src_obj.pk] = dst_obj.pk

        for src_obj in JobBookmark.objects.using(SRC).order_by("pk"):
            uid, jid = user_map[src_obj.user_id], job_map[src_obj.job_id]
            _, created = JobBookmark.objects.using(DST).get_or_create(
                user_id=uid, job_id=jid, defaults={"created_at": src_obj.created_at}
            )
            counts["bookmarks_imported"] = counts.get("bookmarks_imported", 0) + int(created)

        for src_obj in CompanyMembership.objects.using(SRC).order_by("pk"):
            uid, cid = user_map[src_obj.user_id], company_map[src_obj.company_id]
            _, created = CompanyMembership.objects.using(DST).get_or_create(
                user_id=uid, company_id=cid,
                defaults={"role": src_obj.role, "is_active": src_obj.is_active, "created_at": src_obj.created_at},
            )
            counts["memberships_imported"] = counts.get("memberships_imported", 0) + int(created)

        for src_obj in Conversation.objects.using(SRC).order_by("pk"):
            sid = swipe_map[src_obj.swipe_id]
            dst_obj = Conversation.objects.using(DST).filter(swipe_id=sid).first()
            if not dst_obj:
                dst_obj = Conversation.objects.using(DST).create(
                    swipe_id=sid, created_at=src_obj.created_at, updated_at=src_obj.updated_at
                )
                counts["conversations_imported"] = counts.get("conversations_imported", 0) + 1
            else:
                counts["conversations_matched_existing"] = counts.get("conversations_matched_existing", 0) + 1
            conversation_map[src_obj.pk] = dst_obj.pk

        for src_obj in Message.objects.using(SRC).order_by("pk"):
            cid, uid = conversation_map[src_obj.conversation_id], user_map[src_obj.sender_id]
            exists = Message.objects.using(DST).filter(
                conversation_id=cid, sender_id=uid, body=src_obj.body,
                created_at=src_obj.created_at,
            ).exists()
            if not exists:
                Message.objects.using(DST).create(
                    conversation_id=cid, sender_id=uid, body=src_obj.body,
                    created_at=src_obj.created_at, read_at=src_obj.read_at,
                )
                counts["messages_imported"] = counts.get("messages_imported", 0) + 1
            else:
                counts["messages_skipped_existing"] = counts.get("messages_skipped_existing", 0) + 1

    # Print counts only; never print emails, passwords, or connection strings.
    print("Migration committed successfully.")
    for key in sorted(counts):
        print(f"{key}: {counts[key]}")
    print("Target totals: users={}, companies={}, jobs={}, swipes={}, conversations={}, messages={}".format(
        User.objects.using(DST).count(), Company.objects.using(DST).count(),
        Job.objects.using(DST).count(), JobSwipe.objects.using(DST).count(),
        Conversation.objects.using(DST).count(), Message.objects.using(DST).count(),
    ))
    if notes:
        print("\nReview notes:")
        for note in notes:
            print("- " + note)
    print("Note: local resume/media files and Django admin log history are not copied by this script.")

run_migration()
