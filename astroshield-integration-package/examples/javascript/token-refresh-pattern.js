/**
 * Example of token refresh pattern for AstroShield API integration
 * 
 * This example demonstrates how to handle authentication token refresh
 * in a long-running application to maintain continuous API access.
 */

const axios = require('axios');

class AstroShieldClient {
  constructor(config) {
    this.baseUrl = config.baseUrl || 'https://api.astroshield.com';
    this.username = config.username;
    this.password = config.password;
    this.apiKey = config.apiKey;
    
    this.token = null;
    this.tokenExpiry = null;
    this.refreshThresholdMs = config.refreshThresholdMs || 5 * 60 * 1000; // 5 minutes
    
    // Create axios instance with interceptors
    this.api = axios.create({
      baseURL: this.baseUrl,
      timeout: 10000
    });
    
    // Add request interceptor to handle token insertion and refresh
    this.api.interceptors.request.use(
      async (config) => {
        // Check if we need to get a token
        if (this.needsAuthentication(config)) {
          await this.ensureValidToken();
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    // Add response interceptor to handle token expiration
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        // If 401 error and not already retrying, refresh token and retry
        if (error.response && 
            error.response.status === 401 && 
            !originalRequest._retry) {
          
          originalRequest._retry = true;
          
          try {
            // Force token refresh
            this.token = null;
            await this.ensureValidToken();
            
            // Retry with new token
            originalRequest.headers.Authorization = `Bearer ${this.token}`;
            return this.api(originalRequest);
          } catch (refreshError) {
            return Promise.reject(refreshError);
          }
        }
        
        return Promise.reject(error);
      }
    );
  }
  
  /**
   * Check if the request needs authentication
   */
  needsAuthentication(config) {
    // Skip authentication for login endpoint
    if (config.url === '/auth/token') {
      return false;
    }
    
    // Skip if already has Authorization header
    if (config.headers && config.headers.Authorization) {
      return false;
    }
    
    return true;
  }
  
  /**
   * Ensure we have a valid token, refreshing if necessary
   */
  async ensureValidToken() {
    // If token exists and not expired (with threshold), use it
    if (this.token && this.tokenExpiry) {
      const now = Date.now();
      if (now < this.tokenExpiry - this.refreshThresholdMs) {
        return;
      }
      console.log('Token nearing expiry, refreshing...');
    }
    
    // Get new token
    await this.refreshToken();
  }
  
  /**
   * Get a new token from the API
   */
  async refreshToken() {
    try {
      let response;
      
      if (this.apiKey) {
        // Use API key authentication if available
        response = await axios.post(`${this.baseUrl}/auth/token`, {}, {
          headers: {
            'X-API-Key': this.apiKey
          }
        });
      } else {
        // Otherwise use username/password
        response = await axios.post(`${this.baseUrl}/auth/token`, {
          username: this.username,
          password: this.password
        });
      }
      
      // Store the token and calculate expiry time
      this.token = response.data.token;
      
      // Parse expiry from token or use default (1 hour)
      const expiresIn = response.data.expiresIn || 3600;
      this.tokenExpiry = Date.now() + (expiresIn * 1000);
      
      console.log('Token refreshed successfully');
    } catch (error) {
      console.error('Failed to refresh token:', error.message);
      throw new Error('Authentication failed: ' + error.message);
    }
  }
  
  /**
   * Example API method using the authenticated client
   */
  async getSpacecraftData(spacecraftId) {
    try {
      const response = await this.api.get(`/api/v1/spacecraft/${spacecraftId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching spacecraft data:', error.message);
      throw error;
    }
  }
  
  /**
   * Example API method for Kafka topic management
   */
  async getKafkaTopics() {
    try {
      const response = await this.api.get('/api/v1/kafka/topics');
      return response.data;
    } catch (error) {
      console.error('Error fetching Kafka topics:', error.message);
      throw error;
    }
  }
}

// Example usage
async function runExample() {
  // Create client with authentication details
  const client = new AstroShieldClient({
    baseUrl: process.env.ASTROSHIELD_API_URL,
    username: process.env.ASTROSHIELD_USERNAME,
    password: process.env.ASTROSHIELD_PASSWORD,
    // Or use API key instead:
    // apiKey: process.env.ASTROSHIELD_API_KEY,
    refreshThresholdMs: 10 * 60 * 1000 // 10 minutes
  });
  
  try {
    // Example API calls
    const spacecraft = await client.getSpacecraftData('SAT12345');
    console.log('Spacecraft data:', spacecraft);
    
    const topics = await client.getKafkaTopics();
    console.log('Available Kafka topics:', topics);
    
    // Simulate a long-running application with periodic API calls
    setInterval(async () => {
      try {
        const refreshedData = await client.getSpacecraftData('SAT12345');
        console.log('Refreshed data timestamp:', refreshedData.lastUpdated);
      } catch (error) {
        console.error('Periodic update failed:', error.message);
      }
    }, 15 * 60 * 1000); // Every 15 minutes
  } catch (error) {
    console.error('Example failed:', error.message);
  }
}

// Only run example if this file is executed directly
if (require.main === module) {
  runExample().catch(console.error);
}

module.exports = { AstroShieldClient }; 