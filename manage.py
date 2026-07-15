#!/usr/bin/env python
"""
ESPPA root-level manage.py — convenience wrapper.

Auto-detects the virtual environment, activates it, changes to
src/ directory, and delegates to the real manage.py at src/manage.py.

Usage (from project root):
    python manage.py runserver
    python manage.py migrate
    python manage.py test
"""
import os
import sys
import subprocess
import platform


def _find_venv_python(project_root: str) -> str:
    """Locate the venv Python interpreter relative to the project root."""
    if platform.system() == 'Windows':
        candidates = [
            os.path.join(project_root, 'venv', 'Scripts', 'python.exe'),
        ]
    else:
        candidates = [
            os.path.join(project_root, 'venv', 'bin', 'python'),
        ]

    for path in candidates:
        abspath = os.path.abspath(path)
        if os.path.exists(abspath):
            return abspath

    return ''  # not found


def main() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, 'src')
    manage_py = os.path.join(src_dir, 'manage.py')

    if not os.path.exists(manage_py):
        print(f"Error: Could not find {manage_py}")
        print("Make sure you're running from the ESPPA project root.")
        sys.exit(1)

    # ── Pick the right Python interpreter ──────────────────────────────
    venv_python = _find_venv_python(base_dir)
    python_exe = venv_python if venv_python else sys.executable

    if not venv_python:
        print(
            "Warning: Virtual environment not found at venv/Scripts/python.exe\n"
            "         Falling back to system Python — make sure Django is installed.\n"
            "         Recommended: activate the venv first or use run.bat (Windows).\n"
        )

    # ── Delegate to src/manage.py ──────────────────────────────────────
    os.chdir(src_dir)
    cmd = [python_exe, 'manage.py'] + sys.argv[1:]

    try:
        proc = subprocess.run(cmd)
        sys.exit(proc.returncode)
    except FileNotFoundError:
        print(f"Error: Python interpreter not found: {python_exe}")
        print("Make sure the virtual environment exists at 'venv/' and is not corrupted.")
        sys.exit(1)


if __name__ == '__main__':
    main()
