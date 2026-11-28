from typing import Any, cast

from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic.base import View

from apps.ai.services.ai_cabinet_service import AICabinetService
from apps.users.models import User
from config.mixins import UserAuthenticationCheckMixin
from config.renderers import render_inertia_from_dto


class AICabinetView(UserAuthenticationCheckMixin, View):
    """AI-кабинет автора (Inertia: AICabinet).

    Данные собираются из AIInsight, Post, TelegramChannel и ChannelStats.
    """

    def get(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        user = cast(User, request.user)

        assignments = user.moderated_channels.select_related(
            "channel"
        ).order_by("channel_id")

        requested_channel_id = request.GET.get("channel_id")

        if requested_channel_id is None:
            assignment = assignments.first()

            if assignment is None:
                raise PermissionDenied(
                    "Кабинет доступен только владельцам и модераторам каналов"
                )
        else:
            if not requested_channel_id.isdecimal():
                raise Http404("Канал не найден")

            assignment = get_object_or_404(
                assignments,
                channel_id=int(requested_channel_id),
            )

        dto = AICabinetService(
            user=user,
            channel=assignment.channel,
        ).build()

        return render_inertia_from_dto(
            request,
            "AICabinet",
            props=dto,
        )
