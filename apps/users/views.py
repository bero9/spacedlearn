from rest_framework_simplejwt.views import TokenObtainPairView

from apps.users.serializers import LoginSerializer


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    