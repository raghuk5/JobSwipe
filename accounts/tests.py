from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from .models import JobPreference, Profile

User = get_user_model()

class AuthenticationTests(TestCase):
    def test_registration_creates_and_logs_in_user(self):
        response = self.client.post(reverse("accounts:register"), {
            "full_name":"Test User", "email":"test@example.com",
            "password1":"Strong-Test-Password-42!", "password2":"Strong-Test-Password-42!",
        })
        self.assertRedirects(response, reverse("accounts:dashboard"))
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_login_uses_email_and_password(self):
        User.objects.create_user(email="login@example.com", password="Strong-Test-Password-42!")
        response = self.client.post(reverse("accounts:login"), {"username":"login@example.com","password":"Strong-Test-Password-42!"})
        self.assertRedirects(response, reverse("accounts:dashboard"))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('accounts:dashboard')}")

    def test_candidate_logout_redirects_to_candidate_login(self):
        candidate = User.objects.create_user(email="logout-candidate@example.com", password="Strong-Test-Password-42!")
        self.client.force_login(candidate)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_employer_logout_redirects_to_company_login(self):
        employer = User.objects.create_user(
            email="logout-employer@example.com", password="Strong-Test-Password-42!", role=User.Role.EMPLOYER
        )
        self.client.force_login(employer)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:employer_login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_rejects_get_requests(self):
        candidate = User.objects.create_user(email="logout-get@example.com", password="Strong-Test-Password-42!")
        self.client.force_login(candidate)
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)

class ProfilePreferenceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="person@example.com", password="Strong-Test-Password-42!")
        self.client.force_login(self.user)

    def test_profile_can_be_saved(self):
        response = self.client.post(reverse("accounts:profile"), {"qualification":"B.Tech ECE","skills":"Python, SQL","experience_years":"0"})
        self.assertRedirects(response, reverse("accounts:profile"))
        self.assertEqual(Profile.objects.get(user=self.user).qualification, "B.Tech ECE")

    def test_invalid_resume_extension_is_rejected(self):
        bad_file = SimpleUploadedFile("resume.exe", b"bad file", content_type="application/octet-stream")
        response = self.client.post(reverse("accounts:profile"), {"qualification":"B.Tech","skills":"Python","experience_years":"0","resume":bad_file})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upload a PDF, DOC, or DOCX resume.")
        self.assertFalse(Profile.objects.get(user=self.user).resume)

    def test_preferences_can_be_saved(self):
        response = self.client.post(reverse("accounts:preferences"), {
            "preferred_roles":"Python Developer, Data Analyst", "preferred_locations":"Chennai, Bengaluru, Remote",
            "minimum_salary":"300000", "maximum_salary":"600000", "work_mode":"remote",
            "employment_type":"full_time", "experience_level":"fresher", "willing_to_relocate":"on",
        })
        self.assertRedirects(response, reverse("accounts:preferences"))
        prefs = JobPreference.objects.get(user=self.user)
        self.assertEqual(prefs.minimum_salary, 300000)
        self.assertEqual(prefs.work_mode, "remote")
        self.assertTrue(prefs.willing_to_relocate)

    def test_maximum_salary_must_not_be_below_minimum(self):
        response = self.client.post(reverse("accounts:preferences"), {
            "preferred_roles":"Developer", "preferred_locations":"India",
            "minimum_salary":"600000", "maximum_salary":"300000",
            "work_mode":"any", "employment_type":"any", "experience_level":"any",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maximum salary must be greater than or equal to minimum salary.")

class EmployerAccountTests(TestCase):
    def test_employer_registration_creates_unverified_company_and_owner_membership(self):
        response = self.client.post(reverse("accounts:employer_register"), {
            "full_name": "Recruiter User",
            "email": "recruiter@example.com",
            "company_name": "Recruiter Test Company",
            "company_website": "https://company.example",
            "company_headquarters": "Chennai, Tamil Nadu",
            "company_description": "A company for testing employer registration.",
            "password1": "Strong-Test-Password-42!",
            "password2": "Strong-Test-Password-42!",
        })
        self.assertRedirects(response, reverse("jobs:employer_dashboard"))
        user = User.objects.get(email="recruiter@example.com")
        self.assertEqual(user.role, User.Role.EMPLOYER)
        from jobs.models import Company, CompanyMembership
        company = Company.objects.get(name="Recruiter Test Company")
        self.assertFalse(company.is_verified)
        self.assertTrue(CompanyMembership.objects.filter(user=user, company=company, role=CompanyMembership.Role.OWNER).exists())

    def test_candidate_credentials_cannot_use_company_login(self):
        User.objects.create_user(email="candidate-login@example.com", password="Strong-Test-Password-42!")
        response = self.client.post(reverse("accounts:employer_login"), {
            "username": "candidate-login@example.com", "password": "Strong-Test-Password-42!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "not linked to a company account")
        self.assertFalse(response.wsgi_request.user.is_authenticated)
