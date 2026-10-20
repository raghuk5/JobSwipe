from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST
from .forms import EmailAuthenticationForm, EmployerRegisterForm, JobPreferenceForm, ProfileForm, RegisterForm
from .models import JobPreference, Profile, User


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account has been created.")
        return redirect("accounts:dashboard")
    return render(request, "accounts/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = EmailAuthenticationForm(request=request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Welcome back.")
        next_url = request.GET.get("next", "")
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return redirect(next_url)
        return redirect("jobs:employer_dashboard" if request.user.role == User.Role.EMPLOYER else "accounts:dashboard")
    return render(request, "accounts/login.html", {"form": form})


@require_http_methods(["GET", "POST"])
def employer_login_view(request):
    if request.user.is_authenticated:
        return redirect("jobs:employer_dashboard" if request.user.role == User.Role.EMPLOYER else "accounts:dashboard")
    form = EmailAuthenticationForm(request=request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if user.role != User.Role.EMPLOYER:
            form.add_error(None, "These credentials are not linked to a company account.")
        else:
            login(request, user)
            messages.success(request, "Welcome to your company workspace.")
            return redirect("jobs:employer_dashboard")
    return render(request, "accounts/employer_login.html", {"form": form})


@require_http_methods(["GET", "POST"])
def employer_register_view(request):
    if request.user.is_authenticated:
        return redirect("jobs:employer_dashboard" if request.user.role == User.Role.EMPLOYER else "accounts:dashboard")
    form = EmployerRegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        from jobs.models import Company, CompanyMembership
        with transaction.atomic():
            user = form.save(commit=False)
            user.role = User.Role.EMPLOYER
            user.save()
            company = Company.objects.create(
                name=form.cleaned_data["company_name"],
                website=form.cleaned_data.get("company_website", ""),
                headquarters=form.cleaned_data["company_headquarters"],
                description=form.cleaned_data.get("company_description", ""),
                is_verified=False,
            )
            CompanyMembership.objects.create(user=user, company=company, role=CompanyMembership.Role.OWNER)
        login(request, user)
        messages.success(request, "Company account created. Your company must be verified by an administrator before jobs can be published.")
        return redirect("jobs:employer_dashboard")
    return render(request, "accounts/employer_register.html", {"form": form})


@login_required
def dashboard_view(request):
    if request.user.role == User.Role.EMPLOYER:
        return redirect("jobs:employer_dashboard")
    profile, _ = Profile.objects.get_or_create(user=request.user)
    preferences, _ = JobPreference.objects.get_or_create(user=request.user)
    return render(request, "accounts/dashboard.html", {"profile":profile, "preferences":preferences})


@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your profile has been saved.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form":form, "profile":profile})


@login_required
@require_http_methods(["GET", "POST"])
def preferences_view(request):
    preferences, _ = JobPreference.objects.get_or_create(user=request.user)
    form = JobPreferenceForm(request.POST or None, instance=preferences)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, "Your job preferences have been saved.")
        return redirect("accounts:preferences")
    return render(request, "accounts/preferences.html", {"form":form})


def home_view(request):
    return redirect("accounts:dashboard" if request.user.is_authenticated else "accounts:login")


@require_POST
def logout_view(request):
    """Log out safely, then send each account type to its own login page."""
    is_employer = request.user.is_authenticated and request.user.role == User.Role.EMPLOYER
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("accounts:employer_login" if is_employer else "accounts:login")
