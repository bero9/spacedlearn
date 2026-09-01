from django.db import models

from apps.decks.models import Deck
from apps.notes.models import Note


class Card(models.Model):

    deck = models.ForeignKey(
        Deck,
        on_delete=models.CASCADE,
        related_name="cards",
    )

    note = models.OneToOneField(
        Note,
        on_delete=models.CASCADE,
        related_name="card",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.deck.name} - {self.note.id}"