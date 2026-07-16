"""
API URL configuration for the ESPPA application.
Uses DRF's DefaultRouter for clean RESTful routing.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import (
    UserViewSet, UserProfileViewSet, EmployeeViewSet,
    AnalysisViewSet, PredictionViewSet, DashboardViewSet,
    ModelAnalysisViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet, basename='api-user')
router.register(r'profiles', UserProfileViewSet, basename='api-profile')
router.register(r'employees', EmployeeViewSet, basename='api-employee')
router.register(r'analyses', AnalysisViewSet, basename='api-analysis')
router.register(r'predictions', PredictionViewSet, basename='api-prediction')
router.register(r'dashboard', DashboardViewSet, basename='api-dashboard')
router.register(r'models', ModelAnalysisViewSet, basename='api-model')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
