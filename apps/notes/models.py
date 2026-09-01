from django.conf import settings
from django.db import models


class NoteType(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="note_types",
    )

    name = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    fields_schema = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Note(models.Model):
    note_type = models.ForeignKey(
        NoteType,
        on_delete=models.CASCADE,
        related_name="notes",
    )

    fields = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.note_type.name} Note"