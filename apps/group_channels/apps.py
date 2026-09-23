from django.apps import AppConfig


class ChannelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.group_channels"

    def ready(self) -> None:
        from apps.group_channels import signals  # noqa: F401
