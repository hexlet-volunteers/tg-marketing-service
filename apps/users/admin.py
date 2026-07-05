from django.contrib import admin
from guardian.admin import GuardedModelAdminMixin

from apps.parser.models import ChannelModerator
from apps.users.models import PartnerProfile, User


class ChannelModeratorInline(admin.TabularInline):
    model = ChannelModerator
    extra = 0
    fields = ('channel', 'is_owner', 'can_edit', 'can_delete', 'can_manage_moderators', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True


class PartnerProfileInline(admin.StackedInline):
    model = PartnerProfile
    extra = 0
    fields = ('status', 'balance', 'payment_details')
    readonly_fields = ('partner_since', 'partner_code')
    show_change_link = True


@admin.register(User)
class CustomUserAdmin(GuardedModelAdminMixin, admin.ModelAdmin):
    list_display = ('username', 'email', 'date_joined', 'is_staff', 'is_partner', 'is_channel_moderator')
    list_select_related = ('partner_profile',)
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    inlines = [PartnerProfileInline, ChannelModeratorInline]

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'email', 'avatar_image', 'bio')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    def is_partner(self, obj):
        return hasattr(obj, 'partner_profile') and obj.partner_profile.status == 'active'

    is_partner.boolean = True
    is_partner.short_description = 'Партнер'

    def is_channel_moderator(self, obj):
        return obj.moderated_channels.exists()

    is_channel_moderator.boolean = True
    is_channel_moderator.short_description = 'Модератор канала'


@admin.register(PartnerProfile)
class PartnerProfileAdmin(GuardedModelAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'status', 'formatted_balance', 'partner_since', 'truncated_payment_details')
    list_editable = ('status',)
    list_filter = ('status', ('partner_since', admin.DateFieldListFilter))
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('partner_since', 'partner_code')
    raw_id_fields = ('user',)
    date_hierarchy = 'partner_since'
    actions = ['activate_selected', 'deactivate_selected']

    fieldsets = (
        (None, {
            'fields': ('user', 'status', 'balance')
        }),
        ('Платежная информация', {
            'fields': ('payment_details',),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('partner_code', 'partner_since'),
            'classes': ('collapse',)
        }),
    )

    def formatted_balance(self, obj):
        return f"{obj.balance:.2f}" if obj.balance else "0.00"

    formatted_balance.short_description = 'Баланс'

    def truncated_payment_details(self, obj):
        return obj.payment_details[:50] + '...' if obj.payment_details else ''

    truncated_payment_details.short_description = 'Реквизиты'

    @admin.action(description='Активировать выбранных партнеров')
    def activate_selected(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'Активировано {updated} партнерских профилей')

    @admin.action(description='Деактивировать выбранных партнеров')
    def deactivate_selected(self, request, queryset):
        updated = queryset.update(status='suspended')
        self.message_user(request, f'Деактивировано {updated} партнерских профилей')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
