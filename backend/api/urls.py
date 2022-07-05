from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet, TagViewSet


app_name = "api"

router = routers.DefaultRouter()

router.register("users", UserViewSet, basename="users")
router.register("tags", TagViewSet, basename="tags")

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]

