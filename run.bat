@echo off
REM ═══════════════════════════════════════════════════════════════
REM  ESPPA Development Server Launcher (Windows)
REM  Activates the virtual environment and starts the dev server.
REM ═══════════════════════════════════════════════════════════════

cd /d "%~dp0"

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo.
    echo [ERROR] Virtual environment not found at venv\Scripts\activate.bat
    echo         Run: py -m venv venv
    echo         Then: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║        ESPPA - Development Server Starting...            ║
echo ╠══════════════════════════════════════════════════════════╣
echo ║  URL:   http://127.0.0.1:8000                           ║
echo ║  API:   http://127.0.0.1:8000/api/docs/                 ║
echo ║  Admin: http://127.0.0.1:8000/admin/                    ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

python src/manage.py runserver %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Server exited with code %ERRORLEVEL%
    pause
)
