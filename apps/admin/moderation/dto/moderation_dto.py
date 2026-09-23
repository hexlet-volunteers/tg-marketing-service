from pydantic import BaseModel

from apps.admin.moderation.types import ModerationRequestData


class PaginationDTO(BaseModel):
    page: int
    perPage: int
    pages: int
    hasNext: bool
    hasPrevious: bool


class ModerationDTO(BaseModel):
    pendingRequests: list[ModerationRequestData]
    pendingCount: int
    pagination: PaginationDTO
