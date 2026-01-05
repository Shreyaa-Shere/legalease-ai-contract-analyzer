/**
 * Layout Component
 * 
 * This is a wrapper component that provides navigation and layout structure.
 * It wraps all pages so they have consistent navigation.
 * 
 * Props:
 * - children: The page content that will be rendered inside this layout
 */

import { Link, useNavigate } from 'react-router-dom';
import { logout } from '../services/api';

function Layout({ children }) {
  const navigate = useNavigate();
  
  /**
   * Handle logout
   */
  const handleLogout = () => {
    logout();  // Remove tokens from localStorage
    navigate('/login');  // Redirect to login
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Bar */}
      <nav className="bg-gray-800 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Left side: Logo and Links */}
            <div className="flex items-center">
              <Link to="/contracts" className="text-xl font-bold">
                LegalEase
              </Link>
              
              <div className="ml-10 flex space-x-4">
                <Link
                  to="/contracts"
                  className="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700"
                >
                  My Contracts
                </Link>
                <Link
                  to="/contracts/upload"
                  className="px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-700"
                >
                  Upload Contract
                </Link>
              </div>
            </div>
            
            {/* Right side: User info and Logout */}
            <div className="flex items-center space-x-4">
              <span className="text-sm">Welcome, {localStorage.getItem('username') || 'User'}!</span>
              <button
                onClick={handleLogout}
                className="px-3 py-2 rounded-md text-sm font-medium bg-red-600 hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>
      
      {/* Page Content */}
      <main>
        {children}
      </main>
    </div>
  );
}

export default Layout;

