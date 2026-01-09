@echo off
REM Start Celery worker for background task processing
REM Make sure Redis is running before starting Celery

echo Starting Celery worker...
echo.

cd /d %~dp0
call venv\Scripts\activate.bat
celery -A legalease worker --loglevel=info --pool=solo

pause

