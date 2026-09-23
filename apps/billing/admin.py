from django.contrib import admin

from .models import Plan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "monthly_price",
        "annual_price",
        "currency",
        "channels_limit",
        "ai_requests_limit",
        "is_highlighted",
        "ordering",
    )
    list_display_links = ("name",)
    list_editable = (
        "is_highlighted",
        "ordering",
    )
    ordering = ("ordering", "id")
    search_fields = (
        "name",
        "code",
        "description",
    )
