# ESPPA — Employee Skill & Project Performance Analyzer

> **AI-powered employee performance analytics with Django, Machine Learning, and a full REST API.**

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-green)](https://djangoproject.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

**📖 Full documentation:** [`docs/README.md`](docs/README.md)

**🚀 Live demo (API docs):** `/api/docs/` after running the server

---

### Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate     # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the project
python manage.py migrate
python manage.py import_employees --clear
python manage.py runserver
# → http://127.0.0.1:8000/
# → API docs: http://127.0.0.1:8000/api/docs/
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 6.0, Django REST Framework |
| ML Models | Random Forest, XGBoost, Neural Network (MLP) |
| Frontend | Tailwind CSS (Apple Design System), Bootstrap 5 |
| API | RESTful with Swagger/OpenAPI docs |
| Deployment | Docker, Gunicorn |

---

*Built for the ESPPA project — Employee Skill & Project Performance Analyzer*
