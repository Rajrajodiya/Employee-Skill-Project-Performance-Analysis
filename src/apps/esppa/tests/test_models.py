"""
Tests for ESPPA models.

Covers model creation, string representation, ordering, uniqueness constraints,
and relationship integrity for all four core models.
"""

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError

from apps.esppa.models import Employee, Analysis, Prediction, UserProfile


# ═════════════════════════════════════════════════════════════════════════════
#  Employee Model Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestEmployeeModel:
    """Comprehensive tests for the Employee model."""

    def test_create_employee(self, db):
        """Verify that an employee can be created with all required fields."""
        employee = Employee.objects.create(
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
            remote_work_frequency=0.2,
            team_size=8,
            training_hours=40,
            promotions=2,
            employee_satisfaction_score=4.2,
            resigned=False,
        )
        assert employee.employee_id == 1001
        assert employee.name == 'Test Employee'
        assert employee.department == 'IT'
        assert not employee.resigned
        assert str(employee) == 'Test Employee (ID: 1001)'

    def test_employee_ordering(self, db):
        """Verify employees are ordered by employee_id by default."""
        Employee.objects.create(employee_id=3, name='C', department='IT',
                                 job_title='Dev', age=25, years_at_company=1,
                                 performance_score=3.0, monthly_salary=3000.0,
                                 monthly_salary_inr=249000, hire_date='2023-01-01',
                                 gender='Male', education_level='Bachelor',
                                 work_hours_per_week=40, projects_handled=1,
                                 overtime_hours=0, sick_days=0,
                                 remote_work_frequency=0, team_size=5,
                                 training_hours=10, promotions=0,
                                 employee_satisfaction_score=3.0, resigned=False)
        Employee.objects.create(employee_id=1, name='A', department='IT',
                                 job_title='Dev', age=25, years_at_company=1,
                                 performance_score=3.0, monthly_salary=3000.0,
                                 monthly_salary_inr=249000, hire_date='2023-01-01',
                                 gender='Female', education_level='Master',
                                 work_hours_per_week=40, projects_handled=1,
                                 overtime_hours=0, sick_days=0,
                                 remote_work_frequency=0, team_size=5,
                                 training_hours=10, promotions=0,
                                 employee_satisfaction_score=3.0, resigned=False)
        employees = Employee.objects.all()
        assert employees[0].employee_id < employees[1].employee_id

    def test_employee_id_unique(self, db):
        """Verify employee_id must be unique."""
        Employee.objects.create(employee_id=1, name='First', department='IT',
                                 job_title='Dev', age=25, years_at_company=1,
                                 performance_score=3.0, monthly_salary=3000.0,
                                 monthly_salary_inr=249000, hire_date='2023-01-01',
                                 gender='Male', education_level='Bachelor',
                                 work_hours_per_week=40, projects_handled=1,
                                 overtime_hours=0, sick_days=0,
                                 remote_work_frequency=0, team_size=5,
                                 training_hours=10, promotions=0,
                                 employee_satisfaction_score=3.0, resigned=False)
        with pytest.raises(IntegrityError):
            Employee.objects.create(employee_id=1, name='Duplicate',
                                     department='IT', job_title='Dev',
                                     age=30, years_at_company=2,
                                     performance_score=3.5, monthly_salary=4000.0,
                                     monthly_salary_inr=332000,
                                     hire_date='2022-06-01', gender='Female',
                                     education_level='Master',
                                     work_hours_per_week=40, projects_handled=2,
                                     overtime_hours=2, sick_days=1,
                                     remote_work_frequency=10, team_size=6,
                                     training_hours=20, promotions=1,
                                     employee_satisfaction_score=4.0, resigned=False)

    def test_employee_timestamps(self, db):
        """Verify auto_now_add and auto_now work."""
        employee = Employee.objects.create(
            employee_id=100, name='Time Test', department='HR',
            job_title='Manager', age=35, years_at_company=10,
            performance_score=4.0, monthly_salary=6000.0,
            monthly_salary_inr=498000, hire_date='2015-03-01',
            gender='Female', education_level='Master',
            work_hours_per_week=40, projects_handled=15,
            overtime_hours=3, sick_days=5, remote_work_frequency=30,
            team_size=10, training_hours=50, promotions=3,
            employee_satisfaction_score=4.5, resigned=False,
        )
        assert employee.created_at is not None
        assert employee.updated_at is not None

    def test_employee_resigned_default(self, db):
        """Verify resigned defaults to False."""
        employee = Employee.objects.create(
            employee_id=200, name='Active Emp', department='Sales',
            job_title='Rep', age=28, years_at_company=3,
            performance_score=3.8, monthly_salary=4500.0,
            monthly_salary_inr=373500, hire_date='2021-07-01',
            gender='Male', education_level='Bachelor',
            work_hours_per_week=45, projects_handled=8,
            overtime_hours=10, sick_days=2, remote_work_frequency=0,
            team_size=6, training_hours=30, promotions=1,
            employee_satisfaction_score=3.9, resigned=False,
        )
        assert employee.resigned is False


# ═════════════════════════════════════════════════════════════════════════════
#  Analysis Model Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestAnalysisModel:
    """Tests for the Analysis model."""

    def test_create_analysis(self, db, django_user_model):
        user = django_user_model.objects.create_user(username='testuser',
                                                      password='testpass123')
        analysis = Analysis.objects.create(
            analysis_type='department',
            chart_type='bar',
            chart_data={'labels': ['IT', 'HR'], 'values': [10, 5]},
            created_by=user,
        )
        assert analysis.analysis_type == 'department'
        assert analysis.chart_type == 'bar'
        assert analysis.created_by == user
        assert str(analysis).startswith('Department Analysis')

    def test_analysis_ordering(self, db, django_user_model):
        user = django_user_model.objects.create_user(username='u1',
                                                      password='pass')
        a1 = Analysis.objects.create(analysis_type='performance',
                                      chart_type='histogram',
                                      chart_data={}, created_by=user)
        a2 = Analysis.objects.create(analysis_type='salary',
                                      chart_type='pie',
                                      chart_data={}, created_by=user)
        analyses = Analysis.objects.all()
        assert analyses[0].created_at >= analyses[1].created_at

    def test_analysis_str_with_timestamp(self, db, django_user_model):
        user = django_user_model.objects.create_user(username='u2',
                                                      password='pass')
        analysis = Analysis.objects.create(analysis_type='overall',
                                            chart_type='line', chart_data={},
                                            created_by=user)
        assert str(analysis) is not None
        assert 'Overall' in str(analysis)


# ═════════════════════════════════════════════════════════════════════════════
#  Prediction Model Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestPredictionModel:
    """Tests for the Prediction model."""

    def test_create_prediction(self, db, django_user_model):
        user = django_user_model.objects.create_user(username='preduser',
                                                      password='pass')
        prediction = Prediction.objects.create(
            model_type='random_forest',
            input_data={'age': 30, 'department': 'IT'},
            prediction_result=4.2,
            confidence_score=0.88,
            accuracy=0.92,
            error_rate=0.08,
            created_by=user,
        )
        assert prediction.model_type == 'random_forest'
        assert prediction.prediction_result == 4.2
        assert prediction.confidence_score == 0.88
        assert str(prediction).startswith('Random Forest')

    def test_prediction_nullable_metrics(self, db, django_user_model):
        user = django_user_model.objects.create_user(username='preduser2',
                                                      password='pass')
        prediction = Prediction.objects.create(
            model_type='xgboost',
            input_data={'age': 35},
            prediction_result=3.8,
            created_by=user,
        )
        assert prediction.confidence_score is None
        assert prediction.accuracy is None
        assert prediction.error_rate is None

    def test_prediction_ordering(self, db, django_user_model):
        user = django_user_model.objects.create_user(username='preduser3',
                                                      password='pass')
        p1 = Prediction.objects.create(model_type='random_forest',
                                        input_data={},
                                        prediction_result=4.0,
                                        created_by=user)
        p2 = Prediction.objects.create(model_type='xgboost',
                                        input_data={},
                                        prediction_result=3.5,
                                        created_by=user)
        predictions = Prediction.objects.all()
        assert predictions[0].created_at >= predictions[1].created_at


# ═════════════════════════════════════════════════════════════════════════════
#  UserProfile Model Tests
# ═════════════════════════════════════════════════════════════════════════════


class TestUserProfileModel:
    """Tests for the UserProfile model."""

    def test_create_user_profile_on_creation(self, db, django_user_model):
        """Verify UserProfile auto-created when user is created via form."""
        user = django_user_model.objects.create_user(username='profuser',
                                                      password='pass')
        profile = UserProfile.objects.create(
            user=user,
            department='Engineering',
            role='Developer',
            phone='+1234567890',
        )
        assert profile.user == user
        assert profile.department == 'Engineering'
        assert profile.role == 'Developer'
        assert str(profile) == "profuser's Profile"

    def test_user_profile_defaults(self, db, django_user_model):
        user = django_user_model.objects.create_user(username='defaultprof',
                                                      password='pass')
        profile = UserProfile.objects.create(user=user)
        assert profile.department == ''
        assert profile.role == ''
        assert profile.phone == ''

    def test_user_profile_one_to_one(self, db, django_user_model):
        user = django_user_model.objects.create_user(username='onetoone',
                                                      password='pass')
        UserProfile.objects.create(user=user)
        with pytest.raises(IntegrityError):
            UserProfile.objects.create(user=user)
