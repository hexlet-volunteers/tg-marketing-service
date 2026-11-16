from typing import Optional

from apps.blog.dto.admin_blog_dto import AdminBlogArticleDTO
from apps.blog.dto.blog_dto import ArticleCardDTO
from apps.blog.models import BlogArticle


def get_author_name(article: BlogArticle) -> Optional[str]:
    """Имя автора: полное имя, если есть, иначе username."""
    author = article.author
    if author is None:
        return None
    return author.get_full_name() or author.username


def to_article_card(article: BlogArticle) -> ArticleCardDTO:
    """Карточка статьи: используется в списке и в блоке «Читайте также»."""
    return ArticleCardDTO(
        id=article.id,
        slug=article.slug,
        title=article.title,
        excerpt=article.excerpt,
        cover_image=article.cover_image,
        category=article.category,
        tags=list(article.tags or []),
        read_time=article.read_time,
        published_at=article.published_at,
        views_count=article.views_count,
        author_name=get_author_name(article),
    )


def to_admin_article(article: BlogArticle) -> AdminBlogArticleDTO:
    """Статья для админки: все поля редактора и служебные метаданные."""
    return AdminBlogArticleDTO(
        id=article.id,
        title=article.title,
        slug=article.slug,
        excerpt=article.excerpt,
        cover_image=article.cover_image,
        body=article.body,
        category=article.category,
        tags=list(article.tags or []),
        is_featured=article.is_featured,
        is_published=article.is_published,
        published_at=article.published_at,
        read_time=article.read_time,
        views_count=article.views_count,
        author_name=get_author_name(article),
        created_at=article.created_at,
        updated_at=article.updated_at,
    )
