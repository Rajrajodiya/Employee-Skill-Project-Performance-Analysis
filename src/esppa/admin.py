from django.contrib import admin
from .models import Analysis, Prediction, UserProfile, Employee


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ('analysis_type', 'chart_type', 'created_by', 'created_at')
    list_filter = ('analysis_type', 'chart_type', 'created_at')
    search_fields = ('analysis_type', 'chart_type')
    ordering = ('-created_at',)


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('model_type', 'prediction_result', 'confidence_score', 'created_by', 'created_at')
    list_filter = ('model_type', 'created_at')
    search_fields = ('model_type',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'role', 'created_at')
    list_filter = ('department', 'created_at')
    search_fields = ('user__username', 'user__email', 'department')
    ordering = ('-created_at',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'name', 'department', 'job_title', 'age', 'performance_score', 'monthly_salary_inr', 'resigned')
    list_filter = ('department', 'gender', 'education_level', 'resigned', 'created_at')
    search_fields = ('employee_id', 'name', 'department', 'job_title')
    ordering = ('employee_id',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee_id', 'name', 'department', 'job_title', 'gender', 'education_level', 'hire_date')
        }),
        ('Performance & Work', {
            'fields': ('age', 'years_at_company', 'performance_score', 'work_hours_per_week', 'projects_handled', 'overtime_hours')
        }),
        ('Compensation', {
            'fields': ('monthly_salary', 'monthly_salary_inr')
        }),
        ('Work Environment', {
            'fields': ('sick_days', 'remote_work_frequency', 'team_size', 'training_hours', 'promotions', 'employee_satisfaction_score')
        }),
        ('Status', {
            'fields': ('resigned',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
