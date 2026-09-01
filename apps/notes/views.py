from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.notes.models import Note
from apps.notes.serializers import NoteSerializer
from apps.notes.services.note_service import NoteService
from rest_framework.exceptions import PermissionDenied


class NoteViewSet(ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(
            note_type__owner=self.request.user
        )

    def perform_create(self, serializer):
        note_type = serializer.validated_data["note_type"]

        if note_type.owner != self.request.user:

            raise PermissionDenied(
                "You do not have permission to use this note type."
        )

        NoteService.create_note(
            note_type=note_type,
            fields=serializer.validated_data["fields"],
    )