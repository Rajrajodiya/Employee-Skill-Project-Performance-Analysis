# ESPPA - Employee Skill & Project Performance Analyzer

A comprehensive Django web application for analyzing employee performance, productivity, and making AI-powered predictions using machine learning models.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Features

### 📊 Analytics Dashboard
- **Real-time Statistics**: Employee count, average performance, salary, and resignation rates
- **Department Analysis**: Performance comparison across departments
- **Interactive Charts**: Bar charts, histograms, pie charts, box plots, heatmaps, and scatter plots
- **Data Visualization**: Beautiful charts using Matplotlib, Seaborn, and Chart.js

### 🤖 AI Predictions
- **Multiple ML Models**: Random Forest, Logistic Regression, and Linear Regression
- **Performance Prediction**: Predict employee performance scores
- **Model Comparison**: Compare accuracy, precision, recall, and F1 scores
- **Feature Importance**: Analyze which factors most influence performance

### 👥 Employee Management
- **Employee Directory**: Complete employee listing with filtering and sorting
- **Detailed Profiles**: Comprehensive employee information and metrics
- **Performance Tracking**: Monitor individual and team performance

### 🔐 User Authentication
- **Secure Login/Registration**: User authentication with profile management
- **Role-based Access**: Different access levels for different user types
- **Session Management**: Secure session handling with automatic logout

## 🛠️ Technology Stack

### Backend
- **Django 4.2.7**: Web framework
- **Python 3.8+**: Programming language
- **SQLite**: Database (can be easily changed to PostgreSQL/MySQL)

### Machine Learning
- **Scikit-learn**: ML algorithms and preprocessing
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **SciPy**: Scientific computing
- **Matplotlib & Seaborn**: Data visualization

### Frontend
- **Bootstrap 5**: UI framework
- **Chart.js**: Interactive charts
- **Font Awesome**: Icons
- **Custom CSS/JS**: Enhanced styling and functionality

### Additional Libraries
- **Django Crispy Forms**: Form styling
- **Django Widget Tweaks**: Enhanced form widgets
- **Pillow**: Image processing
- **Jupyter**: Interactive analysis notebooks

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)
- Virtual environment (recommended)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Employee-Productivity-Analysis-main
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 5. Load Sample Data
```bash
# Import employee data from CSV
python manage.py import_employees --clear
```

### 6. Create Admin User (Optional)
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

### 8. Access the Application
- Open your browser and navigate to `http://127.0.0.1:8000/`
- Register a new account or use superuser credentials
- Explore the dashboard and features

## 📁 Project Structure

```
Employee-Productivity-Analysis-main/
├── ESPPA/                          # Django project settings
│   ├── __init__.py
│   ├── settings.py                 # Project configuration
│   ├── urls.py                     # Main URL routing
│   ├── wsgi.py                     # WSGI configuration
│   └── asgi.py                     # ASGI configuration
├── analyzer/                       # Main Django application
│   ├── __init__.py
│   ├── admin.py                    # Admin interface configuration
│   ├── apps.py                     # App configuration
│   ├── forms.py                    # Form definitions
│   ├── models.py                   # Database models
│   ├── urls.py                     # App URL routing
│   ├── views.py                    # View functions
│   ├── tests.py                    # Unit tests
│   ├── management/                 # Custom management commands
│   │   └── commands/
│   │       └── import_employees.py # Employee data import command
│   ├── migrations/                 # Database migrations
│   └── templatetags/               # Custom template tags
├── templates/                      # HTML templates
│   ├── base.html                   # Base template
│   ├── registration/               # Authentication templates
│   │   └── login.html
│   └── analyzer/                   # App-specific templates
│       ├── dashboard.html
│       ├── analysis.html
│       ├── prediction.html
│       ├── employee_list.html
│       └── profile.html
├── static/                         # Static files
│   ├── employee_data.csv           # Sample employee data
│   └── style.css                   # Custom CSS
├── media/                          # User-uploaded files
│   └── profile_pics/               # Profile pictures
├── models/                         # Trained ML models
│   ├── employee_productivity_model.pkl
│   ├── linear_regression.pkl
│   ├── logistic_regression.pkl
│   └── random_forest_performance.pkl
├── Analysis.ipynb                  # Jupyter notebook for analysis
├── db.sqlite3                      # SQLite database
├── manage.py                       # Django management script
├── requirements.txt                # Python dependencies
└── README.md                       # Project documentation
```

## 🎯 Usage Guide

### Dashboard Overview
The main dashboard provides:
- Key performance indicators (KPIs)
- Quick access to analysis and prediction tools
- Recent activity overview
- Navigation to all major features

### Employee Analysis
1. **Select Analysis Type**: Choose from department, performance, salary, overtime, or satisfaction analysis
2. **Choose Visualization**: Select chart type (bar, pie, histogram, box plot, heatmap, scatter plot)
3. **Generate Insights**: View interactive charts and statistical summaries
4. **Export Results**: Save charts and reports for presentations

### ML Predictions
1. **Choose Model**: Select from Random Forest, Logistic Regression, or Linear Regression
2. **Input Data**: Enter employee information through the prediction form
3. **Get Results**: Receive performance predictions with confidence scores
4. **Model Metrics**: View accuracy, precision, recall, and F1 scores

### Employee Management
- **Browse Directory**: Filter and sort employees by various criteria
- **View Profiles**: Access detailed employee information and metrics
- **Track Performance**: Monitor individual and team performance trends

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Database Configuration
The default setup uses SQLite for development. For production, consider:

**PostgreSQL**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'esppa_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**MySQL**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'esppa_db',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## 📊 Data Schema

### Employee Model
The core employee model includes:

- **Personal Info**: ID, name, age, gender, education level
- **Work Details**: Department, job title, hire date, years at company
- **Performance Metrics**: Performance score, monthly salary, work hours
- **Project Data**: Projects handled, overtime hours, team size
- **Wellness**: Sick days, remote work frequency, training hours
- **Career**: Promotions, satisfaction score, resignation status

### Analysis Model
Stores analysis results with:
- Analysis type and chart type
- Generated chart data (JSON format)
- User association and timestamps

### Prediction Model
Tracks ML predictions with:
- Model type and input parameters
- Prediction results and confidence scores
- Performance metrics and error rates

## 🤖 Machine Learning Models

### Random Forest Regressor
- **Purpose**: Primary performance prediction model
- **Advantages**: Handles non-linear relationships, provides feature importance
- **Use Case**: Complex pattern recognition in employee data

### Logistic Regression
- **Purpose**: Binary classification (e.g., resignation prediction)
- **Advantages**: Interpretable results, probability outputs
- **Use Case**: Risk assessment and categorical predictions

### Linear Regression
- **Purpose**: Continuous value prediction
- **Advantages**: Simple, fast, highly interpretable
- **Use Case**: Salary estimation and linear trend analysis

### Model Training Process
1. **Data Preprocessing**: Label encoding, scaling, feature selection
2. **Train-Test Split**: 80/20 split for model validation
3. **Model Training**: Automated training with hyperparameter optimization
4. **Evaluation**: Comprehensive metrics including accuracy, precision, recall
5. **Model Persistence**: Serialized models saved for production use

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test analyzer

# Run with verbose output
python manage.py test --verbosity=2
```

### Test Coverage
The test suite covers:
- Model functionality and validation
- View responses and permissions
- Form validation and processing
- Machine learning model integration

## 📈 Performance Optimization

### Database Optimization
- **Indexing**: Add indexes for frequently queried fields
- **Query Optimization**: Use select_related() and prefetch_related()
- **Pagination**: Implement pagination for large datasets

### ML Model Optimization
- **Model Caching**: Cache trained models to avoid retraining
- **Batch Processing**: Process multiple predictions efficiently
- **Feature Engineering**: Optimize feature selection for better performance

### Frontend Optimization
- **Static File Compression**: Enable gzip compression
- **CDN Integration**: Use CDN for static assets
- **Lazy Loading**: Implement lazy loading for charts and images

## 🔒 Security Features

### Authentication & Authorization
- Secure password hashing with Django's built-in system
- Session-based authentication with configurable timeouts
- CSRF protection on all forms
- User role management and permissions

### Data Protection
- Input validation and sanitization
- SQL injection prevention through ORM
- XSS protection with Django's template system
- Secure file upload handling

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Configure production database
- [ ] Set up static file serving (WhiteNoise or CDN)
- [ ] Configure HTTPS with SSL certificates
- [ ] Set up proper logging
- [ ] Configure email backend
- [ ] Set secure environment variables

### Deployment Options

#### Heroku
```bash
# Install Heroku CLI and login
heroku create your-app-name
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py import_employees --clear
```

#### Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

#### Traditional VPS
1. Set up virtual environment
2. Configure web server (Nginx/Apache)
3. Set up WSGI server (Gunicorn/uWSGI)
4. Configure database
5. Set up SSL certificates

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the Repository**
2. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make Changes**
   - Follow PEP 8 style guidelines
   - Add tests for new functionality
   - Update documentation as needed
4. **Commit Changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
5. **Push to Branch**
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open Pull Request**

### Development Guidelines
- Write clear, documented code
- Include unit tests for new features
- Follow Django best practices
- Update README for significant changes

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Django Community**: For the excellent web framework
- **Scikit-learn Team**: For comprehensive ML tools
- **Bootstrap Team**: For responsive UI components
- **Contributors**: All developers who contributed to this project

## 📞 Support & Contact

### Getting Help
- **Issues**: Report bugs and request features on GitHub Issues
- **Documentation**: Check this README and code comments
- **Community**: Join discussions in the project repository

### Maintainers
- **Project Lead**: Rajkumar Rajodiya
- **Contributors**: See GitHub contributors page

## 🔄 Version History

### v1.0.0 (Current)
- ✅ Complete Django web application
- ✅ Multiple ML models for predictions
- ✅ Interactive analytics dashboard
- ✅ User authentication system
- ✅ Employee management features
- ✅ Comprehensive data visualization

### Planned Features (v1.1.0)
- 🔄 Advanced ML models (XGBoost, Neural Networks)
- 🔄 Real-time data streaming
- 🔄 RESTful API endpoints
- 🔄 Mobile app integration
- 🔄 Advanced reporting features
- 🔄 Performance monitoring dashboard

---

## 🚀 Quick Commands Reference

```bash
# Setup
python -m venv venv && source venv/bin/activate  # Linux/Mac
python -m venv venv && venv\Scripts\activate     # Windows
pip install -r requirements.txt

# Database
python manage.py makemigrations
python manage.py migrate
python manage.py import_employees --clear

# Development
python manage.py runserver
python manage.py test
python manage.py createsuperuser

# Analysis
jupyter notebook Analysis.ipynb
```

**ESPPA** - Empowering organizations with data-driven employee insights through advanced analytics and machine learning.
