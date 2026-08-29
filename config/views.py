from django.http import JsonResponse


def home(request):
    return JsonResponse({
        "message": "Welcome to SpacedLearn API"
    },
    status=200

    )