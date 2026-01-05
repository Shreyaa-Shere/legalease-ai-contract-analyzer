/**
 * ContractList Component
 * 
 * This component displays a list of all contracts.
 * 
 * React Hooks used:
 * - useState: Store contract data and loading state
 * - useEffect: Fetch contracts when component loads
 * - useNavigate: Navigate to detail/upload pages
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getContracts, deleteContract } from '../services/api';

function ContractList() {
  // State for contracts list
  const [contracts, setContracts] = useState([]);  // Empty array initially
  const [loading, setLoading] = useState(true);     // Start with loading = true
  const [error, setError] = useState('');          // For error messages
  
  const navigate = useNavigate();
  
  /**
   * Fetch contracts from API
   * 
   * useEffect runs when component first loads (like componentDidMount in class components)
   * The empty array [] means it only runs once (on mount)
   */
  useEffect(() => {
    fetchContracts();
  }, []);  // Empty dependency array = run once on mount
  
  /**
   * Function to fetch contracts from API
   */
  const fetchContracts = async () => {
    try {
      setLoading(true);
      // Call API to get contracts
      const response = await getContracts();
      
      // API returns: { count, next, previous, results: [...] }
      // We want the 'results' array
      setContracts(response.results || response);  // Handle both paginated and non-paginated
      setError('');
    } catch (err) {
      setError('Failed to load contracts. Please try again.');
      console.error('Error fetching contracts:', err);
    } finally {
      setLoading(false);
    }
  };
  
  /**
   * Handle delete contract
   */
  const handleDelete = async (id) => {
    // Confirm before deleting
    if (!window.confirm('Are you sure you want to delete this contract?')) {
      return;  // User cancelled
    }
    
    try {
      await deleteContract(id);
      // Remove contract from list
      setContracts(contracts.filter(contract => contract.id !== id));
    } catch (err) {
      alert('Failed to delete contract');
      console.error('Error deleting contract:', err);
    }
  };
  
  /**
   * Get status badge color based on status
   */
  const getStatusColor = (status) => {
    switch (status) {
      case 'analyzed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };
  
  // Show loading spinner while fetching data
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Loading contracts...</div>
      </div>
    );
  }
  
  // Main component render
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">My Contracts</h1>
          <button
            onClick={() => navigate('/contracts/upload')}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            + Upload New Contract
          </button>
        </div>
        
        {/* Error Message */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        {/* Contracts Grid */}
        {contracts.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <h3 className="text-xl font-semibold text-gray-600 mb-2">
              No contracts yet
            </h3>
            <p className="text-gray-500 mb-4">Get started by uploading your first contract.</p>
            <button
              onClick={() => navigate('/contracts/upload')}
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
              Upload Contract
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {contracts.map((contract) => (
              <div
                key={contract.id}
                className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => navigate(`/contracts/${contract.id}`)}
              >
                <div className="p-6">
                  {/* Contract Title */}
                  <h3 className="text-xl font-semibold text-gray-800 mb-2">
                    {contract.title}
                  </h3>
                  
                  {/* Description */}
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                    {contract.description || 'No description'}
                  </p>
                  
                  {/* Badges */}
                  <div className="flex gap-2 mb-4">
                    <span className="px-2 py-1 bg-gray-200 text-gray-700 rounded text-xs">
                      {contract.file_type?.toUpperCase() || 'PDF'}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs ${getStatusColor(contract.status)}`}>
                      {contract.status || 'uploaded'}
                    </span>
                  </div>
                  
                  {/* File Size */}
                  {contract.file_size_mb && (
                    <p className="text-sm text-gray-500 mb-2">
                      Size: {contract.file_size_mb} MB
                    </p>
                  )}
                  
                  {/* Upload Date */}
                  <p className="text-xs text-gray-400 mb-4">
                    Uploaded: {new Date(contract.uploaded_at).toLocaleDateString()}
                  </p>
                  
                  {/* Actions */}
                  <div className="flex gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();  // Prevent card click
                        navigate(`/contracts/${contract.id}`);
                      }}
                      className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-sm font-bold py-2 px-4 rounded"
                    >
                      View
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();  // Prevent card click
                        handleDelete(contract.id);
                      }}
                      className="bg-red-600 hover:bg-red-700 text-white text-sm font-bold py-2 px-4 rounded"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default ContractList;

