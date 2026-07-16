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

from __future__ import annotations

import logging
import threading
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from apps.esppa.services.data_service import DataService
    from apps.esppa.services.ml_service import MLService
    from apps.esppa.services.employee_service import EmployeeService

logger = logging.getLogger(__name__)

# ── Module-level state ──────────────────────────────────────────────────────
_lock = threading.Lock()
_initialised = False
_data_service: "Optional[DataService]" = None
_ml_service: "Optional[MLService]" = None
_employee_service: "Optional[EmployeeService]" = None


def _init_services() -> None:
    """Initialize all services exactly once (thread-safe).

    Lazy imports allow the app to boot gracefully even when ML libraries
    (pandas, numpy, scikit-learn, xgboost, matplotlib) are not installed.
    """
    global _data_service, _ml_service, _employee_service, _initialised
    if _initialised:
        return
    with _lock:
        if _initialised:
            return

        # ── DataService (requires pandas, numpy, sklearn) ─────────────────
        try:
            from apps.esppa.services.data_service import DataService  # noqa: F811
            _data_service = DataService()
        except ImportError:
            logger.warning(
                "DataService unavailable — pandas/numpy/sklearn not installed. "
                "Dashboard and analysis features will be unavailable."
            )
            _data_service = None

        # ── MLService (requires sklearn, xgboost) ─────────────────────────
        if _data_service is not None:
            try:
                from apps.esppa.services.ml_service import MLService  # noqa: F811
                _ml_service = MLService(_data_service)
            except ImportError:
                logger.warning(
                    "MLService unavailable — sklearn/xgboost not installed. "
                    "Prediction and model analysis features will be unavailable."
                )
                _ml_service = None
        else:
            _ml_service = None

        # ── EmployeeService (requires pandas) ─────────────────────────────
        try:
            from apps.esppa.services.employee_service import EmployeeService  # noqa: F811
            _employee_service = EmployeeService()
        except ImportError:
            logger.warning(
                "EmployeeService unavailable — pandas not installed. "
                "Dashboard employee metrics will be unavailable."
            )
            _employee_service = None

        _initialised = True


def get_data_service() -> Optional[DataService]:
    """Return the singleton DataService instance, or None if unavailable."""
    _init_services()
    return _data_service


def get_ml_service() -> Optional[MLService]:
    """Return the singleton MLService instance, or None if unavailable."""
    _init_services()
    return _ml_service


def get_employee_service() -> Optional[EmployeeService]:
    """Return the singleton EmployeeService instance, or None if unavailable."""
    _init_services()
    return _employee_service


def load_ml_models() -> None:
    """Lazily initialise ML models (called once per process on first request).

    Fails fast on known ML errors — does NOT catch broad Exception.
    """
    ml_service = get_ml_service()
    if ml_service is None:
        raise RuntimeError(
            "ML service not available. Install scikit-learn and xgboost."
        )
    if ml_service.models:
        return
    try:
        ml_service.load_or_train_models()
    except (FileNotFoundError, ImportError, RuntimeError, ValueError) as exc:
        logger.error("Failed to load ML models: %s", exc)
        raise
