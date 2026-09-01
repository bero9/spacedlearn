from django.test import TestCase

from rest_framework.test import APIClient

from apps.users.models import User
from apps.decks.models import Deck
from apps.notes.models import NoteType, Note

from apps.cards.models import Card


class CardAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

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

        self.card_a = Card.objects.create(
            deck=self.deck_a,
            note=self.note_a,
        )

        self.card_b = Card.objects.create(
            deck=self.deck_b,
            note=self.note_b,
        )

    def authenticate_as_user_a(self):
        self.client.force_authenticate(user=self.user_a)

    def authenticate_as_user_b(self):
        self.client.force_authenticate(user=self.user_b)

    def test_unauthenticated_user_cannot_access_cards(self):
        response = self.client.get("/api/cards/")

        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_list_own_cards(self):
        self.authenticate_as_user_a()

        response = self.client.get("/api/cards/")

        self.assertEqual(response.status_code, 200)

        returned_ids = [
            item["id"]
            for item in response.data
        ]

        self.assertIn(self.card_a.id, returned_ids)
        self.assertNotIn(self.card_b.id, returned_ids)

    def test_user_can_create_card_with_own_deck_and_note(self):
        self.authenticate_as_user_a()

        note = Note.objects.create(
            note_type=self.note_type_a,
            fields={
                "word": "resilient",
                "meaning": "قادر على التعافي",
            },
        )

        response = self.client.post(
            "/api/cards/",
            {
                "deck": self.deck_a.id,
                "note": note.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        card = Card.objects.get(id=response.data["id"])

        self.assertEqual(card.deck, self.deck_a)
        self.assertEqual(card.note, note)

    def test_user_cannot_create_card_with_other_users_deck(self):
        self.authenticate_as_user_a()

        response = self.client.post(
            "/api/cards/",
            {
                "deck": self.deck_b.id,
                "note": self.note_a.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Card.objects.count(), 2)

    def test_user_cannot_create_card_with_other_users_note(self):
        self.authenticate_as_user_a()

        response = self.client.post(
            "/api/cards/",
            {
                "deck": self.deck_a.id,
                "note": self.note_b.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Card.objects.count(), 2)

    def test_user_can_retrieve_own_card(self):
        self.authenticate_as_user_a()

        response = self.client.get(
            f"/api/cards/{self.card_a.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.card_a.id)

    def test_user_cannot_retrieve_other_users_card(self):
        self.authenticate_as_user_a()

        response = self.client.get(
            f"/api/cards/{self.card_b.id}/"
        )

        self.assertEqual(response.status_code, 404)

    def test_user_cannot_update_other_users_card(self):
        self.authenticate_as_user_a()

        response = self.client.patch(
            f"/api/cards/{self.card_b.id}/",
            {
                "deck": self.deck_a.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_user_cannot_delete_other_users_card(self):
        self.authenticate_as_user_a()

        response = self.client.delete(
            f"/api/cards/{self.card_b.id}/"
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            Card.objects.filter(id=self.card_b.id).exists()
        )