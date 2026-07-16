# ESPPA — Employee Skill & Project Performance Analyzer

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![Django](https://img.shields.io/badge/Django-6.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![CI](https://github.com/Rajrajodiya/Employee-Skill-Project-Performance-Analysis/actions/workflows/ci.yml/badge.svg)

A production-grade Django web application for analyzing employee performance, productivity, and making AI-powered predictions using machine learning (Random Forest, XGBoost, Neural Networks).

---

## ✨ Features

### 📊 Analytics Dashboard
- **Real-time KPIs**: Employee count, average performance, salary, resignation rate
- **Department Analysis**: Performance and salary comparison across departments
- **Performance Distribution**: High/medium/low performer breakdown
- **Interactive Charts**: Matplotlib-generated bar charts, histograms, pie charts

### 🤖 AI Predictions
- **3 ML Models**: Random Forest, XGBoost, Neural Network (MLP)
- **Performance Prediction**: Predict employee performance scores from 16 features
- **Model Comparison**: R², MSE, RMSE, MAE side-by-side with Chart.js visualizations
- **Feature Importance**: Understand which factors most influence performance

### 👥 Employee Management
- **Employee Search**: Look up any employee by ID with full details
- **Performance Tracking**: Monitor individual metrics and satisfaction scores
- **Quick Actions**: Print reports, make predictions directly from employee view

### 🔐 User System
- **Secure Registration/Login**: Django auth with session management
- **User Profiles**: Department, role, phone, profile picture
- **Activity History**: Track predictions and analyses per user

### 🛡️ REST API
- **14 Endpoints**: Full CRUD + custom predict/search/analyze actions
- **Swagger Docs**: Interactive API documentation at `/api/docs/`
- **Rate Limited**: 100 requests/minute per user
- **Versioned**: Namespace-based API versioning

---

## 🏗️ Architecture

```
ESPPA/
├── src/                         # ← All Django source code
│   ├── config/                  # Split settings (base/dev/prod)
│   │   ├── base.py              #   Shared settings (DB, auth, DRF, logging)
│   │   ├── dev.py               #   Development overrides (DEBUG=True)
│   │   ├── prod.py              #   Production overrides (PostgreSQL, HTTPS)
│   │   ├── urls.py              #   Root URL routing
│   │   ├── wsgi.py              #   WSGI for Gunicorn
│   │   └── asgi.py              #   ASGI for Uvicorn
│   ├── esppa/                   # Main Django application
│   │   ├── models.py            #   Employee, Analysis, Prediction, UserProfile
│   │   ├── views.py             #   Thin controller views
│   │   ├── urls.py              #   App URL routing
│   │   ├── forms.py             #   Django forms with validation
│   │   ├── admin.py             #   Admin configuration with fieldsets
│   │   ├── serializers.py       #   DRF serializers (14+ serializers)
│   │   ├── api_views.py         #   REST API ViewSets + custom actions
│   │   ├── api_urls.py          #   API routing via DRF DefaultRouter
│   │   ├── services/            #   Business logic layer
│   │   │   ├── config.py        #     Centralized constants/thresholds
│   │   │   ├── data_service.py  #     CSV loading, caching, preprocessing
│   │   │   ├── ml_service.py    #     ML training, prediction, evaluation
│   │   │   ├── chart_service.py #     Matplotlib chart generation
│   │   │   └── employee_service.py # Dashboard KPIs
│   │   ├── management/          # Custom Django commands
│   │   │   └── import_employees.py  # Bulk CSV import
│   │   └── models/              # Persisted ML model pickles
│   ├── templates/               # HTML templates (Apple design)
│   │   ├── base.html            #   Base with Tailwind + Apple CSS
│   │   └── registration/        #   Login template
│   ├── esppa/templates/esppa/   # App templates (dashboard, analysis, etc.)
│   └── manage.py                # Django CLI with DJANGO_ENV support
├── docs/                        # Documentation
│   ├── README.md                #   This file
│   ├── DESIGN.md                #   Apple design system spec
│   └── *.pptx                   #   Project presentation
├── static/                      # Static assets
│   ├── employee_data.csv        #   Sample employee dataset
│   └── style.css                #   Custom styles
├── manage.py                    # Root wrapper (auto-detects venv)
├── requirements.txt             # Single master dependency file
├── Dockerfile                   # Production Docker build
├── Makefile                     # Common dev commands
├── pyproject.toml               # Python project metadata
├── run.bat                      # Windows one-click launcher
└── .github/workflows/ci.yml     # GitHub Actions CI/CD
```

### Design Pattern: Service Layer

Views are **thin controllers** — they never import pandas, sklearn, or matplotlib directly. All business logic lives in the `services/` package:

```
View (request/response)
  ↓  delegates to
Service (business logic)
  ↓  uses
DataService (CSV loading, preprocessing)
MLService (model training, prediction)
ChartService (matplotlib chart generation)
EmployeeService (dashboard KPI computation)
```

This separation ensures:
- **Testability**: Services can be unit-tested without Django
- **Maintainability**: Change ML logic in one place
- **Readability**: Views show the "what", services show the "how"

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- pip

### Setup

```bash
# 1. Clone & enter
git clone https://github.com/Rajrajodiya/Employee-Skill-Project-Performance-Analysis.git
cd ESPPA

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Database migrations
python manage.py migrate

# 6. Import sample data
python manage.py import_employees --clear

# 7. Create admin (optional)
python manage.py createsuperuser

# 8. Run development server
python manage.py runserver
```

### Access

| Page | URL |
|------|-----|
| App | http://127.0.0.1:8000 |
| Admin | http://127.0.0.1:8000/admin |
| API Docs | http://127.0.0.1:8000/api/docs/ |
| API (ReDoc) | http://127.0.0.1:8000/api/redoc/ |

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src --cov-report=term-missing

# Specific test file
pytest src/esppa/tests/
```

The test suite covers:
- **Model tests**: Employee creation, string representation, ordering, uniqueness
- **View tests**: Dashboard response, analysis rendering, prediction flow
- **Form tests**: Registration validation, prediction form validation
- **API tests**: Employee endpoints, prediction endpoint, authentication
- **Service tests**: DataService loading, MLService training/prediction

---

## 🛡️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | List users (current user only) |
| GET/PUT/PATCH | `/api/profiles` | User profile CRUD |
| GET | `/api/employees` | List all employees |
| GET | `/api/employees/{id}` | Employee detail |
| GET | `/api/employees/search?id=` | Search by employee ID |
| GET | `/api/employees/department_summary` | Department-wise counts |
| GET/POST | `/api/analyses` | Analysis records |
| POST | `/api/predictions/predict` | Run ML prediction |
| GET | `/api/dashboard/metrics` | Dashboard KPIs |
| GET | `/api/dashboard/department_data` | Department analytics |
| GET | `/api/models/compare` | Model performance comparison |
| GET | `/api/models/feature_importance` | Feature importance |

All endpoints require authentication (session or DRF login).

---

## 🤖 Machine Learning

### Models

| Model | Type | Use Case | Hyperparameters |
|-------|------|----------|-----------------|
| Random Forest | Ensemble Regression | Performance prediction | n_estimators=100, max_depth=10 |
| XGBoost | Gradient Boosting | High-accuracy prediction | n_estimators=100, lr=0.1 |
| Neural Network (MLP) | Deep Learning | Complex patterns | (64, 32) hidden layers, early stopping |

### Evaluation Metrics
- **R² Score**: Proportion of variance explained
- **MSE**: Mean squared error
- **RMSE**: Root mean squared error (interpretable scale)
- **MAE**: Mean absolute error

Models are persisted as pickle files and loaded on first request. Training happens automatically if no persisted model is found.

---

## 🔧 Configuration

### Environment Variables (`.env`)

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_ENV=dev
```

### Makefile Commands

```bash
make install      # Install dependencies
make migrate      # Run database migrations
make run          # Start dev server
make test         # Run test suite
make seed         # Import employee CSV data
make superuser    # Create admin user
make check        # Django system checks (deploy)
make clean        # Clean cache files
```

---

## 🐳 Docker

```bash
# Build
docker build -t esppa .

# Run
docker run -e DJANGO_SETTINGS_MODULE=config.prod -p 8000:8000 esppa
```

---

## 📈 Performance

- **CSV Caching**: Employee data loaded once per file modification (not per request)
- **Model Persistence**: ML models trained once, loaded from disk
- **Database Indexes**: Indexed on employee_id, department, performance_score, resigned
- **API Throttling**: Rate-limited to protect against abuse
- **Static Assets**: Served via CDN (Tailwind, Bootstrap, Chart.js, Font Awesome)

---

## 🎨 Design System

The UI follows Apple's web design language (see `docs/DESIGN.md` for full spec):

- **Typography**: SF Pro Display/Text, 17px body copy, negative letter-spacing
- **Single Accent**: Action Blue (#0066cc) for all interactive elements
- **Cards**: 18px radius, thin hairline borders, no shadows on chrome
- **Buttons**: Pill-shaped (9999px radius), with `transform: scale(0.95)` active state
- **Colors**: Near-black (#1d1d1f) text, parchment (#f5f5f7) background, pure black nav
- **No gradients**: Atmosphere comes from data visualization, not decorative CSS

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request
