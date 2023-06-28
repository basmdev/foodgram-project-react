from rest_framework import viewsets

from users.models import CustomUser

from .serializers import CustomUserSerializer

class CustomUserViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели CustomUser."""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer