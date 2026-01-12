/**
 * ContractUpload Component
 * 
 * This component handles uploading new contracts.
 * 
 * What it does:
 * 1. Shows a form with title, description, and file upload
 * 2. Validates file type (PDF/DOCX only) and size (max 10MB)
 * 3. Creates FormData object with the file
 * 4. Sends to API using uploadContract function
 * 5. Redirects to contract detail page on success
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, ArrowLeft, AlertCircle, X } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { uploadContract } from '../services/api';

function ContractUpload() {
  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState(null);  // Store selected file
  const [fileError, setFileError] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();
  
  /**
   * Handle file selection
   * 
   * Validates file type and size before allowing upload
   */
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    
    if (!selectedFile) {
      setFile(null);
      return;
    }
    
    // Validate file type
    const fileExtension = selectedFile.name.split('.').pop().toLowerCase();
    if (fileExtension !== 'pdf' && fileExtension !== 'docx') {
      setFileError('Only PDF and DOCX files are allowed');
      setFile(null);
      return;
    }
    
    // Validate file size (10MB = 10 * 1024 * 1024 bytes)
    const maxSize = 10 * 1024 * 1024;  // 10MB in bytes
    if (selectedFile.size > maxSize) {
      setFileError(`File size must be less than 10MB. Your file is ${(selectedFile.size / (1024 * 1024)).toFixed(2)}MB`);
      setFile(null);
      return;
    }
    
    // File is valid
    setFile(selectedFile);
    setFileError('');
  };
  
  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Clear errors
    setError('');
    setFileError('');
    
    // Validate required fields
    if (!title.trim()) {
      setError('Title is required');
      return;
    }
    
    if (!file) {
      setFileError('Please select a file');
      return;
    }
    
    setLoading(true);
    
    try {
      // Create FormData object (required for file uploads)
      // FormData is like a special object that can hold files and text
      const formData = new FormData();
      formData.append('title', title);
      formData.append('description', description);
      formData.append('file', file);  // Append the file
      
      // Call API to upload contract
      const response = await uploadContract(formData);
      
      // If successful, redirect to contract detail page
      navigate(`/contracts/${response.id}`);
    } catch (err) {
      // Show error message
      if (err.response?.data) {
        // Server returned specific error messages
        const errors = err.response.data;
        if (typeof errors === 'object') {
          const errorMessages = Object.values(errors).flat().join(', ');
          setError(errorMessages);
        } else {
          setError('Upload failed. Please try again.');
        }
      } else {
        setError('Upload failed. Please check your connection and try again.');
      }
      console.error('Upload error:', err);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/contracts')}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-800 mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Contracts
          </button>
          <div className="flex items-center gap-3">
            <div className="bg-blue-100 rounded-full p-2">
              <Upload className="w-6 h-6 text-blue-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-800">Upload New Contract</h1>
          </div>
        </div>
        
        {/* Upload Form Card */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 flex items-start gap-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span className="flex-1">{error}</span>
              <button onClick={() => setError('')} className="text-red-500 hover:text-red-700">
                <X className="w-4 h-4" />
              </button>
            </div>
          )}
          
          <form onSubmit={handleSubmit}>
            {/* Title Input */}
            <div className="mb-6">
              <label 
                htmlFor="title" 
                className="block text-gray-700 text-sm font-bold mb-2"
              >
                Contract Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Employment Contract - John Doe"
                required
              />
            </div>
            
            {/* Description Input */}
            <div className="mb-6">
              <label 
                htmlFor="description" 
                className="block text-gray-700 text-sm font-bold mb-2"
              >
                Description (Optional)
              </label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows="4"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Add any notes or details about this contract..."
              />
            </div>
            
            {/* File Upload */}
            <div className="mb-6">
              <label 
                htmlFor="file" 
                className="block text-gray-700 text-sm font-bold mb-2"
              >
                Contract File (PDF or DOCX) <span className="text-red-500">*</span>
              </label>
              <input
                type="file"
                id="file"
                accept=".pdf,.docx"  // Only allow PDF and DOCX
                onChange={handleFileChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
              
              {/* Show selected file name */}
              {file && (
                <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-center gap-3">
                  <FileText className="w-5 h-5 text-blue-600 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">{file.name}</p>
                    <p className="text-xs text-gray-500">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setFile(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}
              
              {/* File error message */}
              {fileError && (
                <p className="mt-2 text-sm text-red-600">{fileError}</p>
              )}
              
              <p className="mt-2 text-xs text-gray-500">
                Maximum file size: 10MB. Supported formats: PDF, DOCX
              </p>
            </div>
            
            {/* Submit Buttons */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-4 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                <Upload className="w-5 h-5" />
                {loading ? 'Uploading...' : 'Upload Contract'}
              </button>
              <button
                type="button"
                onClick={() => navigate('/contracts')}
                className="px-6 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-2.5 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default ContractUpload;

