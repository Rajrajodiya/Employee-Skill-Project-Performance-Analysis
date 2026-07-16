"""
ESPPA REST API — consolidated ViewSets in api/views.py, serializers in api/serializers.py.

Shared service instances are accessed lazily via core.deps getter functions.
"""

from core.deps import get_data_service, get_ml_service, get_employee_service


def _require_data():
    svc = get_data_service()
    if svc is None:
        raise RuntimeError("Data service is not available. Install pandas, numpy, scikit-learn.")
    return svc


def _require_ml():
    svc = get_ml_service()
    if svc is None:
        raise RuntimeError("ML service is not available. Install scikit-learn, xgboost.")
    return svc


def _require_employee():
    svc = get_employee_service()
    if svc is None:
        raise RuntimeError("Employee service is not available. Install pandas.")
    return svc


# ── Re-export all ViewSets ─────────────────────────────────────────────────
from .views import (                                                    # noqa: E402, F401
    UserViewSet, UserProfileViewSet, EmployeeViewSet,
    AnalysisViewSet, PredictionViewSet, DashboardViewSet,
    ModelAnalysisViewSet,
)

__all__ = [
    'UserViewSet', 'UserProfileViewSet', 'EmployeeViewSet',
    'AnalysisViewSet', 'PredictionViewSet', 'DashboardViewSet',
    'ModelAnalysisViewSet',
]
