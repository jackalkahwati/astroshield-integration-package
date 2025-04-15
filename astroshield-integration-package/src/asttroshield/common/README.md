# AstroShield Common Utilities

This directory contains common utilities and helper functions that are shared across the AstroShield integration package.

## Authentication Utilities

The `auth_utils.js` module provides a robust solution for handling authentication with AstroShield services, including token management and automatic refresh.

### Features

- Automatic token refresh when close to expiration
- Request queueing during token refresh operations
- Axios instance creation with pre-configured interceptors
- Error handling for authentication failures
- Support for concurrent requests with single token refresh

### Usage

```javascript
const { TokenManager } = require('./auth_utils');

// Configuration
const authConfig = {
  authUrl: 'https://api.astroshield.com/auth/token',
  clientId: 'YOUR_CLIENT_ID', 
  clientSecret: 'YOUR_CLIENT_SECRET',
  refreshThreshold: 300 // Refresh token if it expires in less than 5 minutes
};

// Create token manager instance
const tokenManager = new TokenManager(authConfig);

// Get an authenticated axios instance
const api = tokenManager.createAxiosInstance();

// Make authenticated requests
async function fetchData() {
  try {
    const response = await api.get('https://api.astroshield.com/data/observations');
    return response.data;
  } catch (error) {
    console.error('API request failed:', error.message);
    throw error;
  }
}
```

### Example

A complete example of using the authentication utilities is provided in `examples/auth_example.js`.

## Other Utilities

- `logging.js` - Standardized logging configurations
- `validation.js` - Common validation functions for API requests/responses
- `errors.js` - Custom error types for the AstroShield system

## Best Practices

1. **Security**:
   - Never hard-code credentials in your application
   - Store secrets in environment variables or secure configuration stores
   - Protect refresh tokens with appropriate security measures

2. **Performance**:
   - The TokenManager is designed to handle concurrent requests efficiently
   - A single instance should be reused across your application

3. **Error Handling**:
   - Always implement proper error handling for authentication failures
   - Consider implementing retry strategies for transient failures

## Further Documentation

For more detailed information about the AstroShield API authentication requirements, refer to the 
[Official AstroShield API Documentation](https://docs.astroshield.com/api/authentication). 