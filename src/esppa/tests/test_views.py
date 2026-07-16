"""
Tests for ESPPA views.

Covers authentication, response status codes, template usage,
context data, redirects, and form submissions for all view functions.
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User

from esppa.models import Employee, UserProfile


# ═════════════════════════════════════════════════════════════════════════════
#  Authentication Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestAuthentication:
    """Tests for login/registration and authentication guards."""

    def test_login_required_redirect(self, client):
        """Unauthenticated users should be redirected to login."""
        response = client.get(reverse('dashboard'))
        assert response.status_code == 302
        assert '/accounts/login/' in response.url

    def test_register_page_loads(self, client):
        response = client.get(reverse('register'))
        assert response.status_code == 200
        assert 'form' in response.context

    def test_register_creates_user(self, client, db):
        response = client.post(reverse('register'), {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password1': 'Str0ng!Pass123',
            'password2': 'Str0ng!Pass123',
            'department': 'IT',
            'role': 'Developer',
        })
        assert response.status_code == 302
        assert User.objects.filter(username='testuser').exists()
        profile = User.objects.get(username='testuser').esppa_profile
        assert profile.department == 'IT'

    def test_logout(self, client, test_user):
        client.force_login(test_user)
        response = client.get(reverse('logout'))
        assert response.status_code == 302


# ═════════════════════════════════════════════════════════════════════════════
#  Dashboard View Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestDashboardView:
    """Tests for the dashboard view."""

    def test_dashboard_loads(self, client, test_user):
        client.force_login(test_user)
        response = client.get(reverse('dashboard'))
        assert response.status_code == 200
        assert 'esppa/dashboard.html' in [t.name for t in response.templates]

    def test_dashboard_context_keys(self, client, test_user):
        client.force_login(test_user)
        response = client.get(reverse('dashboard'))
        context_keys = ['total_employees', 'avg_performance', 'avg_salary_inr',
                        'resignation_rate']
        for key in context_keys:
            assert key in response.context, f'Missing context key: {key}'


# ═════════════════════════════════════════════════════════════════════════════
#  Analysis View Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestAnalysisView:
    """Tests for the analysis result view."""

    def test_analysis_loads(self, client, test_user):
        client.force_login(test_user)
        response = client.get(reverse('analysis_result'))
        assert response.status_code == 200


# ═════════════════════════════════════════════════════════════════════════════
#  Prediction View Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestPredictionView:
    """Tests for the prediction view."""

    def test_prediction_page_loads(self, client, test_user):
        client.force_login(test_user)
        response = client.get(reverse('prediction'))
        assert response.status_code == 200
        assert 'form' in response.context

    def test_prediction_form_valid(self, client, test_user):
        client.force_login(test_user)
        response = client.post(reverse('prediction'), {
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
        })
        assert response.status_code == 200
        assert 'prediction' in response.context


# ═════════════════════════════════════════════════════════════════════════════
#  Model Analysis View Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestModelAnalysisView:
    """Tests for the model analysis view."""

    def test_model_analysis_loads(self, client, test_user):
        client.force_login(test_user)
        response = client.get(reverse('model_analysis'))
        assert response.status_code == 200


# ═════════════════════════════════════════════════════════════════════════════
#  Employee List View Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestEmployeeListView:
    """Tests for the employee list/search view."""

    def test_employee_list_loads(self, client, test_user):
        client.force_login(test_user)
        response = client.get(reverse('employee_list'))
        assert response.status_code == 200

    def test_employee_search_by_id(self, client, test_user, sample_employee):
        client.force_login(test_user)
        response = client.get(reverse('employee_list'),
                              {'search_id': '1001'})
        assert response.status_code == 200
        assert response.context['search_id'] == '1001'

    def test_employee_search_not_found(self, client, test_user):
        client.force_login(test_user)
        response = client.get(reverse('employee_list'),
                              {'search_id': '9999'})
        assert response.status_code == 200

    def test_employee_search_invalid_id(self, client, test_user):
        client.force_login(test_user)
        response = client.get(reverse('employee_list'),
                              {'search_id': 'abc'})
        assert response.status_code == 200


# ═════════════════════════════════════════════════════════════════════════════
#  Profile View Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestProfileView:
    """Tests for the profile view."""

    def test_profile_loads(self, client, test_user):
        client.force_login(test_user)
        response = client.get(reverse('profile'))
        assert response.status_code == 200
        assert 'form' in response.context

    def test_profile_update(self, client, test_user):
        client.force_login(test_user)
        # Ensure UserProfile exists
        UserProfile.objects.get_or_create(user=test_user)
        response = client.post(reverse('profile'), {
            'department': 'Engineering',
            'role': 'Senior Developer',
            'phone': '+1234567890',
        })
        assert response.status_code == 302
        test_user.refresh_from_db()
        assert test_user.esppa_profile.department == 'Engineering'
