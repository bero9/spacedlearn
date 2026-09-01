from django.test import TestCase

from apps.notes.models import  NoteType

from apps.notes.services.validation import (
    NoteValidationError,
    NoteValidator,
)
from apps.users.models import User
class NoteValidatorTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
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
                        "label": "Word",
                        "required": True,
                        "order": 1,
                    },
                    {
                        "name": "meaning",
                        "type": "text",
                        "label": "Meaning",
                        "required": True,
                        "order": 2,
                    },
                    {
                        "name": "example",
                        "type": "text",
                        "label": "Example",
                        "required": False,
                        "order": 3,
                    },
                ]
            },
        )

        self.validator = NoteValidator(self.note_type)

    def test_valid_note(self):
        fields = {
            "word": "resilient",
            "meaning": "قادر على التعافي",
            "example": "She is resilient.",
        }

        self.assertTrue(
            self.validator.validate(fields)
        )

    def test_optional_field_can_be_missing(self):
        fields = {
            "word": "resilient",
            "meaning": "قادر على التعافي",
        }

        self.assertTrue(
            self.validator.validate(fields)
        )

    def test_required_field_cannot_be_missing(self):
        fields = {
            "word": "resilient",
        }

        with self.assertRaises(NoteValidationError):
            self.validator.validate(fields)

    def test_unknown_field_is_rejected(self):
        fields = {
            "word": "resilient",
            "meaning": "قادر على التعافي",
            "banana": "hello",
        }

        with self.assertRaises(NoteValidationError):
            self.validator.validate(fields)

    def test_invalid_type_is_rejected(self):
        fields = {
            "word": 123,
            "meaning": "قادر على التعافي",
        }

        with self.assertRaises(NoteValidationError):
            self.validator.validate(fields)
