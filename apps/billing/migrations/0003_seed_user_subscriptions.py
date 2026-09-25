from django.conf import settings
from django.db import migrations


def seed_user_subscriptions(apps, schema_editor):
    """Назначает тариф Free всем существующим пользователям."""
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)
    Plan = apps.get_model("billing", "Plan")
    Subscription = apps.get_model("billing", "Subscription")

    free_plan = Plan.objects.filter(code="Free").first()
    if free_plan is None:
        return

    subscribed_user_ids = Subscription.objects.values_list("user_id", flat=True)
    users = User.objects.exclude(pk__in=subscribed_user_ids)

    Subscription.objects.bulk_create(
        Subscription(
            user_id=user.pk,
            plan=free_plan,
            status="active",
            billing_period="monthly",
            is_auto_renew=False,
        )
        for user in users.iterator()
    )


class Migration(migrations.Migration):
    dependencies = [
        ("billing", "0002_subscription"),
    ]

    operations = [
        migrations.RunPython(
            seed_user_subscriptions,
            migrations.RunPython.noop,
        ),
    ]
