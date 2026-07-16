#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks with environment-aware settings."""
    env = os.environ.get('DJANGO_ENV', 'dev')
    settings_module = f'core.settings.{env}'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable?\n\n"
            f"  TIP: Run from the PROJECT ROOT instead:\n"
            f"    cd {project_root}\n"
            f"    python manage.py runserver\n\n"
            f"  The root manage.py auto-activates the virtual environment.\n"
            f"  Or double-click run.bat for one-click launch."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
