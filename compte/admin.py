from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Notification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
    ]
    list_filter = ["role", "is_active", "is_staff"]
    fieldsets = UserAdmin.fieldsets + (
        ("Informations CarthageKids", {"fields": ("role", "telephone")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Informations CarthageKids", {"fields": ("role", "telephone", "email")}),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["destinataire", "message", "lue", "date_creation"]
    list_filter = ["lue"]
