from datetime import datetime

from django.test import SimpleTestCase
from django.urls import reverse

from apps.blog.mock_data import MOCK_ARTICLES, get_featured_mock

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


class BlogListViewTest(SimpleTestCase):
    """Страница списка: всегда моковые данные (реестр mock_data)."""

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

    def test_featured_is_featured_mock(self) -> None:
        props = self._get_inertia_props()

        featured = props["featured"]
        self.assertIsNotNone(featured)
        self.assertEqual(featured["slug"], get_featured_mock()["slug"])

    def test_featured_card_contains_all_fields(self) -> None:
        props = self._get_inertia_props()

        featured = props["featured"]
        self.assertEqual(set(featured.keys()), CARD_FIELDS)
        self.assertEqual(featured["category"], get_featured_mock()["category"])

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
            for article in MOCK_ARTICLES
            if not article["is_featured"]
        }
        self.assertEqual(
            {article["slug"] for article in props["articles"]}, expected
        )

    def test_articles_at_least_three(self) -> None:
        props = self._get_inertia_props()

        self.assertGreaterEqual(len(props["articles"]), 3)


class BlogArticleDetailViewTest(SimpleTestCase):
    """Страница статьи: всегда моковые данные (реестр mock_data)."""

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
        slug = MOCK_ARTICLES[1]["slug"]
        response = self._get_inertia(slug)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("component", data)
        self.assertIn("props", data)
        self.assertIn("url", data)

        self.assertEqual(data["component"], "BlogPost")
        self.assertEqual(data["url"], f"/blog/{slug}/")

    def test_registry_slug_returns_its_mock(self) -> None:
        data = MOCK_ARTICLES[1]

        props = self._get_inertia_props(data["slug"])

        self.assertTrue(DETAIL_FIELDS.issubset(props.keys()))
        self.assertEqual(props["id"], data["id"])
        self.assertEqual(props["slug"], data["slug"])
        self.assertEqual(props["title"], data["title"])
        self.assertEqual(props["excerpt"], data["excerpt"])
        self.assertEqual(props["cover_image"], data["cover_image"])
        self.assertEqual(props["category"], data["category"])
        self.assertEqual(props["tags"], data["tags"])
        self.assertEqual(props["read_time"], data["read_time"])
        self.assertEqual(
            datetime.fromisoformat(props["published_at"]),
            datetime.fromisoformat(data["published_at"]),
        )
        self.assertEqual(props["views_count"], data["views_count"])
        self.assertIsNone(props["author_name"])
        self.assertEqual(props["body"], data["body"])
        self.assertIn("##", props["body"])

    def test_cta_prop_is_button_descriptor(self) -> None:
        props = self._get_inertia_props(MOCK_ARTICLES[0]["slug"])

        self.assertEqual(
            props["cta"],
            {"label": "Разобрать канал", "url": "/ai-cabinet"},
        )

    def test_related_excludes_current_and_respects_limit(self) -> None:
        slug = MOCK_ARTICLES[0]["slug"]

        props = self._get_inertia_props(slug)

        slugs = [item["slug"] for item in props["related"]]
        self.assertNotIn(slug, slugs)
        self.assertEqual(len(slugs), 3)
        self.assertTrue(
            all(set(item.keys()) == CARD_FIELDS for item in props["related"])
        )

    def test_unknown_slug_returns_demo_with_injected_slug(self) -> None:
        props = self._get_inertia_props("net-takogo-sluga")

        self.assertEqual(props["slug"], "net-takogo-sluga")
        self.assertEqual(props["title"], get_featured_mock()["title"])

    def test_known_registry_slug_not_overridden(self) -> None:
        # Slug, совпадающий с реестром, отдаёт статью реестра,
        # а не featured-демо.
        data = MOCK_ARTICLES[2]

        props = self._get_inertia_props(data["slug"])

        self.assertEqual(props["title"], data["title"])
        self.assertNotEqual(props["title"], get_featured_mock()["title"])
