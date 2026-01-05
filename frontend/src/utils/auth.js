/**
 * Authentication Utilities
 * 
 * Helper functions for checking authentication status
 */

/**
 * Check if user is logged in
 * 
 * @returns {boolean} - True if access token exists in localStorage
 */
export const isAuthenticated = () => {
  const token = localStorage.getItem('access_token');
  return !!token;  // Convert to boolean (!!null = false, !!token = true)
};

/**
 * Get the stored access token
 * 
 * @returns {string|null} - Access token or null if not found
 */
export const getToken = () => {
  return localStorage.getItem('access_token');
};

