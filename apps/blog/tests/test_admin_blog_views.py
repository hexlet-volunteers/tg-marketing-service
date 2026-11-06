from typing import Any

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.blog.models import BlogArticle
from apps.users.models import User


class AdminBlogViewTests(TestCase):
    def setUp(self) -> None:
        self.admin = User.objects.create_user(
            username="admin-blog",
            email="admin-blog@example.com",
            password="password",
            role="admin",
        )
        self.url = reverse("admin_blog:list")

    def get_inertia(self, user: User | None = None) -> Any:
        if user is not None:
            self.client.force_login(user)
        return self.client.get(
            self.url,
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

    def create_article(self, slug: str, **overrides: Any) -> BlogArticle:
        data: dict[str, Any] = {
            "title": f"Статья {slug}",
            "slug": slug,
            "excerpt": "Анонс статьи.",
            "body": "## Текст статьи",
        }
        data.update(overrides)
        return BlogArticle.objects.create(**data)

    def test_reverse_list_url(self) -> None:
        self.assertEqual(self.url, "/admin/blog/")

    def test_list_requires_admin(self) -> None:
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_list_forbidden_for_non_admin_roles(self) -> None:
        for role in ("user", "partner", "channel_moderator"):
            with self.subTest(role=role):
                user = User.objects.create_user(
                    username=f"non-admin-{role}",
                    email=f"non-admin-{role}@example.com",
                    password="password",
                    role=role,
                )
                self.client.force_login(user)

                response = self.client.get(self.url)

                self.assertEqual(response.status_code, 403)

    def test_list_returns_component_and_props(self) -> None:
        response = self.get_inertia(self.admin)

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["component"], "AdminBlog")
        self.assertEqual(payload["url"], "/admin/blog/")
        self.assertTrue(
            {"articles", "categories", "errors"}.issubset(payload["props"])
        )
        self.assertEqual(payload["props"]["errors"], {})

    def test_list_includes_drafts_and_published(self) -> None:
        draft = self.create_article("draft")
        published = self.create_article("published", is_published=True)

        response = self.get_inertia(self.admin)

        articles = response.json()["props"]["articles"]
        ids = [article["id"] for article in articles]
        self.assertEqual(ids, [published.id, draft.id])

    def test_list_returns_category_options(self) -> None:
        response = self.get_inertia(self.admin)

        categories = response.json()["props"]["categories"]
        self.assertEqual(
            categories,
            [
                {"value": value, "label": label}
                for value, label in BlogArticle.CATEGORY_CHOICES
            ],
        )

    def article_payload(self, **overrides: Any) -> dict[str, Any]:
        data: dict[str, Any] = {
            "title": "Новая статья",
            "slug": "novaya-statya",
            "excerpt": "Анонс статьи.",
            "body": "## Текст статьи",
            "category": "marketing",
            "tags": ["telegram"],
            "is_published": False,
            "read_time": 5,
        }
        data.update(overrides)
        return data

    def post_json(self, payload: dict[str, Any]) -> Any:
        return self.client.post(
            self.url,
            data=payload,
            content_type="application/json",
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

    def create_non_admin(self, role: str) -> User:
        return User.objects.create_user(
            username=f"{role}-blog-writer",
            email=f"{role}-blog-writer@example.com",
            password="password",
            role=role,
        )

    def test_create_draft_article(self) -> None:
        self.client.force_login(self.admin)

        response = self.post_json(self.article_payload())

        self.assertEqual(response.status_code, 302)
        article = BlogArticle.objects.get(slug="novaya-statya")
        self.assertFalse(article.is_published)
        self.assertIsNone(article.published_at)
        self.assertEqual(article.author, self.admin)
        self.assertEqual(article.tags, ["telegram"])

    def test_create_published_article_sets_published_at(self) -> None:
        self.client.force_login(self.admin)

        response = self.post_json(self.article_payload(is_published=True))

        self.assertEqual(response.status_code, 302)
        article = BlogArticle.objects.get(slug="novaya-statya")
        self.assertTrue(article.is_published)
        self.assertIsNotNone(article.published_at)

    def test_create_accepts_form_encoded_tags(self) -> None:
        self.client.force_login(self.admin)
        payload = self.article_payload(tags='["python", "ai"]')

        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, 302)
        article = BlogArticle.objects.get(slug="novaya-statya")
        self.assertEqual(article.tags, ["python", "ai"])

    def test_create_requires_admin(self) -> None:
        self.client.force_login(self.create_non_admin("user"))

        response = self.post_json(self.article_payload())

        self.assertEqual(response.status_code, 403)
        self.assertFalse(BlogArticle.objects.exists())

    def test_create_invalid_returns_errors_and_saves_nothing(self) -> None:
        self.client.force_login(self.admin)

        response = self.post_json(self.article_payload(title="", slug=""))

        self.assertEqual(response.status_code, 200)
        errors = response.json()["props"]["errors"]
        self.assertIn("title", errors)
        self.assertIn("slug", errors)
        self.assertFalse(BlogArticle.objects.exists())


class AdminBlogArticleViewTests(TestCase):
    def setUp(self) -> None:
        self.admin = User.objects.create_user(
            username="admin-blog-article",
            email="admin-blog-article@example.com",
            password="password",
            role="admin",
        )
        self.article = BlogArticle.objects.create(
            title="Исходная статья",
            slug="ishodnaya-statya",
            excerpt="Анонс статьи.",
            body="## Текст статьи",
            category="marketing",
            tags=["telegram"],
            read_time=7,
        )

    def article_url(self, pk: int | None = None) -> str:
        return reverse(
            "admin_blog:article",
            kwargs={"pk": pk if pk is not None else self.article.pk},
        )

    def patch_json(
        self,
        payload: dict[str, Any],
        *,
        pk: int | None = None,
        user: User | None = None,
    ) -> Any:
        if user is not None:
            self.client.force_login(user)
        return self.client.patch(
            self.article_url(pk),
            data=payload,
            content_type="application/json",
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

    def delete_article(
        self,
        *,
        pk: int | None = None,
        user: User | None = None,
    ) -> Any:
        if user is not None:
            self.client.force_login(user)
        return self.client.delete(
            self.article_url(pk),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

    def create_non_admin(self, role: str) -> User:
        return User.objects.create_user(
            username=f"{role}-article-writer",
            email=f"{role}-article-writer@example.com",
            password="password",
            role=role,
        )

    def test_reverse_article_url(self) -> None:
        self.assertEqual(
            self.article_url(),
            f"/admin/blog/{self.article.pk}/",
        )

    def test_patch_updates_only_submitted_fields(self) -> None:
        response = self.patch_json(
            {"title": "Обновлённая статья"}, user=self.admin
        )

        self.assertEqual(response.status_code, 303)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, "Обновлённая статья")
        self.assertEqual(self.article.slug, "ishodnaya-statya")
        self.assertEqual(self.article.body, "## Текст статьи")
        self.assertEqual(self.article.tags, ["telegram"])
        self.assertEqual(self.article.read_time, 7)

    def test_patch_publishes_draft(self) -> None:
        response = self.patch_json({"is_published": True}, user=self.admin)

        self.assertEqual(response.status_code, 303)
        self.article.refresh_from_db()
        self.assertTrue(self.article.is_published)
        self.assertIsNotNone(self.article.published_at)

    def test_patch_unpublishes_article_and_keeps_published_at(self) -> None:
        published_at = timezone.now()
        BlogArticle.objects.filter(pk=self.article.pk).update(
            is_published=True,
            published_at=published_at,
        )
        self.article.refresh_from_db()

        response = self.patch_json({"is_published": False}, user=self.admin)

        self.assertEqual(response.status_code, 303)
        self.article.refresh_from_db()
        self.assertFalse(self.article.is_published)
        self.assertEqual(self.article.published_at, published_at)

    def test_patch_invalid_returns_errors_and_keeps_data(self) -> None:
        response = self.patch_json({"title": ""}, user=self.admin)

        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.json()["props"]["errors"])
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, "Исходная статья")

    def test_patch_unknown_article_returns_404(self) -> None:
        response = self.patch_json(
            {"title": "Не важно"}, pk=999999, user=self.admin
        )

        self.assertEqual(response.status_code, 404)

    def test_patch_requires_admin(self) -> None:
        user = self.create_non_admin("user")

        response = self.patch_json({"title": "Чужая правка"}, user=user)

        self.assertEqual(response.status_code, 403)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, "Исходная статья")

    def test_delete_removes_article(self) -> None:
        response = self.delete_article(user=self.admin)

        self.assertEqual(response.status_code, 303)
        self.assertFalse(
            BlogArticle.objects.filter(pk=self.article.pk).exists()
        )

    def test_delete_unknown_article_returns_404(self) -> None:
        response = self.delete_article(pk=999999, user=self.admin)

        self.assertEqual(response.status_code, 404)

    def test_delete_requires_admin(self) -> None:
        user = self.create_non_admin("user")

        response = self.delete_article(user=user)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(BlogArticle.objects.filter(pk=self.article.pk).exists())
