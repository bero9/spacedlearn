from datetime import datetime
from unittest.mock import patch

from django.test import TestCase

from rest_framework.test import APIClient

from apps.users.models import User
from apps.decks.models import Deck
from apps.notes.models import NoteType, Note
from apps.cards.models import Card
from apps.reviews.models import ReviewState


class ReviewAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="reviewapi_user",
            email="reviewapi@example.com",
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
                "meaning": "ثابت",
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

    def test_authenticated_user_can_review_card(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.post(
            "/api/reviews/",
            {
                "card_id": self.card.id,
                "rating": "good",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    @patch("apps.reviews.views.ReviewService")
    def test_review_api_calls_review_service(
        self,
        mock_review_service,
    ):
        self.client.force_authenticate(
            user=self.user,
        )

        mock_review_service.return_value.review.return_value = type(
            "SchedulingResult",
            (),
            {
                "state": "review",
                "due_at": datetime(
                    2026,
                    9,
                    10,
                    12,
                    0,
                ),
                "stability": 5.0,
                "difficulty": 4.0,
                "scheduled_days": 6.0,
                "elapsed_days": 2.0,
            },
        )()

        response = self.client.post(
            "/api/reviews/",
            {
                "card_id": self.card.id,
                "rating": "good",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        mock_review_service.return_value.review.assert_called_once()

    @patch("apps.reviews.views.ReviewService")
    def test_review_api_returns_scheduling_result(
        self,
        mock_review_service,
    ):
        self.client.force_authenticate(
            user=self.user,
        )

        due_at = datetime(
            2026,
            9,
            10,
            12,
            0,
        )

        mock_result = type(
            "SchedulingResult",
            (),
            {
                "state": "review",
                "due_at": due_at,
                "stability": 5.0,
                "difficulty": 4.0,
                "scheduled_days": 6.0,
                "elapsed_days": 2.0,
            },
        )()

        mock_review_service.return_value.review.return_value = mock_result

        response = self.client.post(
            "/api/reviews/",
            {
                "card_id": self.card.id,
                "rating": "good",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.data["state"],
            "review",
        )

        self.assertEqual(
            response.data["stability"],
            5.0,
        )

        self.assertEqual(
            response.data["difficulty"],
            4.0,
        )

        self.assertEqual(
            response.data["scheduled_days"],
            6.0,
        )

        self.assertEqual(
            response.data["elapsed_days"],
            2.0,
        )

    def test_invalid_rating_returns_400(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.post(
            "/api/reviews/",
            {
                "card_id": self.card.id,
                "rating": "invalid",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_nonexistent_card_returns_404(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.post(
            "/api/reviews/",
            {
                "card_id": 999999,
                "rating": "good",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            404,
        )
    def test_user_cannot_review_card_owned_by_another_user(self):
        another_user = User.objects.create_user(
            username="another_review_user",
            email="another_review@example.com",
            password="password123",
        )

        self.client.force_authenticate(
            user=another_user,
        )

        response = self.client.post(
            "/api/reviews/",
            {
                "card_id": self.card.id,
                "rating": "good",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            404,
        )