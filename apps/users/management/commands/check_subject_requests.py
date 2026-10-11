from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.users.account_deletion import process_account_deletion
from apps.users.models import DataSubjectRequestLog


class Command(BaseCommand):
    help = "Report overdue subject requests; optionally retry account erasure."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--retry", action="store_true")

    def handle(self, *args: Any, **options: Any) -> None:
        unfinished = DataSubjectRequestLog.objects.exclude(
            status=DataSubjectRequestLog.Status.COMPLETED
        )
        if options["retry"]:
            for request_log in unfinished.filter(
                request_type__in=[
                    DataSubjectRequestLog.RequestType.DELETION,
                    DataSubjectRequestLog.RequestType.WITHDRAWAL,
                ]
            ).iterator():
                process_account_deletion(request_log)
        overdue = unfinished.filter(due_at__lt=timezone.now())
        for request_log in overdue:
            self.stdout.write(
                f"{request_log.pk}: {request_log.request_type} "
                f"{request_log.status}; due {request_log.due_at.isoformat()}"
            )
        if overdue.exists():
            raise CommandError("Overdue subject requests require action")
        self.stdout.write("No overdue subject requests")
