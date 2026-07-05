from django.contrib import admin
from guardian.admin import GuardedModelAdminMixin

# Register your models here.
from apps.group_channels.models import AutoGroupRule, Group

# Register your models here.


class AutoGroupRule(admin.StackedInline):
    model = AutoGroupRule
    can_delete = False
    extra = 0


"""Миксин GuardedModelAdminMixin от guardian расширяет возможости стандартной модели"""
"""и добавляет в админку возможность работать с правами. В верхнем правом углу кнопка <Права на объект>"""


@admin.register(Group)
class GroupAdmin(GuardedModelAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'is_editorial', 'order', 'owner')
    list_filter = ('is_editorial',)
    search_fields = ('name', 'description')
    ordering = ('order', 'name')
    filter_horizontal = ('channels',)

    def get_readonly_fields(self, request, obj=None):
        ro = super().get_readonly_fields(request, obj) or []
        if obj and hasattr(obj, 'auto_rule'):
            return tuple(set(ro) | {'channels'})
        return ro