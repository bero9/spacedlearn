from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.cards.models import Card
from apps.cards.serializers import CardSerializer
from apps.cards.services.card_service import CardService


class CardViewSet(ModelViewSet):

    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Card.objects.filter(
            deck__owner=self.request.user
        )

    def perform_create(self, serializer):
        card = CardService.create_card(
            user=self.request.user,
            deck=serializer.validated_data["deck"],
            note=serializer.validated_data["note"],
        )

        serializer.instance = card