from celery import shared_task
from django.core.management import call_command


@shared_task
def process_subject_requests() -> None:
    call_command("check_subject_requests", retry=True)
