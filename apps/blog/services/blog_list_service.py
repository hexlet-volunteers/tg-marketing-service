from typing import Optional

from django.db.models import QuerySet

from apps.blog.dto.blog_dto import ArticleCardDTO, BlogListDTO
from apps.blog.mock_data import MOCK_ARTICLES, as_card, get_featured_mock
from apps.blog.models import BlogArticle
from apps.blog.services.mappers import to_article_card


class BlogListService:
    """
    Собирает данные для страницы списка блога (Inertia 'Blog', /blog/).

    - build_mock(): моковые данные из реестра apps.blog.mock_data —
      используется вьюхой сейчас;
    - build(): данные из БД (оставлены для prod-переключения позже):
      featured — последняя опубликованная is_featured=True,
      articles — остальные опубликованные по published_at desc.
    """

    def build(self) -> BlogListDTO:
        featured = self._get_featured_article()
        articles_qs = self._get_articles_queryset(featured)

        return BlogListDTO(
            featured=to_article_card(featured) if featured else None,
            articles=[to_article_card(article) for article in articles_qs],
        )

    def build_mock(self) -> BlogListDTO:
        """Моковый payload списка статей из реестра."""
        featured = get_featured_mock()
        featured_slug = featured["slug"]

        articles = sorted(
            (
                article
                for article in MOCK_ARTICLES
                if article["slug"] != featured_slug
            ),
            key=lambda article: article["published_at"] or "",
            reverse=True,
        )

        return BlogListDTO(
            featured=ArticleCardDTO(**as_card(featured)),
            articles=[
                ArticleCardDTO(**as_card(article)) for article in articles
            ],
        )

    # ------------------------
    # QuerySets
    # ------------------------

    def _get_featured_article(self) -> Optional[BlogArticle]:
        return (
            BlogArticle.objects.filter(is_published=True, is_featured=True)
            .order_by("-published_at", "-created_at")
            .select_related("author")
            .first()
        )

    def _get_articles_queryset(
        self, featured: Optional[BlogArticle]
    ) -> QuerySet[BlogArticle]:
        qs = BlogArticle.objects.filter(is_published=True).select_related(
            "author"
        )
        if featured is not None:
            qs = qs.exclude(pk=featured.pk)
        return qs.order_by("-published_at", "-created_at")
