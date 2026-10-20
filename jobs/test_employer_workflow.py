from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Company, CompanyMembership, Conversation, Job, JobSwipe, Message

User = get_user_model()


class EmployerReviewAndChatTests(TestCase):
    def setUp(self):
        self.candidate = User.objects.create_user(
            email="candidate-flow@example.com", password="Strong-Test-Password-123", full_name="Candidate Flow"
        )
        self.employer = User.objects.create_user(
            email="employer-flow@example.com", password="Strong-Test-Password-123",
            full_name="Recruiter Flow", role=User.Role.EMPLOYER,
        )
        self.other_user = User.objects.create_user(
            email="other-flow@example.com", password="Strong-Test-Password-123", full_name="Other User"
        )
        self.company = Company.objects.create(name="Workflow Company", is_verified=True)
        CompanyMembership.objects.create(user=self.employer, company=self.company, role=CompanyMembership.Role.OWNER)
        self.job = Job.objects.create(
            company=self.company, title="Junior Python Developer", description="Python role",
            location="Chennai", application_url="https://example.com/apply",
        )

    def test_candidate_interest_starts_pending_and_does_not_redirect_offsite(self):
        self.client.force_login(self.candidate)
        response = self.client.post(reverse("jobs:swipe", args=[self.job.pk]), {"direction": "interested"})
        self.assertRedirects(response, reverse("jobs:interests"))
        swipe = JobSwipe.objects.get(user=self.candidate, job=self.job)
        self.assertEqual(swipe.interest_status, JobSwipe.InterestStatus.PENDING)
        self.assertFalse(Conversation.objects.filter(swipe=swipe).exists())

    def test_employer_acceptance_creates_conversation(self):
        swipe = JobSwipe.objects.create(
            user=self.candidate, job=self.job, direction=JobSwipe.Direction.INTERESTED,
            interest_status=JobSwipe.InterestStatus.PENDING,
        )
        self.client.force_login(self.employer)
        response = self.client.post(reverse("jobs:review_interest", args=[swipe.pk, "accept"]))
        self.assertRedirects(response, reverse("jobs:employer_interests"))
        swipe.refresh_from_db()
        self.assertEqual(swipe.interest_status, JobSwipe.InterestStatus.ACCEPTED)
        self.assertTrue(Conversation.objects.filter(swipe=swipe).exists())

    def test_rejection_does_not_create_conversation(self):
        swipe = JobSwipe.objects.create(
            user=self.candidate, job=self.job, direction=JobSwipe.Direction.INTERESTED,
            interest_status=JobSwipe.InterestStatus.PENDING,
        )
        self.client.force_login(self.employer)
        self.client.post(reverse("jobs:review_interest", args=[swipe.pk, "reject"]))
        swipe.refresh_from_db()
        self.assertEqual(swipe.interest_status, JobSwipe.InterestStatus.REJECTED)
        self.assertFalse(Conversation.objects.filter(swipe=swipe).exists())

    def test_only_candidate_and_company_member_can_access_accepted_chat(self):
        swipe = JobSwipe.objects.create(
            user=self.candidate, job=self.job, direction=JobSwipe.Direction.INTERESTED,
            interest_status=JobSwipe.InterestStatus.ACCEPTED,
        )
        conversation = Conversation.objects.create(swipe=swipe)
        self.client.force_login(self.other_user)
        response = self.client.get(reverse("jobs:conversation_detail", args=[conversation.pk]))
        self.assertEqual(response.status_code, 404)

    def test_chat_message_persists_for_authorized_participant(self):
        swipe = JobSwipe.objects.create(
            user=self.candidate, job=self.job, direction=JobSwipe.Direction.INTERESTED,
            interest_status=JobSwipe.InterestStatus.ACCEPTED,
        )
        conversation = Conversation.objects.create(swipe=swipe)
        self.client.force_login(self.candidate)
        response = self.client.post(reverse("jobs:conversation_detail", args=[conversation.pk]), {"body": "Hello, thank you for accepting."})
        self.assertRedirects(response, reverse("jobs:conversation_detail", args=[conversation.pk]))
        self.assertTrue(Message.objects.filter(conversation=conversation, sender=self.candidate).exists())

    def test_unverified_company_cannot_publish_jobs(self):
        self.company.is_verified = False
        self.company.save(update_fields=["is_verified"])
        self.client.force_login(self.employer)
        response = self.client.get(reverse("jobs:employer_job_create"))
        self.assertRedirects(response, reverse("jobs:employer_dashboard"))
