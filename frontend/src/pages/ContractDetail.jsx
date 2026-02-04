/**
 * ContractDetail Component
 * 
 * This component displays detailed information about a single contract.
 * 
 * React Router:
 * - useParams: Gets URL parameters (like contract ID from /contracts/:id)
 * - useNavigate: For navigation
 */

import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, CheckCircle, Clock, XCircle, AlertCircle, FileText, Check } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getContract, markContractAnalyzed } from '../services/api';
import { ContractDetailSkeleton } from '../components/SkeletonLoader';

function ContractDetail() {
  // Get contract ID from URL
  // If URL is /contracts/1/, then id = "1"
  const { id } = useParams();
  const navigate = useNavigate();
  
  // State
  const [contract, setContract] = useState(null);  // Contract data
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expandedClauses, setExpandedClauses] = useState(new Set());  // Track which clause groups are expanded
  
  /**
   * Fetch contract details - memoized to avoid infinite loops
   */
  const fetchContract = useCallback(async (showLoading = false) => {
    try {
      if (showLoading) {
        setLoading(true);
      }
      const data = await getContract(id);
      setContract(data);
      setError('');
    } catch (err) {
      setError('Failed to load contract details');
      console.error('Error fetching contract:', err);
    } finally {
      setLoading(false);
    }
  }, [id]);  // Only depend on id
  
  /**
   * Fetch contract details when component loads
   */
  useEffect(() => {
    fetchContract(true);  // Show loading on initial load
  }, [fetchContract]);
  
  /**
   * Poll for status updates when contract is processing.
   * Checks every 2 seconds for updates when status is 'uploaded' or 'processing'.
   */
  useEffect(() => {
    // Only poll if contract is being processed
    if (!contract || (contract.status !== 'uploaded' && contract.status !== 'processing')) {
      return;
    }
    
    console.log(`[Polling] Contract ${id} status: ${contract.status} - checking every 2s...`);
    
    // Set up polling interval (check every 2 seconds for faster updates)
    const intervalId = setInterval(() => {
      console.log(`[Polling] Checking status for contract ${id}...`);
      fetchContract();
    }, 2000);  // 2000 milliseconds = 2 seconds (faster updates)
    
    // Cleanup: stop polling when component unmounts or status changes
    return () => {
      clearInterval(intervalId);
      console.log(`[Polling] Stopped polling for contract ${id}`);
    };
  }, [contract?.status, id, fetchContract]);
  
  /**
   * Handle marking contract as analyzed
   */
  const handleMarkAnalyzed = async () => {
    try {
      await markContractAnalyzed(id);
      toast.success('Contract marked as analyzed');
      fetchContract();
    } catch (err) {
      toast.error('Failed to mark contract as analyzed');
      console.error('Error:', err);
    }
  };
  
  /**
   * Format date for display
   */
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };
  
  /**
   * Get status badge color
   */
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
  
  // Loading state
  if (loading && !contract) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <ContractDetailSkeleton />
        </div>
      </div>
    );
  }
  
  // Error state
  if (error || !contract) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Contract not found'}</p>
          <button
            onClick={() => navigate('/contracts')}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Back to Contracts
          </button>
        </div>
      </div>
    );
  }
  
  // Main render
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/contracts')}
            className="text-blue-600 hover:text-blue-800 mb-4"
          >
            ← Back to Contracts
          </button>
          <h1 className="text-3xl font-bold text-gray-800">{contract.title}</h1>
        </div>
        
        {/* Contract Details Card */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          {/* Two Column Layout */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            {/* Left Column: Contract Information */}
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">Contract Information</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-bold text-gray-600">Title</label>
                  <p className="text-gray-800">{contract.title}</p>
                </div>
                
                <div>
                  <label className="text-sm font-bold text-gray-600">Description</label>
                  <p className="text-gray-800">{contract.description || 'No description'}</p>
                </div>
                
                <div>
                  <label className="text-sm font-bold text-gray-600">File Name</label>
                  <p className="text-gray-800">{contract.file_name}</p>
                </div>
                
                <div>
                  <label className="text-sm font-bold text-gray-600">File Type</label>
                  <span className="inline-flex items-center gap-1 px-2 py-1 bg-gray-200 text-gray-700 rounded text-sm">
                    <FileText className="w-3 h-3" />
                    {contract.file_type?.toUpperCase() || 'PDF'}
                  </span>
                </div>
                
                <div>
                  <label className="text-sm font-bold text-gray-600">File Size</label>
                  <p className="text-gray-800">
                    {contract.file_size_mb ? `${contract.file_size_mb} MB` : 'N/A'}
                  </p>
                </div>
                
                <div>
                  <label className="text-sm font-bold text-gray-600">Status</label>
                  <div>
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-sm border ${getStatusColor(contract.status)}`}>
                      {getStatusIcon(contract.status)}
                      {(contract.status || 'uploaded').charAt(0).toUpperCase() + (contract.status || 'uploaded').slice(1)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Right Column: Timestamps */}
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">Timestamps</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-bold text-gray-600">Uploaded By</label>
                  <p className="text-gray-800">{contract.uploaded_by_username || contract.uploaded_by}</p>
                </div>
                
                <div>
                  <label className="text-sm font-bold text-gray-600">Uploaded At</label>
                  <p className="text-gray-800">{formatDate(contract.uploaded_at)}</p>
                </div>
                
                {contract.analyzed_at && (
                  <div>
                    <label className="text-sm font-bold text-gray-600">Analyzed At</label>
                    <p className="text-gray-800">{formatDate(contract.analyzed_at)}</p>
                  </div>
                )}
                
                <div>
                  <label className="text-sm font-bold text-gray-600">Last Updated</label>
                  <p className="text-gray-800">{formatDate(contract.updated_at)}</p>
                </div>
              </div>
            </div>
          </div>
          
          {/* Actions */}
          <div className="border-t pt-6 flex gap-4">
            {/* Download Button */}
            {contract.file && (
              <a
                href={contract.file}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
              >
                <Download className="w-5 h-5" />
                Download File
              </a>
            )}
            
            {/* Mark as Analyzed Button (only show if not already analyzed) */}
            {contract.status !== 'analyzed' && (
              <button
                onClick={handleMarkAnalyzed}
                className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
              >
                <Check className="w-5 h-5" />
                Mark as Analyzed
              </button>
            )}
          </div>
          
          {/* Extracted Text Section - Hidden by default to reduce clutter */}
          {/* Users can view full text if needed, but it's not the primary focus */}
          {/* Uncomment below if you want to show extracted text */}
          {false && contract.extracted_text && (
            <div className="border-t pt-6 mt-6">
              <h2 className="text-xl font-semibold text-gray-700 mb-4">Extracted Text</h2>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 max-h-96 overflow-y-auto">
                <p className="text-gray-700 whitespace-pre-wrap text-sm leading-relaxed">
                  {contract.extracted_text}
                </p>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Text extracted from the contract document automatically.
              </p>
            </div>
          )}
          
          {/* Show message if no text extracted (only if not processing) */}
          {!contract.extracted_text && contract.status !== 'processing' && contract.status !== 'uploaded' && (
            <div className="border-t pt-6 mt-6">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-yellow-800 text-sm">
                  <strong>Note:</strong> No text has been extracted from this contract yet. 
                  This may happen if the file was uploaded before text extraction was enabled, 
                  or if text extraction encountered an error.
                </p>
              </div>
            </div>
          )}
          
          {/* Show partial results while processing */}
          {(contract.status === 'processing' || contract.status === 'uploaded') && contract.extracted_text && (
            <div className="border-t pt-6 mt-6">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-green-800 text-sm font-semibold mb-2">
                  ✓ Text extraction complete ({contract.extracted_text.length.toLocaleString()} characters)
                </p>
                {contract.extracted_clauses && contract.extracted_clauses.length > 0 && (
                  <p className="text-green-700 text-sm">
                    ✓ Found {contract.extracted_clauses.length} clause types. AI analysis in progress...
                  </p>
                )}
              </div>
            </div>
          )}
          
          {/* AI Analysis Summary */}
          {contract.analysis_summary && (
            <div className="border-t pt-6 mt-6">
              <h2 className="text-xl font-semibold text-gray-700 mb-3">📋 Contract Summary</h2>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap">
                  {contract.analysis_summary}
                </p>
              </div>
            </div>
          )}
          
          {/* Risk Assessment */}
          {contract.risk_assessment && contract.risk_assessment.overall_risk_level && (
            <div className="border-t pt-6 mt-6">
              <h2 className="text-xl font-semibold text-gray-700 mb-4">⚠️ Risk Assessment</h2>
              
              {/* Overall Risk Level */}
              <div className="mb-4">
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-sm font-bold text-gray-600">Overall Risk Level:</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                    contract.risk_assessment.overall_risk_level === 'CRITICAL' || contract.risk_assessment.overall_risk_level === 'HIGH'
                      ? 'bg-red-200 text-red-800'
                      : contract.risk_assessment.overall_risk_level === 'MEDIUM'
                      ? 'bg-yellow-200 text-yellow-800'
                      : 'bg-green-200 text-green-800'
                  }`}>
                    {contract.risk_assessment.overall_risk_level}
                  </span>
                </div>
                
                {contract.risk_assessment.overall_summary && (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 mt-2">
                    <p className="text-gray-700 text-xs leading-relaxed">
                      {contract.risk_assessment.overall_summary}
                    </p>
                  </div>
                )}
              </div>
              
              {/* Clause Risks */}
              {contract.risk_assessment.clause_risks && contract.risk_assessment.clause_risks.length > 0 && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-700">Identified Risks by Clause:</h3>
                  {contract.risk_assessment.clause_risks.map((risk, index) => (
                    <div key={index} className="bg-white border border-gray-300 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-gray-800">
                          {risk.clause_type?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </h4>
                        <span className={`px-2 py-1 rounded text-xs font-bold ${
                          risk.risk_level === 'CRITICAL' || risk.risk_level === 'HIGH'
                            ? 'bg-red-200 text-red-800'
                            : risk.risk_level === 'MEDIUM'
                            ? 'bg-yellow-200 text-yellow-800'
                            : 'bg-green-200 text-green-800'
                        }`}>
                          {risk.risk_level}
                        </span>
                      </div>
                      
                      {risk.risk_explanation && (
                        <p className="text-gray-600 text-xs mb-2 leading-relaxed">{risk.risk_explanation}</p>
                      )}
                      
                      {risk.concerns && risk.concerns.length > 0 && (
                        <div className="mb-3">
                          <p className="text-xs font-semibold text-gray-600 mb-1">Key Concerns:</p>
                          <ul className="list-disc list-inside text-xs text-gray-700 space-y-0.5">
                            {/* Only show top 3 concerns - be concise */}
                            {risk.concerns.slice(0, 3).map((concern, i) => (
                              <li key={i}>{concern}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {risk.recommendations && (
                        <div className="mt-2 pt-2 border-t border-gray-200">
                          <p className="text-xs font-semibold text-blue-600 mb-1">💡 Recommendation:</p>
                          <p className="text-xs text-gray-700">{risk.recommendations}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          
          {/* Extracted Clauses */}
          {contract.extracted_clauses && contract.extracted_clauses.length > 0 && (
            <div className="border-t pt-6 mt-6">
              <h2 className="text-xl font-semibold text-gray-700 mb-4">🔍 Extracted Key Clauses</h2>
              <div className="space-y-4">
                {contract.extracted_clauses.map((clauseGroup, index) => {
                  const clauseGroupKey = `${clauseGroup.type}-${index}`;
                  const isExpanded = expandedClauses.has(clauseGroupKey);
                  const hasMoreInstances = clauseGroup.clauses && clauseGroup.clauses.length > 2;
                  const instancesToShow = isExpanded ? clauseGroup.clauses : clauseGroup.clauses.slice(0, 2);
                  
                  return (
                    <div key={index} className="bg-white border border-gray-300 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold text-gray-800">
                          {clauseGroup.type?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </h3>
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-1 rounded text-xs font-bold ${
                            clauseGroup.risk_level === 'high'
                              ? 'bg-red-200 text-red-800'
                              : clauseGroup.risk_level === 'medium'
                              ? 'bg-yellow-200 text-yellow-800'
                              : 'bg-green-200 text-green-800'
                          }`}>
                            {clauseGroup.risk_level?.toUpperCase() || 'UNKNOWN'}
                          </span>
                          <span className="text-xs text-gray-500">
                            {clauseGroup.count} instance{clauseGroup.count !== 1 ? 's' : ''}
                          </span>
                        </div>
                      </div>
                      
                      <p className="text-sm text-gray-600 mb-3">{clauseGroup.description}</p>
                      
                      {clauseGroup.clauses && clauseGroup.clauses.length > 0 && (
                        <div className="space-y-2">
                          {/* Show instances based on expanded state */}
                          {instancesToShow.map((clause, clauseIndex) => (
                            <div key={clauseIndex} className="bg-gray-50 border border-gray-200 rounded p-3">
                              {clause.article && (
                                <div className="text-xs font-semibold text-blue-600 mb-1">
                                  Article {clause.article}
                                </div>
                              )}
                              <p className="text-sm text-gray-700 leading-relaxed">
                                {/* Always show complete summaries or full text - no truncation */}
                                {clause.summary ? (
                                  clause.summary
                                ) : (
                                  clause.text || 'No clause text available'
                                )}
                              </p>
                            </div>
                          ))}
                          
                          {/* Collapsible "Show more" / "Show less" button */}
                          {hasMoreInstances && (
                            <button
                              onClick={() => {
                                const newExpanded = new Set(expandedClauses);
                                if (isExpanded) {
                                  newExpanded.delete(clauseGroupKey);
                                } else {
                                  newExpanded.add(clauseGroupKey);
                                }
                                setExpandedClauses(newExpanded);
                              }}
                              className="w-full mt-2 px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 border border-blue-200 rounded-md transition-colors duration-150 flex items-center justify-center gap-2"
                            >
                              {isExpanded ? (
                                <>
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                                  </svg>
                                  Show Less
                                </>
                              ) : (
                                <>
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                  </svg>
                                  Show {clauseGroup.clauses.length - 2} More Instance{clauseGroup.clauses.length - 2 !== 1 ? 's' : ''}
                                </>
                              )}
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
          
          {/* Processing Status - Only show if no clauses yet or no partial results */}
          {(contract.status === 'processing' || contract.status === 'uploaded') && 
           !(contract.extracted_clauses && contract.extracted_clauses.length > 0) && (
            <div className="border-t pt-6 mt-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                  <div>
                    <p className="text-blue-800 font-semibold">
                      {contract.status === 'uploaded' 
                        ? 'Uploaded. Processing will start shortly...'
                        : contract.extracted_text 
                        ? 'Generating AI analysis... This may take 30-60 seconds.'
                        : 'Extracting text and analyzing contract... This may take 30-60 seconds.'}
                    </p>
                    <p className="text-blue-600 text-sm mt-1">
                      The page will automatically refresh when analysis is complete.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Progress indicator during AI analysis (when clauses already extracted) */}
          {(contract.status === 'processing' || contract.status === 'uploaded') && 
           contract.extracted_clauses && contract.extracted_clauses.length > 0 && 
           !contract.analysis_summary && (
            <div className="border-t pt-6 mt-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                  <div>
                    <p className="text-blue-800 font-semibold">
                      Generating AI summaries and risk analysis... Almost done!
                    </p>
                    <p className="text-blue-600 text-sm mt-1">
                      You can already see the extracted clauses below. AI analysis will complete shortly.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ContractDetail;

