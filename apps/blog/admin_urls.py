from django.urls import path

from apps.blog.admin_views import AdminBlogArticleView, AdminBlogView

app_name = "admin_blog"

urlpatterns = [
    path("", AdminBlogView.as_view(), name="list"),
    path("<int:pk>/", AdminBlogArticleView.as_view(), name="article"),
]
