/**
 * Login Component
 * 
 * This component handles user login.
 * 
 * What is a React component?
 * - A component is a reusable piece of UI (User Interface)
 * - It's a JavaScript function that returns JSX (HTML-like syntax)
 * - Components can have state (data that changes) and props (data passed in)
 * 
 * This component:
 * 1. Shows a login form (username and password fields)
 * 2. When user submits, calls the login API
 * 3. Stores the JWT token if login succeeds
 * 4. Redirects to contracts list page
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/api';

function Login() {
  // useState is a React Hook that lets you add state to functional components
  // State is data that can change, and when it changes, React re-renders the component
  
  // State for form inputs
  const [username, setUsername] = useState('');      // Empty string initially
  const [password, setPassword] = useState('');      // Empty string initially
  const [error, setError] = useState('');            // For error messages
  const [loading, setLoading] = useState(false);     // To show loading spinner
  
  // useNavigate is a React Router hook for programmatic navigation
  // It lets us redirect to other pages after login
  const navigate = useNavigate();
  
  /**
   * Handle form submission
   * 
   * This function runs when user clicks "Login" button
   */
  const handleSubmit = async (e) => {
    e.preventDefault();  // Prevent form from submitting normally (page refresh)
    
    // Clear any previous errors
    setError('');
    setLoading(true);  // Show loading state
    
    try {
      // Call the login API function (from services/api.js)
      await login(username, password);
      
      // If login succeeds, redirect to contracts list
      navigate('/contracts');
    } catch (err) {
      // If login fails, show error message
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);  // Server error message
      } else {
        setError('Login failed. Please check your credentials.');
      }
    } finally {
      // Always stop loading, whether success or error
      setLoading(false);
    }
  };
  
  /**
   * JSX Return
   * 
   * This is what gets rendered on the screen.
   * JSX looks like HTML but it's actually JavaScript.
   * 
   * Tailwind CSS classes:
   * - min-h-screen: Minimum height of screen (full height)
   * - flex, items-center, justify-center: Center content
   * - bg-gray-50: Light gray background
   * - max-w-md: Maximum width of medium size
   * - p-8: Padding of 8 (2rem)
   * - rounded-lg: Rounded corners
   * - shadow-lg: Large shadow
   */
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-lg">
        <h2 className="text-3xl font-bold text-center mb-6 text-gray-800">
          LegalEase
        </h2>
        <h3 className="text-xl font-semibold text-center mb-6 text-gray-600">
          Login
        </h3>
        
        {/* Show error message if login fails */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          {/* Username Input */}
          <div className="mb-4">
            <label 
              htmlFor="username" 
              className="block text-gray-700 text-sm font-bold mb-2"
            >
              Username
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}  // Update state when user types
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your username"
              required  // HTML5 validation: field is required
            />
          </div>
          
          {/* Password Input */}
          <div className="mb-6">
            <label 
              htmlFor="password" 
              className="block text-gray-700 text-sm font-bold mb-2"
            >
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}  // Update state when user types
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your password"
              required
            />
          </div>
          
          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}  // Disable button while loading
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;

