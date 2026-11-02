from typing import List, Optional

from pydantic import BaseModel, Field


class ChannelCardDTO(BaseModel):
    """Карточка канала в публичном каталоге (страница Channels).

    Имена полей повторяют контракт props фронтенда из
    docs/inertia-contract.md (ср. csrfToken в post_analysis_dto.py).
    """

    id: int
    name: str
    username: Optional[str] = None
    type: str
    subscribers: int = Field(ge=0)
    category: str
    verified: bool = False
    country: Optional[str] = None
    imageUrl: Optional[str] = None
    er: float = Field(ge=0)
    growth30d: float


class ChannelsCatalogDTO(BaseModel):
    """Props страницы 'Channels' (/channels/).

    Данные каналов берутся из БД; поля, которых нет в модели,
    дополняются из mocks/parser.py.
    """

    channels: List[ChannelCardDTO] = Field(default_factory=list)
