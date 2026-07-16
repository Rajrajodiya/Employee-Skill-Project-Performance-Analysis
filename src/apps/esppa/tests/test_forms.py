"""
Tests for ESPPA forms.

Covers field validation, cleaning, custom validation logic,
and user creation for all form classes.
"""

import pytest
from django.contrib.auth.models import User

from apps.esppa.forms import (
    UserRegistrationForm,
    UserProfileForm,
    PredictionForm,
)


# ═════════════════════════════════════════════════════════════════════════════
#  UserRegistrationForm Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestUserRegistrationForm:
    """Test registration form validation and user creation."""

    VALID_DATA = {
        'username': 'newuser',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'password1': 'Str0ng!Pass123',
        'password2': 'Str0ng!Pass123',
        'department': 'IT',
        'role': 'Developer',
        'phone': '+1234567890',
    }

    def test_valid_registration(self, db):
        form = UserRegistrationForm(data=self.VALID_DATA)
        assert form.is_valid(), form.errors

    def test_password_mismatch(self, db):
        data = self.VALID_DATA.copy()
        data['password2'] = 'DifferentPass123!'
        form = UserRegistrationForm(data=data)
        assert not form.is_valid()
        assert 'password2' in form.errors

    def test_username_required(self, db):
        data = self.VALID_DATA.copy()
        data['username'] = ''
        form = UserRegistrationForm(data=data)
        assert not form.is_valid()

    def test_email_required(self, db):
        data = self.VALID_DATA.copy()
        data['email'] = ''
        form = UserRegistrationForm(data=data)
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_invalid_email(self, db):
        data = self.VALID_DATA.copy()
        data['email'] = 'not-an-email'
        form = UserRegistrationForm(data=data)
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_save_creates_user_and_profile(self, db):
        form = UserRegistrationForm(data=self.VALID_DATA)
        assert form.is_valid()
        user = form.save()
        assert User.objects.filter(username='newuser').exists()
        assert hasattr(user, 'esppa_profile')
        assert user.esppa_profile.department == 'IT'
        assert user.esppa_profile.role == 'Developer'
        assert user.email == 'john@example.com'
        assert user.first_name == 'John'

    def test_duplicate_username(self, db):
        User.objects.create_user(username='newuser', password='test123')
        form = UserRegistrationForm(data=self.VALID_DATA)
        assert not form.is_valid()
        assert 'username' in form.errors


# ═════════════════════════════════════════════════════════════════════════════
#  UserProfileForm Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestUserProfileForm:
    """Test profile form validation."""

    def test_valid_profile_form(self, db, user_profile):
        form = UserProfileForm(instance=user_profile, data={
            'department': 'Engineering',
            'role': 'Senior Dev',
            'phone': '+9876543210',
        })
        assert form.is_valid(), form.errors

    def test_profile_optional_fields(self, db, user_profile):
        form = UserProfileForm(instance=user_profile, data={
            'department': '',
            'role': '',
            'phone': '',
        })
        assert form.is_valid()

    def test_profile_update(self, db, user_profile):
        form = UserProfileForm(instance=user_profile, data={
            'department': 'Marketing',
            'role': 'Manager',
            'phone': '+1112223333',
        })
        assert form.is_valid()
        profile = form.save()
        assert profile.department == 'Marketing'
        assert profile.role == 'Manager'


# ═════════════════════════════════════════════════════════════════════════════
#  PredictionForm Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestPredictionForm:
    """Test prediction form validation with all field constraints."""

    VALID_DATA = {
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
    }

    def test_valid_prediction_form(self, db):
        form = PredictionForm(data=self.VALID_DATA)
        assert form.is_valid(), form.errors

    def test_age_below_minimum(self, db):
        data = self.VALID_DATA.copy()
        data['age'] = 17
        form = PredictionForm(data=data)
        assert not form.is_valid()
        assert 'age' in form.errors

    def test_age_above_maximum(self, db):
        data = self.VALID_DATA.copy()
        data['age'] = 71
        form = PredictionForm(data=data)
        assert not form.is_valid()
        assert 'age' in form.errors

    def test_negative_years_at_company(self, db):
        data = self.VALID_DATA.copy()
        data['years_at_company'] = -1
        form = PredictionForm(data=data)
        assert not form.is_valid()
        assert 'years_at_company' in form.errors

    def test_negative_salary(self, db):
        data = self.VALID_DATA.copy()
        data['monthly_salary'] = -100
        form = PredictionForm(data=data)
        assert not form.is_valid()
        assert 'monthly_salary' in form.errors

    def test_work_hours_exceed_max(self, db):
        data = self.VALID_DATA.copy()
        data['work_hours_per_week'] = 81
        form = PredictionForm(data=data)
        assert not form.is_valid()
        assert 'work_hours_per_week' in form.errors

    @pytest.mark.parametrize('remote_val', [-1, 101])
    def test_remote_work_frequency_out_of_range(self, db, remote_val):
        data = self.VALID_DATA.copy()
        data['remote_work_frequency'] = remote_val
        form = PredictionForm(data=data)
        assert not form.is_valid()
        assert 'remote_work_frequency' in form.errors

    def test_team_size_below_minimum(self, db):
        data = self.VALID_DATA.copy()
        data['team_size'] = 0
        form = PredictionForm(data=data)
        assert not form.is_valid()
        assert 'team_size' in form.errors

    def test_satisfaction_below_min(self, db):
        data = self.VALID_DATA.copy()
        data['employee_satisfaction_score'] = 0.5
        form = PredictionForm(data=data)
        assert not form.is_valid()
        assert 'employee_satisfaction_score' in form.errors

    def test_satisfaction_above_max(self, db):
        data = self.VALID_DATA.copy()
        data['employee_satisfaction_score'] = 5.5
        form = PredictionForm(data=data)
        assert not form.is_valid()
        assert 'employee_satisfaction_score' in form.errors


