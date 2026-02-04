/**
 * Register Component
 * 
 * This component handles user registration.
 * 
 * Features:
 * - Username, email, password, and password confirmation fields
 * - Optional first name and last name fields
 * - Form validation
 * - Error handling
 * - Redirects to login after successful registration
 */

import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { UserPlus, FileText, AlertCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { register } from '../services/api';

function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();
  
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Clear error when user starts typing
    if (error) setError('');
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    setError('');
    setLoading(true);
    
    // Client-side validation
    if (formData.password !== formData.password_confirm) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }
    
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      setLoading(false);
      return;
    }
    
    try {
      await register(formData);
      toast.success('Account created successfully! Please login.');
      navigate('/login');
    } catch (err) {
      // Handle validation errors from backend
      let errorMessage = 'Registration failed. Please check your information.';
      
      if (err.response?.data) {
        const errors = err.response.data;
        
        // Handle field-specific errors
        if (errors.username) {
          errorMessage = Array.isArray(errors.username) 
            ? errors.username[0] 
            : errors.username;
        } else if (errors.email) {
          errorMessage = Array.isArray(errors.email) 
            ? errors.email[0] 
            : errors.email;
        } else if (errors.password) {
          errorMessage = Array.isArray(errors.password) 
            ? errors.password[0] 
            : errors.password;
        } else if (errors.password_confirm) {
          errorMessage = Array.isArray(errors.password_confirm) 
            ? errors.password_confirm[0] 
            : errors.password_confirm;
        } else if (errors.non_field_errors) {
          errorMessage = Array.isArray(errors.non_field_errors) 
            ? errors.non_field_errors[0] 
            : errors.non_field_errors;
        } else {
          // Get first error message
          const firstError = Object.values(errors)[0];
          errorMessage = Array.isArray(firstError) ? firstError[0] : firstError;
        }
      }
      
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-lg">
        <div className="flex flex-col items-center mb-6">
          <div className="bg-blue-100 rounded-full p-3 mb-4">
            <FileText className="w-8 h-8 text-blue-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-800 mb-2">
            LegalEase
          </h2>
          <p className="text-gray-500 text-sm">AI-Powered Contract Analyzer</p>
        </div>
        
        <h3 className="text-xl font-semibold text-center mb-6 text-gray-700">
          Create your account
        </h3>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label 
              htmlFor="username" 
              className="block text-gray-700 text-sm font-semibold mb-2"
            >
              Username *
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Choose a username"
              required
            />
          </div>
          
          <div className="mb-4">
            <label 
              htmlFor="email" 
              className="block text-gray-700 text-sm font-semibold mb-2"
            >
              Email *
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your email"
              required
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label 
                htmlFor="first_name" 
                className="block text-gray-700 text-sm font-semibold mb-2"
              >
                First Name
              </label>
              <input
                type="text"
                id="first_name"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="First name"
              />
            </div>
            
            <div>
              <label 
                htmlFor="last_name" 
                className="block text-gray-700 text-sm font-semibold mb-2"
              >
                Last Name
              </label>
              <input
                type="text"
                id="last_name"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Last name"
              />
            </div>
          </div>
          
          <div className="mb-4">
            <label 
              htmlFor="password" 
              className="block text-gray-700 text-sm font-semibold mb-2"
            >
              Password *
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your password (min. 8 characters)"
              required
              minLength={8}
            />
          </div>
          
          <div className="mb-6">
            <label 
              htmlFor="password_confirm" 
              className="block text-gray-700 text-sm font-semibold mb-2"
            >
              Confirm Password *
            </label>
            <input
              type="password"
              id="password_confirm"
              name="password_confirm"
              value={formData.password_confirm}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Confirm your password"
              required
              minLength={8}
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-4 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            <UserPlus className="w-5 h-5" />
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
          
          <div className="mt-4 text-center">
            <p className="text-gray-600 text-sm">
              Already have an account?{' '}
              <Link 
                to="/login" 
                className="text-blue-600 hover:text-blue-800 font-semibold"
              >
                Login here
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Register;
