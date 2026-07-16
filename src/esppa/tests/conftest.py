"""
Shared pytest fixtures for ESPPA test suite.

Provides test_user, sample_employee, and user_profile fixtures
that are reused across model, view, form, API, and service tests.
"""

import pytest
from django.contrib.auth.models import User

from esppa.models import Employee, UserProfile


@pytest.fixture
def test_user(db):
    """Create a standard test user with known credentials."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User',
    )


@pytest.fixture
def sample_employee(db):
    """Create a sample employee record for testing."""
    return Employee.objects.create(
        employee_id=1001,
        name='Test Employee',
        department='IT',
        job_title='Developer',
        age=30,
        years_at_company=5,
        performance_score=4.5,
        monthly_salary=5000.0,
        monthly_salary_inr=415000,
        hire_date='2020-01-15',
        gender='Male',
        education_level='Bachelor',
        work_hours_per_week=40,
        projects_handled=10,
        overtime_hours=5,
        sick_days=3,
        remote_work_frequency=20.0,
        team_size=8,
        training_hours=40,
        promotions=2,
        employee_satisfaction_score=4.2,
        resigned=False,
    )


@pytest.fixture
def user_profile(db, test_user):
    """Create a UserProfile associated with test_user."""
    return UserProfile.objects.create(
        user=test_user,
        department='IT',
        role='Developer',
        phone='+1234567890',
    )
