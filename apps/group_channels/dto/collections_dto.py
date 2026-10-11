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


class CollectionSectionDTO(BaseModel):
    """Данные секции с группировкой по категориям и посекционным счетчиком"""

    title: str
    collections: list[CollectionDTO]
    count: int = Field(ge=0)


class CollectionsFiltersDTO(BaseModel):
    """Доступные варианты фильтров каталога."""

    q: str | None = None
    country: str | None = None
    category: str | None = None
    country_options: list[str] = Field(default_factory=list)
    category_options: list[str] = Field(default_factory=list)


class CollectionsCatalogDTO(BaseModel):
    """Данные публичного каталога подборок."""

    featured: list[CollectionDTO]
    collections: list[CollectionDTO]
    sections: list[CollectionSectionDTO]
    filters: CollectionsFiltersDTO
