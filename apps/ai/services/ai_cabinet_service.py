from __future__ import annotations

from typing import Any, Optional

from apps.ai.dto.ai_cabinet_dto import (
    AICabinetDTO,
    CompetitorDTO,
    IdeaDTO,
    InsightDTO,
)
from apps.parser.models import AIInsight
from mocks import ai as ai_mocks
from mocks.users import DEMO_USERNAMES

INSIGHTS_LIMIT = 4


class AICabinetService:
    """Собирает props страницы 'AICabinet'.

    Инсайты читаются из БД. Идеи, конкуренты и тепловая карта пока
    отдаются из мок-реестра, пока в БД нет соответствующих данных.
    Моки активны только пока в БД есть демо-инсайты: clear_demo удаляет
    их, и страница начинает отдавать пустые данные.
    """

    def __init__(self, user: Optional[Any] = None) -> None:
        self.user = user

    def build(self) -> AICabinetDTO:
        demo_enabled = self._demo_enabled()
        return AICabinetDTO(
            ideas=(
                [IdeaDTO.model_validate(item) for item in ai_mocks.MOCK_IDEAS]
                if demo_enabled
                else []
            ),
            insights=self._build_insights(demo_enabled),
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

    def _build_insights(self, demo_enabled: bool) -> list[InsightDTO]:
        auth_user = self._authenticated_user()
        if auth_user is not None:
            insights = AIInsight.objects.filter(user=auth_user)
        elif demo_enabled:
            insights = AIInsight.objects.filter(
                user__username__in=DEMO_USERNAMES
            )
        else:
            return []
        return [
            InsightDTO.model_validate(
                {"type": insight.insight_type, "text": insight.insight_text}
            )
            for insight in insights.order_by("-created_at")[:INSIGHTS_LIMIT]
        ]

    def _demo_enabled(self) -> bool:
        return AIInsight.objects.filter(
            user__username__in=DEMO_USERNAMES
        ).exists()

    def _authenticated_user(self) -> Optional[Any]:
        if self.user is None:
            return None
        if getattr(self.user, "is_authenticated", False):
            return self.user
        return None
