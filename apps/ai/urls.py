from django.urls import path

from apps.ai.views import AICabinetView

app_name = "ai"

urlpatterns = [
    path("", AICabinetView.as_view(), name="ai_cabinet"),
]
