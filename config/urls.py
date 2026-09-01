from django.contrib import admin
from django.urls import include, path

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

from apps.users.views import LoginView

from apps.notes.views import NoteViewSet

from apps.decks.views import DeckViewSet

from apps.cards.views import CardViewSet

router = DefaultRouter()

router.register(
    r"notes",
    NoteViewSet,
    basename="note",
)
router.register(
    r"decks",
    DeckViewSet,
    basename="deck",
)
router.register(
    r"cards",
    CardViewSet,
    basename="card",
)

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", include(router.urls)),

    path(
    "api/auth/login/",
    LoginView.as_view(),
    name="login",
),

    path(
        "api/auth/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
]
