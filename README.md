# LegalEase - AI-Powered Contract Analyzer

An intelligent contract analysis platform that uses AI to extract, analyze, and assess risks in legal documents.

## Features

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

## Testing

Run tests with:
```bash
cd backend
pytest
```

## Project Structure

```
legalease-ai-contract-analyzer/
├── backend/
│   ├── contracts/          # Main app
│   │   ├── models.py       # Database models
│   │   ├── serializers.py  # API serializers
│   │   ├── api_views.py    # API endpoints
│   │   ├── tasks.py        # Celery tasks
│   │   ├── clause_extractor.py  # Clause extraction logic
│   │   ├── ai_analyzer.py  # OpenAI integration
│   │   └── utils.py        # Text extraction utilities
│   ├── legalease/          # Django project config
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── pages/          # React components
│   │   ├── services/       # API services
│   │   └── App.jsx
│   └── package.json
└── README.md
```

## API Endpoints

- `POST /api/contracts/` - Upload contract
- `GET /api/contracts/` - List contracts
- `GET /api/contracts/{id}/` - Get contract details
- `PUT /api/contracts/{id}/` - Update contract
- `DELETE /api/contracts/{id}/` - Delete contract
- `POST /api/token/` - Login (get JWT token)
- `POST /api/token/refresh/` - Refresh JWT token

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request
