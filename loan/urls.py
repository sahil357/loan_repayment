from django.urls import path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from loan.views import *

router = DefaultRouter()
router.register(r"loan", LoanViewSet, basename="loan")

urlpatterns = [
    path('', include(router.urls))
]