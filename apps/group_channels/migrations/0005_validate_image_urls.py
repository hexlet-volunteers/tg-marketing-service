from django.core.exceptions import ValidationError
from django.db import migrations, models

from apps.users.validators import validate_http_url


def clear_invalid_image_urls(apps, schema_editor):
    Group = apps.get_model("group_channels", "Group")
    groups = Group.objects.using(schema_editor.connection.alias)
    for pk, url in (
        groups.exclude(image_url="")
        .values_list("pk", "image_url")
        .iterator(chunk_size=1000)
    ):
        try:
            validate_http_url(url)
        except ValidationError:
            groups.filter(pk=pk).update(image_url="")


class Migration(migrations.Migration):
    dependencies = [
        (
            "group_channels",
            "0004_group_curator_group_saves_count_group_views_count",
        ),
    ]

    operations = [
        migrations.RunPython(
            clear_invalid_image_urls, migrations.RunPython.noop
        ),
        migrations.AlterField(
            model_name="group",
            name="image_url",
            field=models.TextField(
                blank=True,
                max_length=2048,
                validators=[validate_http_url],
                verbose_name="обложка группы",
            ),
        ),
    ]
