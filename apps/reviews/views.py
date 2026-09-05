from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cards.models import Card
from apps.reviews.services.review_service import ReviewService

from apps.reviews.serializers import ReviewSerializer
from django.shortcuts import get_object_or_404


class ReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):


        serializer = ReviewSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )
        card = get_object_or_404(
            Card,
            id=serializer.validated_data["card_id"],
        )
        result = ReviewService().review(
            user=request.user,
            card=card,
            rating=serializer.validated_data["rating"],
            now=timezone.now(),
        )
        return Response(
            {
                "state": result.state,
                "due_at": result.due_at,
                "stability": result.stability,
                "difficulty": result.difficulty,
                "scheduled_days": result.scheduled_days,
                "elapsed_days": result.elapsed_days,
            },
            status=200,
        )
    def test_user_cannot_review_card_owned_by_another_user(self):
        another_user = User.objects.create_user(
            username="another_review_user",
            email="another_review@example.com",
            password="password123",
        )

        self.client.force_authenticate(
            user=another_user,
        )

        response = self.client.post(
            "/api/reviews/",
            {
                "card_id": self.card.id,
                "rating": "good",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403,
        )