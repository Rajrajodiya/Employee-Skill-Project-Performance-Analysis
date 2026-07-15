"""
API URL configuration for the ESPPA application.
Uses DRF's DefaultRouter for clean RESTful routing.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import api_views

router = DefaultRouter(trailing_slash=False)
router.register(r'users', api_views.UserViewSet, basename='api-user')
router.register(r'profiles', api_views.UserProfileViewSet, basename='api-profile')
router.register(r'employees', api_views.EmployeeViewSet, basename='api-employee')
router.register(r'analyses', api_views.AnalysisViewSet, basename='api-analysis')
router.register(r'predictions', api_views.PredictionViewSet, basename='api-prediction')
router.register(r'dashboard', api_views.DashboardViewSet, basename='api-dashboard')
router.register(r'models', api_views.ModelAnalysisViewSet, basename='api-model')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
