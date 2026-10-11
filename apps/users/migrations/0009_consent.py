import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0008_datasubjectrequestlog"),
    ]

    operations = [
        migrations.CreateModel(
            name="Consent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "document_type",
                    models.CharField(
                        choices=[
                            ("privacy_policy", "Privacy policy"),
                            ("personal_data", "Personal data consent"),
                            ("cookie_analytics", "Cookie analytics"),
                        ],
                        max_length=32,
                        verbose_name="Document type",
                    ),
                ),
                (
                    "version",
                    models.CharField(
                        max_length=32,
                        verbose_name="Document version",
                    ),
                ),
                (
                    "timestamp",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="Accepted at",
                    ),
                ),
                (
                    "ip",
                    models.GenericIPAddressField(
                        blank=True,
                        null=True,
                        verbose_name="IP address",
                    ),
                ),
                (
                    "user_agent",
                    models.TextField(blank=True, verbose_name="User agent"),
                ),
                (
                    "source",
                    models.CharField(
                        choices=[
                            ("email_registration", "Email registration"),
                            ("yandex_oauth", "Yandex OAuth"),
                            ("cookie_banner", "Cookie banner"),
                        ],
                        max_length=32,
                        verbose_name="Source",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="consents",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "Consent",
                "verbose_name_plural": "Consents",
                "db_table": "user_consents",
                "ordering": ["-timestamp", "-id"],
                "indexes": [
                    models.Index(
                        fields=["user", "document_type", "version"],
                        name="user_consen_user_id_44adf9_idx",
                    ),
                    models.Index(
                        fields=["timestamp"],
                        name="user_consen_timesta_892bf4_idx",
                    ),
                ],
            },
        ),
    ]
