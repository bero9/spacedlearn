from apps.notes.models import Note
from apps.notes.services.validation import NoteValidator


class NoteService:

    @staticmethod
    def create_note(note_type, fields):
        validator = NoteValidator(note_type)

        validator.validate(fields)

        return Note.objects.create(
            note_type=note_type,
            fields=fields,
        )