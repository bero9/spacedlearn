from rest_framework import serializers

from apps.decks.models import Deck


class DeckSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deck
        fields = [
            "id",
            "name",
            "description",
            "visibility",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]   