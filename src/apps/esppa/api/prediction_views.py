"""Prediction API views — single responsibility: prediction endpoints with custom predict action."""

import logging

from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response

from apps.esppa.models import Prediction
from apps.esppa.schemas import PredictionSerializer, PredictionInputSerializer
from apps.esppa.api import _require_ml

logger = logging.getLogger(__name__)


class PredictionViewSet(viewsets.ModelViewSet):
    """API endpoint for Prediction records with custom predict action."""
    serializer_class = PredictionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Prediction.objects.filter(created_by=self.request.user)

    @decorators.action(detail=False, methods=['post'])
    def predict(self, request):
        """Make a prediction using the specified ML model."""
        serializer = PredictionInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            ml_service = _require_ml()
            if not ml_service.models:
                ml_service.load_or_train_models()

            result = ml_service.predict(
                model_type=serializer.validated_data['model_type'],
                input_data=serializer.validated_data,
            )

            prediction = Prediction.objects.create(
                created_by=request.user,
                model_type=serializer.validated_data['model_type'],
                input_data=serializer.validated_data,
                prediction_result=result.predicted_value,
                confidence_score=result.confidence,
                accuracy=result.accuracy,
                error_rate=result.error_rate,
            )

            return Response({
                'id': prediction.id,
                'model_type': prediction.model_type,
                'model_display': result.model_display_name,
                'prediction_result': result.predicted_value,
                'confidence_score': result.confidence,
                'accuracy': result.accuracy,
                'error_rate': result.error_rate,
                'created_at': prediction.created_at,
            })
        except (FileNotFoundError, ValueError) as exc:
            logger.exception("API prediction input error")
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except (RuntimeError, ImportError) as exc:
            logger.exception("API prediction model error")
            return Response({'error': f'Model error: {exc}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
