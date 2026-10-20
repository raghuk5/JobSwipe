import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jobs", "0003_jobbookmark"),
        ("accounts", "0002_user_role"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="jobswipe",
            name="interest_status",
            field=models.CharField(
                choices=[
                    ("not_applicable", "Not applicable"),
                    ("pending", "Pending review"),
                    ("accepted", "Accepted"),
                    ("rejected", "Rejected"),
                ],
                default="not_applicable",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="jobswipe",
            name="reviewed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="jobswipe",
            name="reviewed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="reviewed_job_interests",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="CompanyMembership",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("owner", "Owner"), ("recruiter", "Recruiter")], default="recruiter", max_length=12)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="jobs.company")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="company_memberships", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["company__name", "user__email"]},
        ),
        migrations.AddConstraint(
            model_name="companymembership",
            constraint=models.UniqueConstraint(fields=("company", "user"), name="unique_company_membership"),
        ),
        migrations.CreateModel(
            name="Conversation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("swipe", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="conversation", to="jobs.jobswipe")),
            ],
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("body", models.TextField(max_length=4000)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("conversation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="jobs.conversation")),
                ("sender", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="job_messages", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["created_at", "pk"]},
        ),
    ]
