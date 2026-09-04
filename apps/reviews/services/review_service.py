from django.db import transaction

from apps.reviews.models import ReviewLog, ReviewState
from apps.reviews.services.schedulers.fsrs import FSRSScheduler

class ReviewService:

    def __init__(self, scheduler=None):
        self.scheduler = scheduler or FSRSScheduler()

    def review(self, *, user, card, rating, now):
        review_state = ReviewState.objects.get(
            user=user,
            card=card,
        )

        state = {
            "state": review_state.state,
            "stability": review_state.stability,
            "difficulty": review_state.difficulty,
            "scheduled_days": review_state.scheduled_days,
            "repetitions": review_state.repetitions,
            "lapses": review_state.lapses,
            "last_review_at": review_state.last_review_at,
        }
        result = self.scheduler.schedule(
            state=state,
            rating=rating,
            now=now,
        )

        previous_state = review_state.state
        previous_stability = review_state.stability
        previous_difficulty = review_state.difficulty
        previous_scheduled_days = review_state.scheduled_days

        with transaction.atomic():
            review_state.state = result.state
            review_state.due_at = result.due_at
            review_state.stability = result.stability
            review_state.difficulty = result.difficulty
            review_state.scheduled_days = result.scheduled_days
            review_state.repetitions = result.repetitions
            review_state.lapses = result.lapses
            review_state.last_review_at = now

            review_state.save()
            ReviewLog.objects.create(
                user=user,
                card=card,
                rating=rating,
                previous_state=previous_state,
                new_state=result.state,
                previous_stability=previous_stability,
                new_stability=result.stability,
                previous_difficulty=previous_difficulty,
                new_difficulty=result.difficulty,
                elapsed_days=result.elapsed_days,
                previous_scheduled_days=previous_scheduled_days,
                new_scheduled_days=result.scheduled_days,
            )

        return result
