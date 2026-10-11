from django.db import migrations

ADMIN_ROLE = {"code": "admin", "name": "Admin"}


def seed_admin_role(apps, schema_editor):
    Role = apps.get_model("users", "Role")
    Role.objects.using(schema_editor.connection.alias).get_or_create(
        code=ADMIN_ROLE["code"],
        defaults={"name": ADMIN_ROLE["name"]},
    )


def unseed_admin_role(apps, schema_editor):
    Role = apps.get_model("users", "Role")
    Role.objects.using(schema_editor.connection.alias).filter(
        code=ADMIN_ROLE["code"]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0010_subject_request_workflow"),
    ]

    operations = [
        migrations.RunPython(seed_admin_role, unseed_admin_role),
    ]
