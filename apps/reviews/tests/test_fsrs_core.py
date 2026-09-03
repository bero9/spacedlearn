import math

from django.test import SimpleTestCase

from apps.reviews.services.schedulers.core.fsrs_core import (
    FSRSCore,
    FSRSState,
)


class FSRSCoreTests(SimpleTestCase):

    def test_fsrs_core_module_exists(self):
        from apps.reviews.services.schedulers.core.fsrs_core import FSRSCore

        self.assertIsNotNone(FSRSCore)

    def test_fsrs_core_can_be_created(self):
        core = FSRSCore()

        self.assertIsNotNone(core)

    def test_fsrs_core_has_default_parameters(self):
        core = FSRSCore()

        self.assertIsNotNone(core.parameters)

    def test_initial_state_can_be_created(self):
        core = FSRSCore()

        state = core.initial_state()

        self.assertEqual(state.stability, 0.0)
        self.assertEqual(state.difficulty, 0.0)
        self.assertEqual(state.elapsed_days, 0.0)
        self.assertEqual(state.scheduled_days, 0.0)
        self.assertEqual(state.repetitions, 0)
        self.assertEqual(state.lapses, 0)

    def test_initial_state_has_zero_repetitions(self):
        core = FSRSCore()

        state = core.initial_state()

        self.assertEqual(state.repetitions, 0)

    def test_initial_state_has_zero_lapses(self):
        core = FSRSCore()

        state = core.initial_state()

        self.assertEqual(state.lapses, 0)

    def test_initial_stability_returns_expected_values(self):
        core = FSRSCore()

        self.assertAlmostEqual(
            core.initial_stability("again"),
            0.212,
            places=10,
        )
        self.assertAlmostEqual(
            core.initial_stability("hard"),
            1.2931,
            places=10,
        )
        self.assertAlmostEqual(
            core.initial_stability("good"),
            2.3065,
            places=10,
        )
        self.assertAlmostEqual(
            core.initial_stability("easy"),
            8.2956,
            places=10,
        )

    def test_initial_stability_increases_with_rating(self):
        core = FSRSCore()
        state = FSRSState()

        again = core.review(state=state, rating="again")
        hard = core.review(state=state,rating= "hard")
        good = core.review(state=state,rating= "good")
        easy = core.review(state=state,rating= "easy")

        self.assertLess(again.stability, hard.stability)
        self.assertLess(hard.stability, good.stability)
        self.assertLess(good.stability, easy.stability)

    def test_initial_stability_depends_on_rating(self):
        core = FSRSCore()
        state = FSRSState()

        again = core.review(state=state, rating="again")
        good = core.review(state=state, rating="good")
        easy = core.review(state=state, rating="easy")

        self.assertGreater(again.stability, 0)
        self.assertGreater(good.stability, 0)
        self.assertGreater(easy.stability, 0)

        self.assertNotEqual(again.stability, good.stability)
        self.assertNotEqual(good.stability, easy.stability)
        self.assertNotEqual(again.stability, easy.stability)

    def test_initial_stability_is_positive_after_rating(self):
        core = FSRSCore()
        state = core.initial_state()

        result = core.review(state=state, rating="good")

        self.assertGreater(result.stability, 0)

    def test_initial_difficulty_is_within_valid_range(self):
        core = FSRSCore()

        for rating in core.SUPPORTED_RATINGS:
            difficulty = core.initial_difficulty(rating)

            self.assertGreaterEqual(difficulty, 1)
            self.assertLessEqual(difficulty, 10)

    def test_initial_difficulty_decreases_with_better_rating(self):
        core = FSRSCore()

        again = core.initial_difficulty("again")
        hard = core.initial_difficulty("hard")
        good = core.initial_difficulty("good")
        easy = core.initial_difficulty("easy")

        self.assertGreater(again, hard)
        self.assertGreater(hard, good)
        self.assertGreater(good, easy)

    def test_review_sets_initial_difficulty_for_new_card(self):
        core = FSRSCore()
        state = core.initial_state()

        result = core.review(state=state,rating= "good")

        self.assertAlmostEqual(
            result.difficulty,
            core.initial_difficulty("good"),
            places=10,
        )

    def test_review_uses_initial_stability_for_new_card(self):
        core = FSRSCore()
        state = core.initial_state()

        result = core.review(state=state,rating= "good")

        self.assertAlmostEqual(
            result.stability,
            core.initial_stability("good"),
            places=10,
        )

    def test_review_increases_repetitions(self):
        core = FSRSCore()
        state = core.initial_state()

        result = core.review(state=state, rating="good")

        self.assertEqual(
            result.repetitions,
            state.repetitions + 1,
        )

    def test_review_does_not_mutate_input_state(self):
        core = FSRSCore()
        state = FSRSState(
            stability=10.0,
            difficulty=5.0,
            elapsed_days=5.0,
            scheduled_days=10.0,
            repetitions=3,
            lapses=1,
        )

        original = FSRSState(
            stability=state.stability,
            difficulty=state.difficulty,
            elapsed_days=state.elapsed_days,
            scheduled_days=state.scheduled_days,
            repetitions=state.repetitions,
            lapses=state.lapses,
        )

        core.review(state=state,rating= "good")

        self.assertEqual(state, original)

    def test_invalid_rating_is_rejected(self):
        core = FSRSCore()
        state = core.initial_state()

        with self.assertRaises(ValueError):
            core.review(state=state, rating="invalid")

    def test_all_ratings_are_supported(self):
        core = FSRSCore()
        state = core.initial_state()

        for rating in ("again", "hard", "good", "easy"):
            result = core.review(state=state, rating=rating)

            self.assertIsNotNone(result)

    def test_review_is_deterministic(self):
        core = FSRSCore()
        state = FSRSState(
            stability=10.0,
            difficulty=5.0,
            elapsed_days=5.0,
            scheduled_days=10.0,
            repetitions=3,
            lapses=1,
        )

        result_a = core.review(state=state,rating= "good")
        result_b = core.review(state=state,rating= "good")

        self.assertEqual(result_a, result_b)

    def test_retrievability_is_one_at_zero_elapsed_days(self):
        core = FSRSCore()

        result = core.retrievability(
            elapsed_days=0,
            stability=10,
        )

        self.assertAlmostEqual(result, 1.0, places=10)

    def test_retrievability_is_point_nine_at_stability(self):
        core = FSRSCore()

        result = core.retrievability(
            elapsed_days=10,
            stability=10,
        )

        self.assertAlmostEqual(result, 0.90, places=10)

    def test_retrievability_decreases_as_time_passes(self):
        core = FSRSCore()

        r1 = core.retrievability(
            elapsed_days=1,
            stability=10,
        )
        r2 = core.retrievability(
            elapsed_days=5,
            stability=10,
        )
        r3 = core.retrievability(
            elapsed_days=20,
            stability=10,
        )

        self.assertGreater(r1, r2)
        self.assertGreater(r2, r3)

    def test_retrievability_is_higher_for_more_stable_memory(self):
        core = FSRSCore()

        less_stable = core.retrievability(
            elapsed_days=10,
            stability=5,
        )
        more_stable = core.retrievability(
            elapsed_days=10,
            stability=20,
        )

        self.assertGreater(more_stable, less_stable)

    def test_retrievability_is_between_zero_and_one(self):
        core = FSRSCore()

        result = core.retrievability(
            elapsed_days=100,
            stability=10,
        )

        self.assertGreater(result, 0)
        self.assertLessEqual(result, 1)

    def test_retrievability_is_deterministic(self):
        core = FSRSCore()

        result_a = core.retrievability(
            elapsed_days=7,
            stability=12.5,
        )
        result_b = core.retrievability(
            elapsed_days=7,
            stability=12.5,
        )

        self.assertEqual(result_a, result_b)

    def test_retrievability_is_used_for_existing_card(self):
        core = FSRSCore()

        state = FSRSState(
            stability=10.0,
            difficulty=5.0,
            elapsed_days=5.0,
            scheduled_days=10.0,
            repetitions=1,
            lapses=0,
        )

        result = core.review(state=state,rating= "good")

        self.assertGreater(result.stability, 0)

    def test_existing_card_updates_difficulty(self):
        core = FSRSCore()

        state = FSRSState(
            stability=10.0,
            difficulty=5.0,
            elapsed_days=5.0,
            scheduled_days=10.0,
            repetitions=1,
            lapses=0,
        )

        result = core.review(state=state, rating="easy")

        self.assertNotEqual(
            result.difficulty,
            state.difficulty,
        )

    def test_existing_card_updates_stability(self):
        core = FSRSCore()

        state = FSRSState(
            stability=10.0,
            difficulty=5.0,
            elapsed_days=5.0,
            scheduled_days=10.0,
            repetitions=1,
            lapses=0,
        )

        result = core.review(state=state,rating= "good")

        self.assertNotEqual(
            result.stability,
            state.stability,
        )

    def test_next_stability_returns_a_different_value(self):
        core = FSRSCore()

        result = core.next_stability(
            stability=10.0,
            difficulty=5.0,
            retrievability=0.9,
            rating="good",
        )

        self.assertNotEqual(result, 10.0)

    def test_existing_card_again_increments_lapses(self):
        core = FSRSCore()

        state = FSRSState(
            stability=10.0,
            difficulty=5.0,
            elapsed_days=5.0,
            scheduled_days=10.0,
            repetitions=3,
            lapses=1,
        )

        result = core.review(state=state,rating= "again")

        self.assertEqual(
            result.lapses,
            state.lapses + 1,
        )

    def test_existing_card_again_updates_stability(self):
        core = FSRSCore()

        state = FSRSState(
            stability=10.0,
            difficulty=5.0,
            elapsed_days=5.0,
            scheduled_days=10.0,
            repetitions=3,
            lapses=1,
        )

        result = core.review(state=state,rating= "again")

        self.assertNotEqual(
            result.stability,
            state.stability,
        )

    def test_next_difficulty_is_reverted_toward_initial_difficulty(self):
        core = FSRSCore()

        result = core.next_difficulty(
            difficulty=9.0,
            rating="good",
        )

        self.assertLess(result, 9.0)

    def test_next_difficulty_uses_good_difficulty_as_mean_reversion_anchor(self):
        core = FSRSCore()

        difficulty = 9.0
        rating = "good"

        weights = core.parameters.weights
        w6 = weights[6]
        w7 = weights[7]

        adjusted = difficulty - w6 * (3 - 3)

        expected = (
            w7 * weights[4]
            + (1 - w7) * adjusted
        )

        result = core.next_difficulty(
            difficulty=difficulty,
            rating=rating,
        )

        self.assertAlmostEqual(
            result,
            expected,
            places=6,
        )

    def test_lapse_stability_is_positive(self):
        core = FSRSCore()

        result = core.next_lapse_stability(
            stability=10.0,
            difficulty=5.0,
            retrievability=0.8,
        )

        self.assertGreater(result, 0)

    def test_hard_rating_produces_less_stability_than_good(self):
        core = FSRSCore()

        hard = core.next_stability(
            stability=10.0,
            difficulty=5.0,
            retrievability=0.8,
            rating="hard",
        )

        good = core.next_stability(
            stability=10.0,
            difficulty=5.0,
            retrievability=0.8,
            rating="good",
        )

        self.assertLess(hard, good)
    def test_easy_rating_has_easy_bonus(self):
        core = FSRSCore()

        good = core.next_stability(
            stability=10.0,
            difficulty=5.0,
            retrievability=0.8,
            rating="good",
        )

        easy = core.next_stability(
            stability=10.0,
            difficulty=5.0,
            retrievability=0.8,
            rating="easy",
        )

        self.assertGreater(easy, good)
    def test_good_stability_matches_fsrs6_formula(self):
        core = FSRSCore()

        stability = 10.0
        difficulty = 5.0
        retrievability = 0.8

        weights = core.parameters.weights

        expected = stability * (
            1.0
            + math.exp(weights[8])
            * (11.0 - difficulty)
            * math.pow(stability, -weights[9])
            * (
                math.exp(
                    (1.0 - retrievability) * weights[10]
                )
                - 1.0
            )
        )

        result = core.next_stability(
            stability=stability,
            difficulty=difficulty,
            retrievability=retrievability,
            rating="good",
        )

        self.assertAlmostEqual(
            result,
            expected,
            places=10,
        )
    def test_hard_stability_uses_hard_penalty(self):
        core = FSRSCore()

        stability = 10.0
        difficulty = 5.0
        retrievability = 0.8

        weights = core.parameters.weights

        base_growth = (
            math.exp(weights[8])
            * (11.0 - difficulty)
            * math.pow(stability, -weights[9])
            * (
                math.exp(
                    (1.0 - retrievability) * weights[10]
                )
                - 1.0
            )
        )

        expected = stability * (
            1.0
            + base_growth * weights[15]
        )

        result = core.next_stability(
            stability=stability,
            difficulty=difficulty,
            retrievability=retrievability,
            rating="hard",
        )

        self.assertAlmostEqual(
            result,
            expected,
            places=10,
        )
    def test_lapse_stability_matches_fsrs6_formula(self):
        core = FSRSCore()

        stability = 10.0
        difficulty = 5.0
        retrievability = 0.8

        weights = core.parameters.weights

        long_term = (
            weights[11]
            * math.pow(
                difficulty,
                -weights[12],
            )
            * (
                math.pow(
                    stability + 1.0,
                    weights[13],
                )
                - 1.0
            )
            * math.exp(
                weights[14]
                * (1.0 - retrievability)
            )
        )

        short_term = (
            stability
            / math.exp(
                weights[17] * weights[18]
            )
        )

        expected = min(
            long_term,
            short_term,
        )

        result = core.next_lapse_stability(
            stability=stability,
            difficulty=difficulty,
            retrievability=retrievability,
        )

        self.assertAlmostEqual(
            result,
            expected,
            places=10,
        )
    def test_again_review_uses_lapse_stability(self):
        core = FSRSCore()

        state = FSRSState(
            stability=10.0,
            difficulty=5.0,
            elapsed_days=5.0,
            scheduled_days=10.0,
            repetitions=3,
            lapses=1,
        )

        retrievability = core.retrievability(
            elapsed_days=state.elapsed_days,
            stability=state.stability,
        )

        expected = core.next_lapse_stability(
            stability=state.stability,
            difficulty=state.difficulty,
            retrievability=retrievability,
        )

        result = core.review(
            state=state,
            rating="again",
        )

        self.assertAlmostEqual(
            result.stability,
            expected,
            places=10,
        )