from django.db import migrations
from django.utils import timezone

OLD_CODE = "moderated_channels"
NEW_CODE = "channel_moderator"
NEW_NAME = "Модератор канала"


def forwards(apps, schema_editor):
    db = schema_editor.connection.alias
    Role = apps.get_model("users", "Role")
    User = apps.get_model("users", "User")
    UserRoleHistory = apps.get_model("users", "UserRoleHistory")

    old = Role.objects.using(db).filter(code=OLD_CODE).first()
    new = Role.objects.using(db).filter(code=NEW_CODE).first()

    if old and not new:
        old.code = NEW_CODE
        old.name = NEW_NAME
        old.save(using=db, update_fields=["code", "name"])
    elif old and new:
        conflicting = (
            UserRoleHistory.objects.using(db)
            .filter(role=new, end_date__isnull=True)
            .values_list("user_id", flat=True)
        )

        UserRoleHistory.objects.using(db).filter(
            role=old,
            end_date__isnull=True,
            user_id__in=list(conflicting),
        ).update(end_date=timezone.now())

        UserRoleHistory.objects.using(db).filter(role=old).update(role=new)
        old.delete(using=db)
    elif not old and not new:
        Role.objects.using(db).create(code=NEW_CODE, name=NEW_NAME)

    User.objects.using(db).filter(role=OLD_CODE).update(role=NEW_CODE)


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0014_seed_admin_role"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
