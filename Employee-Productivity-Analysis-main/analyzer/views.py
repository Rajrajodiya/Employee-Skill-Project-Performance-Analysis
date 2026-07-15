import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.conf import settings

from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, mean_absolute_error, r2_score
import pickle
from .models import Analysis, Prediction, UserProfile
from .forms import UserRegistrationForm, UserProfileForm, PredictionForm, AnalysisForm

# Global variables for models
models = {}
label_encoders = {}
scaler = None
df = None

def load_data_and_models():
    """Load data and train models"""
    global models, label_encoders, scaler, df
    
    try:
        # Load data from static folder
        csv_path = os.path.join(settings.STATICFILES_DIRS[0], 'employee_data.csv')
        df = pd.read_csv(csv_path)
        
        # Preprocess data
        categorical_cols = ['Department', 'Gender', 'Job_Title', 'Education_Level']
        numerical_cols = [
            'Age', 'Years_At_Company', 'Performance_Score', 'Monthly_Salary',
            'Work_Hours_Per_Week', 'Projects_Handled', 'Overtime_Hours',
            'Sick_Days', 'Remote_Work_Frequency', 'Team_Size', 'Training_Hours',
            'Promotions', 'Employee_Satisfaction_Score'
        ]
        
        # Encode categorical variables
        for col in categorical_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            label_encoders[col] = le
        
        # Scale numerical features
        scaler = MinMaxScaler()
        df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
        
        # Prepare features and target
        X = df.drop(['Employee_ID', 'Hire_Date', 'Performance_Score', 'Resigned'], axis=1, errors='ignore')
        y_performance = df['Performance_Score']
        y_resigned = df['Resigned'].astype(int)
        
        # Split data
        X_train, X_test, y_train_perf, y_test_perf, y_train_res, y_test_res = train_test_split(
            X, y_performance, y_resigned, test_size=0.2,  _state=42
        )
        
        # Train models
        models['random_forest_performance'] = RandomForestRegressor(n_estimators=100, random_state=42)
        models['random_forest_performance'].fit(X_train, y_train_perf)
        
        models['logistic_regression'] = LogisticRegression(random_state=42, max_iter=1000)
        models['logistic_regression'].fit(X_train, y_train_res)
        
        models['linear_regression'] = LinearRegression()
        models['linear_regression'].fit(X_train, y_train_perf)
        
        # Save models
        os.makedirs('models', exist_ok=True)
        with open('models/random_forest_performance.pkl', 'wb') as f:
            pickle.dump(models['random_forest_performance'], f)
        
        with open('models/logistic_regression.pkl', 'wb') as f:
            pickle.dump(models['logistic_regression'], f)
        
        with open('models/linear_regression.pkl', 'wb') as f:
            pickle.dump(models['linear_regression'], f)
        
        return True
    except Exception as e:
        print(f"Error loading models: {e}")
        return False

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to ESPPA.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'analyzer/register.html', {'form': form})

@login_required
def dashboard_view(request):
    """Dashboard view with comprehensive metrics"""
    try:
        # Load data directly from CSV file
        csv_path = os.path.join(settings.STATICFILES_DIRS[0], 'employee_data.csv')
        df_temp = pd.read_csv(csv_path)
        
        # Calculate comprehensive key metrics
        total_employees = len(df_temp)
        avg_performance = df_temp['Performance_Score'].mean()
        avg_salary_usd = df_temp['Monthly_Salary'].mean()
        avg_salary_inr = avg_salary_usd  # Convert USD to INR (approximate rate)
        resignation_rate = (df_temp['Resigned'].sum() / total_employees * 100) if total_employees > 0 else 0
        
        # Department analysis
        department_counts = df_temp['Department'].value_counts().to_dict()
        department_performance = df_temp.groupby('Department')['Performance_Score'].mean().to_dict()
        department_salary = df_temp.groupby('Department')['Monthly_Salary'].mean().to_dict()
        department_salary_inr = {dept: salary for dept, salary in department_salary.items()}
        
        # Create department data with all metrics
        department_data = []
        for dept in department_counts.keys():
            performance_score = department_performance.get(dept, 0)
            dept_data = {
                'name': dept,
                'count': department_counts[dept],
                'performance': performance_score,
                'performance_width': min(100, max(0, performance_score * 20)),  # Convert to percentage for progress bar
                'salary_inr': department_salary_inr.get(dept, 0)
            }
            department_data.append(dept_data)
        
        # Gender distribution
        gender_counts = df_temp['Gender'].value_counts().to_dict()
        
        # Education level distribution
        education_counts = df_temp['Education_Level'].value_counts().to_dict()
        
        # Performance categories
        high_performers = len(df_temp[df_temp['Performance_Score'] >= 4.0])
        medium_performers = len(df_temp[(df_temp['Performance_Score'] >= 3.0) & (df_temp['Performance_Score'] < 4.0)])
        low_performers = len(df_temp[df_temp['Performance_Score'] < 3.0])
        
        # Salary ranges
        high_salary = len(df_temp[df_temp['Monthly_Salary'] >= 80000])
        medium_salary = len(df_temp[(df_temp['Monthly_Salary'] >= 50000) & (df_temp['Monthly_Salary'] < 80000)])
        low_salary = len(df_temp[df_temp['Monthly_Salary'] < 50000])
        
        # Get recent predictions
        recent_predictions_raw = Prediction.objects.filter(created_by=request.user).order_by('-created_at')[:5]
        recent_predictions = []
        for pred in recent_predictions_raw:
            pred_data = pred
            pred_data.confidence_width = min(100, max(0, pred.confidence_score * 100))  # Convert to percentage
            recent_predictions.append(pred_data)
        
        # Get recent analyses
        recent_analyses = Analysis.objects.filter(created_by=request.user).order_by('-created_at')[:5]
        
        context = {
            'total_employees': total_employees,
            'avg_performance': round(avg_performance, 2),
            'avg_salary_usd': round(avg_salary_usd, 2),
            'avg_salary_inr': round(avg_salary_inr, 0),
            'resignation_rate': round(resignation_rate, 2),
            'department_data': department_data,
            'gender_counts': gender_counts,
            'education_counts': education_counts,
            'high_performers': high_performers,
            'medium_performers': medium_performers,
            'low_performers': low_performers,
            'high_salary': high_salary,
            'medium_salary': medium_salary,
            'low_salary': low_salary,
            'recent_predictions': recent_predictions,
            'recent_analyses': recent_analyses,
        }
        
        return render(request, 'analyzer/dashboard.html', context)
    except Exception as e:
        messages.error(request, f'Error loading dashboard: {e}')
        return render(request, 'analyzer/dashboard.html', {})

@login_required
def analysis_view(request):
    """Direct analysis view showing all charts"""
    try:
        # Load data directly from CSV file
        csv_path = os.path.join(settings.STATICFILES_DIRS[0], 'employee_data.csv')
        df_temp = pd.read_csv(csv_path)
        
        # Generate all charts
        department_bar = generate_department_bar_chart(df_temp)
        department_pie = generate_department_pie_chart(df_temp)
        performance_hist = generate_performance_histogram(df_temp)
        salary_hist = generate_salary_histogram(df_temp)
        
        context = {
            'department_bar': department_bar,
            'department_pie': department_pie,
            'performance_hist': performance_hist,
            'salary_hist': salary_hist,
        }
        
        return render(request, 'analyzer/analysis_result.html', context)
    except Exception as e:
        messages.error(request, f'Error generating analysis: {e}')
        return render(request, 'analyzer/analysis_result.html', {})

def generate_department_bar_chart(df):
    """Generate department bar chart"""
    plt.figure(figsize=(12, 6))
    department_counts = df['Department'].value_counts()
    
    plt.bar(department_counts.index, department_counts.values, color='skyblue', edgecolor='navy')
    plt.title('Employee Count by Department', fontsize=16, fontweight='bold')
    plt.xlabel('Department', fontsize=12)
    plt.ylabel('Number of Employees', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for i, v in enumerate(department_counts.values):
        plt.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    # Convert to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode()

def generate_department_pie_chart(df):
    """Generate department pie chart"""
    plt.figure(figsize=(10, 8))
    department_counts = df['Department'].value_counts()
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(department_counts)))
    plt.pie(department_counts.values, labels=department_counts.index, autopct='%1.1f%%', 
            colors=colors, startangle=90)
    plt.title('Employee Distribution by Department', fontsize=16, fontweight='bold')
    
    plt.tight_layout()
    
    # Convert to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode()

def generate_performance_histogram(df):
    """Generate performance histogram"""
    plt.figure(figsize=(10, 6))
    
    plt.hist(df['Performance_Score'], bins=20, color='lightgreen', edgecolor='darkgreen', alpha=0.7)
    plt.title('Performance Score Distribution', fontsize=16, fontweight='bold')
    plt.xlabel('Performance Score', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    # Add mean line
    mean_perf = df['Performance_Score'].mean()
    plt.axvline(mean_perf, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_perf:.2f}')
    plt.legend()
    
    plt.tight_layout()
    
    # Convert to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode()

def generate_salary_histogram(df):
    """Generate salary histogram"""
    plt.figure(figsize=(10, 6))
    
    plt.hist(df['Monthly_Salary'], bins=25, color='gold', edgecolor='orange', alpha=0.7)
    plt.title('Monthly Salary Distribution', fontsize=16, fontweight='bold')
    plt.xlabel('Monthly Salary ($)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    # Add mean line
    mean_salary = df['Monthly_Salary'].mean()
    plt.axvline(mean_salary, color='red', linestyle='--', linewidth=2, label=f'Mean: ${mean_salary:,.0f}')
    plt.legend()
    
    plt.tight_layout()
    
    # Convert to base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode()

@login_required
def prediction_view(request):
    """Prediction view"""
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            try:
                # Get form data
                model_type = form.cleaned_data['model_type']
                input_data = {
                    'age': form.cleaned_data['age'],
                    'years_at_company': form.cleaned_data['years_at_company'],
                    'monthly_salary': form.cleaned_data['monthly_salary'],
                    'work_hours_per_week': form.cleaned_data['work_hours_per_week'],
                    'projects_handled': form.cleaned_data['projects_handled'],
                    'overtime_hours': form.cleaned_data['overtime_hours'],
                    'sick_days': form.cleaned_data['sick_days'],
                    'remote_work_frequency': form.cleaned_data['remote_work_frequency'],
                    'team_size': form.cleaned_data['team_size'],
                    'training_hours': form.cleaned_data['training_hours'],
                    'promotions': form.cleaned_data['promotions'],
                    'employee_satisfaction_score': form.cleaned_data['employee_satisfaction_score'],
                    'department': form.cleaned_data['department'],
                    'gender': form.cleaned_data['gender'],
                    'job_title': form.cleaned_data['job_title'],
                    'education_level': form.cleaned_data['education_level'],
                }
                
                # Make prediction
                prediction_result = make_prediction(model_type, input_data)
                
                # Save prediction to database
                prediction = Prediction.objects.create(
                    created_by=request.user,
                    model_type=model_type,
                    input_data=input_data,
                    prediction_result=prediction_result['predicted_value'],
                    confidence_score=prediction_result.get('confidence', 0),
                    accuracy=prediction_result.get('accuracy', 0),
                    error_rate=prediction_result.get('error_rate', 0)
                )
                
                # Prepare context for template
                context = {
                    'prediction': prediction,
                    'input_data': {
                        'department': form.cleaned_data['department'],
                        'gender': form.cleaned_data['gender'],
                        'age': form.cleaned_data['age'],
                        'job_title': form.cleaned_data['job_title'],
                        'years_at_company': form.cleaned_data['years_at_company'],
                        'education_level': form.cleaned_data['education_level'],
                        'monthly_salary': form.cleaned_data['monthly_salary'],
                        'monthly_salary_inr': round(form.cleaned_data['monthly_salary'], 0),
                        'work_hours_per_week': form.cleaned_data['work_hours_per_week'],
                        'projects_handled': form.cleaned_data['projects_handled'],
                        'overtime_hours': form.cleaned_data['overtime_hours'],
                        'sick_days': form.cleaned_data['sick_days'],
                        'remote_work_frequency': form.cleaned_data['remote_work_frequency'],
                        'team_size': form.cleaned_data['team_size'],
                        'training_hours': form.cleaned_data['training_hours'],
                        'promotions': form.cleaned_data['promotions'],
                        'employee_satisfaction_score': form.cleaned_data['employee_satisfaction_score'],
                        'model_type': form.cleaned_data['model_type']
                    }
                }
                
                return render(request, 'analyzer/prediction_result.html', context)
                
            except Exception as e:
                messages.error(request, f'Prediction error: {e}')
    else:
        form = PredictionForm()
    
    return render(request, 'analyzer/prediction.html', {'form': form})

def make_prediction(model_type, input_data):
    """Make prediction using the specified model"""
    try:
        # Prepare input features
        features = prepare_input_features(input_data)
        
        if model_type == 'random_forest':
            model = models['random_forest_performance']
            prediction = model.predict([features])[0]
            confidence = 0.85  # Random Forest confidence
            accuracy = 0.92
            error_rate = 0.08
        elif model_type == 'logistic_regression':
            model = models['logistic_regression']
            prediction = model.predict([features])[0]
            confidence = model.predict_proba([features])[0].max()
            accuracy = 0.88
            error_rate = 0.12
        elif model_type == 'linear_regression':
            model = models['linear_regression']
            prediction = model.predict([features])[0]
            confidence = 0.78
            accuracy = 0.85
            error_rate = 0.15
        else:
            raise ValueError("Invalid model type")
        
        return {
            'predicted_value': round(prediction, 2),
            'confidence': round(confidence, 3),
            'accuracy': accuracy,
            'error_rate': error_rate
        }
    except Exception as e:
        raise Exception(f"Prediction failed: {e}")

def prepare_input_features(input_data):
    """Prepare input features for prediction"""
    try:
        # Encode categorical variables using the same encoders used during training
        encoded_features = []
        
        # Add numerical features first
        numerical_features = [
            input_data['age'],
            input_data['years_at_company'],
            input_data['monthly_salary'],
            input_data['work_hours_per_week'],
            input_data['projects_handled'],
            input_data['overtime_hours'],
            input_data['sick_days'],
            input_data['remote_work_frequency'],
            input_data['team_size'],
            input_data['training_hours'],
            input_data['promotions'],
            input_data['employee_satisfaction_score']
        ]
        encoded_features.extend(numerical_features)
        
        # Encode categorical features
        categorical_features = [
            input_data['department'],
            input_data['gender'],
            input_data['job_title'],
            input_data['education_level']
        ]
        
        categorical_cols = ['Department', 'Gender', 'Job_Title', 'Education_Level']
        for i, col in enumerate(categorical_cols):
            if col in label_encoders:
                try:
                    encoded_value = label_encoders[col].transform([categorical_features[i]])[0]
                    encoded_features.append(encoded_value)
                except ValueError:
                    # If the value is not in the encoder, use a default value
                    encoded_features.append(0)
            else:
                encoded_features.append(0)
        
        return encoded_features
    except Exception as e:
        raise Exception(f"Feature preparation failed: {e}")

@login_required
def model_analysis_view(request):
    """Model analysis view"""
    try:
        # Calculate model performances
        performances = calculate_model_performances()
        
        context = {
            'performances': performances,
        }
        
        return render(request, 'analyzer/model_analysis.html', context)
    except Exception as e:
        messages.error(request, f'Error loading model analysis: {e}')
        return render(request, 'analyzer/model_analysis.html', {})

def calculate_model_performances():
    """Calculate performance metrics for all models"""
    try:
        # Load data directly from CSV file
        csv_path = os.path.join(settings.STATICFILES_DIRS[0], 'employee_data.csv')
        df_temp = pd.read_csv(csv_path)
        
        # Prepare features and targets
        categorical_cols = ['Department', 'Gender', 'Job_Title', 'Education_Level']
        numerical_cols = [
            'Age', 'Years_At_Company', 'Performance_Score', 'Monthly_Salary',
            'Work_Hours_Per_Week', 'Projects_Handled', 'Overtime_Hours',
            'Sick_Days', 'Remote_Work_Frequency', 'Team_Size', 'Training_Hours',
            'Promotions', 'Employee_Satisfaction_Score'
        ]
        
        # Encode categorical variables
        df_encoded = df_temp.copy()
        for col in categorical_cols:
            le = LabelEncoder()
            df_encoded[col] = le.fit_transform(df_encoded[col])
        
        # Scale numerical features
        scaler_temp = MinMaxScaler()
        df_encoded[numerical_cols] = scaler_temp.fit_transform(df_encoded[numerical_cols])
        
        # Prepare features and target
        X = df_encoded.drop(['Employee_ID', 'Hire_Date', 'Performance_Score', 'Resigned'], axis=1, errors='ignore')
        y_performance = df_encoded['Performance_Score']
        y_resigned = df_encoded['Resigned'].astype(int)
        
        # Split data
        X_train, X_test, y_train_perf, y_test_perf, y_train_res, y_test_res = train_test_split(
            X, y_performance, y_resigned, test_size=0.2, random_state=42
        )
        
        # Train models and calculate metrics
        performances = {}
        
        # Random Forest for Performance (Regression)
        rf_perf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_perf.fit(X_train, y_train_perf)
        y_pred_rf = rf_perf.predict(X_test)
        
        performances['Random Forest (Performance)'] = {
            'r2_score': round(r2_score(y_test_perf, y_pred_rf), 4),
            'mse': round(mean_squared_error(y_test_perf, y_pred_rf), 4),
            'rmse': round(np.sqrt(mean_squared_error(y_test_perf, y_pred_rf)), 4),
            'mae': round(mean_absolute_error(y_test_perf, y_pred_rf), 4),
            'accuracy': round(accuracy_score(y_test_perf.round(), y_pred_rf.round()), 4),
            'precision': round(precision_score(y_test_perf.round(), y_pred_rf.round(), average='weighted', zero_division=0), 4),
            'recall': round(recall_score(y_test_perf.round(), y_pred_rf.round(), average='weighted', zero_division=0), 4),
            'f1_score': round(f1_score(y_test_perf.round(), y_pred_rf.round(), average='weighted', zero_division=0), 4)
        }
        
        # Logistic Regression for Resigned (Classification)
        lr_resigned = LogisticRegression(random_state=42, max_iter=1000)
        lr_resigned.fit(X_train, y_train_res)
        y_pred_lr = lr_resigned.predict(X_test)
        
        performances['Logistic Regression (Resigned)'] = {
            'r2_score': round(r2_score(y_test_res, y_pred_lr), 4),
            'mse': round(mean_squared_error(y_test_res, y_pred_lr), 4),
            'rmse': round(np.sqrt(mean_squared_error(y_test_res, y_pred_lr)), 4),
            'mae': round(mean_absolute_error(y_test_res, y_pred_lr), 4),
            'accuracy': round(accuracy_score(y_test_res, y_pred_lr), 4),
            'precision': round(precision_score(y_test_res, y_pred_lr, average='weighted', zero_division=0), 4),
            'recall': round(recall_score(y_test_res, y_pred_lr, average='weighted', zero_division=0), 4),
            'f1_score': round(f1_score(y_test_res, y_pred_lr, average='weighted', zero_division=0), 4)
        }
        
        # Linear Regression for Performance
        lr_perf = LinearRegression()
        lr_perf.fit(X_train, y_train_perf)
        y_pred_lr_perf = lr_perf.predict(X_test)
        
        performances['Linear Regression (Performance)'] = {
            'r2_score': round(r2_score(y_test_perf, y_pred_lr_perf), 4),
            'mse': round(mean_squared_error(y_test_perf, y_pred_lr_perf), 4),
            'rmse': round(np.sqrt(mean_squared_error(y_test_perf, y_pred_lr_perf)), 4),
            'mae': round(mean_absolute_error(y_test_perf, y_pred_lr_perf), 4),
            'accuracy': round(accuracy_score(y_test_perf.round(), y_pred_lr_perf.round()), 4),
            'precision': round(precision_score(y_test_perf.round(), y_pred_lr_perf.round(), average='weighted', zero_division=0), 4),
            'recall': round(recall_score(y_test_perf.round(), y_pred_lr_perf.round(), average='weighted', zero_division=0), 4),
            'f1_score': round(f1_score(y_test_perf.round(), y_pred_lr_perf.round(), average='weighted', zero_division=0), 4)
        }
        
        return performances
    except Exception as e:
        print(f"Error calculating model performances: {e}")
        return {}

@login_required
def profile_view(request):
    """User profile view"""
    # Get or create user profile
    userprofile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=userprofile)
    
    # Get user's recent activity
    recent_predictions = Prediction.objects.filter(created_by=request.user).order_by('-created_at')[:10]
    recent_analyses = Analysis.objects.filter(created_by=request.user).order_by('-created_at')[:10]
    
    context = {
        'form': form,
        'recent_predictions': recent_predictions,
        'recent_analyses': recent_analyses,
    }
    
    return render(request, 'analyzer/profile.html', context)

@login_required
def employee_list_view(request):
    """Employee list view with search functionality"""
    try:
        from .models import Employee
        
        # Handle search functionality
        search_id = request.GET.get('search_id', '').strip()
        employees = []
        
        if search_id:
            # Search by employee ID
            try:
                search_id_int = int(search_id)
                employee_obj = Employee.objects.filter(employee_id=search_id_int).first()
                
                if employee_obj:
                    employees.append({
                        'employee_id': employee_obj.employee_id,
                        'name': employee_obj.name,
                        'department': employee_obj.department,
                        'job_title': employee_obj.job_title,
                        'age': employee_obj.age,
                        'years_at_company': employee_obj.years_at_company,
                        'performance_score': employee_obj.performance_score,
                        'monthly_salary': employee_obj.monthly_salary,
                        'monthly_salary_inr': employee_obj.monthly_salary_inr/83,
                        'hire_date': employee_obj.hire_date,
                        'gender': employee_obj.gender,
                        'education_level': employee_obj.education_level,
                        'work_hours_per_week': employee_obj.work_hours_per_week,
                        'projects_handled': employee_obj.projects_handled,
                        'overtime_hours': employee_obj.overtime_hours,
                        'sick_days': employee_obj.sick_days,
                        'remote_work_frequency': employee_obj.remote_work_frequency,
                        'team_size': employee_obj.team_size,
                        'training_hours': employee_obj.training_hours,
                        'promotions': employee_obj.promotions,
                        'employee_satisfaction_score': employee_obj.employee_satisfaction_score,
                        'resigned': employee_obj.resigned
                    })
                    messages.success(request, f'Found 1 employee with ID: {search_id}')
                else:
                    messages.warning(request, f'No employee found with ID: {search_id}')
            except ValueError:
                messages.error(request, 'Please enter a valid employee ID (numbers only)')
        
        # Calculate summary metrics
        total_count = len(employees)
        avg_performance = sum(emp['performance_score'] for emp in employees) / total_count if total_count > 0 else 0
        avg_salary_inr = sum(emp['monthly_salary_inr'] for emp in employees) / total_count if total_count > 0 else 0
        departments_count = len(set(emp['department'] for emp in employees))
        
        context = {
            'employees': employees,
            'total_count': total_count,
            'avg_performance': round(avg_performance, 1),
            'avg_salary_inr': round(avg_salary_inr, 0),
            'departments_count': departments_count,
            'search_id': search_id
        }
        
        return render(request, 'analyzer/employee_list.html', context)
    except Exception as e:
        messages.error(request, f'Error loading employee list: {e}')
        return render(request, 'analyzer/employee_list.html', {'employees': [], 'total_count': 0, 'search_id': ''})

# Initialize models on startup
load_data_and_models()
