from django.urls import path

from apps.blog.views import BlogArticleDetailView, BlogListView

app_name = "blog"

urlpatterns = [
    path("", BlogListView.as_view(), name="list"),
    path("<slug:slug>/", BlogArticleDetailView.as_view(), name="detail"),
]
