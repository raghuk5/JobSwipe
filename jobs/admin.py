from django.contrib import admin
from .models import Company, CompanyMembership, Conversation, Job, JobBookmark, JobSwipe, Message


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "headquarters", "is_verified", "updated_at")
    list_filter = ("is_verified",)
    search_fields = ("name", "headquarters", "website")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "work_mode", "employment_type", "experience_level", "is_active", "closing_date", "posted_at")
    list_filter = ("is_active", "work_mode", "employment_type", "experience_level", "company__is_verified")
    search_fields = ("title", "company__name", "location", "required_skills")
    autocomplete_fields = ("company",)
    date_hierarchy = "posted_at"
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("company",)


@admin.register(JobSwipe)
class JobSwipeAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "direction", "interest_status", "reviewed_at", "created_at", "updated_at")
    list_filter = ("direction", "interest_status", "created_at")
    search_fields = ("user__email", "job__title", "job__company__name")
    autocomplete_fields = ("user", "job")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("user", "job", "job__company")


@admin.register(CompanyMembership)
class CompanyMembershipAdmin(admin.ModelAdmin):
    list_display = ("company", "user", "role", "is_active", "created_at")
    list_filter = ("role", "is_active", "company__is_verified")
    search_fields = ("company__name", "user__email")
    autocomplete_fields = ("company", "user")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "swipe", "created_at", "updated_at")
    search_fields = ("swipe__user__email", "swipe__job__title", "swipe__job__company__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "sender", "created_at", "read_at")
    search_fields = ("sender__email", "body", "conversation__swipe__job__title")
    readonly_fields = ("created_at",)


@admin.register(JobBookmark)
class JobBookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "created_at")
    search_fields = ("user__email", "job__title", "job__company__name")
    autocomplete_fields = ("user", "job")
    readonly_fields = ("created_at",)
    list_select_related = ("user", "job", "job__company")
