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

# ── Shared Field Choices (DRY: used by both forms and serializers) ─────────────
GENDER_CHOICES: List[tuple] = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]

EDUCATION_CHOICES: List[tuple] = [
    ('High School', 'High School'), ('Bachelor', 'Bachelor'),
    ('Master', 'Master'), ('PhD', 'PhD'),
]

DEPARTMENT_CHOICES: List[tuple] = [
    ('IT', 'IT'), ('Finance', 'Finance'), ('Marketing', 'Marketing'),
    ('Sales', 'Sales'), ('HR', 'HR'), ('Operations', 'Operations'),
    ('Customer Support', 'Customer Support'), ('Engineering', 'Engineering'),
    ('Research', 'Research'),
]

JOB_TITLE_CHOICES: List[tuple] = [
    ('Specialist', 'Specialist'), ('Developer', 'Developer'),
    ('Analyst', 'Analyst'), ('Manager', 'Manager'),
    ('Engineer', 'Engineer'), ('Consultant', 'Consultant'),
    ('Technician', 'Technician'),
]

# ── Prediction field validation specs (data-driven) ─────────────────────────
PREDICTION_FIELD_SPECS: List[dict] = [
    {'name': 'age', 'min': 18, 'max': 70},
    {'name': 'years_at_company', 'min': 0, 'max': None},
    {'name': 'monthly_salary', 'min': 0, 'max': None},
    {'name': 'work_hours_per_week', 'min': 0, 'max': 80},
    {'name': 'remote_work_frequency', 'min': 0, 'max': 100},
    {'name': 'team_size', 'min': 1, 'max': None},
    {'name': 'employee_satisfaction_score', 'min': 1.0, 'max': 5.0},
]

# ── Employee dict mapping (field_name -> human label for display) ───────────
EMPLOYEE_DISPLAY_FIELDS: List[str] = [
    'employee_id', 'name', 'department', 'job_title', 'age',
    'years_at_company', 'performance_score', 'monthly_salary',
    'monthly_salary_inr', 'hire_date', 'gender', 'education_level',
    'work_hours_per_week', 'projects_handled', 'overtime_hours',
    'sick_days', 'remote_work_frequency', 'team_size', 'training_hours',
    'promotions', 'employee_satisfaction_score', 'resigned',
]

PREDICTION_INPUT_FIELDS: List[str] = [
    'age', 'years_at_company', 'monthly_salary', 'work_hours_per_week',
    'projects_handled', 'overtime_hours', 'sick_days',
    'remote_work_frequency', 'team_size', 'training_hours',
    'promotions', 'employee_satisfaction_score', 'department',
    'gender', 'job_title', 'education_level',
]

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
