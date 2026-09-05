from rest_framework import serializers


class ReviewSerializer(serializers.Serializer):

    card_id = serializers.IntegerField()

    rating = serializers.ChoiceField(
        choices=[
            "again",
            "hard",
            "good",
            "easy",
        ],
    )