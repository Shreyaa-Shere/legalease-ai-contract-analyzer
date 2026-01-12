/**
 * ContractList Component
 * 
 * Displays a list of all contracts with search, filter, and sort functionality.
 */

import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Upload, FileText, CheckCircle, Clock, XCircle, AlertCircle, Eye, Trash2, Filter, ArrowUpDown } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getContracts, deleteContract } from '../services/api';
import { ContractListSkeleton } from '../components/SkeletonLoader';
import ConfirmationDialog from '../components/ConfirmationDialog';

function ContractList() {
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('newest');
  const [deleteDialog, setDeleteDialog] = useState({ isOpen: false, contractId: null, contractTitle: '' });
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchContracts();
  }, []);

  const fetchContracts = async () => {
    try {
      setLoading(true);
      const response = await getContracts();
      setContracts(response.results || response);
      setError('');
    } catch (err) {
      setError('Failed to load contracts. Please try again.');
      toast.error('Failed to load contracts');
      console.error('Error fetching contracts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteContract(id);
      setContracts(contracts.filter(contract => contract.id !== id));
      toast.success('Contract deleted successfully');
    } catch (err) {
      toast.error('Failed to delete contract');
      console.error('Error deleting contract:', err);
    }
  };

  const openDeleteDialog = (id, title) => {
    setDeleteDialog({ isOpen: true, contractId: id, contractTitle: title });
  };

  const closeDeleteDialog = () => {
    setDeleteDialog({ isOpen: false, contractId: null, contractTitle: '' });
  };

  const confirmDelete = () => {
    if (deleteDialog.contractId) {
      handleDelete(deleteDialog.contractId);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'analyzed':
        return <CheckCircle className="w-4 h-4" />;
      case 'processing':
        return <Clock className="w-4 h-4" />;
      case 'error':
        return <XCircle className="w-4 h-4" />;
      default:
        return <AlertCircle className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'analyzed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  // Filter and sort contracts
  const filteredAndSortedContracts = useMemo(() => {
    let filtered = contracts;

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(contract =>
        contract.title?.toLowerCase().includes(query) ||
        contract.description?.toLowerCase().includes(query)
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(contract => contract.status === statusFilter);
    }

    // Sort
    const sorted = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.uploaded_at) - new Date(a.uploaded_at);
        case 'oldest':
          return new Date(a.uploaded_at) - new Date(b.uploaded_at);
        case 'name-asc':
          return (a.title || '').localeCompare(b.title || '');
        case 'name-desc':
          return (b.title || '').localeCompare(a.title || '');
        default:
          return 0;
      }
    });

    return sorted;
  }, [contracts, searchQuery, statusFilter, sortBy]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-800">My Contracts</h1>
          </div>
          <ContractListSkeleton />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800">My Contracts</h1>
          <button
            onClick={() => navigate('/contracts/upload')}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors shadow-sm"
          >
            <Upload className="w-5 h-5" />
            Upload New Contract
          </button>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search Bar */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search contracts..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Status Filter */}
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-500" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Status</option>
                <option value="uploaded">Uploaded</option>
                <option value="processing">Processing</option>
                <option value="analyzed">Analyzed</option>
                <option value="error">Error</option>
              </select>
            </div>

            {/* Sort */}
            <div className="flex items-center gap-2">
              <ArrowUpDown className="w-5 h-5 text-gray-500" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="name-asc">Name (A-Z)</option>
                <option value="name-desc">Name (Z-A)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            {error}
          </div>
        )}

        {/* Contracts Grid or Empty State */}
        {filteredAndSortedContracts.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            {contracts.length === 0 ? (
              // No contracts at all
              <>
                <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  No contracts yet
                </h3>
                <p className="text-gray-500 mb-6 max-w-md mx-auto">
                  Upload your first contract to get started with AI-powered analysis and risk assessment.
                </p>
                <button
                  onClick={() => navigate('/contracts/upload')}
                  className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors"
                >
                  <Upload className="w-5 h-5" />
                  Upload Your First Contract
                </button>
                <p className="text-sm text-gray-400 mt-4">
                  Supported formats: PDF, DOCX (Max 10MB)
                </p>
              </>
            ) : (
              // No results from search/filter
              <>
                <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  No contracts found
                </h3>
                <p className="text-gray-500 mb-4">
                  Try adjusting your search or filter criteria.
                </p>
                <button
                  onClick={() => {
                    setSearchQuery('');
                    setStatusFilter('all');
                  }}
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  Clear filters
                </button>
              </>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAndSortedContracts.map((contract) => (
              <div
                key={contract.id}
                className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-100"
              >
                <div className="p-6">
                  {/* Contract Title */}
                  <h3 className="text-lg font-semibold text-gray-800 mb-2 line-clamp-2">
                    {contract.title}
                  </h3>

                  {/* Description */}
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2 min-h-[2.5rem]">
                    {contract.description || 'No description'}
                  </p>

                  {/* Badges */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium">
                      <FileText className="w-3 h-3" />
                      {contract.file_type?.toUpperCase() || 'PDF'}
                    </span>
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium border ${getStatusColor(contract.status)}`}>
                      {getStatusIcon(contract.status)}
                      {(contract.status || 'uploaded').charAt(0).toUpperCase() + (contract.status || 'uploaded').slice(1)}
                    </span>
                  </div>

                  {/* File Size and Date */}
                  <div className="text-xs text-gray-500 mb-4 space-y-1">
                    {contract.file_size_mb && (
                      <p>Size: {contract.file_size_mb} MB</p>
                    )}
                    <p>Uploaded: {new Date(contract.uploaded_at).toLocaleDateString()}</p>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-4 border-t border-gray-100">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/contracts/${contract.id}`);
                      }}
                      className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors"
                    >
                      <Eye className="w-4 h-4" />
                      View
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        openDeleteDialog(contract.id, contract.title);
                      }}
                      className="flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Confirmation Dialog */}
        <ConfirmationDialog
          isOpen={deleteDialog.isOpen}
          onClose={closeDeleteDialog}
          onConfirm={confirmDelete}
          title="Delete Contract"
          message={`Are you sure you want to delete "${deleteDialog.contractTitle}"? This action cannot be undone.`}
          confirmText="Delete"
          cancelText="Cancel"
          type="danger"
        />
      </div>
    </div>
  );
}

export default ContractList;
