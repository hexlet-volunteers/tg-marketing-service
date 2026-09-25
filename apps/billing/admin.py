from django.contrib import admin

from .models import Plan, Subscription


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


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "status",
        "billing_period",
        "current_period_end",
        "days_left",
        "is_auto_renew",
    )
    list_filter = (
        "status",
        "billing_period",
        "plan",
        "is_auto_renew",
    )
    list_select_related = ("user", "plan")
    search_fields = (
        "user__username",
        "user__email",
        "plan__name",
        "plan__code",
    )
    raw_id_fields = ("user",)
    date_hierarchy = "started_at"
    readonly_fields = ("days_left", "channels_used", "ai_requests_used")

    fieldsets = (
        (None, {"fields": ("user", "plan", "status", "billing_period")}),
        (
            "Период",
            {
                "fields": (
                    "started_at",
                    "current_period_end",
                    "is_auto_renew",
                )
            },
        ),
        (
            "Использование",
            {
                "fields": (
                    "days_left",
                    "channels_used",
                    "ai_requests_used",
                )
            },
        ),
    )

    @admin.display(description="Дней осталось")
    def days_left(self, obj: Subscription) -> int:
        return obj.days_left

    @admin.display(description="Каналов используется")
    def channels_used(self, obj: Subscription) -> int:
        return obj.channels_used

    @admin.display(description="AI-запросов использовано")
    def ai_requests_used(self, obj: Subscription) -> int:
        return obj.ai_requests_used
