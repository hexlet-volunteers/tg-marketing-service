from __future__ import annotations

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.blog.models import BlogArticle
from apps.homepage.models import HomePageComponent
from apps.users.demo.base import BaseSeedStep
from apps.users.demo.context import DemoSeedContext
from mocks import blog as blog_mocks
from mocks import landing as landing_mocks


class LandingStep(BaseSeedStep):
    def seed(self, ctx: DemoSeedContext) -> None:
        for item in landing_mocks.LANDING_COMPONENTS:
            HomePageComponent.objects.update_or_create(
                component_type=item["component_type"],
                defaults={
                    "title": item["title"],
                    "content": item["content"],
                    "is_active": item["is_active"],
                    "order": item["order"],
                },
            )

    def summary(self, ctx: DemoSeedContext) -> str | None:
        return f"Главная: {HomePageComponent.objects.count()}"


class BlogStep(BaseSeedStep):
    def seed(self, ctx: DemoSeedContext) -> None:
        author = ctx.users.get("demo_admin")
        for data in blog_mocks.ARTICLES:
            published_at = parse_datetime(str(data["published_at"]))
            BlogArticle.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "title": data["title"],
                    "excerpt": data.get("excerpt", ""),
                    "body": data.get("body", ""),
                    "cover_image": data.get("cover_image", ""),
                    "category": data.get("category", ""),
                    "tags": data.get("tags", []),
                    "read_time": data.get("read_time", 5),
                    "is_featured": data.get("is_featured", False),
                    "is_published": True,
                    "published_at": published_at or timezone.now(),
                    "author": author,
                },
            )

    def summary(self, ctx: DemoSeedContext) -> str | None:
        blog_slugs = [article["slug"] for article in blog_mocks.ARTICLES]
        count = BlogArticle.objects.filter(slug__in=blog_slugs).count()
        return f"Статьи блога: {count}"
