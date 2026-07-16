"""Analysis API views — single responsibility: analysis record CRUD."""

from rest_framework import viewsets, permissions

from apps.esppa.models import Analysis
from apps.esppa.schemas import AnalysisSerializer


class AnalysisViewSet(viewsets.ModelViewSet):
    """API endpoint for Analysis records."""
    serializer_class = AnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Analysis.objects.filter(created_by=self.request.user)
