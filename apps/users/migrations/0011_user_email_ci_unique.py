from django.db import migrations, models
from django.db.models.functions import Lower


def check_email_duplicates(apps, schema_editor):
    User = apps.get_model("users", "User")
    users = User.objects.using(schema_editor.connection.alias)
    duplicates = (
        users.annotate(email_ci=Lower("email"))
        .values("email_ci")
        .annotate(count=models.Count("pk"))
        .filter(count__gt=1)
    )
    user_ids = list(
        users.annotate(email_ci=Lower("email"))
        .filter(email_ci__in=duplicates.values("email_ci"))
        .order_by("pk")
        .values_list("pk", flat=True)[:20]
    )
    if user_ids:
        raise RuntimeError(
            "Cannot add users_email_ci_unique: case-insensitive email "
            "duplicates exist. Resolve conflicting accounts manually before "
            f"migrating. Conflicting user IDs (first 20): {user_ids}"
        )


class Migration(migrations.Migration):
    dependencies = [("users", "0010_subject_request_workflow")]

    operations = [
        migrations.RunPython(check_email_duplicates, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                Lower("email"), name="users_email_ci_unique"
            ),
        ),
    ]
