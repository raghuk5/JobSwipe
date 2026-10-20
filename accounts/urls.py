from django.urls import path
from . import views
app_name = "accounts"
urlpatterns = [
    path("", views.home_view, name="home"),
    path("register/", views.register_view, name="register"),
    path("employer/register/", views.employer_register_view, name="employer_register"),
    path("login/", views.login_view, name="login"),
    path("employer/login/", views.employer_login_view, name="employer_login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path("preferences/", views.preferences_view, name="preferences"),
]
