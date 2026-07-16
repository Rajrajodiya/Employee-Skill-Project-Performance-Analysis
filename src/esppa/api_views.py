"""
REST API views for the ESPPA application.

Uses Django REST Framework ViewSets for clean, CRUD-based endpoints.
Includes custom actions for predictions, dashboard metrics, and model analysis.
"""

import logging

from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import models as django_models

from .models import Employee, Analysis, Prediction, UserProfile
from .serializers import (
    UserSerializer, UserProfileSerializer, EmployeeSerializer,
    EmployeeListSerializer, AnalysisSerializer, PredictionSerializer,
    PredictionInputSerializer, DashboardMetricsSerializer,
)
from .services.data_service import DataService
from .services.ml_service import MLService
from .services.employee_service import EmployeeService

logger = logging.getLogger(__name__)

_data_service = DataService()
_ml_service = MLService(_data_service)
_employee_service = EmployeeService()


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


class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only API endpoint for Employee data."""
    queryset = Employee.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return EmployeeListSerializer if self.action == 'list' else EmployeeSerializer

    @decorators.action(detail=False, methods=['get'])
    def search(self, request):
        """Search for an employee by employee_id."""
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
        """Get department-wise employee counts."""
        dept_counts = (
            Employee.objects.values('department')
            .annotate(count=django_models.Count('id'))
            .order_by('-count')
        )
        return Response(list(dept_counts))


class AnalysisViewSet(viewsets.ModelViewSet):
    """API endpoint for Analysis records."""
    serializer_class = AnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Analysis.objects.filter(created_by=self.request.user)


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
            if not _ml_service.models:
                _ml_service.load_or_train_models()

            result = _ml_service.predict(
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


class DashboardViewSet(viewsets.ViewSet):
    """API endpoint for dashboard metrics and analysis."""
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=False, methods=['get'])
    def metrics(self, request):
        """Return all dashboard KPIs."""
        try:
            df = _data_service.load_csv()
            metrics = _employee_service.build_dashboard_metrics(df)
            return Response(DashboardMetricsSerializer({
                'total_employees': metrics.total_employees,
                'avg_performance': metrics.avg_performance,
                'avg_salary_inr': metrics.avg_salary_inr,
                'resignation_rate': metrics.resignation_rate,
                'high_performers': metrics.high_performers,
                'medium_performers': metrics.medium_performers,
                'low_performers': metrics.low_performers,
            }).data)
        except FileNotFoundError as exc:
            return Response({'error': f'Data file not found: {exc}'},
                            status=status.HTTP_404_NOT_FOUND)
        except (ValueError, KeyError) as exc:
            return Response({'error': f'Data processing error: {exc}'},
                            status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=['get'])
    def department_data(self, request):
        """Return department-wise analytics data."""
        try:
            df = _data_service.load_csv()
            metrics = _employee_service.build_dashboard_metrics(df)
            return Response([{
                'name': d.name, 'count': d.count,
                'performance': d.performance,
                'performance_width': d.performance_width,
                'salary_inr': d.salary_inr,
            } for d in metrics.department_data])
        except FileNotFoundError as exc:
            return Response({'error': f'Data file not found: {exc}'},
                            status=status.HTTP_404_NOT_FOUND)
        except (ValueError, KeyError) as exc:
            return Response({'error': f'Data processing error: {exc}'},
                            status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=False, methods=['get'])
    def demographics(self, request):
        """Return gender and education demographics."""
        try:
            df = _data_service.load_csv()
            metrics = _employee_service.build_dashboard_metrics(df)
            return Response({
                'gender_counts': metrics.gender_counts,
                'education_counts': metrics.education_counts,
            })
        except FileNotFoundError as exc:
            return Response({'error': f'Data file not found: {exc}'},
                            status=status.HTTP_404_NOT_FOUND)
        except (ValueError, KeyError) as exc:
            return Response({'error': f'Data processing error: {exc}'},
                            status=status.HTTP_400_BAD_REQUEST)


class ModelAnalysisViewSet(viewsets.ViewSet):
    """API endpoint for model performance comparison."""
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=False, methods=['get'])
    def compare(self, request):
        """Return model performance metrics for comparison."""
        try:
            if not _ml_service.models:
                _ml_service.load_or_train_models()
            performances = _ml_service.evaluate_all_models()
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
            if not _ml_service.models:
                _ml_service.load_or_train_models()
            importance = _ml_service.get_feature_importance('random_forest')
            if importance:
                return Response(importance)
            return Response({'error': 'Feature importance not available'},
                            status=status.HTTP_404_NOT_FOUND)
        except (FileNotFoundError, ValueError, RuntimeError) as exc:
            return Response({'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
