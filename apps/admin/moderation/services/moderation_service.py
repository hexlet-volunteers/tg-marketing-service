from django.core.paginator import Page, Paginator

from apps.admin.moderation.dto.moderation_dto import (
    ModerationDTO,
    PaginationDTO,
)
from apps.admin.moderation.types import ModerationRequestData


class ModerationListService:
    def build(
        self,
        paginator: Paginator,
        page: Page,
        data: list[ModerationRequestData],
    ) -> ModerationDTO:
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
        )
