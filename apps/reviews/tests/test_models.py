from django.test import TestCase

from apps.users.models import User
from apps.decks.models import Deck
from apps.notes.models import NoteType, Note
from apps.cards.models import Card

from apps.reviews.models import ReviewState, ReviewLog

class ReviewStateModelTests(TestCase):

    def setUp(self):
        self.user_a = User.objects.create_user(
            username="user_a",
            email="a@example.com",
            password="password123",
        )

        self.user_b = User.objects.create_user(
            username="user_b",
            email="b@example.com",
            password="password123",
        )

        self.deck = Deck.objects.create(
            owner=self.user_a,
            name="English Vocabulary",
        )

        self.note_type = NoteType.objects.create(
            owner=self.user_a,
            name="Vocabulary",
            fields_schema={
                "fields": [
                    {
                        "name": "word",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "name": "meaning",
                        "type": "text",
                        "required": True,
                    },
                ]
            },
        )

        self.note = Note.objects.create(
            note_type=self.note_type,
            fields={
                "word": "persistent",
                "meaning": "مثابر",
            },
        )

        self.card = Card.objects.create(
            deck=self.deck,
            note=self.note,
        )

    def test_user_can_have_review_state_for_card(self):
        review_state = ReviewState.objects.create(
            user=self.user_a,
            card=self.card,
        )

        self.assertEqual(review_state.user, self.user_a)
        self.assertEqual(review_state.card, self.card)

    def test_review_state_is_unique_per_user_and_card(self):
        ReviewState.objects.create(
            user=self.user_a,
            card=self.card,
        )

        with self.assertRaises(Exception):
            ReviewState.objects.create(
                user=self.user_a,
                card=self.card,
            )

    def test_different_users_can_have_state_for_same_card(self):
        state_a = ReviewState.objects.create(
            user=self.user_a,
            card=self.card,
        )

        state_b = ReviewState.objects.create(
            user=self.user_b,
            card=self.card,
        )

        self.assertNotEqual(state_a.id, state_b.id)

    def test_default_state_is_new(self):
        review_state = ReviewState.objects.create(
            user=self.user_a,
            card=self.card,
        )

        self.assertEqual(
            review_state.state,
            ReviewState.State.NEW,
        )

    def test_new_card_has_no_due_date(self):
        review_state = ReviewState.objects.create(
            user=self.user_a,
            card=self.card,
        )

        self.assertIsNone(review_state.due_at)

    def test_initial_repetitions_and_lapses_are_zero(self):
        review_state = ReviewState.objects.create(
            user=self.user_a,
            card=self.card,
        )

        self.assertEqual(review_state.repetitions, 0)
        self.assertEqual(review_state.lapses, 0)

    def test_new_card_has_no_last_review(self):
        review_state = ReviewState.objects.create(
            user=self.user_a,
            card=self.card,
        )

        self.assertIsNone(review_state.last_review_at)

    def test_different_users_have_independent_states(self):
        state_a = ReviewState.objects.create(
            user=self.user_a,
            card=self.card,
        )

        state_b = ReviewState.objects.create(
            user=self.user_b,
            card=self.card,
        )

        self.assertEqual(state_a.state, ReviewState.State.NEW)
        self.assertEqual(state_b.state, ReviewState.State.NEW)

        self.assertEqual(state_a.repetitions, 0)
        self.assertEqual(state_b.repetitions, 0)

class ReviewLogModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="reviewuser",
            email="review@example.com",
            password="password123",
        )

        self.deck = Deck.objects.create(
            owner=self.user,
            name="English Vocabulary",
        )

        self.note_type = NoteType.objects.create(
            owner=self.user,
            name="Vocabulary",
            fields_schema={
                "fields": [
                    {
                        "name": "word",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "name": "meaning",
                        "type": "text",
                        "required": True,
                    },
                ]
            },
        )

        self.note = Note.objects.create(
            note_type=self.note_type,
            fields={
                "word": "persistent",
                "meaning": "مثابر",
            },
        )

        self.card = Card.objects.create(
            deck=self.deck,
            note=self.note,
        )

        self.review_state = ReviewState.objects.create(
            user=self.user,
            card=self.card,
        )

    def test_review_log_can_be_created(self):
        log = ReviewLog.objects.create(
            user=self.user,
            card=self.card,
            rating=ReviewLog.Rating.GOOD,
            previous_state=ReviewState.State.NEW,
            new_state=ReviewState.State.REVIEW,
        )

        self.assertIsNotNone(log.id)
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.card, self.card)

    def test_review_log_stores_rating(self):
        log = ReviewLog.objects.create(
            user=self.user,
            card=self.card,
            rating=ReviewLog.Rating.GOOD,
            previous_state=ReviewState.State.NEW,
            new_state=ReviewState.State.REVIEW,
        )

        self.assertEqual(
            log.rating,
            ReviewLog.Rating.GOOD,
        )

    def test_review_log_stores_state_transition(self):
        log = ReviewLog.objects.create(
            user=self.user,
            card=self.card,
            rating=ReviewLog.Rating.AGAIN,
            previous_state=ReviewState.State.REVIEW,
            new_state=ReviewState.State.RELEARNING,
        )

        self.assertEqual(
            log.previous_state,
            ReviewState.State.REVIEW,
        )

        self.assertEqual(
            log.new_state,
            ReviewState.State.RELEARNING,
        )

    def test_review_log_has_reviewed_at(self):
        log = ReviewLog.objects.create(
            user=self.user,
            card=self.card,
            rating=ReviewLog.Rating.GOOD,
            previous_state=ReviewState.State.NEW,
            new_state=ReviewState.State.REVIEW,
        )

        self.assertIsNotNone(log.reviewed_at)

    def test_review_log_stores_previous_and_new_stability(self):
        log = ReviewLog.objects.create(
            user=self.user,
            card=self.card,
            rating=ReviewLog.Rating.GOOD,
            previous_state=ReviewState.State.NEW,
            new_state=ReviewState.State.REVIEW,
            previous_stability=0.0,
            new_stability=5.5,
        )

        self.assertEqual(log.previous_stability, 0.0)
        self.assertEqual(log.new_stability, 5.5)

    def test_review_log_stores_previous_and_new_difficulty(self):
        log = ReviewLog.objects.create(
            user=self.user,
            card=self.card,
            rating=ReviewLog.Rating.GOOD,
            previous_state=ReviewState.State.NEW,
            new_state=ReviewState.State.REVIEW,
            previous_difficulty=0.0,
            new_difficulty=6.2,
        )

        self.assertEqual(log.previous_difficulty, 0.0)
        self.assertEqual(log.new_difficulty, 6.2)

    def test_review_log_belongs_to_user_and_card(self):
        log = ReviewLog.objects.create(
            user=self.user,
            card=self.card,
            rating=ReviewLog.Rating.EASY,
            previous_state=ReviewState.State.LEARNING,
            new_state=ReviewState.State.REVIEW,
        )

        self.assertIn(
            log,
            self.user.review_logs.all(),
        )

        self.assertIn(
            log,
            self.card.review_logs.all(),
        )

    def test_review_log_supports_all_ratings(self):
        ratings = [
            ReviewLog.Rating.AGAIN,
            ReviewLog.Rating.HARD,
            ReviewLog.Rating.GOOD,
            ReviewLog.Rating.EASY,
        ]

        for index, rating in enumerate(ratings):
            log = ReviewLog.objects.create(
                user=self.user,
                card=Card.objects.create(
                    deck=self.deck,
                    note=Note.objects.create(
                        note_type=self.note_type,
                        fields={
                            "word": f"word-{index}",
                            "meaning": f"meaning-{index}",
                        },
                    ),
                ),
                rating=rating,
                previous_state=ReviewState.State.NEW,
                new_state=ReviewState.State.LEARNING,
            )

            self.assertEqual(log.rating, rating)