/**
 * API Service Layer
 * 
 * This file handles all communication with the Django REST API backend.
 * 
 * What is a service layer?
 * - Centralized place for all API calls
 * - Makes it easy to change API endpoints in one place
 * - Handles authentication tokens automatically
 * - Provides reusable functions for components
 */

import axios from 'axios';

// Base URL for Django API
// This is where your Django backend is running
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Create axios instance with default configuration
// Axios is a library that makes HTTP requests (like fetch, but easier)
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',  // Tell server we're sending JSON
  },
});

/**
 * Request Interceptor
 * 
 * This runs BEFORE every API request.
 * It automatically adds the JWT token to the Authorization header.
 * 
 * How it works:
 * 1. User logs in → gets JWT token
 * 2. Token is stored in localStorage
 * 3. Before each API request, this function runs
 * 4. It gets the token from localStorage
 * 5. Adds it to the request header: "Authorization: Bearer {token}"
 */
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage (where we store it after login)
    const token = localStorage.getItem('access_token');
    
    // If token exists, add it to the request header
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      // This becomes: Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
    }
    
    return config;  // Return the modified config
  },
  (error) => {
    // If something goes wrong, return the error
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor
 * 
 * This runs AFTER every API response.
 * If we get a 401 (Unauthorized), it means the token expired.
 * We can handle token refresh here if needed.
 */
api.interceptors.response.use(
  (response) => {
    // If request was successful, just return the response
    return response;
  },
  async (error) => {
    // If we get 401 Unauthorized, token might be expired
    if (error.response?.status === 401) {
      // Clear the stored token
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      // Redirect to login page (we'll handle this later)
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

// ============================================
// AUTHENTICATION API FUNCTIONS
// ============================================

/**
 * Login function
 * 
 * Sends username and password to /api/token/
 * Returns access token and refresh token
 * 
 * @param {string} username - User's username
 * @param {string} password - User's password
 * @returns {Promise} - Contains access and refresh tokens
 */
export const login = async (username, password) => {
  try {
    // Send POST request to /api/token/
    const response = await api.post('/token/', {
      username: username,
      password: password,
    });
    
    // Response contains: { access: "...", refresh: "..." }
    const { access, refresh } = response.data;
    
    // Store tokens in localStorage (browser storage)
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    localStorage.setItem('username', username);  // Store username for display
    
    return response.data;  // Return tokens
  } catch (error) {
    // If login fails, throw error so component can handle it
    throw error;
  }
};

/**
 * Logout function
 * 
 * Removes tokens and user data from localStorage
 */
export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('username');
};

/**
 * Refresh access token
 * 
 * When access token expires (after 1 hour), use refresh token to get a new one
 * 
 * @returns {Promise} - New access token
 */
export const refreshToken = async () => {
  try {
    const refresh = localStorage.getItem('refresh_token');
    
    if (!refresh) {
      throw new Error('No refresh token available');
    }
    
    // Send refresh token to /api/token/refresh/
    const response = await api.post('/token/refresh/', {
      refresh: refresh,
    });
    
    // Update stored access token
    const { access } = response.data;
    localStorage.setItem('access_token', access);
    
    return access;
  } catch (error) {
    // If refresh fails, logout user
    logout();
    throw error;
  }
};

// ============================================
// CONTRACT API FUNCTIONS
// ============================================

/**
 * Get all contracts for the current user
 * 
 * GET /api/contracts/
 * Returns a list of contracts (paginated)
 */
export const getContracts = async () => {
  try {
    const response = await api.get('/contracts/');
    return response.data;  // Returns: { count, next, previous, results: [...] }
  } catch (error) {
    throw error;
  }
};

/**
 * Get a specific contract by ID
 * 
 * GET /api/contracts/{id}/
 * Returns full contract details
 */
export const getContract = async (id) => {
  try {
    const response = await api.get(`/contracts/${id}/`);
    return response.data;  // Returns contract object
  } catch (error) {
    throw error;
  }
};

/**
 * Upload a new contract
 * 
 * POST /api/contracts/
 * Requires FormData with title, description, and file
 * 
 * @param {FormData} formData - FormData object with contract data
 * @returns {Promise} - Created contract object
 */
export const uploadContract = async (formData) => {
  try {
    // For file uploads, we need to send FormData
    // Note: Don't set Content-Type header - browser will set it automatically with boundary
    const response = await api.post('/contracts/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',  // Required for file uploads
      },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Update a contract
 * 
 * PATCH /api/contracts/{id}/
 * Updates only the fields you send
 */
export const updateContract = async (id, data) => {
  try {
    const response = await api.patch(`/contracts/${id}/`, data);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Delete a contract
 * 
 * DELETE /api/contracts/{id}/
 */
export const deleteContract = async (id) => {
  try {
    await api.delete(`/contracts/${id}/`);
  } catch (error) {
    throw error;
  }
};

/**
 * Mark contract as analyzed
 * 
 * POST /api/contracts/{id}/mark_analyzed/
 * Custom action endpoint
 */
export const markContractAnalyzed = async (id) => {
  try {
    const response = await api.post(`/contracts/${id}/mark_analyzed/`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Export the api instance in case we need it directly
export default api;

