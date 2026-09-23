from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ArticleCardDTO(BaseModel):
    """Карточка статьи для списка блога."""

    id: int
    slug: str
    title: str
    excerpt: str
    cover_image: str = ""
    category: str
    tags: List[str] = Field(default_factory=list)
    read_time: int = Field(ge=0)
    published_at: Optional[datetime] = None
    views_count: int = Field(ge=0)
    author_name: Optional[str] = None


class BlogListDTO(BaseModel):
    """
    Props для Inertia-страницы 'Blog' (/blog/).

    - featured: выделенная статья (последняя is_featured & is_published);
    - articles: остальные статьи, упорядоченные по published_at desc.
    """

    featured: Optional[ArticleCardDTO] = None
    articles: List[ArticleCardDTO]


class CallToActionDTO(BaseModel):
    """Дескриптор CTA-кнопки внизу статьи: текст и ссылка."""

    label: str
    url: str


class ArticleDetailDTO(BaseModel):
    """
    Props для Inertia-страницы 'BlogArticle' (/blog/<slug>/).

    Отдаётся только для опубликованной статьи (is_published=True);
    для отсутствующей или неопубликованной вью отвечает 404.

    - id, slug, title, excerpt, cover_image, category, tags, read_time,
      published_at, views_count, author_name: как в ArticleCardDTO;
    - body: тело статьи в формате Markdown, HTML собирает фронтенд;
    - cta: дескриптор кнопки внизу статьи;
    - related: блок «Читайте также», другие опубликованные статьи.
    """

    id: int
    slug: str
    title: str
    excerpt: str
    cover_image: str = ""
    category: str
    tags: List[str] = Field(default_factory=list)
    read_time: int = Field(ge=0)
    published_at: Optional[datetime] = None
    views_count: int = Field(ge=0)
    author_name: Optional[str] = None
    body: str
    cta: CallToActionDTO
    related: List[ArticleCardDTO]
