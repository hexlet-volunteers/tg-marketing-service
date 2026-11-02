"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from apps.admin.moderation.views import AdminChannelsView
from apps.group_channels.views import (
    CollectionDetailView,
    CollectionsCatalogView,
)
from apps.parser.views import ChannelCatalogView, CompareView, PostPageView
from config.views import IndexView, NotFoundView

urlpatterns = [
    path("", IndexView.as_view(), name="main_index"),
    path(
        "collections/",
        CollectionsCatalogView.as_view(),
        name="collections_catalog",
    ),
    path(
        "collections/<int:pk>/",
        CollectionDetailView.as_view(),
        name="collection_detail",
    ),
    path("channels/", ChannelCatalogView.as_view(), name="channels_catalog"),
    path("compare/", CompareView.as_view(), name="compare"),
    path("post/", PostPageView.as_view(), name="post_page"),
    path("dashboard/", include("apps.homepage.urls")),
    path("ai-cabinet/", include("apps.ai.urls")),
    path("auth/", include("apps.users.urls")),
    path("group/", include("apps.group_channels.urls")),
    path("blog/", include("apps.blog.urls")),
    path("accounts/", include("allauth.urls")),
    path("parser/", include("apps.parser.urls")),
    path(
        "admin/moderation/",
        include("apps.admin.moderation.urls"),
    ),
    path("legal/", include("apps.legal.urls")),
    path(
        "admin/channels/",
        AdminChannelsView.as_view(),
        name="admin_channels",
    ),
    path("admin/", admin.site.urls),
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="robots.txt",
            content_type="text/plain",
        ),
    ),
    # Catch-all: только URL с завершающим слэшем, чтобы работал
    # APPEND_SLASH-редирект для адресов без слэша.
    path(
        "<path:missing>/",
        NotFoundView.as_view(),
        name="not_found",
    ),
]
