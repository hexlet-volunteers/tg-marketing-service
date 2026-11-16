from django.urls import path

from apps.admin.moderation.views import (
    AdminChannelAddView,
    AdminChannelCategoryView,
    AdminChannelsView,
    AdminChannelVerifiedView,
    ModerationRequestListView,
)

app_name = "admin_moderation"

urlpatterns = [
    path("", ModerationRequestListView.as_view(), name="list"),
    path(
        "channels/",
        AdminChannelsView.as_view(),
        name="channels",
    ),
    path(
        "channels/verified/",
        AdminChannelVerifiedView.as_view(),
        name="channel_verified",
    ),
    path(
        "channels/add/",
        AdminChannelAddView.as_view(),
        name="channel_add",
    ),
    path(
        "channels/category/",
        AdminChannelCategoryView.as_view(),
        name="channel_category",
    ),
]
