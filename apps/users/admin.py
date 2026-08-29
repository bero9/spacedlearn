from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ("SpacedLearn", {
            "fields": ("role",)
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("SpacedLearn", {
            "fields": ("role",)
        }),
    )