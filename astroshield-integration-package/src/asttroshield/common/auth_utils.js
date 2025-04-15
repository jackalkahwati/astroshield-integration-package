/**
 * Authentication Utilities for AstroShield API
 * 
 * This module provides utilities for managing authentication with AstroShield services,
 * including token acquisition, refreshing, and validation.
 */

// Dependency for secure token storage
const KeytarModule = (() => {
  try {
    return require('keytar');
  } catch (err) {
    // Keytar is optional and only works in desktop environments
    return null;
  }
})();

class TokenManager {
  /**
   * Creates a new token manager
   * 
   * @param {Object} config Configuration object
   * @param {string} config.authServerUrl Base URL of the auth server
   * @param {string} config.clientId Client ID for authentication
   * @param {string} config.clientSecret Client secret for authentication
   * @param {string} config.scope OAuth scopes to request
   * @param {Function} config.acquireTokenFn Function to acquire a new token
   * @param {Function} config.refreshTokenFn Function to refresh an existing token
   * @param {number} config.refreshThresholdSeconds Seconds before expiry to trigger refresh (default: 300)
   * @param {boolean} config.useSecureStorage Whether to use secure storage via keytar (default: true)
   * @param {string} config.storageKey Key to use for secure storage (default: 'astroshield-auth')
   */
  constructor(config) {
    this.config = {
      refreshThresholdSeconds: 300, // 5 minutes by default
      useSecureStorage: true,
      storageKey: 'astroshield-auth',
      ...config
    };
    
    // Validate required config
    const requiredFields = ['authServerUrl', 'clientId', 'clientSecret'];
    for (const field of requiredFields) {
      if (!this.config[field]) {
        throw new Error(`TokenManager requires ${field} in configuration`);
      }
    }
    
    this.tokenData = null;
    this.tokenPromise = null;
    this.secureStorage = this.config.useSecureStorage && KeytarModule;
  }

  /**
   * Get the current token, acquiring or refreshing if necessary
   * 
   * @returns {Promise<Object>} Token object containing accessToken and other properties
   */
  async getToken() {
    // If we have a token promise in progress, reuse it
    if (this.tokenPromise) {
      return this.tokenPromise;
    }
    
    try {
      // If we have a token, check if it's still valid
      if (this.tokenData) {
        // Check expiration
        const now = Math.floor(Date.now() / 1000);
        const expiresAt = this.tokenData.acquiredAt + this.tokenData.expiresIn;
        
        // If token is still valid and not near expiration, return it
        if (now < expiresAt - this.config.refreshThresholdSeconds) {
          return this.tokenData;
        }
        
        // Token is near expiration, try to refresh
        if (this.tokenData.refreshToken) {
          return this.refreshToken();
        }
      }
      
      // Try to load token from secure storage if available
      if (!this.tokenData && this.secureStorage) {
        try {
          const storedToken = await KeytarModule.getPassword(
            this.config.storageKey,
            this.config.clientId
          );
          
          if (storedToken) {
            this.tokenData = JSON.parse(storedToken);
            
            // Check if the loaded token is still valid
            const now = Math.floor(Date.now() / 1000);
            const expiresAt = this.tokenData.acquiredAt + this.tokenData.expiresIn;
            
            if (now < expiresAt - this.config.refreshThresholdSeconds) {
              return this.tokenData;
            }
            
            // Try to refresh the loaded token
            if (this.tokenData.refreshToken) {
              return this.refreshToken();
            }
          }
        } catch (err) {
          // Ignore errors when loading from secure storage
          console.warn('Failed to load token from secure storage:', err.message);
        }
      }
      
      // If we get here, we need to acquire a new token
      this.tokenPromise = this.acquireNewToken();
      const token = await this.tokenPromise;
      this.tokenPromise = null;
      return token;
      
    } catch (error) {
      this.tokenPromise = null;
      throw error;
    }
  }

  /**
   * Acquire a new token
   * 
   * @returns {Promise<Object>} Token data
   * @private
   */
  async acquireNewToken() {
    // If an acquire function is provided, use it
    if (this.config.acquireTokenFn) {
      this.tokenData = await this.config.acquireTokenFn(this.config);
    } else {
      // Default token acquisition logic
      throw new Error('No token acquisition method provided');
    }
    
    // Add acquisition timestamp
    this.tokenData.acquiredAt = Math.floor(Date.now() / 1000);
    
    // Store in secure storage if available
    await this.storeToken();
    
    return this.tokenData;
  }

  /**
   * Refresh the current token
   * 
   * @returns {Promise<Object>} Refreshed token data
   */
  async refreshToken() {
    if (!this.tokenData || !this.tokenData.refreshToken) {
      return this.acquireNewToken();
    }
    
    try {
      this.tokenPromise = this._refreshTokenInternal();
      const token = await this.tokenPromise;
      this.tokenPromise = null;
      return token;
    } catch (error) {
      this.tokenPromise = null;
      // If refresh fails, try acquiring a new token
      return this.acquireNewToken();
    }
  }
  
  /**
   * Internal method to refresh token
   * 
   * @returns {Promise<Object>} Refreshed token data
   * @private
   */
  async _refreshTokenInternal() {
    // If a refresh function is provided, use it
    if (this.config.refreshTokenFn) {
      this.tokenData = await this.config.refreshTokenFn(
        this.config,
        this.tokenData.refreshToken
      );
    } else {
      // Default token refresh logic
      throw new Error('No token refresh method provided');
    }
    
    // Update the acquisition timestamp
    this.tokenData.acquiredAt = Math.floor(Date.now() / 1000);
    
    // Store in secure storage if available
    await this.storeToken();
    
    return this.tokenData;
  }
  
  /**
   * Store the current token in secure storage if available
   * 
   * @returns {Promise<void>}
   * @private
   */
  async storeToken() {
    if (this.secureStorage && this.tokenData) {
      try {
        await KeytarModule.setPassword(
          this.config.storageKey,
          this.config.clientId,
          JSON.stringify(this.tokenData)
        );
      } catch (err) {
        // Log but don't fail if secure storage fails
        console.warn('Failed to store token in secure storage:', err.message);
      }
    }
  }
  
  /**
   * Clear current token and remove from secure storage
   * 
   * @returns {Promise<void>}
   */
  async clearTokens() {
    this.tokenData = null;
    this.tokenPromise = null;
    
    if (this.secureStorage) {
      try {
        await KeytarModule.deletePassword(
          this.config.storageKey,
          this.config.clientId
        );
      } catch (err) {
        // Log but don't fail if secure storage fails
        console.warn('Failed to clear token from secure storage:', err.message);
      }
    }
  }
}

module.exports = {
  TokenManager
}; 