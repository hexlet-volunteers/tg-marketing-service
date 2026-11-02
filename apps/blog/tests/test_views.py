from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils.dateparse import parse_datetime

from apps.blog.models import BlogArticle
from mocks.blog import ARTICLES

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
    """Страница списка: данные из БД."""

    @classmethod
    def setUpTestData(cls):
        for data in ARTICLES:
            BlogArticle.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "title": data["title"],
                    "excerpt": data.get("excerpt", ""),
                    "body": data.get("body", ""),
                    "cover_image": data.get("cover_image", ""),
                    "category": data.get("category", "") or "marketing",
                    "tags": data.get("tags", []),
                    "read_time": data.get("read_time", 5),
                    "is_featured": data.get("is_featured", False),
                    "is_published": True,
                    "published_at": (
                        parse_datetime(str(data["published_at"]))
                        if data.get("published_at")
                        else None
                    ),
                    "views_count": data.get("views_count", 0),
                },
            )

    def _get_inertia_props(self) -> dict[str, object]:
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

    def test_featured_is_featured_article(self) -> None:
        props = self._get_inertia_props()

        expected = (
            BlogArticle.objects.filter(is_featured=True)
            .order_by("-published_at")
            .first()
        )
        self.assertIsNotNone(expected)
        featured = props["featured"]
        self.assertIsNotNone(featured)
        self.assertEqual(featured["slug"], expected.slug)

    def test_featured_card_contains_all_fields(self) -> None:
        props = self._get_inertia_props()

        expected = BlogArticle.objects.get(slug=props["featured"]["slug"])
        featured = props["featured"]
        self.assertEqual(set(featured.keys()), CARD_FIELDS)
        self.assertEqual(featured["category"], expected.category)

    def test_featured_excluded_from_articles(self) -> None:
        props = self._get_inertia_props()

        featured_slug = props["featured"]["slug"]
        articles_slugs = {article["slug"] for article in props["articles"]}
        self.assertNotIn(featured_slug, articles_slugs)

    def test_articles_sorted_by_published_at_desc(self) -> None:
        props = self._get_inertia_props()

        dates = [article["published_at"] for article in props["articles"]]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_articles_cover_registry_without_featured(self) -> None:
        props = self._get_inertia_props()

        expected = {
            article["slug"]
            for article in ARTICLES
            if not article["is_featured"]
        }
        self.assertEqual(
            {article["slug"] for article in props["articles"]}, expected
        )

    def test_articles_at_least_three(self) -> None:
        props = self._get_inertia_props()

        self.assertGreaterEqual(len(props["articles"]), 3)


class BlogArticleDetailViewTest(TestCase):
    """Страница статьи: данные из БД."""

    @classmethod
    def setUpTestData(cls):
        for data in ARTICLES:
            BlogArticle.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "title": data["title"],
                    "excerpt": data.get("excerpt", ""),
                    "body": data.get("body", ""),
                    "cover_image": data.get("cover_image", ""),
                    "category": data.get("category", "") or "marketing",
                    "tags": data.get("tags", []),
                    "read_time": data.get("read_time", 5),
                    "is_featured": data.get("is_featured", False),
                    "is_published": True,
                    "published_at": (
                        parse_datetime(str(data["published_at"]))
                        if data.get("published_at")
                        else None
                    ),
                    "views_count": data.get("views_count", 0),
                },
            )

    def _detail_url(self, slug: str) -> str:
        return reverse("blog:detail", kwargs={"slug": slug})

    def _get_inertia(self, slug: str) -> object:
        return self.client.get(
            self._detail_url(slug),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

    def _get_inertia_props(self, slug: str) -> dict[str, object]:
        response = self._get_inertia(slug)
        self.assertEqual(response.status_code, 200)
        return response.json()["props"]

    def test_reverse_blog_detail_url(self) -> None:
        self.assertEqual(self._detail_url("demo-slug"), "/blog/demo-slug/")

    def test_view_returns_blog_article_component_and_url(self) -> None:
        slug = ARTICLES[1]["slug"]
        response = self._get_inertia(slug)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("component", data)
        self.assertIn("props", data)
        self.assertIn("url", data)

        self.assertEqual(data["component"], "BlogPost")
        self.assertEqual(data["url"], f"/blog/{slug}/")

    def test_known_slug_returns_db_article(self) -> None:
        data = ARTICLES[1]
        article = BlogArticle.objects.get(slug=data["slug"])

        props = self._get_inertia_props(data["slug"])

        self.assertTrue(DETAIL_FIELDS.issubset(props.keys()))
        self.assertEqual(props["id"], article.id)
        self.assertEqual(props["slug"], article.slug)
        self.assertEqual(props["title"], article.title)
        self.assertEqual(props["excerpt"], article.excerpt)
        self.assertEqual(props["cover_image"], article.cover_image)
        self.assertEqual(props["category"], article.category)
        self.assertEqual(props["tags"], article.tags)
        self.assertEqual(props["read_time"], article.read_time)
        self.assertEqual(
            datetime.fromisoformat(props["published_at"]),
            article.published_at,
        )
        self.assertEqual(props["views_count"], article.views_count)
        self.assertIsNone(props["author_name"])
        self.assertEqual(props["body"], article.body)
        self.assertIn("##", props["body"])

    def test_cta_prop_is_button_descriptor(self) -> None:
        props = self._get_inertia_props(ARTICLES[0]["slug"])

        self.assertEqual(
            props["cta"],
            {"label": "Разобрать канал", "url": "/ai-cabinet"},
        )

    def test_related_excludes_current_and_respects_limit(self) -> None:
        slug = ARTICLES[0]["slug"]

        props = self._get_inertia_props(slug)

        slugs = [item["slug"] for item in props["related"]]
        self.assertNotIn(slug, slugs)
        self.assertEqual(len(slugs), 3)
        self.assertTrue(
            all(set(item.keys()) == CARD_FIELDS for item in props["related"])
        )

    def test_unknown_slug_returns_404(self) -> None:
        response = self._get_inertia("net-takogo-sluga")

        self.assertEqual(response.status_code, 404)

    def test_unpublished_slug_returns_404(self) -> None:
        article = BlogArticle.objects.create(
            title="Черновик",
            slug="chernovik-view",
            excerpt="Анонс.",
            body="Черновик",
            category="news",
            is_published=False,
        )

        response = self._get_inertia(article.slug)

        self.assertEqual(response.status_code, 404)

    def test_known_slug_returns_its_title(self) -> None:
        data = ARTICLES[2]

        props = self._get_inertia_props(data["slug"])

        self.assertEqual(props["title"], data["title"])
