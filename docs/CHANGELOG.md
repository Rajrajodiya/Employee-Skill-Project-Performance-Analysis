# Changelog

All notable changes to the ESPPA project will be documented in this file.

## [1.0.0] - 2026-07-16

### Added
- Django 6.0 project with environment-aware settings (dev/prod)
- REST API with DRF ViewSets, Swagger/OpenAPI docs, rate limiting
- ML Service with Random Forest, XGBoost, and Neural Network models
- 5-fold cross-validation for robust model evaluation
- DVC (Data Version Control) for dataset and ML model versioning
- Supabase PostgreSQL database configuration
- 108 unit tests across models, forms, views, API, and services
- CI/CD pipeline with GitHub Actions (lint, test, security check)
- MIT License, Contributing Guide, and Code of Conduct

### Changed
- Restructured to FastAPI-inspired architecture: `core/` + `apps/` layout
- Split 5 monolithic files into 30 focused modules (SRP)
- Applied Apple Design System to all templates
- Replaced SQLite logging with single `server.log` rotation
- Data-driven form validation and widget configuration

### Fixed
- Numerical features now properly MinMaxScaled during prediction
- Model analysis uses persisted models instead of re-training
- Broad `except Exception` replaced with specific exception types
- CSV data cached with file-mtime invalidation
