from django.db.models import QuerySet

from apps.admin.moderation.models import ModerationRequest
from apps.admin.moderation.types import ModerationRequestData


class ModerationQueue:
    """Возвращает очередь заявок, ожидающих модерации."""

    def get_queue(self) -> QuerySet[ModerationRequest]:
        moderation_requests = ModerationRequest.objects.pending_queue()
        return moderation_requests

    def get_queue_data(
        self,
        moderation_request: ModerationRequest,
    ) -> ModerationRequestData:
        queue: ModerationRequestData = {
            "id": moderation_request.id,
            "submitted_by": (
                {
                    "id": moderation_request.submitted_by.id,
                    "username": moderation_request.submitted_by.username,
                }
                if moderation_request.submitted_by
                else None
            ),
            "channel_identifier": moderation_request.channel_identifier,
            "channel": (
                {
                    "id": moderation_request.channel_by.id,
                    "username": moderation_request.channel_by.username,
                    "title": moderation_request.channel_by.title,
                }
                if moderation_request.channel_by
                else None
            ),
            "category": moderation_request.category,
            "country": moderation_request.country,
            "language": moderation_request.language,
            "status": moderation_request.status,
            "reject_reason": moderation_request.reject_reason,
            "created_at": moderation_request.created_at.isoformat(),
            "resolved_at": (
                moderation_request.resolved_at.isoformat()
                if moderation_request.resolved_at
                else None
            ),
        }

        return queue
