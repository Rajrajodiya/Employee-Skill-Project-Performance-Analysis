"""
Service responsible for loading and preprocessing employee data from CSV.
Encapsulates all DataFrame operations so views never touch pandas directly.
"""

import os
import logging
from functools import lru_cache
from typing import Optional, Tuple

import pandas as pd
import numpy as np
from django.conf import settings
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

from .config import (
    CATEGORICAL_COLS,
    NUMERICAL_COLS,
    FEATURE_NUMERICAL_COLS,
    DROP_COLS,
)

logger = logging.getLogger(__name__)

# Track CSV modification time for cache invalidation
_csv_cache: dict = {
    'path': None,
    'mtime': None,
    'dataframe': None,
}


def _load_csv_with_cache(csv_path: str) -> pd.DataFrame:
    """Load CSV with file-mtime-based cache to avoid re-reading on every request."""
    global _csv_cache
    try:
        current_mtime = os.path.getmtime(csv_path)
    except OSError:
        current_mtime = None

    if (_csv_cache['path'] == csv_path
            and _csv_cache['mtime'] == current_mtime
            and _csv_cache['dataframe'] is not None):
        logger.debug("CSV cache hit: %s", csv_path)
        return _csv_cache['dataframe']

    df = pd.read_csv(csv_path)
    _csv_cache = {
        'path': csv_path,
        'mtime': current_mtime,
        'dataframe': df,
    }
    logger.info("Loaded CSV with %d rows from %s (cached)", len(df), csv_path)
    return df


class DataService:
    """Handles loading, encoding, and scaling of employee CSV data."""

    def __init__(self) -> None:
        self.df: Optional[pd.DataFrame] = None
        self.label_encoders: dict = {}
        self.scaler: Optional[MinMaxScaler] = None

    def load_csv(self, csv_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load employee data from a CSV file.
        Falls back to the default path inside STATICFILES_DIRS.
        Uses file-mtime-based caching to avoid re-reading on every request.
        """
        if csv_path is None:
            csv_path = os.path.join(
                settings.STATICFILES_DIRS[0],
                'employee_data.csv',
            )
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Employee CSV not found at: {csv_path}")

        self.df = _load_csv_with_cache(csv_path)
        return self.df

    def preprocess(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Encode categorical columns and scale numerical columns in-place."""
        data = df if df is not None else self.df
        if data is None:
            raise ValueError("No DataFrame loaded – call load_csv() first.")

        df_encoded = data.copy()

        self.label_encoders.clear()
        for col in CATEGORICAL_COLS:
            le = LabelEncoder()
            df_encoded[col] = le.fit_transform(df_encoded[col])
            self.label_encoders[col] = le

        self.scaler = MinMaxScaler()
        df_encoded[FEATURE_NUMERICAL_COLS] = self.scaler.fit_transform(
            df_encoded[FEATURE_NUMERICAL_COLS]
        )

        logger.info("Preprocessing complete: %d features", df_encoded.shape[1])
        return df_encoded

    def prepare_features_and_targets(
        self,
        df_encoded: Optional[pd.DataFrame] = None,
    ) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
        """Split preprocessed DataFrame into feature matrix X and target vectors."""
        data = df_encoded if df_encoded is not None else self.df
        if data is None:
            raise ValueError("No data available – load and preprocess first.")

        X = data.drop(columns=DROP_COLS, errors='ignore')
        y_performance = data['Performance_Score']
        y_resigned = data['Resigned'].astype(int)
        return X, y_performance, y_resigned

    def set_encoders_and_scaler(
        self,
        label_encoders: dict,
        scaler: MinMaxScaler,
    ) -> None:
        """Restore fitted encoders and scaler for prediction (loaded from disk)."""
        self.label_encoders = label_encoders
        self.scaler = scaler

    def encode_categorical_features(self, raw_values: list) -> list:
        """Encode a list of raw categorical values using the fitted label encoders."""
        encoded = []
        for i, col in enumerate(CATEGORICAL_COLS):
            encoder = self.label_encoders.get(col)
            if encoder is None:
                encoded.append(0)
                continue
            try:
                encoded.append(int(encoder.transform([raw_values[i]])[0]))
            except (ValueError, TypeError):
                encoded.append(0)
        return encoded

    def scale_numerical_features(self, raw_values: list) -> list:
        """Scale numerical features using the fitted MinMaxScaler."""
        if self.scaler is None:
            return raw_values
        scaled = self.scaler.transform([raw_values])[0]
        return [float(v) for v in scaled]
