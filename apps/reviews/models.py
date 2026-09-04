from django.conf import settings
from django.db import models

from apps.cards.models import Card


class ReviewState(models.Model):

    class State(models.TextChoices):
        NEW = "new", "New"
        LEARNING = "learning", "Learning"
        REVIEW = "review", "Review"
        RELEARNING = "relearning", "Relearning"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="review_states",
    )

    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name="review_states",
    )

    state = models.CharField(
        max_length=20,
        choices=State.choices,
        default=State.NEW,
    )

    due_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    stability = models.FloatField(
        default=0.0,
    )

    difficulty = models.FloatField(
        default=0.0,
    )
    scheduled_days = models.FloatField(
        default=0.0,
    )
    repetitions = models.PositiveIntegerField(
        default=0,
    )

    lapses = models.PositiveIntegerField(
        default=0,
    )

    last_review_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "card"],
                name="unique_review_state_per_user_card",
            ),
        ]
class ReviewLog(models.Model):

    class Rating(models.TextChoices):
        AGAIN = "again", "Again"
        HARD = "hard", "Hard"
        GOOD = "good", "Good"
        EASY = "easy", "Easy"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="review_logs",
    )

    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name="review_logs",
    )

    rating = models.CharField(
        max_length=10,
        choices=Rating.choices,
    )

    previous_state = models.CharField(
        max_length=20,
        choices=ReviewState.State.choices,
    )

    new_state = models.CharField(
        max_length=20,
        choices=ReviewState.State.choices,
    )

    reviewed_at = models.DateTimeField(
        auto_now_add=True,
    )

    previous_stability = models.FloatField(
        default=0.0,
    )

    new_stability = models.FloatField(
        default=0.0,
    )

    previous_difficulty = models.FloatField(
        default=0.0,
    )

    new_difficulty = models.FloatField(
        default=0.0,
    )
    elapsed_days = models.FloatField(
        default=0.0,
    )
    previous_scheduled_days = models.FloatField(
        default=0.0,
    )

    new_scheduled_days = models.FloatField(
        default=0.0,
    )
