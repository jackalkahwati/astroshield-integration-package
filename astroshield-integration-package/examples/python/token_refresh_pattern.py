"""
Example of token refresh pattern for AstroShield API integration

This example demonstrates how to handle authentication token refresh
in a long-running Python application to maintain continuous API access.
"""

import os
import time
import threading
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class AstroShieldClient:
    """Client for AstroShield API with automatic token refresh"""
    
    def __init__(self, 
                 base_url: str = "https://api.astroshield.com",
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 api_key: Optional[str] = None,
                 refresh_threshold_sec: int = 300):  # 5 minutes
        """
        Initialize the AstroShield API client
        
        Args:
            base_url: Base URL for the AstroShield API
            username: Username for authentication (if not using API key)
            password: Password for authentication (if not using API key)
            api_key: API key for authentication (if not using username/password)
            refresh_threshold_sec: Time in seconds before token expiry to trigger a refresh
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.api_key = api_key
        self.refresh_threshold_sec = refresh_threshold_sec
        
        # Token state
        self.token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self._token_lock = threading.RLock()
        self._session = requests.Session()
        
        # For logging purposes only
        self.refresh_count = 0
    
    def _headers(self) -> Dict[str, str]:
        """
        Get headers including authorization if token is available
        
        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        return headers
    
    def refresh_token(self) -> None:
        """
        Get a new token from the API
        
        Raises:
            Exception: If authentication fails
        """
        with self._token_lock:
            try:
                if self.api_key:
                    # Use API key authentication if available
                    response = requests.post(
                        f"{self.base_url}/auth/token",
                        headers={'X-API-Key': self.api_key}
                    )
                else:
                    # Otherwise use username/password
                    response = requests.post(
                        f"{self.base_url}/auth/token",
                        json={
                            'username': self.username,
                            'password': self.password
                        }
                    )
                
                response.raise_for_status()
                data = response.json()
                
                # Store the token and calculate expiry time
                self.token = data['token']
                
                # Parse expiry from token or use default (1 hour)
                expires_in = data.get('expiresIn', 3600)
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                
                self.refresh_count += 1
                print(f"Token refreshed successfully (#{self.refresh_count})")
                
            except Exception as e:
                print(f"Failed to refresh token: {str(e)}")
                self.token = None
                self.token_expiry = None
                raise Exception(f"Authentication failed: {str(e)}")
    
    def ensure_valid_token(self) -> None:
        """
        Ensure we have a valid token, refreshing if necessary
        
        Raises:
            Exception: If authentication fails
        """
        with self._token_lock:
            # If token exists and not near expiry, use it
            if self.token and self.token_expiry:
                time_until_expiry = (self.token_expiry - datetime.now()).total_seconds()
                if time_until_expiry > self.refresh_threshold_sec:
                    return
                print("Token nearing expiry, refreshing...")
            
            # Get new token
            self.refresh_token()
    
    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        """
        Make an authenticated request to the API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            **kwargs: Additional arguments to pass to requests
        
        Returns:
            HTTP response
            
        Raises:
            Exception: If the request fails
        """
        # Skip authentication for token endpoint
        needs_auth = not path.endswith('/auth/token')
        
        url = f"{self.base_url}/{path.lstrip('/')}"
        
        if needs_auth:
            self.ensure_valid_token()
            kwargs.setdefault('headers', {}).update(self._headers())
        
        try:
            response = self._session.request(method, url, **kwargs)
            
            # If unauthorized, try refreshing token once and retry
            if response.status_code == 401 and needs_auth:
                print("Request unauthorized, refreshing token and retrying...")
                self.token = None  # Force refresh
                self.ensure_valid_token()
                
                # Update headers with new token
                kwargs.setdefault('headers', {}).update(self._headers())
                
                # Retry request
                response = self._session.request(method, url, **kwargs)
            
            response.raise_for_status()
            return response
            
        except requests.RequestException as e:
            print(f"API request failed: {str(e)}")
            raise
    
    def get(self, path: str, **kwargs) -> Dict[str, Any]:
        """
        Make a GET request to the API
        
        Args:
            path: API endpoint path
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            JSON response as dictionary
        """
        response = self.request('GET', path, **kwargs)
        return response.json()
    
    def post(self, path: str, **kwargs) -> Dict[str, Any]:
        """
        Make a POST request to the API
        
        Args:
            path: API endpoint path
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            JSON response as dictionary
        """
        response = self.request('POST', path, **kwargs)
        return response.json()
    
    # Example API methods
    
    def get_spacecraft_data(self, spacecraft_id: str) -> Dict[str, Any]:
        """
        Get data for a specific spacecraft
        
        Args:
            spacecraft_id: ID of the spacecraft
            
        Returns:
            Spacecraft data
        """
        return self.get(f"/api/v1/spacecraft/{spacecraft_id}")
    
    def get_kafka_topics(self) -> Dict[str, Any]:
        """
        Get available Kafka topics
        
        Returns:
            List of Kafka topics
        """
        return self.get("/api/v1/kafka/topics")


def run_example():
    """Example usage of the AstroShield client"""
    # Create client with authentication details
    client = AstroShieldClient(
        base_url=os.environ.get('ASTROSHIELD_API_URL', 'https://api.astroshield.com'),
        username=os.environ.get('ASTROSHIELD_USERNAME'),
        password=os.environ.get('ASTROSHIELD_PASSWORD'),
        # Or use API key instead:
        # api_key=os.environ.get('ASTROSHIELD_API_KEY'),
        refresh_threshold_sec=600  # 10 minutes
    )
    
    try:
        # Example API calls
        spacecraft = client.get_spacecraft_data('SAT12345')
        print('Spacecraft data:', spacecraft)
        
        topics = client.get_kafka_topics()
        print('Available Kafka topics:', topics)
        
        # Simulate a long-running application with periodic API calls
        while True:
            try:
                # Sleep for 15 minutes
                time.sleep(15 * 60)
                
                # Make a periodic API call
                refreshed_data = client.get_spacecraft_data('SAT12345')
                print('Refreshed data timestamp:', refreshed_data.get('lastUpdated'))
                
            except KeyboardInterrupt:
                print("Stopping example")
                break
            except Exception as e:
                print(f"Periodic update failed: {str(e)}")
                # Continue running despite errors
    
    except Exception as e:
        print(f"Example failed: {str(e)}")


if __name__ == "__main__":
    run_example() 