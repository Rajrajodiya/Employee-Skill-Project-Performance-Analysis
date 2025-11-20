from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Prediction

class UserRegistrationForm(UserCreationForm):
    """Custom user registration form"""
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
            # Create user profile
            UserProfile.objects.create(
                user=user,
                department=self.cleaned_data.get('department', ''),
                role=self.cleaned_data.get('role', ''),
                phone=self.cleaned_data.get('phone', '')
            )
        return user

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = UserProfile
        fields = ['department', 'role', 'phone', 'profile_picture']

class PredictionForm(forms.ModelForm):
    """Form for making predictions with all employee features"""
    
    # Model selection
    model_type = forms.ChoiceField(
        choices=Prediction.MODEL_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Personal Information
    age = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter age'})
    )
    gender = forms.ChoiceField(
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    education_level = forms.ChoiceField(
        choices=[
            ('High School', 'High School'),
            ('Bachelor', 'Bachelor'),
            ('Master', 'Master'),
            ('PhD', 'PhD'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Work Information
    department = forms.ChoiceField(
        choices=[
            ('IT', 'IT'),
            ('Finance', 'Finance'),
            ('Marketing', 'Marketing'),
            ('Sales', 'Sales'),
            ('HR', 'HR'),
            ('Operations', 'Operations'),
            ('Customer Support', 'Customer Support'),
            ('Engineering', 'Engineering'),
            ('Research', 'Research'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    job_title = forms.ChoiceField(
        choices=[
            ('Specialist', 'Specialist'),
            ('Developer', 'Developer'),
            ('Analyst', 'Analyst'),
            ('Manager', 'Manager'),
            ('Engineer', 'Engineer'),
            ('Consultant', 'Consultant'),
            ('Technician', 'Technician'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    years_at_company = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years at company'})
    )
    
    # Performance Metrics
    monthly_salary = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Monthly salary in Rupees'})
    )
    work_hours_per_week = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Work hours per week'})
    )
    projects_handled = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of projects handled'})
    )
    overtime_hours = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Overtime hours per week'})
    )
    
    # Additional Metrics
    sick_days = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Sick days per year'})
    )
    remote_work_frequency = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Remote work frequency (%)'})
    )
    team_size = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Team size'})
    )
    training_hours = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Training hours per month'})
    )
    
    # Career Development
    promotions = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of promotions'})
    )
    employee_satisfaction_score = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Satisfaction score (1-5)'})
    )
    
    class Meta:
        model = Prediction
        fields = ['model_type']
    
    def clean(self):
        """Custom validation for the form"""
        cleaned_data = super().clean()
        
        # Validate age
        age = cleaned_data.get('age')
        if age is not None and (age < 18 or age > 70):
            self.add_error('age', 'Age must be between 18 and 70 years.')
        
        # Validate years at company
        years = cleaned_data.get('years_at_company')
        if years is not None and years < 0:
            self.add_error('years_at_company', 'Years at company cannot be negative.')
        
        # Validate salary
        salary = cleaned_data.get('monthly_salary')
        if salary is not None and salary < 0:
            self.add_error('monthly_salary', 'Salary cannot be negative.')
        
        # Validate work hours
        hours = cleaned_data.get('work_hours_per_week')
        if hours is not None and (hours < 0 or hours > 80):
            self.add_error('work_hours_per_week', 'Work hours must be between 0 and 80.')
        
        # Validate projects
        projects = cleaned_data.get('projects_handled')
        if projects is not None and projects < 0:
            self.add_error('projects_handled', 'Projects handled cannot be negative.')
        
        # Validate overtime
        overtime = cleaned_data.get('overtime_hours')
        if overtime is not None and overtime < 0:
            self.add_error('overtime_hours', 'Overtime hours cannot be negative.')
        
        # Validate sick days
        sick_days = cleaned_data.get('sick_days')
        if sick_days is not None and (sick_days < 0 or sick_days > 365):
            self.add_error('sick_days', 'Sick days must be between 0 and 365.')
        
        # Validate remote work frequency
        remote = cleaned_data.get('remote_work_frequency')
        if remote is not None and (remote < 0 or remote > 100):
            self.add_error('remote_work_frequency', 'Remote work frequency must be between 0 and 100%.')
        
        # Validate team size
        team_size = cleaned_data.get('team_size')
        if team_size is not None and team_size < 1:
            self.add_error('team_size', 'Team size must be at least 1.')
        
        # Validate training hours
        training = cleaned_data.get('training_hours')
        if training is not None and training < 0:
            self.add_error('training_hours', 'Training hours cannot be negative.')
        
        # Validate promotions
        promotions = cleaned_data.get('promotions')
        if promotions is not None and promotions < 0:
            self.add_error('promotions', 'Promotions cannot be negative.')
        
        # Validate satisfaction score
        satisfaction = cleaned_data.get('employee_satisfaction_score')
        if satisfaction is not None and (satisfaction < 1.0 or satisfaction > 5.0):
            self.add_error('employee_satisfaction_score', 'Satisfaction score must be between 1.0 and 5.0.')
        
        return cleaned_data

class AnalysisForm(forms.Form):
    """Form for selecting analysis type and chart type"""
    analysis_type = forms.ChoiceField(
        choices=[
            ('department', 'Department Analysis'),
            ('performance', 'Performance Analysis'),
            ('salary', 'Salary Analysis'),
            ('overtime', 'Overtime Analysis'),
            ('satisfaction', 'Satisfaction Analysis'),
            ('overall', 'Overall Analysis'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    chart_type = forms.ChoiceField(
        choices=[
            ('bar', 'Bar Chart'),
            ('histogram', 'Histogram'),
            ('pie', 'Pie Chart'),
            ('box', 'Box Plot'),
            ('heatmap', 'Heatmap'),
            ('scatter', 'Scatter Plot'),
            ('line', 'Line Chart'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    ) 