from django.urls import path

from apps.parser import views

app_name = "parser"

urlpatterns = [
    path('', views.ParserView.as_view(), name='parser'),
    path('list', views.ParserListView.as_view(), name='list'),
    path('<int:pk>/', views.ParserDetailView.as_view(), name='detail'),
    path('lookup/', views.ChannelLookupView.as_view(), name='channel_lookup'),
]
