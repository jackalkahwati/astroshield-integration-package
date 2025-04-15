/**
 * AstroShield Authentication Example
 * 
 * This example demonstrates how to use the TokenManager to handle authentication
 * with automatic token refresh for AstroShield API endpoints.
 */

const axios = require('axios');
const { TokenManager } = require('../auth_utils');

/**
 * Example API client with authentication refresh
 */
class AstroShieldApiClient {
  /**
   * Create a new API client
   * 
   * @param {Object} config Configuration object
   */
  constructor(config) {
    // Configure the token manager
    this.tokenManager = new TokenManager({
      authServerUrl: config.authServerUrl || 'https://auth.astroshield.io/oauth/token',
      clientId: config.clientId,
      clientSecret: config.clientSecret,
      scope: 'read write',
      
      // Function to acquire a new token
      acquireTokenFn: async (config) => {
        try {
          const response = await axios.post(config.authServerUrl, {
            grant_type: 'client_credentials',
            client_id: config.clientId,
            client_secret: config.clientSecret,
            scope: config.scope
          });
          
          return {
            accessToken: response.data.access_token,
            refreshToken: response.data.refresh_token,
            expiresIn: response.data.expires_in
          };
        } catch (error) {
          console.error('Token acquisition failed:', error.message);
          throw new Error(`Failed to acquire token: ${error.message}`);
        }
      },
      
      // Function to refresh an existing token
      refreshTokenFn: async (config, refreshToken) => {
        try {
          const response = await axios.post(config.authServerUrl, {
            grant_type: 'refresh_token',
            refresh_token: refreshToken,
            client_id: config.clientId,
            client_secret: config.clientSecret
          });
          
          return {
            accessToken: response.data.access_token,
            refreshToken: response.data.refresh_token || refreshToken, // Some OAuth servers don't return a new refresh token
            expiresIn: response.data.expires_in
          };
        } catch (error) {
          console.error('Token refresh failed:', error.message);
          throw new Error(`Failed to refresh token: ${error.message}`);
        }
      }
    });
    
    // Base URL for API requests
    this.baseUrl = config.baseUrl || 'https://api.astroshield.io/v1';
    
    // Create axios instance with interceptors
    this.api = this._createAxiosInstance();
  }
  
  /**
   * Create an axios instance with auth token management
   * 
   * @returns {Object} Configured axios instance
   * @private
   */
  _createAxiosInstance() {
    const instance = axios.create({
      baseURL: this.baseUrl,
      timeout: 10000
    });
    
    // Add request interceptor to inject the auth token
    instance.interceptors.request.use(async (config) => {
      try {
        // Get token (will refresh automatically if needed)
        const tokenData = await this.tokenManager.getToken();
        
        // Add the token to the Authorization header
        config.headers.Authorization = `Bearer ${tokenData.accessToken}`;
        return config;
      } catch (error) {
        return Promise.reject(error);
      }
    });
    
    // Add response interceptor to handle 401 errors (token expired)
    instance.interceptors.response.use(
      (response) => response,
      async (error) => {
        // Get the original request configuration
        const originalRequest = error.config;
        
        // If the error is due to an expired token and we haven't retried yet
        if (error.response?.status === 401 && !originalRequest._retry) {
          // Mark this request as retried to prevent infinite loops
          originalRequest._retry = true;
          
          try {
            // Force a token refresh
            await this.tokenManager.refreshToken();
            
            // Retry the original request with the new token
            // The request interceptor above will add the new token
            return instance(originalRequest);
          } catch (refreshError) {
            // If refresh fails, pass through the original error
            return Promise.reject(error);
          }
        }
        
        // For other errors, just pass them through
        return Promise.reject(error);
      }
    );
    
    return instance;
  }
  
  /**
   * Get space objects
   * 
   * @param {Object} params Query parameters
   * @returns {Promise<Array>} List of space objects
   */
  async getSpaceObjects(params = {}) {
    try {
      const response = await this.api.get('/space-objects', { params });
      return response.data;
    } catch (error) {
      console.error('Failed to get space objects:', error.message);
      throw error;
    }
  }
  
  /**
   * Get a specific space object by ID
   * 
   * @param {string} id Space object ID
   * @returns {Promise<Object>} Space object details
   */
  async getSpaceObject(id) {
    try {
      const response = await this.api.get(`/space-objects/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to get space object ${id}:`, error.message);
      throw error;
    }
  }
}

/**
 * Example usage
 */
async function example() {
  // Create client with credentials
  const client = new AstroShieldApiClient({
    clientId: 'your-client-id',
    clientSecret: 'your-client-secret',
    // Optional configuration:
    // baseUrl: 'https://api.astroshield.io/v1',
    // authServerUrl: 'https://auth.astroshield.io/oauth/token'
  });
  
  try {
    // This call will automatically acquire a token
    const spaceObjects = await client.getSpaceObjects({ 
      limit: 10,
      orbit_type: 'LEO'
    });
    console.log('Space objects:', spaceObjects);
    
    // Make more API calls
    // If the token expires, it will automatically refresh
    
    // If the first call to an object fails with 401, it will
    // automatically refresh the token and retry
    if (spaceObjects.length > 0) {
      const details = await client.getSpaceObject(spaceObjects[0].id);
      console.log('Space object details:', details);
    }
  } catch (error) {
    console.error('API request failed:', error.message);
  }
}

// Run the example
// example();

// Export for reuse
module.exports = {
  AstroShieldApiClient
}; 