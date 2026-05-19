from django.urls import path
from apps.homepage.views import DashboardView

app_name = 'homepage'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
]