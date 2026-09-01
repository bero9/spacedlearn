from django.test import TestCase

from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken

from apps.notes.models import Note, NoteType
from apps.notes.serializers import NoteSerializer

from apps.notes.views import NoteViewSet
from apps.users.models import User
class NoteAuthorizationTests(TestCase):

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

    # ثم NoteTypes...
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
    def test_user_sees_only_own_notes(self):
        factory = APIRequestFactory()

        request = factory.get("/api/notes/")
        request.user = self.user_a

        view = NoteViewSet()
        view.request = request

        queryset = view.get_queryset()

        self.assertIn(self.note_a, queryset)
        self.assertNotIn(self.note_b, queryset)
    def test_user_cannot_access_other_users_note(self):
        factory = APIRequestFactory()

        request = factory.get(
            f"/api/notes/{self.note_b.id}/"
    )
        request.user = self.user_a

        view = NoteViewSet()
        view.request = request

        queryset = view.get_queryset()

        self.assertNotIn(self.note_b, queryset)
    def test_user_cannot_create_note_using_other_users_note_type(self):
        serializer = NoteSerializer(
            data={
                "note_type": self.note_type_b.id,
                "fields": {
                    "word": "computer",
                    "meaning": "حاسوب",
            },
        }
    )

        self.assertTrue(serializer.is_valid())

        view = NoteViewSet()

        factory = APIRequestFactory()
        request = factory.post("/api/notes/")
        request.user = self.user_a

        view.request = request

        

        with self.assertRaises(PermissionDenied):
            view.perform_create(serializer)

    