from django.urls import path
from .views import ResourceCollectionView, ResourceDetailView

urlpatterns = [
    path("", ResourceCollectionView.as_view()),
    path("<uuid:resource_id>/", ResourceDetailView.as_view()),
]
