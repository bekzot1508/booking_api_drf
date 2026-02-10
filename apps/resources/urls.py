from django.urls import path
from .views import ResourceCreateView

urlpatterns = [
    path("", ResourceCreateView.as_view()),
]
