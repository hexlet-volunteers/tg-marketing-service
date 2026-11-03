from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.users.demo.context import DemoSeedContext


class BaseSeedStep(ABC):
    """One idempotent step of the demo-data pipeline."""

    @abstractmethod
    def seed(self, ctx: DemoSeedContext) -> None:
        """Populate models and update the shared context."""

    def summary(self, ctx: DemoSeedContext) -> str | None:
        """Return a human-readable fragment, or None to stay silent."""
        return None
