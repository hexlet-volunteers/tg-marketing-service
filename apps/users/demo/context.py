from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.parser.models import TelegramChannel
    from apps.users.models import User


@dataclass(slots=True)
class DemoSeedContext:
    """Shared state passed through the demo seeding pipeline."""

    now: datetime
    users: dict[str, User] = field(default_factory=dict)
    channels: list[TelegramChannel] = field(default_factory=list)
