from __future__ import annotations

from apps.ai.dto.ai_cabinet_dto import (
    AICabinetDTO,
    ChannelContextDTO,
    CompetitorDTO,
    IdeaDTO,
    InsightDTO,
)
from apps.parser.models import AIInsight, TelegramChannel
from apps.users.models import User
from mocks import ai as ai_mocks
from mocks.users import DEMO_USERNAMES

INSIGHTS_LIMIT = 4


class AICabinetService:
    """Собирает props страницы 'AICabinet'.

    Инсайты фильтруются по пользователю и выбранному каналу.
    Идеи, конкуренты и тепловая карта пока берутся из мок-реестра,
    если в базе включены демоданные.
    """

    def __init__(
        self,
        user: User,
        channel: TelegramChannel,
    ) -> None:
        self.user = user
        self.channel = channel

    def build(self) -> AICabinetDTO:
        demo_enabled = self._demo_enabled()
        return AICabinetDTO(
            channel=ChannelContextDTO(
                id=self.channel.pk,
                title=self.channel.title,
            ),
            ideas=(
                [IdeaDTO.model_validate(item) for item in ai_mocks.MOCK_IDEAS]
                if demo_enabled
                else []
            ),
            insights=self._build_insights(),
            competitors=(
                [
                    CompetitorDTO.model_validate(item)
                    for item in ai_mocks.MOCK_COMPETITORS
                ]
                if demo_enabled
                else []
            ),
            heatMapData=ai_mocks.MOCK_HEAT_MAP if demo_enabled else {},
        )

    def _build_insights(self) -> list[InsightDTO]:
        insights = AIInsight.objects.filter(
            user=self.user,
            channel=self.channel,
        )
        return [
            InsightDTO.model_validate(
                {
                    "type": insight.insight_type,
                    "text": insight.insight_text,
                }
            )
            for insight in insights.order_by("-created_at")[:INSIGHTS_LIMIT]
        ]

    def _demo_enabled(self) -> bool:
        return AIInsight.objects.filter(
            user__username__in=DEMO_USERNAMES
        ).exists()
