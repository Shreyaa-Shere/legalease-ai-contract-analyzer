/**
 * Layout Component
 * 
 * This is a wrapper component that provides navigation and layout structure.
 * It wraps all pages so they have consistent navigation.
 * 
 * Props:
 * - children: The page content that will be rendered inside this layout
 */

import { Link, useNavigate, useLocation } from 'react-router-dom';
import { FileText, Upload, LogOut, User } from 'lucide-react';
import { logout } from '../services/api';
import { toast } from 'react-hot-toast';

function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();
  
  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;
  
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-gray-800 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/contracts" className="flex items-center gap-2 text-xl font-bold hover:text-gray-200 transition-colors">
                <FileText className="w-6 h-6" />
                LegalEase
              </Link>
              
              <div className="ml-10 flex space-x-1">
                <Link
                  to="/contracts"
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive('/contracts') 
                      ? 'bg-gray-700 text-white' 
                      : 'hover:bg-gray-700 text-gray-300'
                  }`}
                >
                  <FileText className="w-4 h-4" />
                  My Contracts
                </Link>
                <Link
                  to="/contracts/upload"
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive('/contracts/upload') 
                      ? 'bg-gray-700 text-white' 
                      : 'hover:bg-gray-700 text-gray-300'
                  }`}
                >
                  <Upload className="w-4 h-4" />
                  Upload Contract
                </Link>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="flex items-center gap-2 text-sm text-gray-300">
                <User className="w-4 h-4" />
                {localStorage.getItem('username') || 'User'}
              </span>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium bg-red-600 hover:bg-red-700 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>
      
      <main>
        {children}
      </main>
    </div>
  );
}

export default Layout;

