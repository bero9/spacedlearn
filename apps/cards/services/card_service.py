from rest_framework.exceptions import PermissionDenied

from apps.cards.models import Card


class CardService:

    @staticmethod
    def create_card(*, user, deck, note):
        if deck.owner != user:
            raise PermissionDenied(
                "You do not have permission to use this deck."
            )

        if note.note_type.owner != user:
            raise PermissionDenied(
                "You do not have permission to use this note."
            )

        return Card.objects.create(
            deck=deck,
            note=note,
        )