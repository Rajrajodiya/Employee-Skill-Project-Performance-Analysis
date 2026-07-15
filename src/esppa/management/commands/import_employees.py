import os
import logging

import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from tqdm import tqdm

from esppa.models import Employee

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import employee data from CSV file to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            default='',
            help='Path to the CSV file (default: static/employee_data.csv)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing employee data before importing'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file'] or os.path.join(
            settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else getattr(settings, 'PROJECT_ROOT', ''),
            'employee_data.csv'
        )
        clear_existing = options['clear']

        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_file}'))
            return

        try:
            self.stdout.write(f'Reading CSV file: {csv_file}')
            df = pd.read_csv(csv_file)
            total = len(df)
            self.stdout.write(f'Found {total} employees in CSV file')

            if clear_existing:
                self.stdout.write('Clearing existing employee data...')
                deleted, _ = Employee.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'Cleared {deleted} existing records'))

            created_count = 0
            updated_count = 0
            batch_size = 500
            employees = []

            for idx, (_, row) in enumerate(tqdm(df.iterrows(), total=total, desc='Importing')):
                salary_inr = int(round(row['Monthly_Salary'] * 83, 0))
                gender = str(row['Gender']).strip()
                if gender == 'Male':
                    name = f"Mr. Employee {int(row['Employee_ID'])}"
                elif gender == 'Female':
                    name = f"Ms. Employee {int(row['Employee_ID'])}"
                else:
                    name = f"Employee {int(row['Employee_ID'])}"

                employees.append(Employee(
                    employee_id=int(row['Employee_ID']),
                    name=name,
                    department=str(row['Department']),
                    job_title=str(row['Job_Title']),
                    age=int(row['Age']),
                    years_at_company=int(row['Years_At_Company']),
                    performance_score=float(row['Performance_Score']),
                    monthly_salary=float(row['Monthly_Salary']),
                    monthly_salary_inr=salary_inr,
                    hire_date=str(row['Hire_Date']),
                    gender=gender,
                    education_level=str(row['Education_Level']),
                    work_hours_per_week=int(row['Work_Hours_Per_Week']),
                    projects_handled=int(row['Projects_Handled']),
                    overtime_hours=int(row['Overtime_Hours']),
                    sick_days=int(row['Sick_Days']),
                    remote_work_frequency=float(row['Remote_Work_Frequency']),
                    team_size=int(row['Team_Size']),
                    training_hours=int(row['Training_Hours']),
                    promotions=int(row['Promotions']),
                    employee_satisfaction_score=float(row['Employee_Satisfaction_Score']),
                    resigned=bool(row['Resigned']),
                ))

                if len(employees) >= batch_size:
                    Employee.objects.bulk_create(employees, ignore_conflicts=True)
                    created_count += len(employees)
                    employees = []

            if employees:
                Employee.objects.bulk_create(employees, ignore_conflicts=True)
                created_count += len(employees)

            self.stdout.write(self.style.SUCCESS(
                f'Import completed!\nCreated: {created_count}\nTotal: {total}'
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {str(e)}'))
            logger.exception('Import failed')
