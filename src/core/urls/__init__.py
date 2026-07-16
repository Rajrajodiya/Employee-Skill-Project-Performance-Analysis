"""
Root URL configuration for ESPPA project.
"""

from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from apps.esppa.views.auth_views import login_view, register_view

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Application views
    path('', include('apps.esppa.urls')),

    # Authentication — custom login bypasses template file issues
    path('accounts/login/', login_view, name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),

    # REST API
    path('api/', include('apps.esppa.api.router')),

    # API Documentation (Swagger/OpenAPI)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'),
         name='redoc'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
