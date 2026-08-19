from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from guardian.admin import GuardedModelAdmin

from apps.parser.models import (
    ChannelModerator,
    ChannelStats,
    Post,
    PostAnalysis,
    PostReaction,
    TelegramChannel,
)
from apps.parser.serializers import PostSerializer


@admin.register(TelegramChannel)
class TelegramChannelAdmin(GuardedModelAdmin):
    list_display = [
        "channel_id",
        "title",
        "username",
        "participants_count",
        "average_views",
        "parsed_at",
    ]
    list_filter = ["parsed_at", "creation_date"]
    search_fields = ["title", "username", "description"]
    readonly_fields = ["channel_id", "parsed_at", "creation_date"]
    ordering = ["-parsed_at"]

    fieldsets = (
        (
            "Основная информация",
            {"fields": ("channel_id", "username", "title", "description")},
        ),
        (
            "Статистика",
            {
                "fields": (
                    "participants_count",
                    "average_views",
                    "pinned_messages",
                    "last_messages",
                )
            },
        ),
        (
            "Метаданные",
            {
                "fields": ("parsed_at", "creation_date"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(ChannelStats)
class ChannelStatsAdmin(GuardedModelAdmin):
    list_display = [
        "channel",
        "participants_count",
        "daily_growth",
        "parsed_at",
    ]
    list_filter = ["parsed_at", "channel"]
    search_fields = ["channel__title", "channel__username"]
    readonly_fields = ["parsed_at"]
    ordering = ["-parsed_at"]

    fieldsets = (
        ("Канал", {"fields": ("channel",)}),
        (
            "Статистика",
            {"fields": ("participants_count", "daily_growth", "parsed_at")},
        ),
    )


class ChannelModeratorInline(admin.TabularInline):
    model = ChannelModerator
    extra = 1
    fields = [
        "user",
        "is_owner",
        "can_edit",
        "can_delete",
        "can_manage_moderators",
        "created_at",
    ]
    readonly_fields = ["created_at"]


@admin.register(ChannelModerator)
class ChannelModeratorAdmin(GuardedModelAdmin):
    list_display = [
        "user",
        "channel",
        "is_owner",
        "can_edit",
        "can_delete",
        "can_manage_moderators",
        "created_at",
    ]
    list_filter = [
        "is_owner",
        "can_edit",
        "can_delete",
        "can_manage_moderators",
        "created_at",
    ]
    search_fields = [
        "user__username",
        "user__email",
        "channel__title",
        "channel__username",
    ]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]

    fieldsets = (
        ("Связь", {"fields": ("user", "channel")}),
        (
            "Права",
            {
                "fields": (
                    "is_owner",
                    "can_edit",
                    "can_delete",
                    "can_manage_moderators",
                )
            },
        ),
        ("Метаданные", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[ChannelModerator]:
        return super().get_queryset(request).select_related("user", "channel")  # type: ignore[no-untyped-call]


class PostReactionInline(admin.TabularInline):
    model = PostReaction
    extra = 0
    fields = ["emoji", "count"]


class PostAnalysisInline(admin.StackedInline):
    """
    Inline для отображения нового AI-анализа (дизайн §4)
    внутри карточки поста.
    """

    model = PostAnalysis
    can_delete = False
    verbose_name = "AI Анализ (Новый формат)"
    verbose_name_plural = "AI Анализы (Новый формат)"
    extra = 0
    fields = [
        "why_worked",
        "how_to_improve",
        "similar_posts",
        "model_version",
        "created_at",
    ]
    readonly_fields = ["created_at"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = PostSerializer.get_admin_list_display()
    list_filter = PostSerializer.get_admin_list_filter()
    search_fields = PostSerializer.get_admin_search_fields()
    inlines = [PostReactionInline, PostAnalysisInline]

    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    text_preview.short_description = "Текст"  # type: ignore

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("channel")
            .prefetch_related("reactions")
        )


@admin.register(PostAnalysis)
class PostAnalysisAdmin(admin.ModelAdmin):
    list_display = ("post", "created_at", "model_version")
    list_filter = ("created_at",)
    search_fields = ("post__telegram_message_id",)


# Добавляем inline для модераторов в админку каналов
TelegramChannelAdmin.inlines = [ChannelModeratorInline]
