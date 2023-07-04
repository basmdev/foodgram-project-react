from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet

router = DefaultRouter()

router.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/', include('djoser.urls')),
    path('api/', include('djoser.urls.jwt')),
]
