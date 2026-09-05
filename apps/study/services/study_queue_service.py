from django.utils import timezone
from django.db.models import Prefetch

from apps.cards.models import Card
from apps.reviews.models import ReviewState


class StudyQueueService:

    @staticmethod
    def get_queue(*, user, limit=20, deck_id=None, now=None):
        now = now or timezone.now()

        queryset = Card.objects.filter(
            deck__owner=user,
            review_states__user=user,
            review_states__due_at__lte=now,
        )

        if deck_id is not None:
            queryset = queryset.filter(
                deck_id=deck_id,
            )

        return queryset.select_related(
            "deck",
            "note",
        ).prefetch_related(
            Prefetch(
                "review_states",
                queryset=ReviewState.objects.filter(
                    user=user,
                ),
                to_attr="user_review_states",
            ),
        ).order_by(
            "review_states__due_at",
            "id",
        )[:limit]