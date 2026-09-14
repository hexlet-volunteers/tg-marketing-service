from django.urls import path

from apps.legal.views import LegalView

app_name = "legal"

urlpatterns = [
    path("", LegalView.as_view(), name="legal"),
]
