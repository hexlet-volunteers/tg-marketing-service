from typing import List, Optional

from pydantic import BaseModel, Field


class CollectionChannelDTO(BaseModel):
    """Карточка канала внутри подборки (страница Collection)."""

    name: str
    username: Optional[str] = None
    subscribers: int = Field(ge=0)
    er: float = Field(ge=0)
    growth30d: float
    color: str


class CollectionDetailDTO(BaseModel):
    """Props страницы 'Collection' (/collections/<pk>/)."""

    title: str = ""
    description: str = ""
    channel_count: int = Field(default=0, ge=0)
    channels: List[CollectionChannelDTO] = Field(default_factory=list)
