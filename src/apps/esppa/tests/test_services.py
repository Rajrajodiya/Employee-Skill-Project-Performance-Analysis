"""
Tests for ESPPA service layer.

Covers DataService (CSV loading, preprocessing), MLService (training, prediction),
EmployeeService (dashboard metrics), and ChartService (chart generation).

All tests use an in-memory DataFrame approach to avoid Windows file-locking issues
with temp files. DataService is patched to load from a StringIO buffer.
"""

import pytest
import pandas as pd
import numpy as np

from apps.esppa.services.data_service import DataService
from apps.esppa.services.ml_service import MLService
from apps.esppa.services.employee_service import EmployeeService
from apps.esppa.services.chart_service import ChartService


# ═════════════════════════════════════════════════════════════════════════════
#  Helpers & Fixtures
# ═════════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope='module')
def sample_dataframe() -> pd.DataFrame:
    """Create an in-memory DataFrame with sample employee data."""
    return pd.DataFrame({
        'Employee_ID': [1001, 1002, 1003],
        'Department': ['IT', 'HR', 'Sales'],
        'Gender': ['Male', 'Female', 'Male'],
        'Job_Title': ['Developer', 'Manager', 'Rep'],
        'Education_Level': ['Bachelor', 'Master', 'Bachelor'],
        'Age': [30, 35, 28],
        'Years_At_Company': [5, 10, 3],
        'Performance_Score': [4.5, 3.8, 3.2],
        'Monthly_Salary': [5000, 6000, 4000],
        'Work_Hours_Per_Week': [40, 45, 38],
        'Projects_Handled': [10, 8, 6],
        'Overtime_Hours': [5, 3, 8],
        'Sick_Days': [3, 5, 2],
        'Remote_Work_Frequency': [20, 0, 50],
        'Team_Size': [8, 10, 6],
        'Training_Hours': [40, 50, 30],
        'Promotions': [2, 3, 1],
        'Employee_Satisfaction_Score': [4.2, 3.9, 3.5],
        'Resigned': [False, False, True],
        'Hire_Date': ['2020-01-15', '2015-03-01', '2021-07-01'],
    })


@pytest.fixture
def data_service(sample_dataframe) -> DataService:
    """Create a DataService with pre-loaded in-memory DataFrame."""
    ds = DataService()
    ds.df = sample_dataframe.copy()
    return ds


# ═════════════════════════════════════════════════════════════════════════════
#  DataService Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestDataService:
    """Test CSV loading, preprocessing, and feature engineering."""

    def test_load_csv_file_not_found(self):
        ds = DataService()
        with pytest.raises(FileNotFoundError):
            ds.load_csv('/nonexistent/path.csv')

    def test_preprocess(self, data_service):
        df_encoded = data_service.preprocess()
        assert df_encoded is not None
        assert len(df_encoded) == 3
        assert 'Department' in df_encoded.columns
        assert 'Age' in df_encoded.columns

    def test_preprocess_no_data(self):
        ds = DataService()
        with pytest.raises(ValueError, match='load_csv'):
            ds.preprocess()

    def test_prepare_features_and_targets(self, data_service):
        data_service.preprocess()
        X, y_perf, y_resigned = data_service.prepare_features_and_targets()
        assert X is not None
        assert y_perf is not None
        assert y_resigned is not None
        assert 'Performance_Score' not in X.columns
        assert 'Resigned' not in X.columns

    def test_encode_categorical_features(self, data_service):
        data_service.preprocess()
        encoded = data_service.encode_categorical_features(
            ['IT', 'Male', 'Developer', 'Bachelor']
        )
        assert len(encoded) == 4
        assert all(isinstance(v, int) for v in encoded)


# ═════════════════════════════════════════════════════════════════════════════
#  MLService Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestMLService:
    """Test ML model training, prediction, and evaluation."""

    def test_train_all_models(self, data_service):
        ml = MLService(data_service)
        models = ml.train_all_models()
        assert 'random_forest' in models
        assert 'xgboost' in models or models['xgboost'] is None
        assert 'neural_network' in models
        assert models['random_forest'] is not None

    def test_predict_random_forest(self, data_service):
        ml = MLService(data_service)
        ml.train_all_models()
        result = ml.predict('random_forest', {
            'age': 30, 'years_at_company': 5,
            'monthly_salary': 5000, 'work_hours_per_week': 40,
            'projects_handled': 10, 'overtime_hours': 5,
            'sick_days': 3, 'remote_work_frequency': 20,
            'team_size': 8, 'training_hours': 40,
            'promotions': 2, 'employee_satisfaction_score': 4.2,
            'department': 'IT', 'gender': 'Male',
            'job_title': 'Developer', 'education_level': 'Bachelor',
        })
        assert result is not None
        assert 0 <= result.predicted_value <= 5
        assert result.confidence > 0
        assert result.model_display_name == 'Random Forest'

    def test_predict_no_model(self, data_service):
        ml = MLService(data_service)
        with pytest.raises(ValueError, match='not loaded'):
            ml.predict('random_forest', {'age': 30})

    def test_evaluate_all_models(self, data_service):
        ml = MLService(data_service)
        ml.train_all_models()
        metrics = ml.evaluate_all_models(cv_folds=2)
        assert 'Random Forest' in metrics
        rf = metrics['Random Forest']
        assert -1 <= rf.r2_score <= 1
        assert rf.mse >= 0
        assert rf.rmse >= 0
        assert rf.mae >= 0

    def test_get_feature_importance(self, data_service):
        ml = MLService(data_service)
        ml.train_all_models()
        importance = ml.get_feature_importance('random_forest')
        if importance is not None:
            assert len(importance) > 0
            assert all(isinstance(v, float) for v in importance.values())


# ═════════════════════════════════════════════════════════════════════════════
#  EmployeeService Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestEmployeeService:
    """Test dashboard metrics and employee aggregation."""

    def test_build_dashboard_metrics(self, sample_dataframe):
        df = sample_dataframe
        metrics = EmployeeService.build_dashboard_metrics(df)
        assert metrics.total_employees == 3
        assert isinstance(metrics.avg_performance, float)
        assert isinstance(metrics.avg_salary_inr, float)
        assert isinstance(metrics.resignation_rate, float)
        assert len(metrics.department_data) == 3

    def test_performance_distribution(self, sample_dataframe):
        df = sample_dataframe
        metrics = EmployeeService.build_dashboard_metrics(df)
        total = (metrics.high_performers + metrics.medium_performers
                 + metrics.low_performers)
        assert total == metrics.total_employees

    def test_salary_distribution(self, sample_dataframe):
        df = sample_dataframe
        metrics = EmployeeService.build_dashboard_metrics(df)
        total = metrics.high_salary + metrics.medium_salary + metrics.low_salary
        assert total == metrics.total_employees

    def test_gender_counts(self, sample_dataframe):
        df = sample_dataframe
        metrics = EmployeeService.build_dashboard_metrics(df)
        assert 'Male' in metrics.gender_counts
        assert 'Female' in metrics.gender_counts
        assert sum(metrics.gender_counts.values()) == metrics.total_employees


# ═════════════════════════════════════════════════════════════════════════════
#  ChartService Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestChartService:
    """Test chart generation from DataFrame."""

    def test_department_bar_chart(self, sample_dataframe):
        df = sample_dataframe
        result = ChartService.department_bar_chart(df)
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    def test_department_pie_chart(self, sample_dataframe):
        df = sample_dataframe
        result = ChartService.department_pie_chart(df)
        assert result is not None
        assert isinstance(result, str)

    def test_performance_histogram(self, sample_dataframe):
        df = sample_dataframe
        result = ChartService.performance_histogram(df)
        assert result is not None
        assert isinstance(result, str)

    def test_salary_histogram(self, sample_dataframe):
        df = sample_dataframe
        result = ChartService.salary_histogram(df)
        assert result is not None
        assert isinstance(result, str)

    def test_chart_with_empty_data(self):
        """Charts should gracefully handle empty DataFrames by returning None."""
        df = pd.DataFrame({'Department': pd.Series(dtype='str'),
                            'Performance_Score': pd.Series(dtype='float'),
                            'Monthly_Salary': pd.Series(dtype='float')})
        bar = ChartService.department_bar_chart(df)
        perf = ChartService.performance_histogram(df)
        salary = ChartService.salary_histogram(df)
        # Any of these may be None (chart generation catches exceptions)
        # or a valid base64 string (matplotlib can render empty charts)
        for result in [bar, perf, salary]:
            assert result is None or (isinstance(result, str) and len(result) > 0)
