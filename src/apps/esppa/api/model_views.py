"""Model API views — single responsibility: ML model comparison and feature importance."""

import logging

from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response

from apps.esppa.api import _require_ml

logger = logging.getLogger(__name__)


class ModelAnalysisViewSet(viewsets.ViewSet):
    """API endpoint for model performance comparison."""
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=False, methods=['get'])
    def compare(self, request):
        """Return model performance metrics for comparison."""
        try:
            ml_service = _require_ml()
            if not ml_service.models:
                ml_service.load_or_train_models()
            performances = ml_service.evaluate_all_models()
            return Response({
                name: {'r2_score': m.r2_score, 'mse': m.mse, 'rmse': m.rmse, 'mae': m.mae}
                for name, m in performances.items()
            })
        except FileNotFoundError as exc:
            return Response({'error': f'Data file not found: {exc}'},
                            status=status.HTTP_404_NOT_FOUND)
        except (ValueError, RuntimeError) as exc:
            return Response({'error': f'Model evaluation error: {exc}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=False, methods=['get'])
    def feature_importance(self, request):
        """Return feature importance for the Random Forest model."""
        try:
            ml_service = _require_ml()
            if not ml_service.models:
                ml_service.load_or_train_models()
            importance = ml_service.get_feature_importance('random_forest')
            if importance:
                return Response(importance)
            return Response({'error': 'Feature importance not available'},
                            status=status.HTTP_404_NOT_FOUND)
        except (FileNotFoundError, ValueError, RuntimeError) as exc:
            return Response({'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
