import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from analyzer.models import Employee


class Command(BaseCommand):
    help = 'Import employee data from CSV file to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            default='static/employee_data.csv',
            help='Path to the CSV file (default: static/employee_data.csv)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing employee data before importing'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        clear_existing = options['clear']
        
        # Get the full path to the CSV file
        if not os.path.isabs(csv_file):
            csv_file = os.path.join(settings.BASE_DIR, csv_file)
        
        if not os.path.exists(csv_file):
            self.stdout.write(
                self.style.ERROR(f'CSV file not found: {csv_file}')
            )
            return
        
        try:
            # Read CSV file
            self.stdout.write(f'Reading CSV file: {csv_file}')
            df = pd.read_csv(csv_file)
            self.stdout.write(f'Found {len(df)} employees in CSV file')
            
            # Clear existing data if requested
            if clear_existing:
                self.stdout.write('Clearing existing employee data...')
                Employee.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS('Existing employee data cleared')
                )
            
            # Import data
            created_count = 0
            updated_count = 0
            
            for _, row in df.iterrows():
                # Generate name based on gender and ID
                if row['Gender'] == 'Male':
                    name = f"Mr. Employee {row['Employee_ID']}"
                elif row['Gender'] == 'Female':
                    name = f"Ms. Employee {row['Employee_ID']}"
                else:
                    name = f"Employee {row['Employee_ID']}"
                
                # Calculate INR salary
                salary_inr = int(round(row['Monthly_Salary'] * 83, 0))
                
                # Create or update employee
                employee, created = Employee.objects.update_or_create(
                    employee_id=int(row['Employee_ID']),
                    defaults={
                        'name': name,
                        'department': row['Department'],
                        'job_title': row['Job_Title'],
                        'age': int(row['Age']),
                        'years_at_company': int(row['Years_At_Company']),
                        'performance_score': float(row['Performance_Score']),
                        'monthly_salary': float(row['Monthly_Salary']),
                        'monthly_salary_inr': salary_inr,
                        'hire_date': row['Hire_Date'],
                        'gender': row['Gender'],
                        'education_level': row['Education_Level'],
                        'work_hours_per_week': int(row['Work_Hours_Per_Week']),
                        'projects_handled': int(row['Projects_Handled']),
                        'overtime_hours': int(row['Overtime_Hours']),
                        'sick_days': int(row['Sick_Days']),
                        'remote_work_frequency': float(row['Remote_Work_Frequency']),
                        'team_size': int(row['Team_Size']),
                        'training_hours': int(row['Training_Hours']),
                        'promotions': int(row['Promotions']),
                        'employee_satisfaction_score': float(row['Employee_Satisfaction_Score']),
                        'resigned': bool(row['Resigned'])
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            # Summary
            self.stdout.write(
                self.style.SUCCESS(
                    f'Import completed successfully!\n'
                    f'Created: {created_count} employees\n'
                    f'Updated: {updated_count} employees\n'
                    f'Total: {created_count + updated_count} employees'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing data: {str(e)}')
            ) 