from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('analysis/', views.analysis_view, name='analysis'),
    path('analysis/result/', views.analysis_view, name='analysis_result'),
    path('prediction/', views.prediction_view, name='prediction'),
    path('model-analysis/', views.model_analysis_view, name='model_analysis'),
    path('profile/', views.profile_view, name='profile'),
    path('employees/', views.employee_list_view, name='employee_list'),
]
