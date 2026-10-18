from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0011_notificationsettings"),
        ("users", "0011_user_email_ci_unique"),
    ]

    operations = []
