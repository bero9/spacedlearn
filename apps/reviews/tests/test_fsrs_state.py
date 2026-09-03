from django.test import SimpleTestCase


class FSRSStateTests(SimpleTestCase):

    def test_fsrs_state_contains_memory_state_fields(self):
        from apps.reviews.services.schedulers.core.fsrs_core import (
            FSRSState,
        )

        state = FSRSState()

        self.assertTrue(
            hasattr(state, "stability")
        )

        self.assertTrue(
            hasattr(state, "difficulty")
        )

        self.assertTrue(
            hasattr(state, "elapsed_days")
        )

        self.assertTrue(
            hasattr(state, "scheduled_days")
        )

    def test_initial_state_has_zero_stability(self):
        from apps.reviews.services.schedulers.core.fsrs_core import (
            FSRSState,
        )

        state = FSRSState()

        self.assertEqual(
            state.stability,
            0.0,
        )

    def test_initial_state_has_zero_difficulty(self):
        from apps.reviews.services.schedulers.core.fsrs_core import (
            FSRSState,
        )

        state = FSRSState()

        self.assertEqual(
            state.difficulty,
            0.0,
        )

    def test_initial_state_has_zero_elapsed_days(self):
        from apps.reviews.services.schedulers.core.fsrs_core import (
            FSRSState,
        )

        state = FSRSState()

        self.assertEqual(
            state.elapsed_days,
            0.0,
        )

    def test_initial_state_has_zero_scheduled_days(self):
        from apps.reviews.services.schedulers.core.fsrs_core import (
            FSRSState,
        )

        state = FSRSState()

        self.assertEqual(
            state.scheduled_days,
            0.0,
        )

    def test_fsrs_state_is_immutable(self):
        from apps.reviews.services.schedulers.core.fsrs_core import (
            FSRSState,
        )

        state = FSRSState()

        with self.assertRaises(Exception):
            state.stability = 10.0
    def test_fsrs_parameters_have_desired_retention(self):
        from apps.reviews.services.schedulers.core.fsrs_core import (
            FSRSParameters,
        )

        parameters = FSRSParameters()

        self.assertEqual(
            parameters.desired_retention,
            0.90,
        )

    def test_desired_retention_must_be_between_zero_and_one(self):
        from apps.reviews.services.schedulers.core.fsrs_core import (
            FSRSParameters,
        )

        with self.assertRaises(ValueError):
            FSRSParameters(
                desired_retention=0.0,
            )

        with self.assertRaises(ValueError):
            FSRSParameters(
                desired_retention=1.0,
            )

    def test_fsrs_parameters_are_immutable(self):
        from apps.reviews.services.schedulers.core.fsrs_core import (
            FSRSParameters,
        )

        parameters = FSRSParameters()

        with self.assertRaises(Exception):
            parameters.desired_retention = 0.95
    def test_fsrs_parameters_have_21_weights(self):
        from apps.reviews.services.schedulers.core.fsrs_core import (
            FSRSParameters,
        )

        parameters = FSRSParameters()

        self.assertEqual(
            len(parameters.weights),
            21,
        )

    def test_default_fsrs_weights_match_fsrs_6(self):
        from apps.reviews.services.schedulers.core.fsrs_core import (
            FSRSParameters,
        )

        parameters = FSRSParameters()

        expected = (
            0.212,
            1.2931,
            2.3065,
            8.2956,
            6.4133,
            0.8334,
            3.0194,
            0.001,
            1.8722,
            0.1666,
            0.796,
            1.4835,
            0.0614,
            0.2629,
            1.6483,
            0.6014,
            1.8729,
            0.5425,
            0.0912,
            0.0658,
            0.1542,
        )

        self.assertEqual(
            parameters.weights,
            expected,
        )

    def test_fsrs_parameters_have_maximum_interval(self):
        from apps.reviews.services.schedulers.core.fsrs_core import (
            FSRSParameters,
        )

        parameters = FSRSParameters()

        self.assertGreater(
            parameters.maximum_interval,
            0,
        )

    def test_fsrs_weights_are_immutable(self):
        from apps.reviews.services.schedulers.core.fsrs_core import (
            FSRSParameters,
        )

        parameters = FSRSParameters()

        with self.assertRaises(Exception):
            parameters.weights = (1.0,) * 21