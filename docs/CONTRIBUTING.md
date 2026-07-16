# Contributing to ESPPA

Thank you for considering contributing to the Employee Skill & Project Performance Analyzer!

## Development Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/ESPPA.git
cd ESPPA

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set up the database
python src/manage.py migrate

# Import sample employee data
python src/manage.py import_employees --clear
```

## Code Quality

- **Formatting**: Black (`black src/`)
- **Imports**: isort (`isort src/`)
- **Linting**: flake8 (`flake8 src/`)
- **Type hints**: All functions must have type annotations
- **Tests**: Run `python src/manage.py test esppa --verbosity=2`

## Pull Request Process

1. Create a feature branch from `main`
2. Write tests for your changes
3. Ensure all tests pass
4. Update documentation if needed
5. Submit a PR with a clear description

## Principles

- Single Responsibility: each file/class does one thing
- DRY: no duplicated logic
- Fail Fast: validate inputs at boundaries
- Data-Driven: use configuration over conditionals
