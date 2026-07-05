from django.urls import path

from apps.group_channels.views import (
    AddChannelsView,
    CreateGroupView,
    DeleteGroupView,
    GroupDetailView,
    UpdateGroupView,
)

app_name = 'group_channels'

urlpatterns = [
    path('create/', CreateGroupView.as_view(), name='group_create'),
    path('<slug:slug>/update/', UpdateGroupView.as_view(), name='group_update'),
    path('<slug:slug>/delete/', DeleteGroupView.as_view(), name='group_delete'),
    path('<slug:slug>/add-channels/', AddChannelsView.as_view(), name='group_add_channels'),
    path('<slug:slug>/', GroupDetailView.as_view(), name='group_detail'),
]
