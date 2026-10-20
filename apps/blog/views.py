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
    """
    Inertia view для публичного списка блога (/blog/).

    Сейчас всегда отдаются моковые данные (реестр
    apps.blog.mock_data). Логика с БД ниже оставлена
    для prod-переключения позже:
    - featured: последняя опубликованная статья с is_featured=True
      (может отсутствовать, тогда null);
    - articles: остальные опубликованные статьи, published_at desc.

    Страница публичная, авторизация не требуется.
    """

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        service = BlogListService()
        return render_inertia_from_dto(
            request, "Blog", props=service.build_mock()
        )

        dto = service.build()
        return render_inertia_from_dto(request, "Blog", props=dto)


class BlogArticleDetailView(View):
    """
    Inertia view для страницы статьи блога (/blog/<slug>/).

    Сейчас всегда отдаются моковые данные (реестр
    apps.blog.mock_data): страница рендерится всегда, slug вне
    реестра отдаёт featured-демо с подставленным slug.
    Логика с БД ниже оставлена для prod-переключения позже:
    отдаётся только опубликованная статья (is_published=True),
    для отсутствующей или неопубликованной — 404, чтобы черновики
    не утекали наружу; views_count растёт только на полный заход,
    а не на SPA-навигацию.

    Props (Inertia-компонент 'BlogPost') — ArticleDetailDTO:
    - поля карточки (id, slug, title, excerpt, cover_image, category,
      tags, read_time, published_at, views_count, author_name);
    - body: тело статьи в формате Markdown, HTML собирает фронтенд;
    - cta: дескриптор кнопки внизу статьи;
    - related: до трёх других статей (ArticleCardDTO).

    Страница публичная, авторизация не требуется.
    """

    def get(
        self,
        request: HttpRequest,
        slug: str,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        service = BlogArticleDetailService()

        return render_inertia_from_dto(
            request, "BlogPost", props=service.build_mock(slug)
        )

        article = service.get_published_by_slug(slug)
        if article is None:
            raise Http404("Статья не найдена")

        dto = service.build(article)

        # Просмотры считаем только на полный заход: иначе счётчик
        # накручивается на каждой навигации внутри SPA.
        if not _is_inertia_request(request):
            service.record_view(article)

        return render_inertia_from_dto(request, "BlogPost", props=dto)
