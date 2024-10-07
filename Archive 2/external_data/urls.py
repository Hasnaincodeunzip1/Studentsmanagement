# external_data/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExternalLeadViewSet

router = DefaultRouter()
router.register(r'external-leads', ExternalLeadViewSet)

urlpatterns = [
    path('', include(router.urls)),
]