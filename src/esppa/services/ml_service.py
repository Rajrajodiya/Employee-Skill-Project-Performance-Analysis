"""
Service responsible for ML model training, prediction, and evaluation.
Features three modern models:
  - Random Forest (ensemble, interpretable)
  - XGBoost (gradient boosting, state-of-the-art)
  - Neural Network / MLP (deep learning, complex patterns)
"""

import os
import logging
import pickle
from typing import Any, Dict, Optional

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
)

from .config import (
    RANDOM_SEED,
    RF_N_ESTIMATORS,
    RF_MAX_DEPTH,
    XGB_N_ESTIMATORS,
    XGB_LEARNING_RATE,
    XGB_MAX_DEPTH,
    NN_HIDDEN_LAYER_SIZES,
    NN_MAX_ITER,
    NN_LEARNING_RATE_INIT,
    TEST_SIZE,
    MODEL_CONFIDENCE,
    MODEL_ACCURACY,
    MODEL_ERROR_RATE,
    MODEL_DISPLAY_NAMES,
)
from .data_service import DataService

logger = logging.getLogger(__name__)

# Model storage directory (inside the esppa app)
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')


class PredictionResult:
    """Value object holding the result of a single prediction."""

    def __init__(
        self,
        predicted_value: float,
        confidence: float,
        accuracy: float,
        error_rate: float,
        model_display_name: str = '',
    ) -> None:
        self.predicted_value = round(predicted_value, 2)
        self.confidence = round(confidence, 3)
        self.accuracy = accuracy
        self.error_rate = error_rate
        self.model_display_name = model_display_name


class ModelMetrics:
    """Value object holding evaluation metrics for a trained model."""

    def __init__(
        self,
        r2: float,
        mse: float,
        rmse: float,
        mae: float,
    ) -> None:
        self.r2_score = round(r2, 4)
        self.mse = round(mse, 4)
        self.rmse = round(rmse, 4)
        self.mae = round(mae, 4)


class MLService:
    """
    Orchestrates model training, persistence, prediction, and evaluation.
    Uses DataService for data loading / preprocessing.
    """

    MODEL_NAMES = ['random_forest', 'xgboost', 'neural_network']
    MODEL_FILE_NAMES = {
        'random_forest': 'random_forest_performance.pkl',
        'xgboost': 'xgboost_performance.pkl',
        'neural_network': 'neural_network_performance.pkl',
    }

    def __init__(self, data_service: DataService) -> None:
        self.data_service = data_service
        self.models: Dict[str, Any] = {}

    def train_all_models(self) -> Dict[str, Any]:
        """Load data, preprocess, train all three models, persist them."""
        df = self.data_service.load_csv()
        df_encoded = self.data_service.preprocess(df)
        X, y_perf, _ = self.data_service.prepare_features_and_targets(
            df_encoded,
        )

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_perf,
            test_size=TEST_SIZE,
            random_state=RANDOM_SEED,
        )

        # 1. Random Forest
        logger.info("Training Random Forest...")
        rf = RandomForestRegressor(
            n_estimators=RF_N_ESTIMATORS,
            max_depth=RF_MAX_DEPTH,
            random_state=RANDOM_SEED,
            n_jobs=-1,
        )
        rf.fit(X_train, y_train)
        self.models['random_forest'] = rf

        # 2. XGBoost
        logger.info("Training XGBoost...")
        try:
            from xgboost import XGBRegressor
            xgb = XGBRegressor(
                n_estimators=XGB_N_ESTIMATORS,
                learning_rate=XGB_LEARNING_RATE,
                max_depth=XGB_MAX_DEPTH,
                random_state=RANDOM_SEED,
                verbosity=0,
            )
            xgb.fit(X_train, y_train)
            self.models['xgboost'] = xgb
        except ImportError:
            logger.warning("XGBoost not installed. Skipping XGBoost model.")
            self.models['xgboost'] = None

        # 3. Neural Network (MLP)
        logger.info("Training Neural Network (MLP)...")
        nn = MLPRegressor(
            hidden_layer_sizes=NN_HIDDEN_LAYER_SIZES,
            max_iter=NN_MAX_ITER,
            learning_rate_init=NN_LEARNING_RATE_INIT,
            random_state=RANDOM_SEED,
            early_stopping=True,
            validation_fraction=0.1,
            verbose=False,
        )
        nn.fit(X_train, y_train)
        self.models['neural_network'] = nn

        self._persist_models()
        logger.info("All 3 models trained and persisted.")
        return self.models

    def load_or_train_models(self) -> Dict[str, Any]:
        """Load persisted models from disk, or train if missing."""
        if self._load_persisted_models():
            logger.info("Models loaded from disk.")
            return self.models
        logger.info("No persisted models found – training from scratch.")
        return self.train_all_models()

    def predict(
        self, model_type: str, input_data: Dict[str, Any],
    ) -> PredictionResult:
        """Run a single prediction using the specified model."""
        model = self.models.get(model_type)
        if model is None:
            raise ValueError(
                f"Model '{model_type}' is not loaded. Train first."
            )

        features = self._build_feature_vector(input_data)
        prediction = model.predict([features])[0]

        return PredictionResult(
            predicted_value=float(prediction),
            confidence=float(MODEL_CONFIDENCE.get(model_type, 0.8)),
            accuracy=MODEL_ACCURACY.get(model_type, 0.85),
            error_rate=MODEL_ERROR_RATE.get(model_type, 0.15),
            model_display_name=MODEL_DISPLAY_NAMES.get(model_type, model_type),
        )

    def evaluate_all_models(self) -> Dict[str, ModelMetrics]:
        """Re-train models on a fresh train/test split and return metrics."""
        df = self.data_service.load_csv()
        df_encoded = self.data_service.preprocess(df)
        X, y_perf, _ = self.data_service.prepare_features_and_targets(
            df_encoded,
        )

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_perf,
            test_size=TEST_SIZE,
            random_state=RANDOM_SEED,
        )

        results: Dict[str, ModelMetrics] = {}

        # Random Forest
        rf = RandomForestRegressor(
            n_estimators=RF_N_ESTIMATORS,
            max_depth=RF_MAX_DEPTH,
            random_state=RANDOM_SEED,
            n_jobs=-1,
        )
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_test)
        results['Random Forest'] = ModelMetrics(
            r2=r2_score(y_test, y_pred),
            mse=mean_squared_error(y_test, y_pred),
            rmse=np.sqrt(mean_squared_error(y_test, y_pred)),
            mae=mean_absolute_error(y_test, y_pred),
        )

        # XGBoost
        try:
            from xgboost import XGBRegressor
            xgb = XGBRegressor(
                n_estimators=XGB_N_ESTIMATORS,
                learning_rate=XGB_LEARNING_RATE,
                max_depth=XGB_MAX_DEPTH,
                random_state=RANDOM_SEED,
                verbosity=0,
            )
            xgb.fit(X_train, y_train)
            y_pred_xgb = xgb.predict(X_test)
            results['XGBoost'] = ModelMetrics(
                r2=r2_score(y_test, y_pred_xgb),
                mse=mean_squared_error(y_test, y_pred_xgb),
                rmse=np.sqrt(mean_squared_error(y_test, y_pred_xgb)),
                mae=mean_absolute_error(y_test, y_pred_xgb),
            )
        except ImportError:
            results['XGBoost'] = ModelMetrics(r2=0, mse=0, rmse=0, mae=0)

        # Neural Network
        nn = MLPRegressor(
            hidden_layer_sizes=NN_HIDDEN_LAYER_SIZES,
            max_iter=NN_MAX_ITER,
            learning_rate_init=NN_LEARNING_RATE_INIT,
            random_state=RANDOM_SEED,
            early_stopping=True,
            validation_fraction=0.1,
        )
        nn.fit(X_train, y_train)
        y_pred_nn = nn.predict(X_test)
        results['Neural Network (MLP)'] = ModelMetrics(
            r2=r2_score(y_test, y_pred_nn),
            mse=mean_squared_error(y_test, y_pred_nn),
            rmse=np.sqrt(mean_squared_error(y_test, y_pred_nn)),
            mae=mean_absolute_error(y_test, y_pred_nn),
        )

        return results

    def get_feature_importance(self, model_type: str) -> Optional[Dict[str, float]]:
        """Return feature importance for tree-based models."""
        model = self.models.get(model_type)
        if model is None:
            return None

        feature_names = (
            self.data_service.df.drop(
                columns=['Employee_ID', 'Hire_Date', 'Performance_Score', 'Resigned'],
                errors='ignore',
            ).columns.tolist()
            if self.data_service.df is not None
            else []
        )

        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            return dict(sorted(
                zip(feature_names, importances),
                key=lambda x: x[1],
                reverse=True,
            ))
        return None

    def _build_feature_vector(self, input_data: Dict[str, Any]) -> list:
        """Build a single feature vector from a flat dict of raw values."""
        numerical_features = [
            input_data.get('age', 0),
            input_data.get('years_at_company', 0),
            input_data.get('monthly_salary', 0),
            input_data.get('work_hours_per_week', 0),
            input_data.get('projects_handled', 0),
            input_data.get('overtime_hours', 0),
            input_data.get('sick_days', 0),
            input_data.get('remote_work_frequency', 0),
            input_data.get('team_size', 0),
            input_data.get('training_hours', 0),
            input_data.get('promotions', 0),
            input_data.get('employee_satisfaction_score', 0),
        ]

        categorical_raw = [
            input_data.get('department', ''),
            input_data.get('gender', ''),
            input_data.get('job_title', ''),
            input_data.get('education_level', ''),
        ]

        categorical_encoded = self.data_service.encode_categorical_features(
            categorical_raw,
        )

        return numerical_features + categorical_encoded

    def _persist_models(self) -> None:
        """Save all trained models to the models/ directory."""
        os.makedirs(MODELS_DIR, exist_ok=True)
        for name, model in self.models.items():
            if model is None:
                continue
            file_name = self.MODEL_FILE_NAMES.get(name, f'{name}.pkl')
            path = os.path.join(MODELS_DIR, file_name)
            with open(path, 'wb') as f:
                pickle.dump(model, f)

    def _load_persisted_models(self) -> bool:
        """Attempt to load models from disk. Returns True on success."""
        loaded_any = False
        for name in self.MODEL_NAMES:
            file_name = self.MODEL_FILE_NAMES.get(name, f'{name}.pkl')
            path = os.path.join(MODELS_DIR, file_name)
            if os.path.exists(path):
                try:
                    with open(path, 'rb') as f:
                        self.models[name] = pickle.load(f)
                    loaded_any = True
                except Exception as exc:
                    logger.warning("Failed to load %s: %s", path, exc)
            else:
                self.models[name] = None
        return loaded_any
