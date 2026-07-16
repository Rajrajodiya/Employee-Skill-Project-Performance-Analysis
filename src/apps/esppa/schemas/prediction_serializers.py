"""
Prediction serializers — single responsibility: prediction data serialization and input validation.
"""

from rest_framework import serializers

from apps.esppa.models import Prediction


class PredictionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    model_display = serializers.SerializerMethodField()

    class Meta:
        model = Prediction
        fields = ['id', 'model_type', 'model_display', 'input_data',
                  'prediction_result', 'confidence_score', 'accuracy',
                  'error_rate', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at',
                            'prediction_result', 'confidence_score',
                            'accuracy', 'error_rate']

    def get_model_display(self, obj):
        return obj.get_model_type_display()

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class PredictionInputSerializer(serializers.Serializer):
    model_type = serializers.ChoiceField(choices=Prediction.MODEL_TYPES)
    age = serializers.IntegerField(min_value=18, max_value=70)
    gender = serializers.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    education_level = serializers.ChoiceField(choices=[
        ('High School', 'High School'), ('Bachelor', 'Bachelor'),
        ('Master', 'Master'), ('PhD', 'PhD'),
    ])
    department = serializers.ChoiceField(choices=[
        ('IT', 'IT'), ('Finance', 'Finance'), ('Marketing', 'Marketing'),
        ('Sales', 'Sales'), ('HR', 'HR'), ('Operations', 'Operations'),
        ('Customer Support', 'Customer Support'), ('Engineering', 'Engineering'),
        ('Research', 'Research'),
    ])
    job_title = serializers.ChoiceField(choices=[
        ('Specialist', 'Specialist'), ('Developer', 'Developer'),
        ('Analyst', 'Analyst'), ('Manager', 'Manager'),
        ('Engineer', 'Engineer'), ('Consultant', 'Consultant'),
        ('Technician', 'Technician'),
    ])
    years_at_company = serializers.IntegerField(min_value=0)
    monthly_salary = serializers.IntegerField(min_value=0)
    work_hours_per_week = serializers.IntegerField(min_value=0, max_value=80)
    projects_handled = serializers.IntegerField(min_value=0)
    overtime_hours = serializers.IntegerField(min_value=0)
    sick_days = serializers.IntegerField(min_value=0, max_value=365)
    remote_work_frequency = serializers.IntegerField(min_value=0, max_value=100)
    team_size = serializers.IntegerField(min_value=1)
    training_hours = serializers.IntegerField(min_value=0)
    promotions = serializers.IntegerField(min_value=0)
    employee_satisfaction_score = serializers.FloatField(min_value=1.0, max_value=5.0)
