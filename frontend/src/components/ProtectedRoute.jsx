/**
 * ProtectedRoute Component
 * 
 * This component protects routes that require authentication.
 * 
 * How it works:
 * 1. Checks if user is logged in (has token)
 * 2. If logged in → show the protected page
 * 3. If not logged in → redirect to login page
 * 
 * Props:
 * - children: The component/page to render if user is authenticated
 */

import { Navigate } from 'react-router-dom';
import { isAuthenticated } from '../utils/auth';

function ProtectedRoute({ children }) {
  // Check if user is authenticated
  const authenticated = isAuthenticated();
  
  // If not authenticated, redirect to login
  // If authenticated, render the protected component
  return authenticated ? children : <Navigate to="/login" replace />;
}

export default ProtectedRoute;

