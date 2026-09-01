from django.test import TestCase

from apps.users.models import User
from apps.decks.models import Deck
from apps.notes.models import NoteType, Note

from apps.cards.models import Card
from apps.cards.services.card_service import CardService

from rest_framework.exceptions import PermissionDenied


class CardServiceTests(TestCase):

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

        self.deck_a = Deck.objects.create(
            owner=self.user_a,
            name="User A Deck",
        )

        self.deck_b = Deck.objects.create(
            owner=self.user_b,
            name="User B Deck",
        )

        self.note_type_a = NoteType.objects.create(
            owner=self.user_a,
            name="User A Vocabulary",
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

        self.note_type_b = NoteType.objects.create(
            owner=self.user_b,
            name="User B Vocabulary",
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

        self.note_a = Note.objects.create(
            note_type=self.note_type_a,
            fields={
                "word": "persistent",
                "meaning": "مثابر",
            },
        )

        self.note_b = Note.objects.create(
            note_type=self.note_type_b,
            fields={
                "word": "consistent",
                "meaning": "متسق",
            },
        )

    def test_user_can_create_card_with_own_deck_and_note(self):
        card = CardService.create_card(
            user=self.user_a,
            deck=self.deck_a,
            note=self.note_a,
        )

        self.assertIsNotNone(card.id)
        self.assertEqual(card.deck, self.deck_a)
        self.assertEqual(card.note, self.note_a)

    def test_user_cannot_create_card_with_other_users_deck(self):
        with self.assertRaises(PermissionDenied):
            CardService.create_card(
                user=self.user_a,
                deck=self.deck_b,
                note=self.note_a,
            )

    def test_user_cannot_create_card_with_other_users_note(self):
        with self.assertRaises(PermissionDenied):
            CardService.create_card(
                user=self.user_a,
                deck=self.deck_a,
                note=self.note_b,
            )

    def test_card_is_not_created_when_deck_is_not_owned(self):
        with self.assertRaises(PermissionDenied):
            CardService.create_card(
                user=self.user_a,
                deck=self.deck_b,
                note=self.note_a,
            )

        self.assertEqual(Card.objects.count(), 0)

    def test_card_is_not_created_when_note_is_not_owned(self):
        with self.assertRaises(PermissionDenied):
            CardService.create_card(
                user=self.user_a,
                deck=self.deck_a,
                note=self.note_b,
            )

        self.assertEqual(Card.objects.count(), 0)