from __future__ import annotations

import os
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.users.demo import (
    DEFAULT_POSTS_PER_CHANNEL,
    DEFAULT_STATS_DAYS,
    DEMO_CHANNEL_ID_MIN,
    DemoDataSeeder,
)

__all__ = [
    "Command",
    "DEFAULT_POSTS_PER_CHANNEL",
    "DEFAULT_STATS_DAYS",
    "DEMO_CHANNEL_ID_MIN",
]


class Command(BaseCommand):
    help = "Сидирует БД из централизованных моков (mocks/)."

    def handle(self, *args: Any, **options: Any) -> None:
        if os.getenv("PROD") == "t":
            raise CommandError(
                "Команда seed_demo недоступна в production (PROD=t)."
            )

        if not settings.DEBUG:
            raise CommandError(
                "Команда seed_demo доступна только в DEBUG-режиме."
            )

        summary = DemoDataSeeder().seed()
        self.stdout.write(self.style.SUCCESS(summary))
