from __future__ import annotations

from collections.abc import Sequence

from django.db import transaction
from django.utils import timezone

from apps.users.demo.base import BaseSeedStep
from apps.users.demo.context import DemoSeedContext
from apps.users.demo.steps import (
    BlogStep,
    ChannelsStep,
    GroupsStep,
    InsightsStep,
    LandingStep,
    ModeratorsStep,
    PostsStep,
    RolesStep,
    StatsStep,
    SubscriptionsStep,
    UsersStep,
)

DEFAULT_STEPS: tuple[BaseSeedStep, ...] = (
    RolesStep(),
    UsersStep(),
    ChannelsStep(),
    ModeratorsStep(),
    PostsStep(),
    StatsStep(),
    GroupsStep(),
    InsightsStep(),
    LandingStep(),
    SubscriptionsStep(),
    BlogStep(),
)


class DemoDataSeeder:
    """Facade that runs the demo-data seeding pipeline."""

    def __init__(
        self,
        steps: Sequence[BaseSeedStep] = DEFAULT_STEPS,
    ) -> None:
        self._steps = tuple(steps)

    @transaction.atomic
    def seed(self) -> str:
        ctx = DemoSeedContext(now=timezone.now())
        parts: list[str] = []

        for step in self._steps:
            step.seed(ctx)
            summary = step.summary(ctx)
            if summary:
                parts.append(summary)

        return " | ".join(parts)
