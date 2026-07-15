from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Prediction


class UserRegistrationForm(UserCreationForm):
    """Custom user registration form with extended profile fields."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    department = forms.CharField(max_length=100, required=False)
    role = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                department=self.cleaned_data.get('department', ''),
                role=self.cleaned_data.get('role', ''),
                phone=self.cleaned_data.get('phone', '')
            )
        return user


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile."""
    class Meta:
        model = UserProfile
        fields = ['department', 'role', 'phone', 'profile_picture']


class PredictionForm(forms.ModelForm):
    """Form for making predictions with all employee features."""

    model_type = forms.ChoiceField(
        choices=Prediction.MODEL_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    age = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter age (18-70)'})
    )
    gender = forms.ChoiceField(
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    education_level = forms.ChoiceField(
        choices=[('High School', 'High School'), ('Bachelor', 'Bachelor'),
                 ('Master', 'Master'), ('PhD', 'PhD')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    department = forms.ChoiceField(
        choices=[('IT', 'IT'), ('Finance', 'Finance'), ('Marketing', 'Marketing'),
                 ('Sales', 'Sales'), ('HR', 'HR'), ('Operations', 'Operations'),
                 ('Customer Support', 'Customer Support'), ('Engineering', 'Engineering'),
                 ('Research', 'Research')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    job_title = forms.ChoiceField(
        choices=[('Specialist', 'Specialist'), ('Developer', 'Developer'),
                 ('Analyst', 'Analyst'), ('Manager', 'Manager'),
                 ('Engineer', 'Engineer'), ('Consultant', 'Consultant'),
                 ('Technician', 'Technician')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    years_at_company = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years at company'})
    )
    monthly_salary = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Monthly salary (USD)'})
    )
    work_hours_per_week = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Work hours per week'})
    )
    projects_handled = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Projects handled'})
    )
    overtime_hours = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Overtime hours'})
    )
    sick_days = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Sick days per year'})
    )
    remote_work_frequency = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Remote work %'})
    )
    team_size = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Team size'})
    )
    training_hours = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Training hours'})
    )
    promotions = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of promotions'})
    )
    employee_satisfaction_score = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Satisfaction (1-5)'})
    )

    class Meta:
        model = Prediction
        fields = ['model_type']

    def clean(self):
        cleaned_data = super().clean()

        age = cleaned_data.get('age')
        if age is not None and (age < 18 or age > 70):
            self.add_error('age', 'Age must be between 18 and 70 years.')

        years = cleaned_data.get('years_at_company')
        if years is not None and years < 0:
            self.add_error('years_at_company', 'Years at company cannot be negative.')

        salary = cleaned_data.get('monthly_salary')
        if salary is not None and salary < 0:
            self.add_error('monthly_salary', 'Salary cannot be negative.')

        hours = cleaned_data.get('work_hours_per_week')
        if hours is not None and (hours < 0 or hours > 80):
            self.add_error('work_hours_per_week', 'Work hours must be between 0 and 80.')

        remote = cleaned_data.get('remote_work_frequency')
        if remote is not None and (remote < 0 or remote > 100):
            self.add_error('remote_work_frequency', 'Remote work frequency must be between 0 and 100%.')

        team_size = cleaned_data.get('team_size')
        if team_size is not None and team_size < 1:
            self.add_error('team_size', 'Team size must be at least 1.')

        satisfaction = cleaned_data.get('employee_satisfaction_score')
        if satisfaction is not None and (satisfaction < 1.0 or satisfaction > 5.0):
            self.add_error('employee_satisfaction_score', 'Satisfaction score must be between 1.0 and 5.0.')

        return cleaned_data


class AnalysisForm(forms.Form):
    """Form for selecting analysis type and chart type."""
    analysis_type = forms.ChoiceField(
        choices=[('department', 'Department Analysis'), ('performance', 'Performance Analysis'),
                 ('salary', 'Salary Analysis'), ('overtime', 'Overtime Analysis'),
                 ('satisfaction', 'Satisfaction Analysis'), ('overall', 'Overall Analysis')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    chart_type = forms.ChoiceField(
        choices=[('bar', 'Bar Chart'), ('histogram', 'Histogram'), ('pie', 'Pie Chart'),
                 ('box', 'Box Plot'), ('heatmap', 'Heatmap'), ('scatter', 'Scatter Plot'),
                 ('line', 'Line Chart')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
