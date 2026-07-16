"""
Consolidated API views for ESPPA — all ViewSets in one file.
"""

import logging
from typing import Any, Dict, Optional

from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from django.db import models as django_models
from django.contrib.auth.models import User

from apps.esppa.models import Analysis, Prediction, Employee, UserProfile
from apps.esppa.api.serializers import (
    UserSerializer, UserProfileSerializer,
    EmployeeSerializer, EmployeeListSerializer,
    AnalysisSerializer,
    PredictionSerializer, PredictionInputSerializer,
    DashboardMetricsSerializer,
)
from core.deps import get_data_service, get_ml_service, get_employee_service

logger = logging.getLogger(__name__)


# ── Shared helpers ──────────────────────────────────────────────────────────

def _require_data():
    svc = get_data_service()
    if svc is None:
        raise RuntimeError("Data service not available. Install pandas, numpy, scikit-learn.")
    return svc

def _require_ml():
    svc = get_ml_service()
    if svc is None:
        raise RuntimeError("ML service not available. Install scikit-learn, xgboost.")
    return svc

def _require_employee():
    svc = get_employee_service()
    if svc is None:
        raise RuntimeError("Employee service not available. Install pandas.")
    return svc


# ── User Views ──────────────────────────────────────────────────────────────

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only API endpoint for User profiles."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)


class UserProfileViewSet(viewsets.ModelViewSet):
    """API endpoint for UserProfile CRUD operations."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ── Employee Views ──────────────────────────────────────────────────────────

class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only API endpoint for Employee data."""
    queryset = Employee.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return EmployeeListSerializer if self.action == 'list' else EmployeeSerializer

    @decorators.action(detail=False, methods=['get'])
    def search(self, request):
        emp_id = request.query_params.get('id')
        if not emp_id:
            return Response({'error': 'Please provide an employee ID parameter (id=)'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            employee = Employee.objects.get(employee_id=int(emp_id))
            return Response(EmployeeSerializer(employee).data)
        except Employee.DoesNotExist:
            return Response({'error': f'Employee with ID {emp_id} not found'},
                            status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'error': 'Employee ID must be a number'},
                            status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=['get'])
    def department_summary(self, request):
        dept_counts = (
            Employee.objects.values('department')
            .annotate(count=django_models.Count('id'))
            .order_by('-count')
        )
        return Response(list(dept_counts))


# ── Analysis Views ──────────────────────────────────────────────────────────

class AnalysisViewSet(viewsets.ModelViewSet):
    """API endpoint for Analysis records."""
    serializer_class = AnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Analysis.objects.filter(created_by=self.request.user)


# ── Prediction Views ────────────────────────────────────────────────────────

class PredictionViewSet(viewsets.ModelViewSet):
    """API endpoint for Prediction records with custom predict action."""
    serializer_class = PredictionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Prediction.objects.filter(created_by=self.request.user)

    @decorators.action(detail=False, methods=['post'])
    def predict(self, request):
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


# ── Dashboard Views ─────────────────────────────────────────────────────────

def _load_metrics() -> Optional[Dict[str, Any]]:
    try:
        data_service = _require_data()
        employee_service = _require_employee()
        df = data_service.load_csv()
        metrics = employee_service.build_dashboard_metrics(df)
        return metrics
    except (FileNotFoundError, RuntimeError) as exc:
        logger.warning("Dashboard data not found: %s", exc)
        return None


class DashboardViewSet(viewsets.ViewSet):
    """API endpoint for dashboard metrics and analysis."""
    permission_classes = [permissions.IsAuthenticated]

    def _apply_metrics(self, transform):
        metrics = _load_metrics()
        if metrics is None:
            return Response({'error': 'Data file not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            return Response(transform(metrics))
        except (ValueError, KeyError) as exc:
            logger.exception("Dashboard data processing error")
            return Response({'error': f'Data processing error: {exc}'}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=['get'])
    def metrics(self, request):
        return self._apply_metrics(
            lambda m: DashboardMetricsSerializer({
                'total_employees': m.total_employees,
                'avg_performance': m.avg_performance,
                'avg_salary_inr': m.avg_salary_inr,
                'resignation_rate': m.resignation_rate,
                'high_performers': m.high_performers,
                'medium_performers': m.medium_performers,
                'low_performers': m.low_performers,
            }).data,
        )

    @decorators.action(detail=False, methods=['get'])
    def department_data(self, request):
        return self._apply_metrics(
            lambda m: [{
                'name': d.name, 'count': d.count,
                'performance': d.performance,
                'performance_width': d.performance_width,
                'salary_inr': d.salary_inr,
            } for d in m.department_data],
        )

    @decorators.action(detail=False, methods=['get'])
    def demographics(self, request):
        return self._apply_metrics(
            lambda m: {
                'gender_counts': m.gender_counts,
                'education_counts': m.education_counts,
            },
        )


# ── Model Analysis Views ────────────────────────────────────────────────────

class ModelAnalysisViewSet(viewsets.ViewSet):
    """API endpoint for model performance comparison."""
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=False, methods=['get'])
    def compare(self, request):
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
