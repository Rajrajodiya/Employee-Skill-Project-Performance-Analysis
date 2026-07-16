"""
Prediction form — single responsibility: ML prediction input with validation.
"""

from django import forms

from apps.esppa.models import Prediction
from apps.esppa.services.config import (
    GENDER_CHOICES, EDUCATION_CHOICES, DEPARTMENT_CHOICES, JOB_TITLE_CHOICES,
    PREDICTION_FIELD_SPECS,
)


# ── Default widget attrs (DRY: applied to all fields) ───────────────────────
DEFAULT_ATTRS = {'class': 'form-control'}

FIELD_PLACEHOLDERS = {
    'age': 'Enter age (18-70)',
    'years_at_company': 'Years at company',
    'monthly_salary': 'Monthly salary (USD)',
    'work_hours_per_week': 'Work hours per week',
    'projects_handled': 'Projects handled',
    'overtime_hours': 'Overtime hours',
    'sick_days': 'Sick days per year',
    'remote_work_frequency': 'Remote work %',
    'team_size': 'Team size',
    'training_hours': 'Training hours',
    'promotions': 'Number of promotions',
    'employee_satisfaction_score': 'Satisfaction (1-5)',
}

FIELD_OVERRIDES = {
    'age': {'step': None},
    'employee_satisfaction_score': {'step': 0.1},
}


def _field_attrs(name: str) -> dict:
    """Build widget attrs dict for a given prediction field name."""
    attrs = dict(DEFAULT_ATTRS)
    if name in FIELD_PLACEHOLDERS:
        attrs['placeholder'] = FIELD_PLACEHOLDERS[name]
    override = FIELD_OVERRIDES.get(name)
    if override:
        for k, v in override.items():
            if v is not None:
                attrs[k] = v
    return attrs


class PredictionForm(forms.ModelForm):
    """Form for making predictions with all employee features."""

    model_type = forms.ChoiceField(
        choices=Prediction.MODEL_TYPES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )

    age = forms.IntegerField(widget=forms.NumberInput(attrs=_field_attrs('age')))
    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.Select(attrs=DEFAULT_ATTRS))
    education_level = forms.ChoiceField(choices=EDUCATION_CHOICES, widget=forms.Select(attrs=DEFAULT_ATTRS))
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, widget=forms.Select(attrs=DEFAULT_ATTRS))
    job_title = forms.ChoiceField(choices=JOB_TITLE_CHOICES, widget=forms.Select(attrs=DEFAULT_ATTRS))
    years_at_company = forms.IntegerField(widget=forms.NumberInput(attrs=_field_attrs('years_at_company')))
    monthly_salary = forms.IntegerField(widget=forms.NumberInput(attrs=_field_attrs('monthly_salary')))
    work_hours_per_week = forms.IntegerField(widget=forms.NumberInput(attrs=_field_attrs('work_hours_per_week')))
    projects_handled = forms.IntegerField(widget=forms.NumberInput(attrs=_field_attrs('projects_handled')))
    overtime_hours = forms.IntegerField(widget=forms.NumberInput(attrs=_field_attrs('overtime_hours')))
    sick_days = forms.IntegerField(widget=forms.NumberInput(attrs=_field_attrs('sick_days')))
    remote_work_frequency = forms.IntegerField(widget=forms.NumberInput(attrs=_field_attrs('remote_work_frequency')))
    team_size = forms.IntegerField(widget=forms.NumberInput(attrs=_field_attrs('team_size')))
    training_hours = forms.IntegerField(widget=forms.NumberInput(attrs=_field_attrs('training_hours')))
    promotions = forms.IntegerField(widget=forms.NumberInput(attrs=_field_attrs('promotions')))
    employee_satisfaction_score = forms.FloatField(widget=forms.NumberInput(attrs=_field_attrs('employee_satisfaction_score')))

    class Meta:
        model = Prediction
        fields = ['model_type']

    def clean(self):
        """Data-driven validation: iterate PREDICTION_FIELD_SPECS instead of 7 if-blocks."""
        cleaned_data = super().clean()

        for spec in PREDICTION_FIELD_SPECS:
            name = spec['name']
            value = cleaned_data.get(name)
            if value is None:
                continue
            min_val, max_val = spec['min'], spec['max']
            errors = []
            if min_val is not None and value < min_val:
                errors.append(f'{name.replace("_", " ").title()} must be at least {min_val}.')
            if max_val is not None and value > max_val:
                errors.append(f'{name.replace("_", " ").title()} must be at most {max_val}.')
            for err in errors:
                self.add_error(name, err)

        return cleaned_data
