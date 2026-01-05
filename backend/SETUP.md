# LegalEase Backend Setup Guide

This guide will help you set up the Django backend for the LegalEase project.

## Prerequisites

1. **Python 3.8+** installed on your system
2. **PostgreSQL** installed and running
3. **Virtual environment** (we'll create this)

## Step 1: Create and Activate Virtual Environment

If you haven't already, activate the virtual environment:

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your command prompt when activated.

## Step 2: Install Dependencies

All dependencies are already installed, but if you need to reinstall:

```bash
pip install -r requirements.txt
```

## Step 3: Set Up PostgreSQL Database

1. **Create a PostgreSQL database:**

   Open PostgreSQL command line (psql) or use pgAdmin:
   
   ```sql
   CREATE DATABASE legalease_db;
   CREATE USER your_username WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE legalease_db TO your_username;
   ```

2. **Create `.env` file:**
   
   Copy the example file and fill in your actual values:
   
   ```bash
   # On Windows
   copy env.example .env
   
   # On macOS/Linux
   cp env.example .env
   ```

3. **Edit `.env` file:**
   
   Open `.env` and update these values:
   ```
   SECRET_KEY=generate-a-long-random-string-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   DB_NAME=legalease_db
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```
   
   **Important:** Generate a secure SECRET_KEY. You can use Python:
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

## Step 4: Run Migrations

Django needs to set up its initial database tables:

```bash
python manage.py migrate
```

## Step 5: Create a Superuser (Optional)

To access Django admin panel:

```bash
python manage.py createsuperuser
```

## Step 6: Run the Development Server

```bash
python manage.py runserver
```

Your Django backend should now be running at `http://127.0.0.1:8000/`

## Project Structure

```
backend/
├── legalease/           # Main Django project folder
│   ├── settings.py      # Project settings (configured for PostgreSQL)
│   ├── urls.py          # URL routing
│   ├── wsgi.py          # WSGI configuration
│   └── asgi.py          # ASGI configuration
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
├── env.example          # Example environment variables
├── .env                 # Your actual environment variables (DO NOT COMMIT!)
└── venv/                # Virtual environment folder
```

## Important Notes

- **Never commit `.env` file** - it contains sensitive information
- The `.env` file is already in `.gitignore` for safety
- `DEBUG=True` is fine for development, but **must be False in production**
- Always use environment variables for sensitive data (passwords, API keys, etc.)

## Troubleshooting

**If you get a database connection error:**
- Make sure PostgreSQL is running
- Verify your database credentials in `.env`
- Check that the database exists in PostgreSQL

**If you get import errors:**
- Make sure your virtual environment is activated
- Run `pip install -r requirements.txt` again

