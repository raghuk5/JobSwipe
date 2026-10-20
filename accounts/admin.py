from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import JobPreference, Profile, User

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email","full_name","role","is_staff","is_active")
    search_fields = ("email","full_name")
    fieldsets = (
        (None, {"fields":("email","password")}),
        ("Personal info", {"fields":("full_name","first_name","last_name","role")}),
        ("Permissions", {"fields":("is_active","is_staff","is_superuser","groups","user_permissions")}),
        ("Important dates", {"fields":("last_login","date_joined")}),
    )
    add_fieldsets = ((None, {"classes":("wide",),"fields":("email","full_name","password1","password2","is_staff","is_superuser")}),)
    filter_horizontal = ("groups","user_permissions")

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user","qualification","experience_years","updated_at")
    search_fields = ("user__email","qualification","skills")

@admin.register(JobPreference)
class JobPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user","work_mode","employment_type","experience_level","willing_to_relocate")
    search_fields = ("user__email","preferred_roles","preferred_locations")
    list_filter = ("work_mode","employment_type","experience_level","willing_to_relocate")
