from datetime import datetime, timezone
from typing import Any

from django.test import TestCase

from apps.blog.models import BlogArticle
from apps.blog.services.admin_blog_service import AdminBlogService
from apps.users.models import User


class AdminBlogServiceTests(TestCase):
    def setUp(self) -> None:
        self.author = User.objects.create_user(
            username="blog-admin",
            email="blog-admin@example.com",
            password="password",
            role="admin",
            first_name="Иван",
            last_name="Иванов",
        )

    def create_article(
        self,
        slug: str,
        *,
        created_at: datetime | None = None,
        **overrides: Any,
    ) -> BlogArticle:
        data: dict[str, Any] = {
            "title": f"Статья {slug}",
            "slug": slug,
            "excerpt": "Анонс статьи.",
            "body": "## Текст статьи",
            "author": self.author,
        }
        data.update(overrides)
        article = BlogArticle.objects.create(**data)
        if created_at is not None:
            BlogArticle.objects.filter(pk=article.pk).update(
                created_at=created_at
            )
            article.refresh_from_db()
        return article

    def test_build_dto_returns_all_articles_including_drafts(self) -> None:
        published = self.create_article("published", is_published=True)
        draft = self.create_article("draft")

        dto = AdminBlogService.build_dto()

        self.assertEqual(
            {article.id for article in dto.articles},
            {published.id, draft.id},
        )

    def test_articles_ordered_by_created_at_desc(self) -> None:
        older = self.create_article(
            "older",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        newer = self.create_article(
            "newer",
            created_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
        )

        dto = AdminBlogService.build_dto()

        self.assertEqual(
            [article.id for article in dto.articles],
            [newer.id, older.id],
        )

    def test_article_dto_maps_all_fields(self) -> None:
        article = self.create_article(
            "fields",
            tags=["python", "telegram"],
            read_time=9,
            views_count=12,
            is_featured=True,
            is_published=True,
        )

        dto = AdminBlogService.build_dto()

        self.assertEqual(len(dto.articles), 1)
        data = dto.articles[0].model_dump(mode="json")
        self.assertEqual(
            set(data),
            {
                "id",
                "title",
                "slug",
                "excerpt",
                "cover_image",
                "body",
                "category",
                "tags",
                "is_featured",
                "is_published",
                "published_at",
                "read_time",
                "views_count",
                "author_name",
                "created_at",
                "updated_at",
            },
        )
        self.assertEqual(data["id"], article.id)
        self.assertEqual(data["tags"], ["python", "telegram"])
        self.assertEqual(data["author_name"], "Иван Иванов")
        self.assertTrue(data["is_published"])
        self.assertIsNotNone(data["published_at"])

    def test_categories_follow_model_choices(self) -> None:
        dto = AdminBlogService.build_dto()

        self.assertEqual(
            [category.model_dump() for category in dto.categories],
            [
                {"value": value, "label": label}
                for value, label in BlogArticle.CATEGORY_CHOICES
            ],
        )

    def test_errors_are_empty_by_default(self) -> None:
        self.assertEqual(AdminBlogService.build_dto().errors, {})

    def test_errors_are_passed_to_dto(self) -> None:
        dto = AdminBlogService.build_dto(
            errors={
                "title": [{"message": "Обязательное поле.", "code": "required"}]
            }
        )

        self.assertEqual(dto.errors["title"][0].code, "required")
