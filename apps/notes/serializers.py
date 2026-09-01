from rest_framework import serializers

from apps.notes.models import Note
from apps.notes.models import NoteType


class NoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Note
        fields = [
            "id",
            "note_type",
            "fields",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]