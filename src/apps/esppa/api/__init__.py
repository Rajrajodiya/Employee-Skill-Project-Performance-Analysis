"""ESPPA REST API — split by resource (user, employee, analysis, prediction, dashboard, models).

Shared service instances imported from core.deps (FastAPI DI pattern).
"""

from core.deps import get_data_service, get_ml_service, get_employee_service

_data_service = get_data_service()
_ml_service = get_ml_service()
_employee_service = get_employee_service()

# ── Re-export all ViewSets ─────────────────────────────────────────────────
from .user_views import UserViewSet, UserProfileViewSet               # noqa: E402, F401
from .employee_views import EmployeeViewSet                           # noqa: E402, F401
from .analysis_views import AnalysisViewSet                           # noqa: E402, F401
from .prediction_views import PredictionViewSet                       # noqa: E402, F401
from .dashboard_views import DashboardViewSet                         # noqa: E402, F401
from .model_views import ModelAnalysisViewSet                          # noqa: E402, F401

__all__ = [
    'UserViewSet', 'UserProfileViewSet', 'EmployeeViewSet',
    'AnalysisViewSet', 'PredictionViewSet', 'DashboardViewSet',
    'ModelAnalysisViewSet',
]

