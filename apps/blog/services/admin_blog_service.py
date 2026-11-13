from typing import Any

from apps.blog.dto.admin_blog_dto import (
    AdminBlogCategoryDTO,
    AdminBlogDTO,
)
from apps.blog.models import BlogArticle
from apps.blog.services.mappers import to_admin_article


class AdminBlogService:
    """Собирает props для админской вкладки «Статьи блога»."""

    @staticmethod
    def build_dto(
        errors: dict[str, Any] | None = None,
    ) -> AdminBlogDTO:
        articles = BlogArticle.objects.select_related("author").order_by(
            "-created_at"
        )
        return AdminBlogDTO(
            articles=[to_admin_article(article) for article in articles],
            categories=[
                AdminBlogCategoryDTO(value=value, label=label)
                for value, label in BlogArticle.CATEGORY_CHOICES
            ],
            errors=errors or {},
        )
