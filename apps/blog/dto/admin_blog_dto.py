from datetime import datetime

from pydantic import BaseModel, Field


class AdminBlogArticleDTO(BaseModel):
    """Статья блога для админской вкладки «Статьи блога»."""

    id: int
    title: str
    slug: str
    excerpt: str
    cover_image: str = ""
    body: str
    category: str
    tags: list[str] = Field(default_factory=list)
    is_featured: bool
    is_published: bool
    published_at: datetime | None = None
    read_time: int = Field(ge=0)
    views_count: int = Field(ge=0)
    author_name: str | None = None
    created_at: datetime
    updated_at: datetime


class AdminBlogCategoryDTO(BaseModel):
    """Вариант категории статьи для редактора."""

    value: str
    label: str


class FieldErrorDTO(BaseModel):
    """Ошибка валидации одного поля формы."""

    message: str
    code: str


class AdminBlogDTO(BaseModel):
    """
    Props для Inertia-страницы 'AdminBlog' (/admin/blog/).

    - articles: все статьи, включая черновики, по created_at desc;
    - categories: варианты из BlogArticle.CATEGORY_CHOICES;
    - errors: ошибки формы, пустой словарь при успешном ответе.
    """

    articles: list[AdminBlogArticleDTO]
    categories: list[AdminBlogCategoryDTO]
    errors: dict[str, list[FieldErrorDTO]] = Field(default_factory=dict)
