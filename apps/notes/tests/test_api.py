from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.notes.models import Note, NoteType
from apps.users.models import User


class NoteAPITests(TestCase):

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

        self.token_a = str(
            RefreshToken.for_user(self.user_a).access_token
        )

        self.token_b = str(
            RefreshToken.for_user(self.user_b).access_token
        )

        self.note_type_a = NoteType.objects.create(
            owner=self.user_a,
            name="User A Vocabulary",
            description="Private vocabulary.",
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
            description="Private vocabulary.",
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
                "word": "apple",
                "meaning": "تفاحة",
            },
        )

        self.note_b = Note.objects.create(
            note_type=self.note_type_b,
            fields={
                "word": "book",
                "meaning": "كتاب",
            },
        )

    def test_unauthenticated_user_cannot_access_notes(self):
        response = self.client.get("/api/notes/")

        self.assertEqual(response.status_code, 401)

    def test_authenticated_user_can_access_notes(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.token_a}"
        )

        response = self.client.get("/api/notes/")

        self.assertEqual(response.status_code, 200)

    def test_user_a_sees_only_own_notes(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.token_a}"
        )

        response = self.client.get("/api/notes/")

        self.assertEqual(response.status_code, 200)

        returned_ids = [
            item["id"]
            for item in response.data
        ]

        self.assertIn(self.note_a.id, returned_ids)
        self.assertNotIn(self.note_b.id, returned_ids)

    def test_user_b_sees_only_own_notes(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.token_b}"
        )

        response = self.client.get("/api/notes/")

        self.assertEqual(response.status_code, 200)

        returned_ids = [
            item["id"]
            for item in response.data
        ]

        self.assertIn(self.note_b.id, returned_ids)
        self.assertNotIn(self.note_a.id, returned_ids)