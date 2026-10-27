from django.urls import path
from . import views

app_name = "jobs"
urlpatterns = [
    path("", views.job_feed_view, name="feed"),
    path("history/", views.swipe_history_view, name="history"),
    path("saved/", views.saved_jobs_view, name="saved"),
    path("activity/", views.activity_view, name="activity"),
    path("interests/", views.candidate_interests_view, name="interests"),
    path("conversations/", views.conversation_list_view, name="conversations"),
    path("conversations/unread-counts/", views.conversation_unread_counts_view, name="conversation_unread_counts"),
    path("conversations/<int:conversation_id>/", views.conversation_detail_view, name="conversation_detail"),
    path("employer/", views.employer_dashboard_view, name="employer_dashboard"),
    path("employer/jobs/new/", views.employer_job_create_view, name="employer_job_create"),
    path("employer/interests/", views.employer_interests_view, name="employer_interests"),
    path("employer/interests/<int:swipe_id>/resume/", views.candidate_resume_view, name="candidate_resume"),
    path("employer/interests/<int:swipe_id>/<str:decision>/", views.review_interest_view, name="review_interest"),
    path("<int:pk>/", views.job_detail_view, name="detail"),
    path("<int:pk>/swipe/", views.swipe_job_view, name="swipe"),
    path("<int:pk>/save/", views.toggle_bookmark_view, name="bookmark"),
]
