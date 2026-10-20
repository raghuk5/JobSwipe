from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import JobPreference
from .models import Company, Job, JobSwipe


class JobFeedViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="candidate@example.com",
            password="Strong-Test-Password-123",
            full_name="Test Candidate",
        )
        self.client.force_login(self.user)
        self.company = Company.objects.create(
            name="Example Technologies", website="https://example.com", is_verified=True
        )
        self.python_job = Job.objects.create(
            company=self.company,
            title="Junior Python Developer",
            description="Build web applications with Python.",
            required_skills="Python, Django, SQL",
            location="Chennai, Tamil Nadu",
            work_mode=Job.WorkMode.HYBRID,
            employment_type=Job.EmploymentType.FULL_TIME,
            experience_level=Job.ExperienceLevel.FRESHER,
            minimum_salary=300000,
            maximum_salary=500000,
            application_url="https://example.com/careers/python",
        )
        self.expired_job = Job.objects.create(
            company=self.company, title="Expired Data Analyst", description="An expired role.",
            location="Chennai", application_url="https://example.com/careers/expired",
            closing_date=timezone.localdate() - timedelta(days=1),
        )
        self.inactive_job = Job.objects.create(
            company=self.company, title="Inactive QA Engineer", description="Not active.",
            location="Chennai", application_url="https://example.com/careers/inactive", is_active=False,
        )

    def test_feed_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("jobs:feed"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_feed_shows_open_jobs_only(self):
        response = self.client.get(reverse("jobs:feed") + "?all=1")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Junior Python Developer")
        self.assertNotContains(response, "Expired Data Analyst")
        self.assertNotContains(response, "Inactive QA Engineer")

    def test_saved_role_and_location_preferences_filter_feed(self):
        preference, _ = JobPreference.objects.get_or_create(user=self.user)
        preference.preferred_roles = "Python Developer"
        preference.preferred_locations = "Chennai"
        preference.save()
        response = self.client.get(reverse("jobs:feed"))
        self.assertContains(response, "Junior Python Developer")
        self.assertNotContains(response, "Expired Data Analyst")

    def test_keyword_filter(self):
        response = self.client.get(reverse("jobs:feed") + "?all=1&q=Python")
        self.assertContains(response, "Junior Python Developer")
        self.assertNotContains(response, "Expired Data Analyst")

    def test_job_detail_has_application_link(self):
        response = self.client.get(reverse("jobs:detail", args=[self.python_job.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "https://example.com/careers/python")

    def test_expired_job_detail_returns_404(self):
        self.assertEqual(self.client.get(reverse("jobs:detail", args=[self.expired_job.pk])).status_code, 404)


class JobSwipeViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="swiper@example.com",
            password="Strong-Test-Password-123",
            full_name="Swipe Candidate",
        )
        self.client.force_login(self.user)
        self.company = Company.objects.create(name="Swipe Test Ltd")
        self.job = Job.objects.create(
            company=self.company,
            title="Graduate Software Engineer",
            description="Entry-level role.",
            location="Trichy, Tamil Nadu",
            application_url="https://example.com/careers/graduate-engineer",
        )

    def test_skip_records_swipe_and_removes_job_from_feed(self):
        response = self.client.post(reverse("jobs:swipe", args=[self.job.pk]), {"direction": "skipped"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("jobs:feed"))
        self.assertTrue(JobSwipe.objects.filter(user=self.user, job=self.job, direction=JobSwipe.Direction.SKIPPED).exists())
        feed = self.client.get(reverse("jobs:feed") + "?all=1")
        self.assertNotContains(feed, "Graduate Software Engineer")

    def test_interested_records_pending_review_and_redirects_to_interest_list(self):
        response = self.client.post(reverse("jobs:swipe", args=[self.job.pk]), {"direction": "interested"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("jobs:interests"))
        swipe = JobSwipe.objects.get(user=self.user, job=self.job, direction=JobSwipe.Direction.INTERESTED)
        self.assertEqual(swipe.interest_status, JobSwipe.InterestStatus.PENDING)

    def test_invalid_direction_does_not_record_swipe(self):
        response = self.client.post(reverse("jobs:swipe", args=[self.job.pk]), {"direction": "maybe"})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(JobSwipe.objects.filter(user=self.user, job=self.job).exists())

    def test_swipe_endpoint_rejects_get(self):
        response = self.client.get(reverse("jobs:swipe", args=[self.job.pk]))
        self.assertEqual(response.status_code, 405)

    def test_user_cannot_see_another_users_swipe_history(self):
        other = get_user_model().objects.create_user(
            email="other@example.com", password="Strong-Test-Password-123", full_name="Other Candidate"
        )
        JobSwipe.objects.create(user=other, job=self.job, direction=JobSwipe.Direction.SKIPPED)
        response = self.client.get(reverse("jobs:history"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Graduate Software Engineer")

    def test_history_shows_own_swipes(self):
        JobSwipe.objects.create(user=self.user, job=self.job, direction=JobSwipe.Direction.INTERESTED)
        response = self.client.get(reverse("jobs:history"))
        self.assertContains(response, "Graduate Software Engineer")
        self.assertContains(response, "Interested")

    def test_duplicate_swipe_does_not_create_duplicate_record(self):
        url = reverse("jobs:swipe", args=[self.job.pk])
        self.client.post(url, {"direction": "skipped"})
        self.client.post(url, {"direction": "interested"})
        self.assertEqual(JobSwipe.objects.filter(user=self.user, job=self.job).count(), 1)
        self.assertEqual(JobSwipe.objects.get(user=self.user, job=self.job).direction, JobSwipe.Direction.SKIPPED)
