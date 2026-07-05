from django.contrib import admin
from apps.homepage.models import HomePageComponent
from guardian.admin import GuardedModelAdminMixin


@admin.register(HomePageComponent)
class HomePageComponentAdmin(GuardedModelAdminMixin, admin.ModelAdmin):
    list_display = [
        "title",
        "component_type",
        "is_active",
        "order",
        "created_at",
    ]
    list_filter = ["component_type", "is_active"]
    list_editable = ["is_active", "order"]
    search_fields = ["title"]
    ordering = ["order", "created_at"]

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("title", "component_type", "is_active", "order")},
        ),
        (
            "Содержимое",
            {
                "fields": ("content",),
                "description": "JSON с данными компонента.",
            },
        ),
    )
