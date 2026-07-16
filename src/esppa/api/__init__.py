"""ESPPA REST API — split by resource (user, employee, analysis, prediction, dashboard, models).

Shared service instances live here and are imported by individual view modules.
"""

import logging

from esppa.services.data_service import DataService
from esppa.services.ml_service import MLService
from esppa.services.employee_service import EmployeeService

logger = logging.getLogger(__name__)

_data_service = DataService()
_ml_service = MLService(_data_service)
_employee_service = EmployeeService()

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
