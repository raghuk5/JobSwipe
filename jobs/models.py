from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.conf import settings


class Company(models.Model):
    name = models.CharField(max_length=160, unique=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    headquarters = models.CharField(max_length=120, blank=True)
    logo_url = models.URLField(blank=True, help_text="Optional public logo image URL.")
    is_verified = models.BooleanField(default=False, help_text="Mark only after checking the company.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


class Job(models.Model):
    class WorkMode(models.TextChoices):
        ONSITE = "onsite", "On-site"
        HYBRID = "hybrid", "Hybrid"
        REMOTE = "remote", "Remote"

    class EmploymentType(models.TextChoices):
        FULL_TIME = "full_time", "Full-time"
        PART_TIME = "part_time", "Part-time"
        CONTRACT = "contract", "Contract"
        INTERNSHIP = "internship", "Internship"

    class ExperienceLevel(models.TextChoices):
        FRESHER = "fresher", "Fresher / Entry-level"
        ONE_TO_THREE = "1_3", "1–3 years"
        THREE_TO_FIVE = "3_5", "3–5 years"
        FIVE_PLUS = "5_plus", "5+ years"

    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="jobs")
    title = models.CharField(max_length=180)
    description = models.TextField()
    responsibilities = models.TextField(blank=True)
    required_skills = models.TextField(blank=True, help_text="Comma-separated skills.")
    location = models.CharField(max_length=120, help_text="City/state, Remote, or Pan India.")
    work_mode = models.CharField(max_length=12, choices=WorkMode.choices, default=WorkMode.ONSITE)
    employment_type = models.CharField(max_length=12, choices=EmploymentType.choices, default=EmploymentType.FULL_TIME)
    experience_level = models.CharField(max_length=12, choices=ExperienceLevel.choices, default=ExperienceLevel.FRESHER)
    minimum_salary = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0)], help_text="Optional annual salary in INR.")
    maximum_salary = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0)], help_text="Optional annual salary in INR.")
    application_url = models.URLField(help_text="Official company application page or approved application URL.")
    posted_at = models.DateField(default=timezone.localdate)
    closing_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-posted_at", "-created_at"]
        indexes = [
            models.Index(fields=["is_active", "posted_at"]),
            models.Index(fields=["location", "work_mode"]),
            models.Index(fields=["employment_type", "experience_level"]),
        ]

    def clean(self):
        super().clean()
        errors = {}
        if self.minimum_salary is not None and self.maximum_salary is not None and self.minimum_salary > self.maximum_salary:
            errors["maximum_salary"] = "Maximum salary must be greater than or equal to minimum salary."
        if self.closing_date and self.posted_at and self.closing_date < self.posted_at:
            errors["closing_date"] = "Closing date cannot be earlier than the posted date."
        if errors:
            raise ValidationError(errors)

    @property
    def is_open(self):
        today = timezone.localdate()
        return self.is_active and (self.closing_date is None or self.closing_date >= today)

    def __str__(self):
        return f"{self.title} — {self.company.name}"


class JobSwipe(models.Model):
    """A candidate's latest recorded decision for one job."""
    class Direction(models.TextChoices):
        INTERESTED = "interested", "Interested"
        SKIPPED = "skipped", "Skipped"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_swipes")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="swipes")
    direction = models.CharField(max_length=12, choices=Direction.choices)
    class InterestStatus(models.TextChoices):
        NOT_APPLICABLE = "not_applicable", "Not applicable"
        PENDING = "pending", "Pending review"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    interest_status = models.CharField(max_length=16, choices=InterestStatus.choices, default=InterestStatus.NOT_APPLICABLE)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_job_interests")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "job"], name="unique_job_swipe_per_user"),
        ]
        indexes = [
            models.Index(fields=["user", "direction"]),
            models.Index(fields=["job", "direction"]),
        ]

    def __str__(self):
        return f"{self.user} — {self.job.title}: {self.get_direction_display()}"



class JobBookmark(models.Model):
    """A private saved-job record for a candidate."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_bookmarks",
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="bookmarks",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "job"],
                name="unique_job_bookmark_per_user",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user} saved {self.job.title}"


class CompanyMembership(models.Model):
    """Grants an account permission to act for one company."""
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        RECRUITER = "recruiter", "Recruiter"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="company_memberships")
    role = models.CharField(max_length=12, choices=Role.choices, default=Role.RECRUITER)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["company", "user"], name="unique_company_membership")]
        ordering = ["company__name", "user__email"]

    def __str__(self):
        return f"{self.user.email} — {self.company.name} ({self.role})"


class Conversation(models.Model):
    """A private candidate/employer conversation enabled by an accepted interest."""
    swipe = models.OneToOneField(JobSwipe, on_delete=models.CASCADE, related_name="conversation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation: {self.swipe.user.email} / {self.swipe.job.title}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_messages")
    body = models.TextField(max_length=4000)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at", "pk"]

    def __str__(self):
        return f"Message from {self.sender.email} at {self.created_at:%Y-%m-%d %H:%M}"
