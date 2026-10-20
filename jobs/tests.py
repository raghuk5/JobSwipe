from datetime import timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from .models import Company, Job


class CompanyJobModelTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Example Technologies",
            website="https://example.com",
            headquarters="Chennai, Tamil Nadu",
            is_verified=True,
        )

    def test_create_job(self):
        job = Job.objects.create(
            company=self.company,
            title="Junior Python Developer",
            description="Build Python web applications.",
            required_skills="Python, Django, SQL",
            location="Chennai, Tamil Nadu",
            work_mode=Job.WorkMode.HYBRID,
            employment_type=Job.EmploymentType.FULL_TIME,
            experience_level=Job.ExperienceLevel.FRESHER,
            minimum_salary=300000,
            maximum_salary=500000,
            application_url="https://example.com/careers/python-developer",
        )
        self.assertEqual(job.company.name, "Example Technologies")
        self.assertTrue(job.is_open)

    def test_salary_range_validation(self):
        job = Job(company=self.company, title="Python Developer", description="Role",
                  location="India", application_url="https://example.com/jobs",
                  minimum_salary=600000, maximum_salary=300000)
        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_closing_date_before_posted_date_is_invalid(self):
        today = timezone.localdate()
        job = Job(company=self.company, title="Analyst", description="Role",
                  location="Remote", application_url="https://example.com/jobs",
                  posted_at=today, closing_date=today - timedelta(days=1))
        with self.assertRaises(ValidationError):
            job.full_clean()

    def test_expired_or_inactive_job_is_not_open(self):
        expired = Job.objects.create(company=self.company, title="Expired",
            description="Role", location="India", application_url="https://example.com/jobs",
            closing_date=timezone.localdate() - timedelta(days=1))
        inactive = Job.objects.create(company=self.company, title="Inactive",
            description="Role", location="India", application_url="https://example.com/jobs",
            is_active=False)
        self.assertFalse(expired.is_open)
        self.assertFalse(inactive.is_open)

    def test_company_cannot_be_deleted_while_jobs_exist(self):
        Job.objects.create(company=self.company, title="Existing", description="Role",
            location="India", application_url="https://example.com/jobs")
        with self.assertRaises(Exception):
            self.company.delete()
