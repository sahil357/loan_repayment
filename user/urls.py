from django.urls import path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from user.views import AuthViewSet

router = DefaultRouter()
router.register(r"user", AuthViewSet, basename="users")

urlpatterns = [
    path('', include(router.urls))
]