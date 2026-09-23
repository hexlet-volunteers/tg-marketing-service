from typing import Any

from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.views import View
from inertia import InertiaResponse

from apps.admin.moderation.services.moderation import (
    ModerationError,
    ModerationService,
)
from apps.admin.moderation.services.moderation_service import (
    ModerationListService,
)
from apps.admin.moderation.services.queue import ModerationQueue
from apps.users.models import User
from config.mixins import AdminRequiredMixin
from config.renderers import render_inertia_from_dto


class ModerationRequestListView(AdminRequiredMixin, View):
    def get(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> InertiaResponse:
        paginator = Paginator(ModerationQueue().get_queue(), 10)
        page = paginator.get_page(request.GET.get("page", 1))
        requests_data = [
            ModerationQueue().get_queue_data(queue_item)
            for queue_item in page.object_list
        ]

        dto = ModerationListService().build(paginator, page, requests_data)
        return render_inertia_from_dto(request, "AdminModeration", props=dto)

    def post(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        action = request.POST.get("action")
        try:
            request_id = int(request.POST.get("request_id", ""))
        except (TypeError, ValueError):
            return HttpResponseBadRequest("Некорректный идентификатор заявки")

        moderator = request.user
        if not isinstance(moderator, User):
            return HttpResponseBadRequest("Некорректный пользователь")

        try:
            if action == "approve":
                category = request.POST.get("category", "")
                is_verified = request.POST.get("is_verified", "") == "true"
                ModerationService.approve(
                    request_id=request_id,
                    moderator=moderator,
                    category=category,
                    is_verified=is_verified,
                )
                flash = {"success": "Заявка одобрена"}
            elif action == "reject":
                reason = request.POST.get("reason", "")
                ModerationService.reject(
                    request_id=request_id,
                    moderator=moderator,
                    reason=reason,
                )
                flash = {"success": "Заявка отклонена"}
            else:
                return HttpResponseBadRequest("Неизвестное действие")
        except ModerationError as error:
            flash = {"error": str(error)}
        request.session["flash"] = flash

        url = request.get_full_path()
        return redirect(url)
