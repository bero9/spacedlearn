from django.test import TestCase

from apps.users.models import User

from rest_framework.test import APIClient

from apps.decks.serializers import DeckSerializer

from apps.decks.models import Deck

class DeckAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
        )

    def test_unauthenticated_user_cannot_access_decks(self):
        response = self.client.get("/api/decks/")

        self.assertEqual(response.status_code, 401)
    def test_deck_name_is_required(self):
        serializer = DeckSerializer(
            data={
                "description": "English vocabulary",
                "visibility": "private",
        }
    )

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)
    def test_authenticated_user_can_create_deck(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/decks/",
        {
                "name": "English Vocabulary",
                "description": "My English words",
                "visibility": "private",
        },
            format="json",
    )

        self.assertEqual(response.status_code, 201)

        deck = Deck.objects.get(id=response.data["id"])

        self.assertEqual(deck.owner, self.user)
        self.assertEqual(deck.name, "English Vocabulary")
        self.assertEqual(
            deck.description,
            "My English words",
    )
        self.assertEqual(
            deck.visibility,
            Deck.Visibility.PRIVATE,
    )
    def test_authenticated_user_can_update_own_deck(self):
        self.client.force_authenticate(user=self.user)

        deck = Deck.objects.create(
            owner=self.user,
            name="Old Name",
            description="Old description",
            visibility=Deck.Visibility.PRIVATE,
    )

        response = self.client.patch(
            f"/api/decks/{deck.id}/",
        {
                "name": "New Name",
        },
            format="json",
    )

        self.assertEqual(response.status_code, 200)

        deck.refresh_from_db()

        self.assertEqual(deck.name, "New Name")
        self.assertEqual(deck.description, "Old description")
        self.assertEqual(
            deck.owner,
            self.user,
    )
    def test_user_cannot_update_another_users_deck(self):
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="password123",
    )

        deck = Deck.objects.create(
            owner=other_user,
            name="Other User Deck",
            description="Private deck",
            visibility=Deck.Visibility.PRIVATE,
    )

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f"/api/decks/{deck.id}/",
        {
                "name": "Hacked Name",
        },
            format="json",
    )

        self.assertEqual(response.status_code, 404)

        deck.refresh_from_db()

        self.assertEqual(
            deck.name,
            "Other User Deck",
    )
    def test_authenticated_user_can_delete_own_deck(self):
        self.client.force_authenticate(user=self.user)

        deck = Deck.objects.create(
            owner=self.user,
            name="Deck To Delete",
            description="Temporary deck",
            visibility=Deck.Visibility.PRIVATE,
    )

        response = self.client.delete(
            f"/api/decks/{deck.id}/"
    )

        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            Deck.objects.filter(id=deck.id).exists()
    )
    def test_user_cannot_delete_another_users_deck(self):
        other_user = User.objects.create_user(
            username="delete_other_user",
            email="delete_other@example.com",
            password="password123",
    )

        deck = Deck.objects.create(
            owner=other_user,
            name="Other User Deck",
            description="Private deck",
            visibility=Deck.Visibility.PRIVATE,
    )

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f"/api/decks/{deck.id}/"
    )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Deck.objects.filter(id=deck.id).exists()
    )
    def test_authenticated_user_can_create_public_deck(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/decks/",
        {
                "name": "Public English",
                "description": "Public vocabulary",
                "visibility": "public",
        },
            format="json",
    )

        self.assertEqual(response.status_code, 201)

        deck = Deck.objects.get(id=response.data["id"])

        self.assertEqual(
            deck.visibility,
            Deck.Visibility.PUBLIC,
    )
        self.assertEqual(
            deck.owner,
            self.user,
    )
    def test_invalid_visibility_is_rejected(self):
        serializer = DeckSerializer(
            data={
                "name": "Invalid Deck",
                "description": "Test deck",
                "visibility": "secret",
        }
    )

        self.assertFalse(serializer.is_valid())
        self.assertIn("visibility", serializer.errors)
    def test_owner_cannot_be_set_by_client(self):
        self.client.force_authenticate(user=self.user)

        other_user = User.objects.create_user(
            username="anotheruser",
            email="another@example.com",
            password="password123",
    )

        response = self.client.post(
            "/api/decks/",
        {
                "name": "Test Deck",
                "description": "Trying to fake owner",
                "visibility": "private",
                "owner": other_user.id,
        },
            format="json",
    )

        self.assertEqual(response.status_code, 201)

        deck = Deck.objects.get(id=response.data["id"])

        self.assertEqual(deck.owner, self.user)
        self.assertNotEqual(deck.owner, other_user)
    def test_description_is_optional_when_creating_deck(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/decks/",
        {
                "name": "English Vocabulary",
                "visibility": "private",
        },
            format="json",
    )

        self.assertEqual(response.status_code, 201)

        deck = Deck.objects.get(id=response.data["id"])

        self.assertEqual(deck.name, "English Vocabulary")
        self.assertEqual(deck.description, "")
        self.assertEqual(deck.owner, self.user)
    def test_user_does_not_see_other_users_public_deck_in_own_list(self):
        other_user = User.objects.create_user(
            username="public_owner",
            email="public_owner@example.com",
            password="password123",
    )

        public_deck = Deck.objects.create(
            owner=other_user,
            name="Public English",
            description="Public vocabulary",
            visibility=Deck.Visibility.PUBLIC,
    )

        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/decks/")

        self.assertEqual(response.status_code, 200)

        returned_ids = [
            item["id"]
            for item in response.data
    ]

        self.assertNotIn(
            public_deck.id,
            returned_ids,
    )
    def test_other_user_can_access_public_deck(self):
        other_user = User.objects.create_user(
            username="public_owner",
            email="public_owner@example.com",
            password="password123",
    )

        public_deck = Deck.objects.create(
            owner=other_user,
            name="Public English",
            description="Public vocabulary",
            visibility=Deck.Visibility.PUBLIC,
    )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f"/api/decks/{public_deck.id}/"
    )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["id"],
            public_deck.id,
    )

        self.assertEqual(
            response.data["visibility"],
            Deck.Visibility.PUBLIC,
    )
    def test_other_user_cannot_access_unlisted_deck(self):
        other_user = User.objects.create_user(
            username="unlisted_owner",
            email="unlisted_owner@example.com",
            password="password123",
    )

        unlisted_deck = Deck.objects.create(
            owner=other_user,
            name="Unlisted English",
            description="Unlisted vocabulary",
            visibility=Deck.Visibility.UNLISTED,
    )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f"/api/decks/{unlisted_deck.id}/"
    )

        self.assertEqual(response.status_code, 404)
    def test_owner_can_access_own_unlisted_deck(self):
        unlisted_deck = Deck.objects.create(
            owner=self.user,
            name="My Unlisted Deck",
            description="Private shareable deck",
            visibility=Deck.Visibility.UNLISTED,
    )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f"/api/decks/{unlisted_deck.id}/"
    )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["id"],
            unlisted_deck.id,
    )

        self.assertEqual(
            response.data["visibility"],
            Deck.Visibility.UNLISTED,
    )
    def test_other_user_cannot_update_public_deck(self):
        other_user = User.objects.create_user(
            username="public_owner_update",
            email="public_owner_update@example.com",
            password="password123",
    )

        public_deck = Deck.objects.create(
            owner=other_user,
            name="Original Name",
            description="Original description",
            visibility=Deck.Visibility.PUBLIC,
    )

        self.client.force_authenticate(user=self.user)

        response = self.client.put(
            f"/api/decks/{public_deck.id}/",
        {
                "name": "Hacked Name",
                "description": "Hacked description",
                "visibility": "public",
        },
            format="json",
    )

        self.assertEqual(response.status_code, 403)

        public_deck.refresh_from_db()

        self.assertEqual(
            public_deck.name,
            "Original Name",
    )