from django.core.exceptions import ValidationError
from django.db import migrations, models

from apps.users.validators import validate_http_url


def clear_invalid_avatar_urls(apps, schema_editor):
    User = apps.get_model("users", "User")
    users = User.objects.using(schema_editor.connection.alias)
    for pk, url in (
        users.exclude(avatar_image__isnull=True)
        .exclude(avatar_image="")
        .values_list("pk", "avatar_image")
        .iterator(chunk_size=1000)
    ):
        try:
            validate_http_url(url)
        except ValidationError:
            users.filter(pk=pk).update(avatar_image="")


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0012_merge_email_uniqueness_notifications"),
    ]

    operations = [
        migrations.RunPython(
            clear_invalid_avatar_urls, migrations.RunPython.noop
        ),
        migrations.AlterField(
            model_name="user",
            name="avatar_image",
            field=models.CharField(
                blank=True,
                null=True,
                max_length=2048,
                validators=[validate_http_url],
                verbose_name="url изображения профиля",
            ),
        ),
    ]
