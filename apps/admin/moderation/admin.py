from django.contrib import admin

from apps.admin.moderation.models import ModerationRequest


@admin.register(ModerationRequest)
class ModerationRequestAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "submitted_by",
        "channel_identifier",
        "channel_by",
        "category",
        "country",
        "language",
        "status",
        "moderator",
    ]
    list_filter = ["status"]
    search_fields = ["channel_identifier", "category", "country", "language"]
    readonly_fields = ["id"]
    ordering = ["-id"]
