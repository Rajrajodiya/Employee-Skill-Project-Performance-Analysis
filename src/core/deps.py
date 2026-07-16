"""
Dependency Injection Container — FastAPI-inspired pattern.

Provides lazily-initialized, thread-safe shared service instances
to both HTML views and API views. Eliminates duplication of service
initialization logic.

Usage:
    from core.deps import get_data_service, get_ml_service, get_employee_service

    data_service = get_data_service()
    ml_service = get_ml_service()
    employee_service = get_employee_service()
"""

import logging
import threading
from typing import Optional

from apps.esppa.services.data_service import DataService
from apps.esppa.services.ml_service import MLService
from apps.esppa.services.employee_service import EmployeeService

logger = logging.getLogger(__name__)

# ── Module-level state ──────────────────────────────────────────────────────
_lock = threading.Lock()
_initialised = False
_data_service: Optional[DataService] = None
_ml_service: Optional[MLService] = None
_employee_service: Optional[EmployeeService] = None


def _init_services() -> None:
    """Initialize all services exactly once (thread-safe)."""
    global _data_service, _ml_service, _employee_service, _initialised
    if _initialised:
        return
    with _lock:
        if _initialised:
            return
        _data_service = DataService()
        _ml_service = MLService(_data_service)
        _employee_service = EmployeeService()
        _initialised = True


def get_data_service() -> DataService:
    """Return the singleton DataService instance."""
    _init_services()
    assert _data_service is not None
    return _data_service


def get_ml_service() -> MLService:
    """Return the singleton MLService instance."""
    _init_services()
    assert _ml_service is not None
    return _ml_service


def get_employee_service() -> EmployeeService:
    """Return the singleton EmployeeService instance."""
    _init_services()
    assert _employee_service is not None
    return _employee_service


def load_ml_models() -> None:
    """Lazily initialise ML models (called once per process on first request).

    Fails fast on known ML errors — does NOT catch broad Exception.
    """
    ml_service = get_ml_service()
    if ml_service.models:
        return
    try:
        ml_service.load_or_train_models()
    except (FileNotFoundError, ImportError, RuntimeError, ValueError) as exc:
        logger.error("Failed to load ML models: %s", exc)
        raise
