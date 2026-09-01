from rest_framework import serializers

from apps.cards.models import Card
from apps.decks.models import Deck
from apps.notes.models import Note


class CardSerializer(serializers.ModelSerializer):

    deck = serializers.PrimaryKeyRelatedField(
        queryset=Deck.objects.all()
    )

    note = serializers.PrimaryKeyRelatedField(
        queryset=Note.objects.all()
    )

    class Meta:
        model = Card
        fields = [
            "id",
            "deck",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]