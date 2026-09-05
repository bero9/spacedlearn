from django.urls import path

from apps.reviews.views import ReviewAPIView


urlpatterns = [
    path(
        "reviews/",
        ReviewAPIView.as_view(),
        name="review",
    ),
]