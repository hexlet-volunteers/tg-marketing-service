from datetime import datetime, timezone
from typing import Any
from unittest.mock import patch

from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from apps.blog.models import BlogArticle
from apps.users.models import User

CARD_FIELDS = {
    "id",
    "slug",
    "title",
    "excerpt",
    "cover_image",
    "category",
    "tags",
    "read_time",
    "published_at",
    "views_count",
    "author_name",
}

DETAIL_FIELDS = CARD_FIELDS | {"body", "cta", "related"}


class BlogListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username="blog_author",
            email="blog_author@example.com",
            password="secret123",
            role="partner",
            first_name="Иван",
            last_name="Иванов",
        )

        cls.featured = BlogArticle.objects.create(
            title="Главная статья",
            slug="glavnaya-statya",
            excerpt="Анонс главной статьи.",
            cover_image="https://example.com/cover.jpg",
            author=cls.author,
            category="dev",
            tags=["python"],
            is_featured=True,
            is_published=True,
            published_at=datetime(2026, 8, 4, 8, 0, tzinfo=timezone.utc),
            read_time=12,
            views_count=120,
        )

        cls.featured_older = BlogArticle.objects.create(
            title="Старая featured",
            slug="staraya-featured",
            excerpt="Тоже в избранном, но опубликована раньше.",
            is_featured=True,
            is_published=True,
            published_at=datetime(2026, 7, 20, 10, 0, tzinfo=timezone.utc),
        )

        cls.article_recent = BlogArticle.objects.create(
            title="Свежая статья",
            slug="svezhaya-statya",
            excerpt="Анонс свежей статьи.",
            author=cls.author,
            category="telegram",
            tags=["telegram"],
            is_featured=False,
            is_published=True,
            published_at=datetime(2026, 7, 28, 14, 35, tzinfo=timezone.utc),
            read_time=6,
            views_count=40,
        )

        cls.article_middle = BlogArticle.objects.create(
            title="Средняя статья",
            slug="srednyaya-statya",
            excerpt="Анонс средней статьи.",
            category="ai",
            tags=["ai"],
            is_featured=False,
            is_published=True,
            published_at=datetime(2026, 7, 10, 9, 0, tzinfo=timezone.utc),
            read_time=5,
            views_count=10,
        )

        cls.article_old = BlogArticle.objects.create(
            title="Старая статья",
            slug="staraya-statya",
            excerpt="Анонс старой статьи.",
            category="marketing",
            tags=["marketing"],
            is_featured=False,
            is_published=True,
            published_at=datetime(2026, 7, 5, 14, 0, tzinfo=timezone.utc),
            read_time=8,
            views_count=5,
        )

        cls.unpublished = BlogArticle.objects.create(
            title="Черновик",
            slug="chernovik",
            excerpt="Ещё не опубликовано.",
            is_featured=False,
            is_published=False,
        )

        cls.featured_unpublished = BlogArticle.objects.create(
            title="Черновик featured",
            slug="chernovik-featured",
            excerpt="Featured, но не опубликовано.",
            is_featured=True,
            is_published=False,
        )

    def _get_inertia_props(self) -> dict[str, Any]:
        response = self.client.get(
            reverse("blog:list"),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["props"]

    def test_reverse_blog_list_url(self) -> None:
        self.assertEqual(reverse("blog:list"), "/blog/")

    def test_view_returns_blog_component_and_props(self) -> None:
        response = self.client.get(
            reverse("blog:list"),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )
        self.assertEqual(response.status_code, 200)

        # Inertia-обёртка
        data = response.json()
        self.assertIn("component", data)
        self.assertIn("props", data)
        self.assertIn("url", data)

        self.assertEqual(data["component"], "Blog")
        self.assertEqual(data["url"], "/blog/")

        props = data["props"]
        self.assertIn("featured", props)
        self.assertIn("articles", props)

    def test_featured_is_latest_published_featured(self) -> None:
        props = self._get_inertia_props()

        featured = props["featured"]
        self.assertIsNotNone(featured)
        # Выбирается самая свежая
        self.assertEqual(featured["slug"], self.featured.slug)

    def test_featured_card_contains_all_fields(self) -> None:
        props = self._get_inertia_props()

        featured = props["featured"]
        self.assertEqual(set(featured.keys()), CARD_FIELDS)
        self.assertEqual(featured["author_name"], "Иван Иванов")
        self.assertEqual(featured["tags"], ["python"])
        self.assertEqual(featured["category"], "dev")

    def test_only_published_articles_returned(self) -> None:
        props = self._get_inertia_props()

        articles_slugs = {article["slug"] for article in props["articles"]}
        self.assertNotIn(self.unpublished.slug, articles_slugs)
        self.assertNotIn(self.featured_unpublished.slug, articles_slugs)

    def test_featured_excluded_from_articles(self) -> None:
        props = self._get_inertia_props()

        featured_slug = props["featured"]["slug"]
        articles_slugs = {article["slug"] for article in props["articles"]}
        self.assertNotIn(featured_slug, articles_slugs)

    def test_articles_sorted_by_published_at_desc(self) -> None:
        props = self._get_inertia_props()

        slugs = [article["slug"] for article in props["articles"]]
        self.assertEqual(
            slugs,
            [
                self.article_recent.slug,
                self.featured_older.slug,
                self.article_middle.slug,
                self.article_old.slug,
            ],
        )

    def test_articles_at_least_three(self) -> None:
        props = self._get_inertia_props()

        self.assertGreaterEqual(len(props["articles"]), 3)


class BlogArticleDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username="detail_view_author",
            email="detail_view_author@example.com",
            password="secret123",
            role="partner",
            first_name="Иван",
            last_name="Иванов",
        )

        cls.article = BlogArticle.objects.create(
            title="Статья для страницы",
            slug="statya-dlya-stranicy",
            excerpt="Анонс статьи.",
            cover_image="https://example.com/cover.jpg",
            body="## Заголовок\n\nТело статьи.",
            author=cls.author,
            category="dev",
            tags=["python"],
            is_published=True,
            published_at=datetime(2026, 8, 4, 8, 0, tzinfo=timezone.utc),
            read_time=12,
            views_count=120,
        )

        cls.other = BlogArticle.objects.create(
            title="Другая статья",
            slug="drugaya-statya",
            excerpt="Анонс другой статьи.",
            category="dev",
            is_published=True,
            published_at=datetime(2026, 8, 1, 8, 0, tzinfo=timezone.utc),
        )

        cls.unpublished = BlogArticle.objects.create(
            title="Черновик",
            slug="chernovik-view",
            excerpt="Ещё не опубликовано.",
            category="dev",
            is_published=False,
        )

    def _detail_url(self, slug: str) -> str:
        return reverse("blog:detail", kwargs={"slug": slug})

    def _get_inertia(self, slug: str) -> Any:
        return self.client.get(
            self._detail_url(slug),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

    def _get_inertia_props(self) -> dict[str, Any]:
        response = self._get_inertia(self.article.slug)
        self.assertEqual(response.status_code, 200)
        return response.json()["props"]

    def test_reverse_blog_detail_url(self) -> None:
        self.assertEqual(
            self._detail_url(self.article.slug),
            f"/blog/{self.article.slug}/",
        )

    def test_view_returns_blog_article_component_and_url(self) -> None:
        response = self._get_inertia(self.article.slug)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("component", data)
        self.assertIn("props", data)
        self.assertIn("url", data)

        self.assertEqual(data["component"], "BlogArticle")
        self.assertEqual(data["url"], f"/blog/{self.article.slug}/")

    def test_props_contain_all_detail_fields(self) -> None:
        props = self._get_inertia_props()

        self.assertTrue(DETAIL_FIELDS.issubset(props.keys()))

    def test_props_map_article_fields(self) -> None:
        props = self._get_inertia_props()

        self.assertEqual(props["id"], self.article.id)
        self.assertEqual(props["slug"], self.article.slug)
        self.assertEqual(props["title"], self.article.title)
        self.assertEqual(props["excerpt"], self.article.excerpt)
        self.assertEqual(props["cover_image"], self.article.cover_image)
        self.assertEqual(props["category"], "dev")
        self.assertEqual(props["tags"], ["python"])
        self.assertEqual(props["read_time"], 12)
        self.assertEqual(props["views_count"], 120)
        self.assertEqual(props["author_name"], "Иван Иванов")
        self.assertEqual(props["published_at"], "2026-08-04T08:00:00Z")

    def test_body_prop_is_raw_markdown(self) -> None:
        props = self._get_inertia_props()

        self.assertEqual(props["body"], self.article.body)

    def test_cta_prop_is_button_descriptor(self) -> None:
        props = self._get_inertia_props()

        self.assertEqual(
            props["cta"],
            {"label": "Разобрать канал", "url": "/ai-cabinet"},
        )

    def test_related_excludes_current_and_unpublished(self) -> None:
        props = self._get_inertia_props()
        slugs = [item["slug"] for item in props["related"]]

        self.assertNotIn(self.article.slug, slugs)
        self.assertNotIn(self.unpublished.slug, slugs)
        self.assertIn(self.other.slug, slugs)

    def test_unknown_slug_returns_404(self) -> None:
        response = self._get_inertia("net-takogo-sluga")

        self.assertEqual(response.status_code, 404)

    def test_unpublished_article_returns_404(self) -> None:
        response = self._get_inertia(self.unpublished.slug)

        self.assertEqual(response.status_code, 404)

    def test_views_count_not_incremented_on_inertia_request(self) -> None:
        before = self.article.views_count

        self._get_inertia(self.article.slug)

        self.article.refresh_from_db()
        self.assertEqual(self.article.views_count, before)

    def test_views_count_incremented_on_full_page_load(self) -> None:
        before = self.article.views_count

        # Полный рендер требует собранного Vite-манифеста, поэтому
        # подменяем рендерер - проверяем решение вьюхи считать просмотр.
        with patch(
            "apps.blog.views.render_inertia_from_dto",
            return_value=HttpResponse(),
        ):
            self.client.get(self._detail_url(self.article.slug))

        self.article.refresh_from_db()
        self.assertEqual(self.article.views_count, before + 1)

    def test_views_count_not_incremented_on_404(self) -> None:
        before = self.unpublished.views_count

        self.client.get(self._detail_url(self.unpublished.slug))

        self.unpublished.refresh_from_db()
        self.assertEqual(self.unpublished.views_count, before)
