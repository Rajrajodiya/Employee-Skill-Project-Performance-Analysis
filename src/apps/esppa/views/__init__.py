"""ESPPA views — split by responsibility (auth, dashboard, analysis, prediction, models, employees, profile)."""

import logging
import threading

# ── Shared service initialisation (lazy, thread-safe) ──────────────────────
_service_lock = threading.Lock()
_services_initialised = False
_data_service = None  # type: ignore
_ml_service = None    # type: ignore
_employee_service = None  # type: ignore

logger = logging.getLogger(__name__)


def _init_services() -> None:
    """Initialize all services exactly once (thread-safe)."""
    from apps.esppa.services.data_service import DataService
    from apps.esppa.services.ml_service import MLService
    from apps.esppa.services.employee_service import EmployeeService

    global _data_service, _ml_service, _employee_service, _services_initialised
    if _services_initialised:
        return
    with _service_lock:
        if _services_initialised:
            return
        _data_service = DataService()
        _ml_service = MLService(_data_service)
        _employee_service = EmployeeService()
        _services_initialised = True


def _get_data_service():
    _init_services()
    return _data_service


def _get_ml_service():
    _init_services()
    return _ml_service


def _get_employee_service():
    _init_services()
    return _employee_service


def _load_ml_models() -> None:
    """Lazily initialise models (called once per process on first request)."""
    ml_service = _get_ml_service()
    if not ml_service.models:
        try:
            ml_service.load_or_train_models()
        except Exception as exc:
            logger.error("Failed to load models: %s", exc)


# ── Re-export all view functions ──────────────────────────────────────────
from .auth_views import register_view                           # noqa: E402, F401
from .dashboard_views import dashboard_view                     # noqa: E402, F401
from .analysis_views import analysis_view                       # noqa: E402, F401
from .prediction_views import prediction_view                   # noqa: E402, F401
from .model_analysis_views import model_analysis_view           # noqa: E402, F401
from .employee_views import employee_list_view                  # noqa: E402, F401
from .profile_views import profile_view                         # noqa: E402, F401

__all__ = [
    'register_view', 'dashboard_view', 'analysis_view',
    'prediction_view', 'model_analysis_view', 'employee_list_view', 'profile_view',
]
