from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import JobPreference
from .models import Company, Job, JobBookmark, JobSwipe


class JobBookmarkAndRankingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="candidate6@example.com",
            password="Strong-Test-Password-123",
            full_name="Candidate Six",
        )
        self.client.force_login(self.user)
        self.company = Company.objects.create(name="Matching Test Company", website="https://example.com")
        self.python_job = Job.objects.create(
            company=self.company, title="Junior Python Developer",
            description="Build Python and Django services.", required_skills="Python, Django, SQL",
            location="Chennai, Tamil Nadu", work_mode=Job.WorkMode.REMOTE,
            employment_type=Job.EmploymentType.FULL_TIME,
            experience_level=Job.ExperienceLevel.FRESHER,
            minimum_salary=400000, maximum_salary=600000,
            application_url="https://example.com/careers/python",
        )
        self.other_job = Job.objects.create(
            company=self.company, title="Senior Embedded Engineer",
            description="Firmware development.", required_skills="C, C++, Embedded",
            location="Bengaluru, Karnataka", work_mode=Job.WorkMode.ONSITE,
            employment_type=Job.EmploymentType.FULL_TIME,
            experience_level=Job.ExperienceLevel.FIVE_PLUS,
            application_url="https://example.com/careers/embedded",
        )

    def test_saved_jobs_page_only_shows_current_users_bookmarks(self):
        other = get_user_model().objects.create_user(
            email="other6@example.com", password="Strong-Test-Password-123", full_name="Other Six"
        )
        JobBookmark.objects.create(user=other, job=self.python_job)
        JobBookmark.objects.create(user=self.user, job=self.other_job)
        response = self.client.get(reverse("jobs:saved"))
        self.assertContains(response, "Senior Embedded Engineer")
        self.assertNotContains(response, "Junior Python Developer")

    def test_bookmark_toggle_adds_then_removes(self):
        url = reverse("jobs:bookmark", args=[self.python_job.pk])
        response = self.client.post(url, {"next": "feed"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(JobBookmark.objects.filter(user=self.user, job=self.python_job).exists())
        self.client.post(url, {"next": "feed"})
        self.assertFalse(JobBookmark.objects.filter(user=self.user, job=self.python_job).exists())

    def test_bookmark_endpoint_rejects_get(self):
        response = self.client.get(reverse("jobs:bookmark", args=[self.python_job.pk]))
        self.assertEqual(response.status_code, 405)

    def test_feed_displays_preference_match_score(self):
        preference, _ = JobPreference.objects.get_or_create(user=self.user)
        preference.preferred_roles = "Python Developer"
        preference.preferred_locations = "Chennai"
        preference.work_mode = JobPreference.WorkMode.REMOTE
        preference.experience_level = JobPreference.ExperienceLevel.FRESHER
        preference.save()
        response = self.client.get(reverse("jobs:feed"))
        self.assertContains(response, "preference match")
        self.assertContains(response, "Junior Python Developer")

    def test_activity_page_shows_own_summary(self):
        JobSwipe.objects.create(user=self.user, job=self.python_job, direction=JobSwipe.Direction.INTERESTED)
        JobBookmark.objects.create(user=self.user, job=self.other_job)
        response = self.client.get(reverse("jobs:activity"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Activity")
        self.assertContains(response, "Senior Embedded Engineer")

    def test_expired_jobs_are_not_bookmarkable(self):
        expired = Job.objects.create(
            company=self.company, title="Expired Role", description="Closed",
            location="Chennai", application_url="https://example.com/expired",
            closing_date=timezone.localdate() - timedelta(days=1),
        )
        response = self.client.post(reverse("jobs:bookmark", args=[expired.pk]), {"next": "feed"})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(JobBookmark.objects.filter(user=self.user, job=expired).exists())
