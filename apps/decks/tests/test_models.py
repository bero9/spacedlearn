from django.test import TestCase

from apps.decks.models import Deck
from apps.users.models import User


class DeckModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="deckuser",
            email="deck@example.com",
            password="password123",
        )

    def test_deck_is_created_with_owner(self):
        deck = Deck.objects.create(
            owner=self.user,
            name="English Vocabulary",
        )

        self.assertIsNotNone(deck.id)
        self.assertEqual(deck.owner, self.user)
        self.assertEqual(deck.name, "English Vocabulary")

    def test_description_is_optional(self):
        deck = Deck.objects.create(
            owner=self.user,
            name="English Vocabulary",
        )

        self.assertEqual(deck.description, "")

    def test_default_visibility_is_private(self):
        deck = Deck.objects.create(
            owner=self.user,
            name="English Vocabulary",
        )

        self.assertEqual(
            deck.visibility,
            Deck.Visibility.PRIVATE,
        )

    def test_deck_can_be_public(self):
        deck = Deck.objects.create(
            owner=self.user,
            name="Public English",
            visibility=Deck.Visibility.PUBLIC,
        )

        self.assertEqual(
            deck.visibility,
            Deck.Visibility.PUBLIC,
        )

    def test_deck_can_be_unlisted(self):
        deck = Deck.objects.create(
            owner=self.user,
            name="Unlisted English",
            visibility=Deck.Visibility.UNLISTED,
        )

        self.assertEqual(
            deck.visibility,
            Deck.Visibility.UNLISTED,
        )

    def test_user_can_access_owned_decks_through_related_name(self):
        Deck.objects.create(
            owner=self.user,
            name="English",
        )

        Deck.objects.create(
            owner=self.user,
            name="Programming",
        )

        self.assertEqual(
            self.user.decks.count(),
            2,
        )

    def test_string_representation(self):
        deck = Deck.objects.create(
            owner=self.user,
            name="English Vocabulary",
        )

        self.assertEqual(
            str(deck),
            "English Vocabulary",
        )