# LegalEase - AI-Powered Contract Analyzer

An intelligent contract analysis platform that uses AI to extract, analyze, and assess risks in legal documents.

## Features

- **User Authentication**: Secure JWT-based authentication with user registration and login
- **Automated Text Extraction**: Extracts text from PDF and DOCX files
- **Intelligent Clause Detection**: Identifies key legal clauses using pattern matching
- **AI-Powered Risk Analysis**: Uses OpenAI GPT to assess contract risks and provide summaries
- **Real-time Processing**: Asynchronous processing with Celery for instant API responses
- **User-Friendly Interface**: Modern React frontend with real-time status updates
- **Comprehensive Analysis**: Risk levels, clause summaries, and actionable recommendations

## Tech Stack

- **Backend**: Django REST Framework, PostgreSQL, Celery, Redis
- **Frontend**: React, Tailwind CSS, Vite
- **AI**: OpenAI GPT-4o-mini
- **Testing**: PyTest, GitHub Actions CI/CD

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL
- Redis
- OpenAI API Key

## Installation

### Backend Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd legalease-ai-contract-analyzer
```

2. Navigate to backend directory:
```bash
cd backend
```

3. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your configuration
```

6. Set up database:
```bash
python manage.py migrate
python manage.py createsuperuser
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Start Redis

**Windows:**
```bash
cd C:\Redis-x64-5.0.14.1
.\redis-server.exe
```

**Linux/Mac:**
```bash
redis-server
```

### Start Celery Worker

**Windows:**
```bash
cd backend
.\start_celery.bat
```

**Linux/Mac:**
```bash
cd backend
./start_celery.sh
```

### Start Django Server

```bash
cd backend
python manage.py runserver
```

### Start Frontend

```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:5173`

**Note:** Make sure all services are running:
- Redis (for Celery message broker)
- Celery Worker (for background task processing)
- Django Server (backend API)
- Frontend Dev Server (React app)

## Configuration

### Environment Variables

Required environment variables in `backend/.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=legalease_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

OPENAI_API_KEY=your-openai-api-key

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Usage

### First Time Setup

1. **Create a superuser account** (for Django admin):
   ```bash
   cd backend
   python manage.py createsuperuser
   ```

2. **Register a new user** via the frontend:
   - Navigate to `http://localhost:5173/register`
   - Fill in the registration form
   - After registration, you'll be redirected to login

3. **Login** to access the application:
   - Navigate to `http://localhost:5173/login`
   - Use your registered credentials

### Using the Application

1. **Upload Contracts**: Click "Upload Contract" to add a new contract (PDF or DOCX)
2. **View Contracts**: Browse your uploaded contracts on the main page
3. **View Analysis**: Click on any contract to see detailed AI-powered analysis
4. **Manage Contracts**: Update or delete contracts as needed

## Testing

Run tests with:
```bash
cd backend
pytest
```

For more detailed test output:
```bash
cd backend
pytest -v  # Verbose output
pytest --cov  # With coverage report
```

## Project Structure

```
legalease-ai-contract-analyzer/
├── backend/
│   ├── contracts/          # Main app
│   │   ├── models.py       # Database models
│   │   ├── serializers.py  # API serializers (includes UserRegistrationSerializer)
│   │   ├── api_views.py    # API endpoints (includes registration)
│   │   ├── api_urls.py     # API URL routing
│   │   ├── tasks.py        # Celery tasks
│   │   ├── clause_extractor.py  # Clause extraction logic
│   │   ├── ai_analyzer.py  # OpenAI integration
│   │   └── utils.py        # Text extraction utilities
│   ├── legalease/          # Django project config
│   │   ├── settings.py     # Django settings
│   │   └── urls.py         # Main URL configuration
│   ├── manage.py
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables (create from env.example)
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable React components
│   │   │   ├── Login.jsx   # Login page
│   │   │   ├── Register.jsx  # Registration page
│   │   │   ├── Layout.jsx  # Main layout wrapper
│   │   │   └── ProtectedRoute.jsx  # Auth guard
│   │   ├── pages/          # Page components
│   │   │   ├── ContractList.jsx
│   │   │   ├── ContractUpload.jsx
│   │   │   └── ContractDetail.jsx
│   │   ├── services/       # API services
│   │   │   └── api.js      # API client with authentication
│   │   ├── utils/          # Utility functions
│   │   │   └── auth.js     # Authentication helpers
│   │   └── App.jsx         # Main app component with routing
│   └── package.json
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/register/` - Register a new user account
- `POST /api/token/` - Login (get JWT token)
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/token/verify/` - Verify JWT token validity

### Contracts
- `POST /api/contracts/` - Upload contract (requires authentication)
- `GET /api/contracts/` - List contracts (requires authentication)
- `GET /api/contracts/{id}/` - Get contract details (requires authentication)
- `PUT /api/contracts/{id}/` - Update contract (requires authentication)
- `DELETE /api/contracts/{id}/` - Delete contract (requires authentication)
- `POST /api/contracts/{id}/mark_analyzed/` - Mark contract as analyzed (requires authentication)

## Troubleshooting

### Common Issues

**Redis Connection Error:**
- Make sure Redis is running before starting Celery
- Check Redis is accessible at `localhost:6379`
- On Windows, ensure Redis server is started from the correct directory

**Celery Worker Not Processing Tasks:**
- Verify Redis is running
- Check Celery worker logs for errors
- Ensure Django server is running (Celery needs database access)

**Database Connection Error:**
- Verify PostgreSQL is running
- Check database credentials in `.env` file
- Ensure database `legalease_db` exists (or run migrations to create it)

**Frontend Can't Connect to Backend:**
- Ensure Django server is running on `http://127.0.0.1:8000`
- Check CORS settings in `backend/legalease/settings.py`
- Verify API_BASE_URL in `frontend/src/services/api.js`

**Module Not Found Errors:**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again
- For frontend: run `npm install` again

**Registration/Login Issues:**
- Ensure database migrations are applied: `python manage.py migrate`
- Check that PostgreSQL is running and accessible
- Verify environment variables are set correctly in `.env`

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request
