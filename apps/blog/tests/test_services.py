from datetime import datetime, timezone

from django.test import TestCase

from apps.blog.dto.blog_dto import (
    ArticleCardDTO,
    ArticleDetailDTO,
    BlogListDTO,
    CallToActionDTO,
)
from apps.blog.models import BlogArticle
from apps.blog.services.blog_article_detail_service import (
    BlogArticleDetailService,
)
from apps.blog.services.blog_list_service import BlogListService
from apps.users.models import User


class BlogListServiceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.featured = BlogArticle.objects.create(
            title="Главная статья",
            slug="glavnaya-statya",
            excerpt="Анонс главной статьи.",
            is_featured=True,
            is_published=True,
            published_at=datetime(2026, 8, 4, 8, 0, tzinfo=timezone.utc),
        )

        cls.featured_older = BlogArticle.objects.create(
            title="Старая featured",
            slug="staraya-featured",
            excerpt="Тоже в избранном, но опубликована раньше.",
            is_featured=True,
            is_published=True,
            published_at=datetime(2026, 7, 20, 10, 0, tzinfo=timezone.utc),
        )

        cls.article = BlogArticle.objects.create(
            title="Обычная статья",
            slug="obychnaya-statya",
            excerpt="Анонс обычной статьи.",
            is_featured=False,
            is_published=True,
            published_at=datetime(2026, 7, 10, 9, 0, tzinfo=timezone.utc),
        )

        cls.unpublished = BlogArticle.objects.create(
            title="Черновик",
            slug="chernovik",
            excerpt="Ещё не опубликовано.",
            is_featured=False,
            is_published=False,
        )

    def test_build_returns_blog_list_dto(self) -> None:
        dto = BlogListService().build()

        self.assertIsInstance(dto, BlogListDTO)
        self.assertIsInstance(dto.featured, ArticleCardDTO)
        self.assertTrue(
            all(isinstance(article, ArticleCardDTO) for article in dto.articles)
        )

        self.assertEqual(dto.featured.slug, self.featured.slug)

        articles_slugs = [article.slug for article in dto.articles]
        self.assertEqual(
            articles_slugs, [self.featured_older.slug, self.article.slug]
        )
        self.assertNotIn(self.unpublished.slug, articles_slugs)


class BlogArticleDetailServiceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username="detail_author",
            email="detail_author@example.com",
            password="secret123",
            role="partner",
            first_name="Иван",
            last_name="Иванов",
        )

        cls.article = BlogArticle.objects.create(
            title="Статья дня",
            slug="statya-dnya",
            excerpt="Анонс статьи дня.",
            cover_image="https://example.com/cover.jpg",
            body="## Заголовок\n\nТело статьи.",
            author=cls.author,
            category="dev",
            tags=["python", "django"],
            is_published=True,
            published_at=datetime(2026, 8, 4, 8, 0, tzinfo=timezone.utc),
            read_time=12,
            views_count=120,
        )

        # Обе статьи той же категории, что и article
        cls.same_category_recent = BlogArticle.objects.create(
            title="Свежая dev",
            slug="svezhaya-dev",
            excerpt="Анонс.",
            category="dev",
            is_published=True,
            published_at=datetime(2026, 8, 10, 9, 0, tzinfo=timezone.utc),
        )

        cls.same_category_old = BlogArticle.objects.create(
            title="Старая dev",
            slug="staraya-dev",
            excerpt="Анонс.",
            category="dev",
            is_published=True,
            published_at=datetime(2026, 8, 1, 9, 0, tzinfo=timezone.utc),
        )

        # Другая категория, но свежее всех
        cls.other_category = BlogArticle.objects.create(
            title="Свежая ai",
            slug="svezhaya-ai",
            excerpt="Анонс.",
            category="ai",
            is_published=True,
            published_at=datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc),
        )

        # Третья категория: нужна, чтобы related упирался в лимит
        cls.third_category = BlogArticle.objects.create(
            title="Свежая marketing",
            slug="svezhaya-marketing",
            excerpt="Анонс.",
            category="marketing",
            is_published=True,
            published_at=datetime(2026, 8, 15, 9, 0, tzinfo=timezone.utc),
        )

        cls.unpublished = BlogArticle.objects.create(
            title="Черновик",
            slug="chernovik-detail",
            excerpt="Ещё не опубликовано.",
            category="dev",
            is_published=False,
        )

    def test_get_published_by_slug_returns_article(self) -> None:
        found = BlogArticleDetailService().get_published_by_slug(
            self.article.slug
        )

        self.assertEqual(found, self.article)

    def test_get_published_by_slug_unknown_returns_none(self) -> None:
        found = BlogArticleDetailService().get_published_by_slug(
            "net-takoy-statyi"
        )

        self.assertIsNone(found)

    def test_get_published_by_slug_unpublished_returns_none(self) -> None:
        found = BlogArticleDetailService().get_published_by_slug(
            self.unpublished.slug
        )

        self.assertIsNone(found)

    def test_build_returns_article_detail_dto(self) -> None:
        dto = BlogArticleDetailService().build(self.article)

        self.assertIsInstance(dto, ArticleDetailDTO)

    def test_build_maps_card_fields(self) -> None:
        dto = BlogArticleDetailService().build(self.article)

        self.assertEqual(dto.id, self.article.id)
        self.assertEqual(dto.slug, self.article.slug)
        self.assertEqual(dto.title, self.article.title)
        self.assertEqual(dto.excerpt, self.article.excerpt)
        self.assertEqual(dto.cover_image, self.article.cover_image)
        self.assertEqual(dto.category, self.article.category)
        self.assertEqual(dto.tags, ["python", "django"])
        self.assertEqual(dto.read_time, self.article.read_time)
        self.assertEqual(dto.published_at, self.article.published_at)
        self.assertEqual(dto.views_count, self.article.views_count)
        self.assertEqual(dto.author_name, "Иван Иванов")

    def test_build_author_name_falls_back_to_username(self) -> None:
        author = User.objects.create_user(
            username="nameless_author",
            email="nameless_author@example.com",
            password="secret123",
            role="partner",
        )
        article = BlogArticle.objects.create(
            title="Статья без имени автора",
            slug="statya-bez-imeni",
            excerpt="Анонс.",
            author=author,
            category="news",
            is_published=True,
        )

        dto = BlogArticleDetailService().build(article)

        self.assertEqual(dto.author_name, "nameless_author")

    def test_build_without_author_returns_none_author_name(self) -> None:
        article = BlogArticle.objects.create(
            title="Статья без автора",
            slug="statya-bez-avtora",
            excerpt="Анонс.",
            category="news",
            is_published=True,
        )

        dto = BlogArticleDetailService().build(article)

        self.assertIsNone(dto.author_name)

    def test_build_returns_raw_markdown_body(self) -> None:
        dto = BlogArticleDetailService().build(self.article)

        self.assertEqual(dto.body, self.article.body)

    def test_build_includes_cta_descriptor(self) -> None:
        dto = BlogArticleDetailService().build(self.article)

        self.assertIsInstance(dto.cta, CallToActionDTO)
        self.assertEqual(dto.cta.label, "Разобрать канал")
        self.assertEqual(dto.cta.url, "/ai-cabinet")

    def test_build_related_excludes_current_article(self) -> None:
        dto = BlogArticleDetailService().build(self.article)

        self.assertNotIn(self.article.slug, [item.slug for item in dto.related])

    def test_build_related_excludes_unpublished(self) -> None:
        dto = BlogArticleDetailService().build(self.article)

        self.assertNotIn(
            self.unpublished.slug, [item.slug for item in dto.related]
        )

    def test_build_related_prefers_same_category(self) -> None:
        dto = BlogArticleDetailService().build(self.article)

        self.assertEqual(
            [item.slug for item in dto.related],
            [
                self.same_category_recent.slug,
                self.same_category_old.slug,
                self.other_category.slug,
            ],
        )

    def test_build_related_respects_limit(self) -> None:
        dto = BlogArticleDetailService().build(self.article)
        slugs = [item.slug for item in dto.related]

        self.assertEqual(len(slugs), BlogArticleDetailService.RELATED_LIMIT)
        # third_category идёт четвёртой по приоритету, в блок не попадает
        self.assertNotIn(self.third_category.slug, slugs)

    def test_build_related_items_are_cards(self) -> None:
        dto = BlogArticleDetailService().build(self.article)

        self.assertTrue(
            all(isinstance(item, ArticleCardDTO) for item in dto.related)
        )

    def test_build_related_empty_without_other_published(self) -> None:
        BlogArticle.objects.exclude(pk=self.article.pk).filter(
            is_published=True
        ).delete()

        dto = BlogArticleDetailService().build(self.article)

        self.assertEqual(dto.related, [])

    def test_record_view_increments_counter(self) -> None:
        before = self.article.views_count

        BlogArticleDetailService().record_view(self.article)

        self.article.refresh_from_db()
        self.assertEqual(self.article.views_count, before + 1)

    def test_record_view_does_not_touch_updated_at(self) -> None:
        before = self.article.updated_at

        BlogArticleDetailService().record_view(self.article)

        self.article.refresh_from_db()
        self.assertEqual(self.article.updated_at, before)
