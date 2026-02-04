# LegalEase Frontend

React frontend application for LegalEase - AI-Powered Contract Analyzer.

## What is this?

This is the **frontend** (user interface) of the LegalEase application. It's built with:
- **React** - JavaScript library for building user interfaces
- **Tailwind CSS** - Utility-first CSS framework for styling
- **Axios** - HTTP client for API calls
- **React Router** - Navigation/routing library

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Login.jsx       # Login page component
│   │   ├── Register.jsx    # Registration page component
│   │   ├── Layout.jsx      # Navigation layout wrapper
│   │   └── ProtectedRoute.jsx  # Authentication guard
│   ├── pages/              # Page components
│   │   ├── ContractList.jsx    # List all contracts
│   │   ├── ContractUpload.jsx  # Upload new contract
│   │   └── ContractDetail.jsx  # View contract details
│   ├── services/           # API service layer
│   │   └── api.js          # All API calls (login, CRUD operations)
│   ├── utils/              # Utility functions
│   │   └── auth.js         # Authentication helpers
│   ├── App.jsx             # Main app component with routing
│   └── main.jsx            # App entry point
├── package.json            # Dependencies and scripts
└── tailwind.config.js      # Tailwind CSS configuration
```

## Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

## Running the Development Server

1. **Make sure Django backend is running** (on http://127.0.0.1:8000)

2. **Start the React development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser** and go to the URL shown (usually http://localhost:5173)

## Available Routes

- `/` - Redirects to `/login` or `/contracts` based on authentication
- `/login` - Login page
- `/register` - User registration page
- `/contracts` - List all contracts (protected)
- `/contracts/upload` - Upload new contract (protected)
- `/contracts/:id` - View contract details (protected)

## Key Features

1. **Authentication**
   - User registration with email and password
   - JWT token-based authentication
   - Tokens stored in localStorage
   - Automatic token refresh
   - Protected routes

2. **Contract Management**
   - View all contracts in a card grid
   - Upload new contracts (PDF/DOCX)
   - View contract details
   - Delete contracts
   - Mark contracts as analyzed

3. **User Experience**
   - Responsive design (works on mobile, tablet, desktop)
   - Loading states
   - Error handling
   - Form validation

## API Configuration

The frontend connects to the Django backend API at:
- Base URL: `http://127.0.0.1:8000/api`

To change this, edit `src/services/api.js`:
```javascript
const API_BASE_URL = 'http://your-backend-url/api';
```

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `dist/` folder.
