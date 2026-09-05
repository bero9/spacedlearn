from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from apps.study.services.study_queue_service import StudyQueueService


class StudyQueueAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit_value = request.query_params.get(
            "limit",
            "20",
        )

        try:
            limit = int(limit_value)
        except (TypeError, ValueError):
            raise ValidationError(
                {
                    "limit": "Limit must be a positive integer.",
                }
            )

        if limit <= 0:
            raise ValidationError(
                {
                    "limit": "Limit must be a positive integer.",
                }
            )
        deck_id = request.query_params.get(
            "deck_id",
        )

        if deck_id is not None:
            deck_id = int(deck_id)

        cards = StudyQueueService.get_queue(
            user=request.user,
            limit=limit,
            deck_id=deck_id,
        )

        return Response(
            [
                {
                    "id": card.id,
                    "deck_id": card.deck_id,
                    "note_id": card.note_id,
                    "state": card.user_review_states[0].state,
                    "due_at": card.user_review_states[0].due_at,
                }
                for card in cards
            ],
            status=200,
        )