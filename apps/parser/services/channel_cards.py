from apps.parser.dto.channel_catalog_dto import ChannelCardDTO
from apps.parser.models import TelegramChannel
from mocks.parser import get_mock_channel


def build_channel_card(channel: TelegramChannel) -> ChannelCardDTO:
    """Собирает карточку канала из БД с fallback полей из мока."""
    mock_channel = get_mock_channel(channel.username) or {}

    return ChannelCardDTO(
        id=channel.channel_id,
        name=channel.title,
        username=f"@{channel.username}" if channel.username else None,
        type=mock_channel.get("type") or "channel",
        subscribers=channel.participants_count or 0,
        category=channel.category or "",
        verified=channel.is_verified,
        country=channel.country,
        imageUrl=mock_channel.get("imageUrl") or "",
        er=float(getattr(channel, "citation_index", 0) or 0),
        growth30d=channel.get_growth30d(),
    )
