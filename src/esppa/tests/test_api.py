"""
Tests for ESPPA REST API endpoints.

Covers authentication, CRUD operations, custom viewset actions,
error handling, and data validation for all API views.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


# ═════════════════════════════════════════════════════════════════════════════
#  Fixtures
# ═════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client


# ═════════════════════════════════════════════════════════════════════════════
#  Authentication Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestAPIAuthentication:
    """Test that API endpoints require authentication."""

    def test_employees_require_auth(self, api_client):
        """DRF returns 403 Forbidden when using session auth without credentials."""
        response = api_client.get('/api/employees')
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED,
                                        status.HTTP_403_FORBIDDEN]

    def test_dashboard_require_auth(self, api_client):
        response = api_client.get('/api/dashboard/metrics')
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED,
                                        status.HTTP_403_FORBIDDEN]

    def test_predict_require_auth(self, api_client):
        response = api_client.post('/api/predictions/predict', {})
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED,
                                        status.HTTP_403_FORBIDDEN]


# ═════════════════════════════════════════════════════════════════════════════
#  Employee API Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestEmployeeAPI:
    """Test employee list, detail, search, and department_summary endpoints."""

    def test_list_employees(self, auth_client, sample_employee):
        response = auth_client.get('/api/employees')
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or isinstance(response.data, list)

    def test_employee_detail(self, auth_client, sample_employee):
        response = auth_client.get(f'/api/employees/{sample_employee.id}')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['employee_id'] == 1001

    def test_search_employee_by_id(self, auth_client, sample_employee):
        response = auth_client.get('/api/employees/search?id=1001')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['employee_id'] == 1001

    def test_search_missing_id(self, auth_client):
        response = auth_client.get('/api/employees/search')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_search_nonexistent_id(self, auth_client):
        response = auth_client.get('/api/employees/search?id=9999')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_search_invalid_id(self, auth_client):
        response = auth_client.get('/api/employees/search?id=abc')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_department_summary(self, auth_client, sample_employee):
        response = auth_client.get('/api/employees/department_summary')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0


# ═════════════════════════════════════════════════════════════════════════════
#  Dashboard API Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestDashboardAPI:
    """Test dashboard metrics, department_data, and demographics endpoints."""

    def test_dashboard_metrics(self, auth_client):
        response = auth_client.get('/api/dashboard/metrics')
        assert response.status_code == status.HTTP_200_OK
        assert 'total_employees' in response.data
        assert 'avg_performance' in response.data

    def test_department_data(self, auth_client):
        response = auth_client.get('/api/dashboard/department_data')
        assert response.status_code == status.HTTP_200_OK

    def test_demographics(self, auth_client):
        response = auth_client.get('/api/dashboard/demographics')
        assert response.status_code == status.HTTP_200_OK
        assert 'gender_counts' in response.data
        assert 'education_counts' in response.data


# ═════════════════════════════════════════════════════════════════════════════
#  Prediction API Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestPredictionAPI:
    """Test prediction endpoints including custom predict action."""

    def test_list_predictions(self, auth_client):
        response = auth_client.get('/api/predictions')
        assert response.status_code == status.HTTP_200_OK

    def test_predict_valid_input(self, auth_client):
        response = auth_client.post('/api/predictions/predict', {
            'model_type': 'random_forest',
            'age': 30,
            'gender': 'Male',
            'education_level': 'Bachelor',
            'department': 'IT',
            'job_title': 'Developer',
            'years_at_company': 5,
            'monthly_salary': 5000,
            'work_hours_per_week': 40,
            'projects_handled': 10,
            'overtime_hours': 5,
            'sick_days': 3,
            'remote_work_frequency': 20,
            'team_size': 8,
            'training_hours': 40,
            'promotions': 2,
            'employee_satisfaction_score': 4.2,
        }, format='json')
        assert response.status_code in [status.HTTP_200_OK,
                                        status.HTTP_201_CREATED]
        if response.status_code == status.HTTP_200_OK:
            assert 'prediction_result' in response.data

    def test_predict_invalid_input(self, auth_client):
        response = auth_client.post('/api/predictions/predict', {
            'model_type': 'invalid_model',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_predict_missing_fields(self, auth_client):
        response = auth_client.post('/api/predictions/predict', {},
                                    format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ═════════════════════════════════════════════════════════════════════════════
#  Model Analysis API Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestModelAnalysisAPI:
    """Test model comparison and feature importance endpoints."""

    def test_compare_models(self, auth_client):
        response = auth_client.get('/api/models/compare')
        assert response.status_code == status.HTTP_200_OK
        assert 'Random Forest' in response.data

    def test_feature_importance(self, auth_client):
        response = auth_client.get('/api/models/feature_importance')
        assert response.status_code in [status.HTTP_200_OK,
                                        status.HTTP_404_NOT_FOUND]


# ═════════════════════════════════════════════════════════════════════════════
#  User/Profile API Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestUserAPI:
    """Test user and profile endpoints."""

    def test_current_user(self, auth_client, test_user):
        response = auth_client.get('/api/users')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['username'] == test_user.username

    def test_profile_crud(self, auth_client, test_user):
        # Read
        response = auth_client.get('/api/profiles')
        assert response.status_code == status.HTTP_200_OK

        # Create/update
        response = auth_client.post('/api/profiles', {
            'department': 'Engineering',
            'role': 'Developer',
        }, format='json')
        assert response.status_code in [status.HTTP_200_OK,
                                        status.HTTP_201_CREATED]


# ═════════════════════════════════════════════════════════════════════════════
#  Analysis API Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestAnalysisAPI:
    """Test analysis CRUD endpoints."""

    def test_list_analyses(self, auth_client):
        response = auth_client.get('/api/analyses')
        assert response.status_code == status.HTTP_200_OK

    def test_create_analysis(self, auth_client):
        response = auth_client.post('/api/analyses', {
            'analysis_type': 'department',
            'chart_type': 'bar',
            'chart_data': {'labels': ['A'], 'values': [1]},
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['analysis_type'] == 'department'
