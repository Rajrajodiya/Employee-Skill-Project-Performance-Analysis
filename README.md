# ESPPA — Employee Skill & Project Performance Analyzer

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-green?logo=django&logoColor=white)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.14-red?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-108_✓-brightgreen)](src/apps/esppa/tests/)
[![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000)](https://github.com/psf/black)
[![ML](https://img.shields.io/badge/ML-RF_•_XGBoost_•_MLP-orange)](src/apps/esppa/services/ml_service.py)

**AI-powered employee performance analytics — predict, analyze, and visualize workforce metrics.**

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **ML Predictions** | Random Forest, XGBoost & Neural Network models with 5-fold cross-validation |
| 📊 **Analytics Dashboard** | Department KPIs, performance trends, salary distribution, attrition rates |
| 📈 **Interactive Charts** | Bar, pie, histogram charts generated with matplotlib |
| 🔌 **REST API** | Full CRUD with Swagger/OpenAPI docs, rate limiting, versioning |
| 👤 **User Management** | Registration, profiles, role-based access control |
| 📱 **Responsive Design** | Apple-inspired UI with Tailwind CSS |
| 🐳 **Docker Ready** | Containerized deployment with Gunicorn |
| 🚀 **Vercel Deploy** | Serverless-ready with PostgreSQL (Supabase) |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Vercel / Docker                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │
│  │  HTML     │  │  REST     │  │  Swagger/OpenAPI     │   │
│  │  Views    │  │  API      │  │  Docs                │   │
│  └────┬─────┘  └────┬─────┘  └──────────────────────┘   │
│       └──────┬──────┘                                     │
│              ▼                                            │
│  ┌──────────────────────────────────────────────────┐    │
│  │              Service Layer (core.deps)            │    │
│  │  DataService  │  MLService  │  EmployeeService   │    │
│  │  ChartService │  Config     │                     │    │
│  └──────────────────────┬───────────────────────────┘    │
│                         ▼                                │
│  ┌──────────────────────────────────────────────────┐    │
│  │  Django Models & PostgreSQL / SQLite              │    │
│  └──────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

```bash
# 1. Clone and enter the project
git clone https://github.com/YOUR_USERNAME/ESPPA.git
cd ESPPA

# 2. Create virtual environment
python -m venv venv
# Windows:
source venv/Scripts/activate
# macOS/Linux:
# source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up and run
cp .env.example .env
python src/manage.py migrate
python src/manage.py import_employees --clear
python src/manage.py runserver

# → Open http://127.0.0.1:8000/
```

## 🖥️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 6.0, Django REST Framework 3.14 |
| **ML Models** | Random Forest, XGBoost, Neural Network (MLP) |
| **Data** | Pandas, NumPy, scikit-learn |
| **Frontend** | Tailwind CSS, Bootstrap 5, Cotton components |
| **API Docs** | Swagger UI, ReDoc via drf-spectacular |
| **Database** | SQLite (dev), PostgreSQL via Supabase (prod) |
| **Container** | Docker, Gunicorn |
| **DevOps** | GitHub Actions CI/CD, Vercel |
| **Data Versioning** | DVC (Data Version Control) |

## 📖 Documentation

- **[Full Documentation](docs/README.md)** — Detailed setup, API reference, ML model details
- **[API Docs](http://127.0.0.1:8000/api/docs/)** — Interactive Swagger UI (run locally)
- **[Design System](docs/DESIGN.md)** — Apple-inspired UI/UX guidelines
- **[Changelog](CHANGELOG.md)** — Version history
- **[Contributing](CONTRIBUTING.md)** — How to contribute

## 🧪 Test Suite

```bash
# Run all 108 tests
python src/manage.py test esppa --verbosity=2

# Or using pytest
cd src && pytest apps/esppa/tests/ -v
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/` | List users |
| GET | `/api/employees/` | List employees |
| GET | `/api/employees/search?id=1001` | Search employee |
| POST | `/api/predictions/predict/` | Make ML prediction |
| GET | `/api/dashboard/metrics/` | Dashboard KPIs |
| GET | `/api/models/compare/` | Compare ML models |
| GET | `/api/docs/` | Swagger UI |

## 🐳 Docker

```bash
docker compose build
docker compose up -d
# → http://localhost:8000/
```

## 🚀 Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

1. Fork this repo
2. Connect to Vercel
3. Set environment variables:
   - `SECRET_KEY` — Django secret key
   - `DATABASE_URL` — Supabase PostgreSQL connection string
   - `ALLOWED_HOSTS` — your Vercel domain
4. Deploy!

## 📊 ML Models

| Model | R² Score | RMSE | Best For |
|-------|----------|------|----------|
| **Random Forest** | 0.92 | 0.08 | General performance prediction |
| **XGBoost** | 0.94 | 0.06 | Highest accuracy |
| **Neural Network** | 0.88 | 0.12 | Complex pattern detection |

## 📝 License

This project is [MIT licensed](LICENSE).

---

<div align="center">
⭐ Star this repo if you find it useful!
</div>
