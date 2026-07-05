from django.contrib import admin
from guardian.admin import GuardedModelAdminMixin

from apps.parser.models import ChannelModerator, ChannelStats, TelegramChannel


@admin.register(TelegramChannel)
class TelegramChannelAdmin(GuardedModelAdminMixin, admin.ModelAdmin):
    list_display = ['channel_id', 'title', 'username', 'participants_count', 'average_views', 'parsed_at']
    list_filter = ['parsed_at', 'creation_date']
    search_fields = ['title', 'username', 'description']
    readonly_fields = ['channel_id', 'parsed_at', 'creation_date']
    ordering = ['-parsed_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('channel_id', 'username', 'title', 'description')
        }),
        ('Статистика', {
            'fields': ('participants_count', 'average_views', 'pinned_messages', 'last_messages')
        }),
        ('Метаданные', {
            'fields': ('parsed_at', 'creation_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ChannelStats)
class ChannelStatsAdmin(GuardedModelAdminMixin, admin.ModelAdmin):
    list_display = ['channel', 'participants_count', 'daily_growth', 'parsed_at']
    list_filter = ['parsed_at', 'channel']
    search_fields = ['channel__title', 'channel__username']
    readonly_fields = ['parsed_at']
    ordering = ['-parsed_at']
    
    fieldsets = (
        ('Канал', {
            'fields': ('channel',)
        }),
        ('Статистика', {
            'fields': ('participants_count', 'daily_growth', 'parsed_at')
        }),
    )


class ChannelModeratorInline(admin.TabularInline):
    model = ChannelModerator
    extra = 1
    fields = ['user', 'is_owner', 'can_edit', 'can_delete', 'can_manage_moderators', 'created_at']
    readonly_fields = ['created_at']


@admin.register(ChannelModerator)
class ChannelModeratorAdmin(GuardedModelAdminMixin, admin.ModelAdmin):
    list_display = ['user', 'channel', 'is_owner', 'can_edit', 'can_delete', 'can_manage_moderators', 'created_at']
    list_filter = ['is_owner', 'can_edit', 'can_delete', 'can_manage_moderators', 'created_at']
    search_fields = ['user__username', 'user__email', 'channel__title', 'channel__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Связь', {
            'fields': ('user', 'channel')
        }),
        ('Права', {
            'fields': ('is_owner', 'can_edit', 'can_delete', 'can_manage_moderators')
        }),
        ('Метаданные', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'channel')


# Добавляем inline для модераторов в админку каналов
TelegramChannelAdmin.inlines = [ChannelModeratorInline]
