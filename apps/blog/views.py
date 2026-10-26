from typing import Any

from django.http import Http404, HttpRequest, HttpResponse
from django.views import View

from apps.blog.services.blog_article_detail_service import (
    BlogArticleDetailService,
)
from apps.blog.services.blog_list_service import BlogListService
from config.renderers import render_inertia_from_dto


def _is_inertia_request(request: HttpRequest) -> bool:
    """Отличает Inertia-навигацию от полной загрузки страницы."""
    return request.headers.get("X-Inertia") == "true"


class BlogListView(View):
    """Inertia view для публичного списка блога (/blog/)."""

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        dto = BlogListService().build()
        return render_inertia_from_dto(request, "Blog", props=dto)


class BlogArticleDetailView(View):
    """Inertia view для страницы статьи блога (/blog/<slug>/)."""

    def get(
        self,
        request: HttpRequest,
        slug: str,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        service = BlogArticleDetailService()
        article = service.get_published_by_slug(slug)
        if article is None:
            raise Http404("Статья не найдена")

        dto = service.build(article)
        if not _is_inertia_request(request):
            service.record_view(article)
        return render_inertia_from_dto(request, "BlogPost", props=dto)
