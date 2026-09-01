from django.test import TestCase

from apps.users.models import User
from apps.decks.models import Deck
from apps.notes.models import NoteType, Note

from apps.cards.models import Card

from django.db import IntegrityError

class CardModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="carduser",
            email="card@example.com",
            password="password123",
        )

        self.note_type = NoteType.objects.create(
            owner=self.user,
            name="English Vocabulary",
            description="Vocabulary notes.",
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

        self.deck = Deck.objects.create(
            owner=self.user,
            name="English Vocabulary",
        )
    def test_card_belongs_to_deck(self):
        card = Card.objects.create(
            deck=self.deck,
            note=self.note,
    )

        self.assertEqual(card.deck, self.deck)
        self.assertIn(card, self.deck.cards.all())


    def test_card_is_linked_to_one_note(self):
        card = Card.objects.create(
            deck=self.deck,
            note=self.note,
    )

        self.assertEqual(card.note, self.note)


    def test_same_note_cannot_be_used_by_two_cards(self):
        Card.objects.create(
            deck=self.deck,
            note=self.note,
    )

        another_deck = Deck.objects.create(
            owner=self.user,
            name="Another Deck",
    )

        with self.assertRaises(IntegrityError):
            Card.objects.create(
                deck=another_deck,
                note=self.note,
    )

        #print(type(context.exception))


    def test_note_can_exist_without_card(self):
        another_note = Note.objects.create(
            note_type=self.note_type,
            fields={
                "word": "consistent",
                "meaning": "متسق",
        },
    )

        self.assertIsNotNone(another_note.id)


    def test_card_does_not_have_separate_owner(self):
        card = Card.objects.create(
            deck=self.deck,
            note=self.note,
    )

        self.assertEqual(card.deck.owner, self.user)
        self.assertFalse(hasattr(card, "owner"))