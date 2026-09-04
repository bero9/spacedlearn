from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.reviews.models import ReviewState

class FSRSSchedulerTests(TestCase):

    def setUp(self):
        self.now = timezone.now()

        self.new_state = {
            "state": ReviewState.State.NEW,
            "stability": 0.0,
            "difficulty": 0.0,
            "repetitions": 0,
            "lapses": 0,
            "due_at": None,
            "last_review_at": None,
        }

    def test_fsrs_scheduler_exists(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        self.assertIsNotNone(FSRSScheduler)

    def test_scheduler_returns_scheduling_result(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
            SchedulingResult,
        )

        scheduler = FSRSScheduler()

        result = scheduler.schedule(
            state=self.new_state,
            rating="good",
            now=self.now,
        )

        self.assertIsInstance(
            result,
            SchedulingResult,
        )

    def test_scheduling_result_contains_required_fields(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        result = scheduler.schedule(
            state=self.new_state,
            rating="good",
            now=self.now,
        )

        required_fields = [
            "state",
            "due_at",
            "stability",
            "difficulty",
            "repetitions",
            "lapses",
        ]

        for field in required_fields:
            self.assertTrue(
                hasattr(result, field),
                f"Missing field: {field}",
            )

    def test_scheduler_does_not_modify_input_state(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        original_state = self.new_state.copy()

        scheduler.schedule(
            state=self.new_state,
            rating="good",
            now=self.now,
        )

        self.assertEqual(
            self.new_state,
            original_state,
        )

    def test_scheduler_is_deterministic(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        result_a = scheduler.schedule(
            state=self.new_state,
            rating="good",
            now=self.now,
        )

        result_b = scheduler.schedule(
            state=self.new_state,
            rating="good",
            now=self.now,
        )

        self.assertEqual(result_a, result_b)

    def test_scheduler_respects_explicit_current_time(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        first_now = self.now
        second_now = self.now + timedelta(days=10)

        result_a = scheduler.schedule(
            state=self.new_state,
            rating="good",
            now=first_now,
        )

        result_b = scheduler.schedule(
            state=self.new_state,
            rating="good",
            now=second_now,
        )

        self.assertNotEqual(
            result_a.due_at,
            result_b.due_at,
        )

    def test_due_date_is_after_current_time(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        result = scheduler.schedule(
            state=self.new_state,
            rating="good",
            now=self.now,
        )

        self.assertGreater(
            result.due_at,
            self.now,
        )

    def test_invalid_rating_is_rejected(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        with self.assertRaises(ValueError):
            scheduler.schedule(
                state=self.new_state,
                rating="invalid",
                now=self.now,
            )

    def test_rating_constants_are_supported(self):
        from apps.reviews.models import ReviewLog
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        ratings = [
            ReviewLog.Rating.AGAIN,
            ReviewLog.Rating.HARD,
            ReviewLog.Rating.GOOD,
            ReviewLog.Rating.EASY,
        ]

        for rating in ratings:
            result = scheduler.schedule(
                state=self.new_state,
                rating=rating,
                now=self.now,
            )

            self.assertIsNotNone(result)

    def test_new_card_starts_with_positive_stability(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        result = scheduler.schedule(
            state=self.new_state,
            rating="good",
            now=self.now,
        )

        self.assertGreater(
            result.stability,
            0,
        )

    def test_new_card_gets_valid_difficulty(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        result = scheduler.schedule(
            state=self.new_state,
            rating="good",
            now=self.now,
        )

        self.assertGreater(
            result.difficulty,
            0,
        )

    def test_repetitions_increase_after_successful_review(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        result = scheduler.schedule(
            state=self.new_state,
            rating="good",
            now=self.now,
        )

        self.assertGreaterEqual(
            result.repetitions,
            1,
        )

    def test_again_does_not_produce_negative_values(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        result = scheduler.schedule(
            state=self.new_state,
            rating="again",
            now=self.now,
        )

        self.assertGreaterEqual(result.stability, 0)
        self.assertGreaterEqual(result.difficulty, 0)
        self.assertGreaterEqual(result.repetitions, 0)
        self.assertGreaterEqual(result.lapses, 0)
    def test_good_review_returns_fsrs_values(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        result = scheduler.schedule(
            state=self.new_state,
            rating="good",
            now=self.now,
        )

        self.assertGreater(result.stability, 0)
        self.assertGreater(result.difficulty, 0)
        self.assertEqual(result.repetitions, 1)
        self.assertEqual(result.lapses, 0)
    def test_interval_uses_fsrs_retention_formula(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        state = {
            "state": ReviewState.State.REVIEW,
            "stability": 10.0,
            "difficulty": 5.0,
            "repetitions": 5,
            "lapses": 0,
            "due_at": self.now,
            "last_review_at": self.now,
        }

        result = scheduler.schedule(
            state=state,
            rating="good",
            now=self.now,
        )

        self.assertGreater(
            result.due_at,
            self.now,
        )

        interval_days = (
            result.due_at - self.now
        ).total_seconds() / 86400

        self.assertAlmostEqual(
            interval_days,
            10.0,
            places=5,
        )
    def test_elapsed_days_are_calculated_from_last_review(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        last_review_at = self.now - timedelta(days=5)

        state = {
            "state": ReviewState.State.REVIEW,
            "stability": 10.0,
            "difficulty": 5.0,
            "repetitions": 5,
            "lapses": 0,
            "due_at": self.now,
            "last_review_at": last_review_at,
        }

        result = scheduler.schedule(
            state=state,
            rating="good",
            now=self.now,
        )

        self.assertAlmostEqual(
            result.elapsed_days,
            5.0,
            places=5,
        )
    def test_scheduler_passes_elapsed_days_to_core(self):
        from apps.reviews.services.schedulers.core.fsrs_core import (
            FSRSCore,
        )
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        class SpyFSRSCore(FSRSCore):

            def review(self, *, state, rating):
                self.received_state = state

                return super().review(
                    state=state,
                    rating=rating,
                )

        core = SpyFSRSCore()
        scheduler = FSRSScheduler(core=core)

        last_review_at = self.now - timedelta(days=5)

        state = {
            "state": ReviewState.State.REVIEW,
            "stability": 10.0,
            "difficulty": 5.0,
            "repetitions": 5,
            "lapses": 0,
            "due_at": self.now,
            "last_review_at": last_review_at,
        }

        scheduler.schedule(
            state=state,
            rating="good",
            now=self.now,
        )

        self.assertAlmostEqual(
            core.received_state.elapsed_days,
            5.0,
            places=5,
        )
    def test_new_card_with_good_moves_to_learning(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        result = scheduler.schedule(
            state=self.new_state,
            rating="good",
            now=self.now,
        )

        self.assertEqual(
            result.state,
            ReviewState.State.LEARNING,
        )
    def test_new_card_with_easy_moves_to_review(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        result = scheduler.schedule(
            state=self.new_state,
            rating="easy",
            now=self.now,
        )

        self.assertEqual(
            result.state,
            ReviewState.State.REVIEW,
        )
    def test_new_card_with_again_moves_to_learning(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        result = scheduler.schedule(
            state=self.new_state,
            rating="again",
            now=self.now,
        )

        self.assertEqual(
            result.state,
            ReviewState.State.LEARNING,
        )
    def test_new_card_with_hard_moves_to_learning(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        result = scheduler.schedule(
            state=self.new_state,
            rating="hard",
            now=self.now,
        )

        self.assertEqual(
            result.state,
            ReviewState.State.LEARNING,
        )
    def test_learning_with_again_stays_learning(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        learning_state = {
            **self.new_state,
            "state": ReviewState.State.LEARNING,
            "stability": 2.0,
            "difficulty": 5.0,
            "repetitions": 1,
            "last_review_at": self.now,
        }

        result = scheduler.schedule(
            state=learning_state,
            rating="again",
            now=self.now,
        )

        self.assertEqual(
            result.state,
            ReviewState.State.LEARNING,
        )

    def test_learning_with_hard_stays_learning(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        learning_state = {
            **self.new_state,
            "state": ReviewState.State.LEARNING,
            "stability": 2.0,
            "difficulty": 5.0,
            "repetitions": 1,
            "last_review_at": self.now,
        }

        result = scheduler.schedule(
            state=learning_state,
            rating="hard",
            now=self.now,
        )

        self.assertEqual(
            result.state,
            ReviewState.State.LEARNING,
        )

    def test_learning_with_good_moves_to_review(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        learning_state = {
            **self.new_state,
            "state": ReviewState.State.LEARNING,
            "stability": 2.0,
            "difficulty": 5.0,
            "repetitions": 1,
            "last_review_at": self.now,
        }

        result = scheduler.schedule(
            state=learning_state,
            rating="good",
            now=self.now,
        )

        self.assertEqual(
            result.state,
            ReviewState.State.REVIEW,
        )

    def test_learning_with_easy_moves_to_review(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        learning_state = {
            **self.new_state,
            "state": ReviewState.State.LEARNING,
            "stability": 2.0,
            "difficulty": 5.0,
            "repetitions": 1,
            "last_review_at": self.now,
        }

        result = scheduler.schedule(
            state=learning_state,
            rating="easy",
            now=self.now,
        )

        self.assertEqual(
            result.state,
            ReviewState.State.REVIEW,
        )
    def test_review_with_again_moves_to_relearning(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        review_state = {
            **self.new_state,
            "state": ReviewState.State.REVIEW,
            "stability": 10.0,
            "difficulty": 5.0,
            "repetitions": 5,
            "last_review_at": self.now,
        }

        result = scheduler.schedule(
            state=review_state,
            rating="again",
            now=self.now,
        )

        self.assertEqual(
            result.state,
            ReviewState.State.RELEARNING,
        )

    def test_review_with_hard_stays_review(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        review_state = {
            **self.new_state,
            "state": ReviewState.State.REVIEW,
            "stability": 10.0,
            "difficulty": 5.0,
            "repetitions": 5,
            "last_review_at": self.now,
        }

        result = scheduler.schedule(
            state=review_state,
            rating="hard",
            now=self.now,
        )

        self.assertEqual(
            result.state,
            ReviewState.State.REVIEW,
        )

    def test_review_with_good_stays_review(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        review_state = {
            **self.new_state,
            "state": ReviewState.State.REVIEW,
            "stability": 10.0,
            "difficulty": 5.0,
            "repetitions": 5,
            "last_review_at": self.now,
        }

        result = scheduler.schedule(
            state=review_state,
            rating="good",
            now=self.now,
        )

        self.assertEqual(
            result.state,
            ReviewState.State.REVIEW,
        )

    def test_review_with_easy_stays_review(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        review_state = {
            **self.new_state,
            "state": ReviewState.State.REVIEW,
            "stability": 10.0,
            "difficulty": 5.0,
            "repetitions": 5,
            "last_review_at": self.now,
        }

        result = scheduler.schedule(
            state=review_state,
            rating="easy",
            now=self.now,
        )

        self.assertEqual(
            result.state,
            ReviewState.State.REVIEW,
        )
    def test_relearning_with_again_stays_relearning(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        relearning_state = {
            **self.new_state,
            "state": ReviewState.State.RELEARNING,
            "stability": 5.0,
            "difficulty": 5.0,
            "repetitions": 5,
            "lapses": 1,
            "last_review_at": self.now,
        }

        result = scheduler.schedule(
            state=relearning_state,
            rating="again",
            now=self.now,
        )

        self.assertEqual(
            result.state,
            ReviewState.State.RELEARNING,
        )

    def test_relearning_with_hard_stays_relearning(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        relearning_state = {
            **self.new_state,
            "state": ReviewState.State.RELEARNING,
            "stability": 5.0,
            "difficulty": 5.0,
            "repetitions": 5,
            "lapses": 1,
            "last_review_at": self.now,
        }

        result = scheduler.schedule(
            state=relearning_state,
            rating="hard",
            now=self.now,
        )

        self.assertEqual(
            result.state,
            ReviewState.State.RELEARNING,
        )

    def test_relearning_with_good_moves_to_review(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        relearning_state = {
            **self.new_state,
            "state": ReviewState.State.RELEARNING,
            "stability": 5.0,
            "difficulty": 5.0,
            "repetitions": 5,
            "lapses": 1,
            "last_review_at": self.now,
        }

        result = scheduler.schedule(
            state=relearning_state,
            rating="good",
            now=self.now,
        )

        self.assertEqual(
            result.state,
            ReviewState.State.REVIEW,
        )

    def test_relearning_with_easy_moves_to_review(self):
        from apps.reviews.services.schedulers.fsrs import (
            FSRSScheduler,
        )

        scheduler = FSRSScheduler()

        relearning_state = {
            **self.new_state,
            "state": ReviewState.State.RELEARNING,
            "stability": 5.0,
            "difficulty": 5.0,
            "repetitions": 5,
            "lapses": 1,
            "last_review_at": self.now,
        }

        result = scheduler.schedule(
            state=relearning_state,
            rating="easy",
            now=self.now,
        )

        self.assertEqual(
            result.state,
            ReviewState.State.REVIEW,
        )