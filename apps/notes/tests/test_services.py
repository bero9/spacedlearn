from django.test import TestCase


from apps.notes.models import Note, NoteType
from apps.notes.services.note_service import NoteService
from apps.notes.services.validation import (
    NoteValidationError,
)
from apps.users.models import User
class NoteServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="serviceuser",
            email="service@example.com",
            password="testpassword123",
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
                    {
                        "name": "example",
                        "type": "text",
                        "required": False,
                    },
                ]
            },
        )
    def test_create_note_with_valid_data(self):
        fields = {
            "word": "persistent",
            "meaning": "مثابر",
            "example": "He is persistent.",
    }

        note = NoteService.create_note(
            self.note_type,
            fields,
    )

        self.assertIsNotNone(note.id)
        self.assertEqual(note.note_type, self.note_type)
        self.assertEqual(note.fields, fields)


    def test_create_note_with_invalid_data(self):
        fields = {
            "word": "persistent",
    }

        with self.assertRaises(NoteValidationError):
            NoteService.create_note(
                self.note_type,
                fields,
        )
    def test_invalid_note_is_not_saved(self):
        fields = {
            "word": "persistent",
    }

        with self.assertRaises(NoteValidationError):
            NoteService.create_note(
                self.note_type,
                fields,
        )

        self.assertEqual(
            Note.objects.count(),
            0,
    )
