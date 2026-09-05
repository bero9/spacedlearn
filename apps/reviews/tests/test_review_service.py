from django.test import TestCase
from django.utils import timezone

from apps.users.models import User
from apps.decks.models import Deck
from apps.notes.models import NoteType, Note
from apps.cards.models import Card
from apps.reviews.models import ReviewState
from apps.reviews.services.review_service import ReviewService
from rest_framework.exceptions import PermissionDenied



class ReviewServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="reviewservice_user",
            email="reviewservice@example.com",
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
                "meaning": "ط¸â€¦ط·آ«ط·آ§ط·آ¨ط·آ±",
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

        self.now = timezone.now()

    def test_review_service_can_review_card(self):
        service = ReviewService()

        result = service.review(
            user=self.user,
            card=self.card,
            rating="good",
            now=self.now,
        )

        self.assertIsNotNone(result)
    def test_review_updates_review_state(self):
        service = ReviewService()

        service.review(
            user=self.user,
            card=self.card,
            rating="good",
            now=self.now,
        )

        self.review_state.refresh_from_db()

        self.assertEqual(
            self.review_state.state,
            ReviewState.State.LEARNING,
        )

        self.assertGreater(
            self.review_state.stability,
            0.0,
        )

        self.assertGreater(
            self.review_state.difficulty,
            0.0,
        )

        self.assertGreater(
            self.review_state.scheduled_days,
            0.0,
        )

        self.assertEqual(
            self.review_state.repetitions,
            1,
        )

        self.assertEqual(
            self.review_state.last_review_at,
            self.now,
        )

        self.assertIsNotNone(
            self.review_state.due_at,
        )
    def test_review_creates_review_log(self):
        from apps.reviews.models import ReviewLog

        service = ReviewService()

        service.review(
            user=self.user,
            card=self.card,
            rating="good",
            now=self.now,
        )

        log = ReviewLog.objects.get(
            user=self.user,
            card=self.card,
        )

        self.assertEqual(
            log.rating,
            ReviewLog.Rating.GOOD,
        )

        self.assertEqual(
            log.previous_state,
            ReviewState.State.NEW,
        )

        self.assertEqual(
            log.new_state,
            ReviewState.State.LEARNING,
        )
    def test_review_is_atomic(self):
        from unittest.mock import patch

        from apps.reviews.models import ReviewLog

        service = ReviewService()

        with patch.object(
            ReviewLog.objects,
            "create",
            side_effect=Exception("log failed"),
        ):
            with self.assertRaises(Exception):
                service.review(
                    user=self.user,
                    card=self.card,
                    rating="good",
                    now=self.now,
                )

        self.review_state.refresh_from_db()

        self.assertEqual(
            self.review_state.state,
            ReviewState.State.NEW,
        )
    def test_review_log_stores_elapsed_days(self):
        from datetime import timedelta

        from apps.reviews.models import ReviewLog

        service = ReviewService()

        first_review_at = self.now

        service.review(
            user=self.user,
            card=self.card,
            rating="good",
            now=first_review_at,
        )

        second_review_at = first_review_at + timedelta(days=2)

        service.review(
            user=self.user,
            card=self.card,
            rating="good",
            now=second_review_at,
        )

        log = ReviewLog.objects.filter(
            user=self.user,
            card=self.card,
        ).order_by("-reviewed_at").first()

        self.assertIsNotNone(log)

        self.assertAlmostEqual(
            log.elapsed_days,
            2.0,
            places=5,
        )
    def test_review_log_stores_scheduled_days(self):
        from apps.reviews.models import ReviewLog

        service = ReviewService()

        service.review(
            user=self.user,
            card=self.card,
            rating="good",
            now=self.now,
        )
        self.review_state.refresh_from_db()
        log = ReviewLog.objects.filter(
            user=self.user,
            card=self.card,
        ).order_by("-reviewed_at").first()

        self.assertIsNotNone(log)

        self.assertEqual(
            log.previous_scheduled_days,
            0.0,
        )

        self.assertEqual(
            log.new_scheduled_days,
            self.review_state.scheduled_days,
        )

        self.assertGreater(
            log.new_scheduled_days,
            0.0,
        )
    def test_user_cannot_review_card_owned_by_another_user(self):
        another_user = User.objects.create_user(
            username="another_review_user",
            email="another_review@example.com",
            password="password123",
        )

        service = ReviewService()

        with self.assertRaises(PermissionDenied):
            service.review(
                user=another_user,
                card=self.card,
                rating="good",
                now=self.now,
            )