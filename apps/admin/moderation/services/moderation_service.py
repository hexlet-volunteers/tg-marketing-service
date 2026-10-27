from django.core.paginator import Page, Paginator

from apps.admin.moderation.dto.moderation_dto import (
    ModerationDTO,
    PaginationDTO,
)
from apps.admin.moderation.services.queue import ModerationQueue
from apps.admin.moderation.types import ModerationRequestData


class ModerationListService:
    def __init__(self, queue: ModerationQueue | None = None) -> None:
        self.queue = queue or ModerationQueue()

    def build(
        self,
        paginator: Paginator,
        page: Page,
        data: list[ModerationRequestData],
    ) -> ModerationDTO:
        user_requests = [
            self.queue.get_user_request_data(queue_item)
            for queue_item in page.object_list
        ]

        return ModerationDTO(
            pendingRequests=data,
            pendingCount=paginator.count,
            pagination=PaginationDTO(
                page=page.number,
                perPage=paginator.per_page,
                pages=paginator.num_pages,
                hasNext=page.has_next(),
                hasPrevious=page.has_previous(),
            ),
            userRequests=user_requests,
        )
