from django.urls import path

from apps.admin.moderation.views import ModerationRequestListView

app_name = "admin_moderation"

urlpatterns = [
    path("", ModerationRequestListView.as_view(), name="list"),
]
