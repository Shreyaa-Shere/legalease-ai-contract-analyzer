/**
 * Main App Component
 * 
 * This is the root component of our React application.
 * It sets up routing (which page to show for which URL).
 * 
 * React Router:
 * - BrowserRouter: Wraps the app, enables routing
 * - Routes: Container for all route definitions
 * - Route: Defines a single route (URL → Component)
 * - Navigate: Redirects to another route
 */

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './components/Login';
import Register from './components/Register';
import ContractList from './pages/ContractList';
import ContractUpload from './pages/ContractUpload';
import ContractDetail from './pages/ContractDetail';
import { isAuthenticated } from './utils/auth';

function App() {
  return (
    <Router>
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 4000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
      <Routes>
        {/* 
          Login Route (Public - anyone can access)
          URL: /login
          Component: Login component
        */}
        <Route path="/login" element={<Login />} />
        
        {/* 
          Register Route (Public - anyone can access)
          URL: /register
          Component: Register component
        */}
        <Route path="/register" element={<Register />} />
        
        {/* 
          Protected Routes (Require authentication)
          These are wrapped in ProtectedRoute component
          which checks if user is logged in
        */}
        
        {/* 
          Contracts List Route
          URL: /contracts
          Shows list of all contracts
        */}
        <Route
          path="/contracts"
          element={
            <ProtectedRoute>
              <Layout>
                <ContractList />
              </Layout>
            </ProtectedRoute>
          }
        />
        
        {/* 
          Upload Contract Route
          URL: /contracts/upload
          Shows upload form
        */}
        <Route
          path="/contracts/upload"
          element={
            <ProtectedRoute>
              <Layout>
                <ContractUpload />
              </Layout>
            </ProtectedRoute>
          }
        />
        
        {/* 
          Contract Detail Route
          URL: /contracts/:id (where :id is the contract ID)
          Shows detailed view of one contract
        */}
        <Route
          path="/contracts/:id"
          element={
            <ProtectedRoute>
              <Layout>
                <ContractDetail />
              </Layout>
            </ProtectedRoute>
          }
        />
        
        {/* 
          Root Route (/)
          If user is logged in → redirect to /contracts
          If not logged in → redirect to /login
        */}
        <Route
          path="/"
          element={
            isAuthenticated() ? (
              <Navigate to="/contracts" replace />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        
        {/* 
          404 Route (Page Not Found)
          Matches any URL that doesn't match above routes
        */}
        <Route
          path="*"
          element={
            <div className="min-h-screen flex items-center justify-center">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-gray-800 mb-4">404</h1>
                <p className="text-gray-600 mb-4">Page not found</p>
                <a href="/contracts" className="text-blue-600 hover:text-blue-800">
                  Go to Contracts
        </a>
      </div>
      </div>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
