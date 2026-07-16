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
import copy
from typing import Any, Dict, Optional

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

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
    CATEGORICAL_COLS,
    NUMERICAL_COLS,
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

    def evaluate_all_models(self, cv_folds: int = 5) -> Dict[str, ModelMetrics]:
        """
        Re-train models on a fresh train/test split and return metrics.

        Uses cross-validation (K-fold) for more robust evaluation.
        Returns average metrics across all folds.
        """
        from sklearn.model_selection import cross_validate, KFold

        df = self.data_service.load_csv()
        df_encoded = self.data_service.preprocess(df)
        X, y_perf, _ = self.data_service.prepare_features_and_targets(
            df_encoded,
        )

        cv = KFold(n_splits=cv_folds, shuffle=True, random_state=RANDOM_SEED)
        results: Dict[str, ModelMetrics] = {}

        def _cross_val_metrics(estimator, X, y) -> ModelMetrics:
            scores = cross_validate(
                estimator, X, y,
                cv=cv,
                scoring=('r2', 'neg_mean_squared_error', 'neg_mean_absolute_error'),
                n_jobs=-1,
            )
            return ModelMetrics(
                r2=float(np.mean(scores['test_r2'])),
                mse=float(np.mean(-scores['test_neg_mean_squared_error'])),
                rmse=float(np.sqrt(np.mean(-scores['test_neg_mean_squared_error']))),
                mae=float(np.mean(-scores['test_neg_mean_absolute_error'])),
            )

        # Random Forest
        logger.info("Cross-validating Random Forest (%d folds)...", cv_folds)
        rf = RandomForestRegressor(
            n_estimators=RF_N_ESTIMATORS,
            max_depth=RF_MAX_DEPTH,
            random_state=RANDOM_SEED,
            n_jobs=1,
        )
        results['Random Forest'] = _cross_val_metrics(rf, X, y_perf)

        # XGBoost
        try:
            from xgboost import XGBRegressor
            logger.info("Cross-validating XGBoost (%d folds)...", cv_folds)
            xgb = XGBRegressor(
                n_estimators=XGB_N_ESTIMATORS,
                learning_rate=XGB_LEARNING_RATE,
                max_depth=XGB_MAX_DEPTH,
                random_state=RANDOM_SEED,
                verbosity=0,
            )
            results['XGBoost'] = _cross_val_metrics(xgb, X, y_perf)
        except ImportError:
            results['XGBoost'] = ModelMetrics(r2=0, mse=0, rmse=0, mae=0)

        # Neural Network
        logger.info("Cross-validating Neural Network (%d folds)...", cv_folds)
        nn = MLPRegressor(
            hidden_layer_sizes=NN_HIDDEN_LAYER_SIZES,
            max_iter=NN_MAX_ITER,
            learning_rate_init=NN_LEARNING_RATE_INIT,
            random_state=RANDOM_SEED,
            early_stopping=True,
            validation_fraction=0.1,
        )
        results['Neural Network (MLP)'] = _cross_val_metrics(nn, X, y_perf)

        return results

    def evaluate_persisted_models(self) -> Dict[str, ModelMetrics]:
        """
        Evaluate already-loaded models on a test split (no re-training).
        Preserves the loaded scaler/encoders so evaluation matches what
        predict() would produce — no scaler re-fit drift.
        """
        if not self.models or all(v is None for v in self.models.values()):
            self.load_or_train_models()

        # Snapshot the loaded scaler/encoders before preprocessing re-fits them
        saved_scaler = copy.deepcopy(self.data_service.scaler)
        saved_encoders = copy.deepcopy(self.data_service.label_encoders)

        df = self.data_service.load_csv()
        df_encoded = self.data_service.preprocess(df)

        # Restore the original scaler/encoders so evaluation uses training params
        if saved_scaler is not None:
            self.data_service.set_encoders_and_scaler(
                saved_encoders, saved_scaler,
            )

        X, y_perf, _ = self.data_service.prepare_features_and_targets(
            df_encoded,
        )
        _, X_test, _, y_test = train_test_split(
            X, y_perf,
            test_size=TEST_SIZE,
            random_state=RANDOM_SEED,
        )

        results: Dict[str, ModelMetrics] = {}
        name_map = {
            'random_forest': 'Random Forest',
            'xgboost': 'XGBoost',
            'neural_network': 'Neural Network (MLP)',
        }

        for model_key, display_name in name_map.items():
            model = self.models.get(model_key)
            if model is None:
                results[display_name] = ModelMetrics(r2=0, mse=0, rmse=0, mae=0)
                continue
            y_pred = model.predict(X_test)
            results[display_name] = ModelMetrics(
                r2=float(r2_score(y_test, y_pred)),
                mse=float(mean_squared_error(y_test, y_pred)),
                rmse=float(np.sqrt(mean_squared_error(y_test, y_pred))),
                mae=float(mean_absolute_error(y_test, y_pred)),
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
        """Build a single feature vector from a flat dict of raw values.

        Applies the same transformations (label encoding + MinMax scaling)
        that were used during training — without this, predictions are wrong.
        """
        numerical_raw = [
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

        # Apply same transformations as during training
        numerical_scaled = self.data_service.scale_numerical_features(numerical_raw)
        categorical_encoded = self.data_service.encode_categorical_features(
            categorical_raw,
        )

        return numerical_scaled + categorical_encoded

    def _persist_models(self) -> None:
        """Save models, scaler, and label encoders to the models/ directory."""
        os.makedirs(MODELS_DIR, exist_ok=True)
        for name, model in self.models.items():
            if model is None:
                continue
            file_name = self.MODEL_FILE_NAMES.get(name, f'{name}.pkl')
            path = os.path.join(MODELS_DIR, file_name)
            with open(path, 'wb') as f:
                pickle.dump(model, f)

        # Persist scaler and label encoders alongside models
        scaler_path = os.path.join(MODELS_DIR, 'scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.data_service.scaler, f)

        encoders_path = os.path.join(MODELS_DIR, 'label_encoders.pkl')
        with open(encoders_path, 'wb') as f:
            pickle.dump(self.data_service.label_encoders, f)

    def _load_persisted_models(self) -> bool:
        """Load models, scaler, and label encoders from disk. Returns True on success."""
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

        # Load scaler and label encoders (required for correct prediction)
        scaler_path = os.path.join(MODELS_DIR, 'scaler.pkl')
        if os.path.exists(scaler_path):
            try:
                with open(scaler_path, 'rb') as f:
                    scaler = pickle.load(f)
                encoders_path = os.path.join(MODELS_DIR, 'label_encoders.pkl')
                encoders = {}
                if os.path.exists(encoders_path):
                    with open(encoders_path, 'rb') as f:
                        encoders = pickle.load(f)
                self.data_service.set_encoders_and_scaler(encoders, scaler)
            except Exception as exc:
                logger.warning("Failed to load scaler/encoders: %s", exc)

        return loaded_any
