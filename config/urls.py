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

from config.views import IndexView


urlpatterns = [
    path("", IndexView.as_view(), name="main_index"),
    path("dashboard/", include("apps.homepage.urls")),
    path("auth/", include("apps.users.urls")),
    path("group/", include("apps.group_channels.urls")),
    path("accounts/", include("allauth.urls")),
    path("parser/", include("apps.parser.urls")),
    path("admin/", admin.site.urls),
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="robots.txt", content_type="text/plain"
        ),
    ),
]
