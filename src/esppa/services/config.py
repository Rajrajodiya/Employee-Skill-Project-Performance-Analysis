"""
Centralized configuration constants for the ESPPA application.

All magic numbers, thresholds, and configuration values live here
so they can be changed in one place and are easily discoverable.
"""

from typing import Dict, List

# ── Exchange Rate ────────────────────────────────────────────────────────────
USD_TO_INR_RATE: float = 83.0

# ── Performance Thresholds ───────────────────────────────────────────────────
PERFORMANCE_HIGH_THRESHOLD: float = 4.0
PERFORMANCE_MEDIUM_THRESHOLD: float = 3.0

# ── Salary Thresholds (in USD – the CSV stores USD) ─────────────────────────
SALARY_HIGH_THRESHOLD_USD: float = 80000.0
SALARY_MEDIUM_THRESHOLD_USD: float = 50000.0

# ── Feature Columns ──────────────────────────────────────────────────────────
CATEGORICAL_COLS: List[str] = [
    'Department', 'Gender', 'Job_Title', 'Education_Level',
]

NUMERICAL_COLS: List[str] = [
    'Age', 'Years_At_Company', 'Performance_Score', 'Monthly_Salary',
    'Work_Hours_Per_Week', 'Projects_Handled', 'Overtime_Hours',
    'Sick_Days', 'Remote_Work_Frequency', 'Team_Size', 'Training_Hours',
    'Promotions', 'Employee_Satisfaction_Score',
]

DROP_COLS: List[str] = [
    'Employee_ID', 'Hire_Date', 'Performance_Score', 'Resigned',
]

# ── Model hyper-parameters ───────────────────────────────────────────────────
RANDOM_SEED: int = 42

# Random Forest
RF_N_ESTIMATORS: int = 100
RF_MAX_DEPTH: int = 10

# XGBoost
XGB_N_ESTIMATORS: int = 100
XGB_LEARNING_RATE: float = 0.1
XGB_MAX_DEPTH: int = 6

# Neural Network (MLPRegressor)
NN_HIDDEN_LAYER_SIZES: tuple = (64, 32)
NN_MAX_ITER: int = 500
NN_LEARNING_RATE_INIT: float = 0.001

# Train/Test
TEST_SIZE: float = 0.2

# ── Paths (relative to STATICFILES_DIRS[0]) ──────────────────────────────────
EMPLOYEE_CSV_FILENAME: str = 'employee_data.csv'

# ── Model confidence defaults ────────────────────────────────────────────────
MODEL_CONFIDENCE: Dict[str, float] = {
    'random_forest': 0.88,
    'xgboost': 0.90,
    'neural_network': 0.82,
}

MODEL_ACCURACY: Dict[str, float] = {
    'random_forest': 0.92,
    'xgboost': 0.94,
    'neural_network': 0.88,
}

MODEL_ERROR_RATE: Dict[str, float] = {
    'random_forest': 0.08,
    'xgboost': 0.06,
    'neural_network': 0.12,
}

# ── Model Display Names ──────────────────────────────────────────────────────
MODEL_DISPLAY_NAMES: Dict[str, str] = {
    'random_forest': 'Random Forest',
    'xgboost': 'XGBoost',
    'neural_network': 'Neural Network (MLP)',
}
