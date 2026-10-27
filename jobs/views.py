from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import FileResponse, Http404, HttpResponseForbidden, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from accounts.models import JobPreference, Profile, User
from .forms import EmployerJobForm, MessageForm
from .models import CompanyMembership, Conversation, Job, JobBookmark, JobSwipe, Message


def _tokens(value):
    return [part.strip().lower() for part in value.replace("\n", ",").split(",") if part.strip()]


def _base_open_jobs():
    today = timezone.localdate()
    return Job.objects.select_related("company").filter(is_active=True).filter(
        Q(closing_date__isnull=True) | Q(closing_date__gte=today)
    )


def _preference_score(job, preference, candidate_skills=""):
    """Transparent, explainable score out of 100 for candidate/job fit."""
    score = 0
    reasons = []
    role_terms = _tokens(preference.preferred_roles)
    location_terms = _tokens(preference.preferred_locations)
    skills = _tokens(candidate_skills or "")

    title = job.title.lower()
    location = job.location.lower()
    job_skills = (job.required_skills or "").lower()
    description = (job.description or "").lower()

    if role_terms:
        matched = [term for term in role_terms if term in title]
        if matched:
            score += 30
            reasons.append("Preferred role")
    else:
        score += 15

    if location_terms:
        if any(term in location for term in location_terms):
            score += 20
            reasons.append("Preferred location")
    else:
        score += 10

    if preference.work_mode == JobPreference.WorkMode.ANY or job.work_mode == preference.work_mode:
        score += 10
        if preference.work_mode != JobPreference.WorkMode.ANY:
            reasons.append("Preferred work mode")

    if preference.employment_type == JobPreference.EmploymentType.ANY or job.employment_type == preference.employment_type:
        score += 10
        if preference.employment_type != JobPreference.EmploymentType.ANY:
            reasons.append("Preferred employment type")

    if preference.experience_level == JobPreference.ExperienceLevel.ANY or job.experience_level == preference.experience_level:
        score += 15
        if preference.experience_level != JobPreference.ExperienceLevel.ANY:
            reasons.append("Experience match")

    salary_match = True
    if preference.minimum_salary is not None and job.maximum_salary is not None:
        salary_match = job.maximum_salary >= preference.minimum_salary
    if preference.maximum_salary is not None and job.minimum_salary is not None:
        salary_match = salary_match and job.minimum_salary <= preference.maximum_salary
    if salary_match:
        score += 10
        if preference.minimum_salary is not None or preference.maximum_salary is not None:
            reasons.append("Salary range")

    # Skills are a small bonus; the main score remains based on saved preferences.
    if skills and any(skill in job_skills or skill in description for skill in skills):
        score += 5
        reasons.append("Skills overlap")

    return min(score, 100), reasons


def _annotate_and_rank(jobs, preference, candidate_skills=""):
    ranked = []
    for job in jobs:
        job.match_score, job.match_reasons = _preference_score(job, preference, candidate_skills)
        ranked.append(job)
    ranked.sort(key=lambda item: (item.match_score, item.posted_at, item.created_at), reverse=True)
    return ranked


@login_required
def job_feed_view(request):
    if request.user.role == User.Role.EMPLOYER:
        return redirect("jobs:employer_dashboard")
    preferences, _ = JobPreference.objects.get_or_create(user=request.user)
    jobs = _base_open_jobs()

    swiped_job_ids = JobSwipe.objects.filter(user=request.user).values_list("job_id", flat=True)
    jobs = jobs.exclude(pk__in=swiped_job_ids)

    query = request.GET.get("q", "").strip()
    location = request.GET.get("location", "").strip()
    work_mode = request.GET.get("work_mode", "").strip()
    employment_type = request.GET.get("employment_type", "").strip()
    experience_level = request.GET.get("experience_level", "").strip()
    saved_only = request.GET.get("saved") == "1"

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(required_skills__icontains=query)
            | Q(company__name__icontains=query)
        )
    if location:
        jobs = jobs.filter(location__icontains=location)
    if work_mode in {v for v, _ in Job.WorkMode.choices}:
        jobs = jobs.filter(work_mode=work_mode)
    if employment_type in {v for v, _ in Job.EmploymentType.choices}:
        jobs = jobs.filter(employment_type=employment_type)
    if experience_level in {v for v, _ in Job.ExperienceLevel.choices}:
        jobs = jobs.filter(experience_level=experience_level)
    if saved_only:
        saved_ids = JobBookmark.objects.filter(user=request.user).values_list("job_id", flat=True)
        jobs = jobs.filter(pk__in=saved_ids)

    profile = Profile.objects.filter(user=request.user).first()
    candidate_skills = profile.skills if profile else ""
    ranked_jobs = _annotate_and_rank(jobs, preferences, candidate_skills)
    return render(request, "jobs/job_feed.html", {
        "jobs": ranked_jobs,
        "preferences": preferences,
        "query": query,
        "location": location,
        "selected_work_mode": work_mode,
        "selected_employment_type": employment_type,
        "selected_experience_level": experience_level,
        "work_modes": Job.WorkMode.choices,
        "employment_types": Job.EmploymentType.choices,
        "experience_levels": Job.ExperienceLevel.choices,
        "saved_only": saved_only,
    })


@login_required
def job_detail_view(request, pk):
    if request.user.role == User.Role.EMPLOYER:
        return redirect("jobs:employer_dashboard")
    from django.http import Http404
    today = timezone.localdate()
    job = get_object_or_404(Job.objects.select_related("company"), pk=pk, is_active=True)
    if job.closing_date and job.closing_date < today:
        raise Http404("This job listing has expired.")
    existing_swipe = JobSwipe.objects.filter(user=request.user, job=job).first()
    is_bookmarked = JobBookmark.objects.filter(user=request.user, job=job).exists()
    preferences, _ = JobPreference.objects.get_or_create(user=request.user)
    profile = Profile.objects.filter(user=request.user).first()
    candidate_skills = profile.skills if profile else ""
    job.match_score, job.match_reasons = _preference_score(job, preferences, candidate_skills)
    return render(request, "jobs/job_detail.html", {
        "job": job, "existing_swipe": existing_swipe, "is_bookmarked": is_bookmarked,
    })


@login_required
def swipe_job_view(request, pk):
    if request.user.role == User.Role.EMPLOYER:
        return HttpResponseForbidden("Candidate account required.")
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    direction = request.POST.get("direction", "").strip()
    allowed_directions = {value for value, _ in JobSwipe.Direction.choices}
    if direction not in allowed_directions:
        messages.error(request, "Choose either Interested or Skip.")
        return redirect("jobs:feed")

    today = timezone.localdate()
    job = get_object_or_404(Job.objects.select_related("company"), pk=pk, is_active=True)
    if job.closing_date and job.closing_date < today:
        messages.warning(request, "That job has expired and can no longer be selected.")
        return redirect("jobs:feed")

    swipe, created = JobSwipe.objects.get_or_create(
        user=request.user, job=job, defaults={"direction": direction}
    )
    if not created:
        if (
            direction == JobSwipe.Direction.INTERESTED
            and swipe.direction == JobSwipe.Direction.INTERESTED
            and swipe.interest_status == JobSwipe.InterestStatus.NOT_APPLICABLE
        ):
            swipe.interest_status = JobSwipe.InterestStatus.PENDING
            swipe.save(update_fields=["interest_status", "updated_at"])
            messages.success(request, "Your interest was sent to the company. You can track its response in My Interests.")
            return redirect("jobs:interests")
        messages.info(request, "You've already recorded a decision for this job.")
        if swipe.direction == JobSwipe.Direction.INTERESTED:
            return redirect("jobs:interests")
        return redirect("jobs:feed")

    if direction == JobSwipe.Direction.INTERESTED:
        swipe.interest_status = JobSwipe.InterestStatus.PENDING
        swipe.save(update_fields=["interest_status", "updated_at"])
        messages.success(request, "Your interest was sent to the company. You can track its response in My Interests.")
        return redirect("jobs:interests")

    messages.info(request, "Job skipped. You can review this decision in My Activity.")
    return redirect("jobs:feed")


@login_required
def toggle_bookmark_view(request, pk):
    if request.user.role == User.Role.EMPLOYER:
        return HttpResponseForbidden("Candidate account required.")
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    job = get_object_or_404(_base_open_jobs(), pk=pk)
    bookmark, created = JobBookmark.objects.get_or_create(user=request.user, job=job)
    if created:
        messages.success(request, "Job saved to your list.")
    else:
        bookmark.delete()
        messages.info(request, "Job removed from your saved list.")
    next_url = request.POST.get("next", "")
    if next_url == "detail":
        return redirect("jobs:detail", pk=job.pk)
    if next_url == "saved":
        return redirect("jobs:saved")
    return redirect("jobs:feed")


@login_required
def saved_jobs_view(request):
    if request.user.role == User.Role.EMPLOYER:
        return redirect("jobs:employer_dashboard")
    bookmarks = JobBookmark.objects.filter(user=request.user).select_related("job", "job__company")
    return render(request, "jobs/saved_jobs.html", {"bookmarks": bookmarks})


@login_required
def swipe_history_view(request):
    if request.user.role == User.Role.EMPLOYER:
        return redirect("jobs:employer_dashboard")
    swipes = JobSwipe.objects.filter(user=request.user).select_related("job", "job__company")
    direction = request.GET.get("direction", "").strip()
    if direction in {value for value, _ in JobSwipe.Direction.choices}:
        swipes = swipes.filter(direction=direction)
    return render(request, "jobs/swipe_history.html", {
        "swipes": swipes, "selected_direction": direction, "directions": JobSwipe.Direction.choices,
    })


@login_required
def activity_view(request):
    if request.user.role == User.Role.EMPLOYER:
        return redirect("jobs:employer_dashboard")
    swipes = JobSwipe.objects.filter(user=request.user).select_related("job", "job__company")
    bookmarks = JobBookmark.objects.filter(user=request.user).select_related("job", "job__company")
    interested_count = swipes.filter(direction=JobSwipe.Direction.INTERESTED).count()
    skipped_count = swipes.filter(direction=JobSwipe.Direction.SKIPPED).count()
    return render(request, "jobs/activity.html", {
        "swipes": swipes[:20], "bookmarks": bookmarks[:20],
        "interested_count": interested_count, "skipped_count": skipped_count,
        "saved_count": bookmarks.count(),
    })


# Employer and recruitment workflow views
def _active_membership_for(user):
    return CompanyMembership.objects.filter(user=user, is_active=True).select_related("company").order_by("company__name").first()


def _employer_only(request):
    if request.user.role != User.Role.EMPLOYER:
        return False
    return True


@login_required
def employer_dashboard_view(request):
    if not _employer_only(request):
        return redirect("accounts:dashboard")
    memberships = CompanyMembership.objects.filter(user=request.user, is_active=True).select_related("company")
    membership = memberships.first()
    if membership is None:
        return render(request, "jobs/employer_dashboard.html", {"membership": None, "memberships": memberships, "jobs": [], "pending_count": 0})
    company = membership.company
    company_jobs = Job.objects.filter(company=company).order_by("-created_at")
    pending_count = JobSwipe.objects.filter(job__company=company, direction=JobSwipe.Direction.INTERESTED, interest_status=JobSwipe.InterestStatus.PENDING).count()
    return render(request, "jobs/employer_dashboard.html", {
        "membership": membership, "memberships": memberships, "jobs": company_jobs,
        "pending_count": pending_count, "company": company,
    })


@login_required
def employer_job_create_view(request):
    if not _employer_only(request):
        return HttpResponseForbidden("Employer account required.")
    membership = _active_membership_for(request.user)
    if membership is None:
        return HttpResponseForbidden("You are not an active member of a company.")
    if not membership.company.is_verified:
        messages.warning(request, "Your company must be verified by an administrator before you can publish jobs.")
        return redirect("jobs:employer_dashboard")
    form = EmployerJobForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        job = form.save(commit=False)
        job.company = membership.company
        job.is_active = True
        job.save()
        messages.success(request, "Your job listing has been published.")
        return redirect("jobs:employer_dashboard")
    return render(request, "jobs/employer_job_form.html", {"form": form, "company": membership.company})


@login_required
def employer_interests_view(request):
    if not _employer_only(request):
        return HttpResponseForbidden("Employer account required.")
    membership = _active_membership_for(request.user)
    if membership is None:
        return HttpResponseForbidden("You are not an active member of a company.")
    interests = JobSwipe.objects.filter(
        job__company=membership.company, direction=JobSwipe.Direction.INTERESTED
    ).select_related("user", "job", "job__company", "user__profile").order_by("interest_status", "-updated_at")
    return render(request, "jobs/employer_interests.html", {"interests": interests, "company": membership.company})


@login_required
@require_http_methods(["POST"])
def review_interest_view(request, swipe_id, decision):
    if not _employer_only(request):
        return HttpResponseForbidden("Employer account required.")
    if decision not in {"accept", "reject"}:
        return HttpResponseNotAllowed(["POST"])
    membership = _active_membership_for(request.user)
    if membership is None:
        return HttpResponseForbidden("You are not an active member of a company.")
    with transaction.atomic():
        swipe = get_object_or_404(
            JobSwipe.objects.select_for_update().select_related("job", "user"),
            pk=swipe_id, job__company=membership.company,
            direction=JobSwipe.Direction.INTERESTED,
        )
        if swipe.interest_status != JobSwipe.InterestStatus.PENDING:
            messages.info(request, "This interest has already been reviewed.")
            return redirect("jobs:employer_interests")
        swipe.reviewed_by = request.user
        swipe.reviewed_at = timezone.now()
        if decision == "accept":
            swipe.interest_status = JobSwipe.InterestStatus.ACCEPTED
            swipe.save(update_fields=["interest_status", "reviewed_by", "reviewed_at", "updated_at"])
            Conversation.objects.get_or_create(swipe=swipe)
            messages.success(request, "Candidate accepted. The private conversation is now available.")
        else:
            swipe.interest_status = JobSwipe.InterestStatus.REJECTED
            swipe.save(update_fields=["interest_status", "reviewed_by", "reviewed_at", "updated_at"])
            messages.success(request, "Candidate interest rejected.")
    return redirect("jobs:employer_interests")


@login_required
def candidate_resume_view(request, swipe_id):
    if request.user.role != User.Role.EMPLOYER:
        return HttpResponseForbidden("Employer account required.")
    membership = _active_membership_for(request.user)
    if membership is None:
        return HttpResponseForbidden("You are not an active member of a company.")
    swipe = get_object_or_404(
        JobSwipe.objects.select_related("user", "job", "job__company"),
        pk=swipe_id, job__company=membership.company,
        direction=JobSwipe.Direction.INTERESTED,
        interest_status__in=[JobSwipe.InterestStatus.PENDING, JobSwipe.InterestStatus.ACCEPTED],
    )
    profile = Profile.objects.filter(user=swipe.user).first()
    if profile is None or not profile.resume:
        raise Http404("Resume not found.")
    resume = profile.resume
    response = FileResponse(resume.open("rb"), as_attachment=True, filename=resume.name.rsplit("/", 1)[-1], content_type="application/octet-stream")
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response


@login_required
def candidate_interests_view(request):
    if request.user.role == User.Role.EMPLOYER:
        return redirect("jobs:employer_interests")
    interests = JobSwipe.objects.filter(
        user=request.user, direction=JobSwipe.Direction.INTERESTED
    ).select_related("job", "job__company").order_by("-updated_at")
    return render(request, "jobs/candidate_interests.html", {"interests": interests})


def _conversation_queryset_for(user):
    qs = Conversation.objects.select_related("swipe", "swipe__user", "swipe__job", "swipe__job__company")
    if user.role == User.Role.EMPLOYER:
        company_ids = CompanyMembership.objects.filter(user=user, is_active=True).values_list("company_id", flat=True)
        return qs.filter(swipe__job__company_id__in=company_ids, swipe__interest_status=JobSwipe.InterestStatus.ACCEPTED)
    return qs.filter(swipe__user=user, swipe__interest_status=JobSwipe.InterestStatus.ACCEPTED)


@login_required
def conversation_list_view(request):
    conversations = _conversation_queryset_for(request.user).annotate(
        unread_count=Count(
            "messages",
            filter=Q(messages__read_at__isnull=True) & ~Q(messages__sender=request.user),
        )
    ).order_by("-updated_at")
    return render(request, "jobs/conversation_list.html", {"conversations": conversations})


@login_required
@require_http_methods(["GET"])
def conversation_unread_counts_view(request):
    conversations = _conversation_queryset_for(request.user).annotate(
        unread_count=Count(
            "messages",
            filter=Q(messages__read_at__isnull=True) & ~Q(messages__sender=request.user),
        )
    ).values("id", "unread_count")
    counts = {str(row["id"]): row["unread_count"] for row in conversations}
    return JsonResponse({"counts": counts, "total": sum(counts.values())})


@login_required
@require_http_methods(["GET", "POST"])
def conversation_detail_view(request, conversation_id):
    conversation = get_object_or_404(
        _conversation_queryset_for(request.user), pk=conversation_id,
        swipe__interest_status=JobSwipe.InterestStatus.ACCEPTED,
    )
    membership = CompanyMembership.objects.filter(
        user=request.user, company=conversation.swipe.job.company, is_active=True
    ).exists()
    if request.user != conversation.swipe.user and not membership:
        return HttpResponseForbidden("You do not have access to this conversation.")

    form = MessageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        Message.objects.create(conversation=conversation, sender=request.user, body=form.cleaned_data["body"])
        Conversation.objects.filter(pk=conversation.pk).update(updated_at=timezone.now())
        return redirect("jobs:conversation_detail", conversation_id=conversation.pk)
    unread = conversation.messages.exclude(sender=request.user).filter(read_at__isnull=True)
    unread.update(read_at=timezone.now())
    message_list = conversation.messages.select_related("sender")
    return render(request, "jobs/conversation_detail.html", {
        "conversation": conversation, "messages_list": message_list, "form": form,
        "is_candidate": request.user == conversation.swipe.user,
    })
