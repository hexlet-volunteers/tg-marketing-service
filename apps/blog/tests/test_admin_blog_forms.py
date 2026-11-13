from typing import Any

from django.test import TestCase

from apps.blog.forms import BlogArticleForm
from apps.blog.models import BlogArticle

VALID_DATA: dict[str, Any] = {
    "title": "Новая статья",
    "slug": "novaya-statya",
    "excerpt": "Анонс статьи.",
    "cover_image": "https://example.com/cover.jpg",
    "body": "## Текст статьи",
    "category": "marketing",
    "tags": ["telegram", "ai"],
    "is_featured": False,
    "is_published": False,
    "read_time": 5,
}


class BlogArticleFormTests(TestCase):
    def data(self, **overrides: Any) -> dict[str, Any]:
        return {**VALID_DATA, **overrides}

    def test_valid_draft_is_saved_without_published_at(self) -> None:
        form = BlogArticleForm(self.data())

        self.assertTrue(form.is_valid(), form.errors)
        article = form.save()

        self.assertFalse(article.is_published)
        self.assertIsNone(article.published_at)
        self.assertEqual(article.tags, ["telegram", "ai"])

    def test_published_article_gets_published_at(self) -> None:
        form = BlogArticleForm(self.data(is_published=True))

        self.assertTrue(form.is_valid(), form.errors)
        article = form.save()

        self.assertTrue(article.is_published)
        self.assertIsNotNone(article.published_at)

    def test_blank_title_is_invalid(self) -> None:
        form = BlogArticleForm(self.data(title=""))

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_duplicate_slug_is_invalid(self) -> None:
        BlogArticle.objects.create(
            title="Существующая статья",
            slug=VALID_DATA["slug"],
            excerpt="Анонс.",
            body="Текст.",
        )

        form = BlogArticleForm(self.data())

        self.assertFalse(form.is_valid())
        self.assertIn("slug", form.errors)

    def test_invalid_category_is_invalid(self) -> None:
        form = BlogArticleForm(self.data(category="unknown"))

        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)

    def test_invalid_cover_image_url_is_invalid(self) -> None:
        form = BlogArticleForm(self.data(cover_image="not-a-url"))

        self.assertFalse(form.is_valid())
        self.assertIn("cover_image", form.errors)

    def test_tags_accept_json_string(self) -> None:
        form = BlogArticleForm(self.data(tags='["python", "telegram"]'))

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["tags"], ["python", "telegram"])

    def test_tags_reject_comma_separated_string(self) -> None:
        form = BlogArticleForm(self.data(tags="python,telegram"))

        self.assertFalse(form.is_valid())
        self.assertIn("tags", form.errors)

    def test_tags_reject_non_string_items(self) -> None:
        form = BlogArticleForm(self.data(tags=["python", 42]))

        self.assertFalse(form.is_valid())
        self.assertIn("tags", form.errors)

    def test_tags_drop_empty_values(self) -> None:
        form = BlogArticleForm(self.data(tags=["python", " ", ""]))

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["tags"], ["python"])

    def test_missing_tags_become_empty_list(self) -> None:
        data = self.data()
        data.pop("tags")

        form = BlogArticleForm(data)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["tags"], [])

    def test_missing_read_time_defaults_to_five(self) -> None:
        data = self.data()
        data.pop("read_time")

        form = BlogArticleForm(data)

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["read_time"], 5)

    def test_explicit_read_time_is_kept(self) -> None:
        form = BlogArticleForm(self.data(read_time=12))

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["read_time"], 12)

    def test_author_is_not_editable(self) -> None:
        form = BlogArticleForm(self.data())

        self.assertNotIn("author", form.fields)
        self.assertNotIn("published_at", form.fields)
        self.assertNotIn("views_count", form.fields)
