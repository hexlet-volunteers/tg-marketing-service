from pydantic import BaseModel, Field


class CollectionDTO(BaseModel):
    """Данные одной подборки публичного каталога."""

    id: int
    name: str
    slug: str
    description: str | None = None
    is_editorial: bool
    curator: str | None = None
    channel_count: int = Field(ge=0)
    cover: str = ""
    gradient_key: str


class CollectionsCatalogDTO(BaseModel):
    """Данные публичного каталога подборок."""

    featured: list[CollectionDTO]
    collections: list[CollectionDTO]
