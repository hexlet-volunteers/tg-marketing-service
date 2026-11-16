import json
from typing import Any, cast

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from inertia import InertiaResponse

from apps.blog.forms import EDITABLE_FIELDS, BlogArticleForm
from apps.blog.models import BlogArticle
from apps.blog.services.admin_blog_service import AdminBlogService
from apps.users.models import User
from config.mixins import AdminRequiredMixin
from config.renderers import render_inertia_from_dto

FORM_ERRORS_SESSION_KEY = "admin_blog_form_errors"


def _request_data(request: HttpRequest) -> dict[str, Any]:
    """Данные редактора из JSON-тела или обычного POST."""
    if request.content_type == "application/json":
        try:
            payload = json.loads(request.body or b"{}")
        except json.JSONDecodeError:
            return {}
        return payload if isinstance(payload, dict) else {}
    return request.POST.dict()


def _redirect_with_errors(
    request: HttpRequest, form: BlogArticleForm
) -> HttpResponse:
    """Ошибки формы переживают redirect и отдаются на списке один раз."""
    request.session[FORM_ERRORS_SESSION_KEY] = form.errors.get_json_data()
    return redirect("admin_blog:list")


class AdminBlogView(AdminRequiredMixin, View):
    """Список статей блога и создание новой статьи (/admin/blog/)."""

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> InertiaResponse:
        errors = request.session.pop(FORM_ERRORS_SESSION_KEY, None) or {}
        return render_inertia_from_dto(
            request,
            "AdminBlog",
            props=AdminBlogService.build_dto(errors=errors),
        )

    def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        form = BlogArticleForm(_request_data(request))
        if not form.is_valid():
            return _redirect_with_errors(request, form)

        article = form.save(commit=False)
        article.author = cast(User, request.user)
        article.save()

        request.session["flash"] = {"success": "Статья создана"}
        return redirect("admin_blog:list")


class AdminBlogArticleView(AdminRequiredMixin, View):
    """Обновление и удаление статьи (/admin/blog/<pk>/)."""

    def patch(
        self, request: HttpRequest, pk: int, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        article = get_object_or_404(BlogArticle, pk=pk)
        payload = _request_data(request)
        data = {
            field: payload.get(field, getattr(article, field))
            for field in EDITABLE_FIELDS
        }

        form = BlogArticleForm(data, instance=article)
        if not form.is_valid():
            return _redirect_with_errors(request, form)

        form.save()
        request.session["flash"] = {"success": "Статья обновлена"}
        return redirect("admin_blog:list")

    def delete(
        self, request: HttpRequest, pk: int, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        article = get_object_or_404(BlogArticle, pk=pk)
        article.delete()

        request.session["flash"] = {"success": "Статья удалена"}
        return redirect("admin_blog:list")
