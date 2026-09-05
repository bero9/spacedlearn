from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from rest_framework.test import APIClient

from apps.users.models import User
from apps.decks.models import Deck
from apps.notes.models import NoteType, Note
from apps.cards.models import Card
from apps.reviews.models import ReviewState


class StudyQueueAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="studyqueue_user",
            email="studyqueue@example.com",
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
            due_at=timezone.now() - timedelta(
                minutes=5,
            ),
        )

    def test_authenticated_user_can_get_due_cards(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.get(
            "/api/study/queue/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            self.card.id,
        )
    def test_future_card_is_not_in_queue(self):
        future_note = Note.objects.create(
            note_type=self.note_type,
            fields={
                "word": "future",
                "meaning": "مستقبلي",
            },
        )

        future_card = Card.objects.create(
            deck=self.deck,
            note=future_note,
        )
        ReviewState.objects.create(
            user=self.user,
            card=future_card,
            due_at=timezone.now() + timedelta(
                days=1,
            ),
        )

        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.get(
            "/api/study/queue/",
        )

        card_ids = [
            card["id"]
            for card in response.data
        ]

        self.assertNotIn(
            future_card.id,
            card_ids,
        )

    def test_user_cannot_see_another_users_cards(self):
        another_user = User.objects.create_user(
            username="another_study_user",
            email="another_study@example.com",
            password="password123",
        )

        another_deck = Deck.objects.create(
            owner=another_user,
            name="Another Deck",
        )

        another_note = Note.objects.create(
            note_type=self.note_type,
            fields={
                "word": "another",
                "meaning": "آخر",
            },
        )

        another_card = Card.objects.create(
            deck=another_deck,
            note=another_note,
        )
        ReviewState.objects.create(
            user=another_user,
            card=another_card,
            due_at=timezone.now() - timedelta(
                minutes=5,
            ),
        )

        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.get(
            "/api/study/queue/",
        )

        card_ids = [
            card["id"]
            for card in response.data
        ]

        self.assertNotIn(
            another_card.id,
            card_ids,
        )

    def test_queue_respects_limit(self):
        for index in range(5):
            note = Note.objects.create(
                note_type=self.note_type,
                fields={
                    "word": f"word-{index}",
                    "meaning": f"meaning-{index}",
                },
            )

            card = Card.objects.create(
                deck=self.deck,
                note=note,
            )

            ReviewState.objects.create(
                user=self.user,
                card=card,
                due_at=timezone.now() - timedelta(
                    minutes=index + 1,
                ),
            )

        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.get(
            "/api/study/queue/?limit=3",
        )

        self.assertEqual(
            len(response.data),
            3,
        )

    def test_queue_can_filter_by_deck(self):
        another_deck = Deck.objects.create(
            name="Another Deck",
            owner=self.user,
        )

        another_note = Note.objects.create(
            note_type=self.note_type,
            fields={
                "word": "another deck",
                "meaning": "مجموعة أخرى",
            },
        )

        another_card = Card.objects.create(
            deck=another_deck,
            note=another_note,
        )
        ReviewState.objects.create(
            user=self.user,
            card=another_card,
            due_at=timezone.now() - timedelta(
                minutes=5,
            ),
        )

        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.get(
            f"/api/study/queue/?deck_id={another_deck.id}",
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            another_card.id,
        )
    def test_unauthenticated_user_cannot_access_queue(self):
        response = self.client.get(
            "/api/study/queue/",
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_invalid_limit_returns_bad_request(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.get(
            "/api/study/queue/?limit=abc",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_non_positive_limit_returns_bad_request(self):
        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.get(
            "/api/study/queue/?limit=0",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_queue_is_ordered_by_due_at(self):
        earlier_note = Note.objects.create(
            note_type=self.note_type,
            fields={
                "word": "earlier",
                "meaning": "أبكر",
            },
        )

        earlier_card = Card.objects.create(
            deck=self.deck,
            note=earlier_note,
        )

        later_note = Note.objects.create(
            note_type=self.note_type,
            fields={
                "word": "later",
                "meaning": "لاحق",
            },
        )

        later_card = Card.objects.create(
            deck=self.deck,
            note=later_note,
        )

        now = timezone.now()

        ReviewState.objects.filter(
            user=self.user,
            card=self.card,
        ).update(
            due_at=now - timedelta(
                minutes=10,
            ),
        )

        ReviewState.objects.create(
            user=self.user,
            card=earlier_card,
            due_at=now - timedelta(
                minutes=30,
            ),
        )

        ReviewState.objects.create(
            user=self.user,
            card=later_card,
            due_at=now - timedelta(
                minutes=5,
            ),
        )

        self.client.force_authenticate(
            user=self.user,
        )

        response = self.client.get(
            "/api/study/queue/",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            [item["id"] for item in response.data],
            [
                earlier_card.id,
                self.card.id,
                later_card.id,
            ],
        )