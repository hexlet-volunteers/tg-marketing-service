from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from apps.group_channels.models import AutoGroupRule, Group, SavedCollection

# Register your models here.


class AutoGroupRuleInline(admin.StackedInline):
    model = AutoGroupRule
    can_delete = False
    extra = 0


"""Миксин GuardedModelAdminMixin от guardian расширяет
возможости стандартной модели и добавляет в админку
возможность работать с правами. В верхнем правом углу
кнопка <Права на объект>.
"""


@admin.register(Group)
class GroupAdmin(GuardedModelAdmin):
    list_display = (
        "name",
        "is_editorial",
        "order",
        "owner",
        "curator",
        "channel_count",
        "saves_count",
        "views_count",
    )
    list_filter = ("is_editorial",)
    search_fields = ("name", "description", "curator__username")
    ordering = ("order", "name")
    filter_horizontal = ("channels",)

    @admin.display(description="Каналов")
    def channel_count(self, obj: Group) -> int:
        return obj.channel_count

    def get_readonly_fields(self, request, obj=None):
        ro = super().get_readonly_fields(request, obj) or []
        ro = tuple(set(ro) | {"saves_count", "views_count"})
        if obj and hasattr(obj, "auto_rule"):
            return tuple(set(ro) | {"channels"})
        return ro


@admin.register(SavedCollection)
class SavedCollectionAdmin(admin.ModelAdmin):
    list_display = ("user", "group", "created_at")
    search_fields = ("user__username", "group__name")
    ordering = ("-created_at",)
