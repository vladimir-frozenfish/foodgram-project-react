from rest_framework import viewsets

from recipes.models import User
from .serializers import UserSerializer
from .permissions import IsUserOrReadAndCreate


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsUserOrReadAndCreate]
    queryset = User.objects.all()
    serializer_class = UserSerializer
