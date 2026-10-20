from pathlib import Path
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if not extra_fields.get("is_staff") or not extra_fields.get("is_superuser"):
            raise ValueError("A superuser must have is_staff=True and is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        CANDIDATE = "candidate", "Candidate"
        EMPLOYER = "employer", "Employer"

    role = models.CharField(max_length=12, choices=Role.choices, default=Role.CANDIDATE)
    username = None
    email = models.EmailField("email address", unique=True)
    full_name = models.CharField(max_length=120, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()
    def __str__(self):
        return self.email


def validate_resume(file_obj):
    if file_obj.size > 5 * 1024 * 1024:
        raise ValidationError("Resume must be 5 MB or smaller.")
    if Path(file_obj.name).suffix.lower() not in {".pdf", ".doc", ".docx"}:
        raise ValidationError("Upload a PDF, DOC, or DOCX resume.")


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    qualification = models.CharField(max_length=160, blank=True)
    skills = models.TextField(blank=True, help_text="Enter skills separated by commas.")
    experience_years = models.DecimalField(max_digits=4, decimal_places=1, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(60)])
    resume = models.FileField(upload_to="resumes/", blank=True,
        validators=[validate_resume])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Profile: {self.user.email}"


class JobPreference(models.Model):
    class WorkMode(models.TextChoices):
        ANY = "any", "Any work mode"
        ONSITE = "onsite", "On-site"
        HYBRID = "hybrid", "Hybrid"
        REMOTE = "remote", "Remote"
    class EmploymentType(models.TextChoices):
        ANY = "any", "Any employment type"
        FULL_TIME = "full_time", "Full-time"
        PART_TIME = "part_time", "Part-time"
        CONTRACT = "contract", "Contract"
        INTERNSHIP = "internship", "Internship"
    class ExperienceLevel(models.TextChoices):
        ANY = "any", "Any experience level"
        FRESHER = "fresher", "Fresher / Entry-level"
        ONE_TO_THREE = "1_3", "1–3 years"
        THREE_TO_FIVE = "3_5", "3–5 years"
        FIVE_PLUS = "5_plus", "5+ years"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="job_preference")
    preferred_roles = models.TextField(blank=True, help_text="Examples: Python Developer, Data Analyst")
    preferred_locations = models.TextField(blank=True, help_text="Examples: Chennai, Bengaluru, Remote, Pan India")
    minimum_salary = models.PositiveIntegerField(null=True, blank=True, help_text="Minimum annual salary in INR.")
    maximum_salary = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum annual salary in INR.")
    work_mode = models.CharField(max_length=12, choices=WorkMode.choices, default=WorkMode.ANY)
    employment_type = models.CharField(max_length=12, choices=EmploymentType.choices, default=EmploymentType.ANY)
    experience_level = models.CharField(max_length=12, choices=ExperienceLevel.choices, default=ExperienceLevel.ANY)
    willing_to_relocate = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.minimum_salary is not None and self.maximum_salary is not None and self.minimum_salary > self.maximum_salary:
            raise ValidationError({"maximum_salary": "Maximum salary must be greater than or equal to minimum salary."})
    def __str__(self):
        return f"Job preferences: {self.user.email}"
