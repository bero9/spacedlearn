from django.conf import settings
from django.db import models


class Deck(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="decks",
    )

    name = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name