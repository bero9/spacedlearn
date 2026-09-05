from django.urls import path

from apps.study.views import StudyQueueAPIView


urlpatterns = [
    path(
        "study/queue/",
        StudyQueueAPIView.as_view(),
        name="study-queue",
    ),
]