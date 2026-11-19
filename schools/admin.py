from django.contrib import admin
from .models import School

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "status", "created_at", "approved_at")
    list_filter = ("status",)
    search_fields = ("name", "email", "registration_number")
    readonly_fields = ("id", "slug", "created_at", "updated_at", "approved_at")
