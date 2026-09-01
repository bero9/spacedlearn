from django.db.models import Q

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.decks.models import Deck
from apps.decks.serializers import DeckSerializer

from apps.decks.permissions import IsDeckOwnerOrReadOnly
class DeckViewSet(ModelViewSet):
    serializer_class = DeckSerializer
    permission_classes = [
    IsAuthenticated,
    IsDeckOwnerOrReadOnly,
]

    def get_queryset(self):
        if self.action == "list":
            return Deck.objects.filter(
                owner=self.request.user
            )

        return Deck.objects.filter(
            Q(owner=self.request.user)
            | Q(visibility=Deck.Visibility.PUBLIC)
        )

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user
        )