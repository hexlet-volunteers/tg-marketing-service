from datetime import timedelta

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


def backfill_deadlines(apps, schema_editor):
    RequestLog = apps.get_model("users", "DataSubjectRequestLog")
    for request_log in RequestLog.objects.using(
        schema_editor.connection.alias
    ).iterator():
        deadline = request_log.requested_at + timedelta(days=10)
        RequestLog.objects.using(schema_editor.connection.alias).filter(
            pk=request_log.pk
        ).update(
            due_at=deadline,
            original_due_at=deadline,
            result={"legacy_export": True},
        )


class Migration(migrations.Migration):
    dependencies = [("users", "0009_consent")]

    operations = [
        migrations.AddField(
            model_name="user",
            name="anonymized_at",
            field=models.DateTimeField(null=True, blank=True, editable=False),
        ),
        migrations.AddField(
            model_name="user",
            name="retention_basis",
            field=models.TextField(blank=True, editable=False),
        ),
        migrations.AddField(
            model_name="partnerprofile",
            name="anonymized_at",
            field=models.DateTimeField(null=True, blank=True, editable=False),
        ),
        migrations.AddField(
            model_name="partnerprofile",
            name="retention_basis",
            field=models.TextField(blank=True, editable=False),
        ),
        migrations.AlterField(
            model_name="datasubjectrequestlog",
            name="request_type",
            field=models.CharField(
                max_length=20,
                default="export",
                verbose_name="Тип запроса",
                choices=[
                    ("access", "Access"),
                    ("rectification", "Rectification"),
                    ("deletion", "Deletion"),
                    ("withdrawal", "Consent withdrawal"),
                    ("export", "Экспорт персональных данных"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="datasubjectrequestlog",
            name="status",
            field=models.CharField(
                max_length=20,
                default="received",
                verbose_name="Статус",
                choices=[
                    ("received", "Received"),
                    ("processing", "Processing"),
                    ("failed", "Failed"),
                    ("completed", "Выполнен"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="datasubjectrequestlog",
            name="requested_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                editable=False,
                verbose_name="Дата запроса",
            ),
        ),
        migrations.AlterField(
            model_name="datasubjectrequestlog",
            name="completed_at",
            field=models.DateTimeField(
                null=True, blank=True, verbose_name="Дата выполнения"
            ),
        ),
        migrations.AddField(
            model_name="datasubjectrequestlog",
            name="due_at",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="datasubjectrequestlog",
            name="original_due_at",
            field=models.DateTimeField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name="datasubjectrequestlog",
            name="result",
            field=models.JSONField(default=dict, blank=True),
        ),
        migrations.AddField(
            model_name="datasubjectrequestlog",
            name="extension_reason",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="datasubjectrequestlog",
            name="extended_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="datasubjectrequestlog",
            name="extension_notified_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="datasubjectrequestlog",
            name="extension_notification_reference",
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name="datasubjectrequestlog",
            name="responsible",
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="assigned_data_subject_requests",
            ),
        ),
        migrations.RunPython(backfill_deadlines, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="datasubjectrequestlog",
            name="due_at",
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name="datasubjectrequestlog",
            name="original_due_at",
            field=models.DateTimeField(editable=False),
        ),
        migrations.AddIndex(
            model_name="datasubjectrequestlog",
            index=models.Index(
                fields=["status", "due_at"],
                name="data_subjec_status_cde1a4_idx",
            ),
        ),
        migrations.CreateModel(
            name="ConsentWithdrawal",
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
                    "withdrawn_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                (
                    "consent",
                    models.OneToOneField(
                        to="users.consent",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="withdrawal",
                    ),
                ),
                (
                    "request_log",
                    models.ForeignKey(
                        to="users.datasubjectrequestlog",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="consent_withdrawals",
                    ),
                ),
            ],
        ),
    ]
