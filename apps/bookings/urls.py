from django.urls import path
from .views import BookingCollectionView, BookingCancelView

urlpatterns = [
    path("", BookingCollectionView.as_view()),
    path("<uuid:booking_id>/cancel/", BookingCancelView.as_view()),
]
