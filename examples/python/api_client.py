#!/usr/bin/env python3
"""
AstroShield API Client Example

This script demonstrates how to interact with the AstroShield API using Python.
It includes examples for authentication, retrieving spacecraft data, and handling
pagination.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("astroshield-client")

class AstroShieldClient:
    """Client for interacting with the AstroShield API."""
    
    def __init__(
        self, 
        base_url: str = "https://api.astroshield.com",
        username: Optional[str] = None,
        password: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the AstroShield API client.
        
        Args:
            base_url: Base URL of the AstroShield API
            username: Username for JWT authentication
            password: Password for JWT authentication
            api_key: API key for API key authentication
        """
        self.base_url = base_url.rstrip("/")
        self.username = username or os.environ.get("ASTROSHIELD_USERNAME")
        self.password = password or os.environ.get("ASTROSHIELD_PASSWORD")
        self.api_key = api_key or os.environ.get("ASTROSHIELD_API_KEY")
        self.token = None
        self.token_expiry = None
        
        # Validate authentication options
        if not self.api_key and not (self.username and self.password):
            raise ValueError(
                "Either API key or username/password must be provided"
            )
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers for API requests, including authentication.
        
        Returns:
            Dictionary of headers
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Use API key if available
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            return headers
        
        # Otherwise use JWT token
        if not self.token or (
            self.token_expiry and datetime.now() >= self.token_expiry
        ):
            self._authenticate()
        
        headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _authenticate(self) -> None:
        """
        Authenticate with the API using username and password.
        
        Raises:
            requests.exceptions.HTTPError: If authentication fails
        """
        url = f"{self.base_url}/auth/token"
        payload = {
            "username": self.username,
            "password": self.password
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            self.token = data["access_token"]
            # Set token expiry time (with a small buffer)
            expires_in = data.get("expires_in", 3600)
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)
            
            logger.info("Successfully authenticated with the API")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        retry_auth: bool = True
    ) -> Dict[str, Any]:
        """
        Make a request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            data: Request body data
            retry_auth: Whether to retry with fresh authentication on 401
            
        Returns:
            Response data as dictionary
            
        Raises:
            requests.exceptions.HTTPError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data
            )
            response.raise_for_status()
            
            # Return empty dict for 204 No Content
            if response.status_code == 204:
                return {}
                
            return response.json()
        except requests.exceptions.HTTPError as e:
            # If unauthorized and using JWT, try to re-authenticate once
            if (
                response.status_code == 401 
                and retry_auth 
                and not self.api_key
            ):
                logger.info("Token expired, re-authenticating...")
                self._authenticate()
                return self._make_request(
                    method, endpoint, params, data, retry_auth=False
                )
            
            logger.error(f"API request failed: {e}")
            # Include error response in the exception
            if hasattr(e.response, 'text'):
                try:
                    error_data = json.loads(e.response.text)
                    logger.error(f"Error details: {error_data}")
                except json.JSONDecodeError:
                    logger.error(f"Error response: {e.response.text}")
            
            raise
    
    def get_health(self) -> Dict[str, Any]:
        """
        Get API health status.
        
        Returns:
            Health status information
        """
        return self._make_request("GET", "/health")
    
    def list_spacecraft(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a list of spacecraft.
        
        Args:
            page: Page number for pagination
            limit: Number of items per page
            status: Filter by status (active, inactive, all)
            
        Returns:
            Dictionary containing spacecraft data and pagination metadata
        """
        params = {
            "page": page,
            "limit": limit
        }
        
        if status:
            params["status"] = status
        
        return self._make_request("GET", "/api/v1/spacecraft", params=params)
    
    def get_spacecraft(self, spacecraft_id: int) -> Dict[str, Any]:
        """
        Get details for a specific spacecraft.
        
        Args:
            spacecraft_id: ID of the spacecraft
            
        Returns:
            Spacecraft details
        """
        return self._make_request("GET", f"/api/v1/spacecraft/{spacecraft_id}")
    
    def create_spacecraft(self, spacecraft_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new spacecraft.
        
        Args:
            spacecraft_data: Spacecraft data
            
        Returns:
            Created spacecraft details
        """
        return self._make_request("POST", "/api/v1/spacecraft", data=spacecraft_data)
    
    def update_spacecraft(
        self, 
        spacecraft_id: int, 
        spacecraft_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing spacecraft.
        
        Args:
            spacecraft_id: ID of the spacecraft
            spacecraft_data: Updated spacecraft data
            
        Returns:
            Updated spacecraft details
        """
        return self._make_request(
            "PUT", 
            f"/api/v1/spacecraft/{spacecraft_id}", 
            data=spacecraft_data
        )
    
    def delete_spacecraft(self, spacecraft_id: int) -> None:
        """
        Delete a spacecraft.
        
        Args:
            spacecraft_id: ID of the spacecraft
        """
        self._make_request("DELETE", f"/api/v1/spacecraft/{spacecraft_id}")
    
    def get_conjunctions(
        self,
        spacecraft_id: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        min_probability: Optional[float] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get conjunction events.
        
        Args:
            spacecraft_id: Filter by spacecraft ID
            start_time: Start time in ISO 8601 format
            end_time: End time in ISO 8601 format
            min_probability: Minimum collision probability
            page: Page number for pagination
            limit: Number of items per page
            
        Returns:
            Dictionary containing conjunction data and pagination metadata
        """
        params = {
            "page": page,
            "limit": limit
        }
        
        if spacecraft_id:
            params["spacecraft_id"] = spacecraft_id
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if min_probability:
            params["min_probability"] = min_probability
        
        return self._make_request("GET", "/api/v1/conjunctions", params=params)
    
    def get_conjunction(self, conjunction_id: int) -> Dict[str, Any]:
        """
        Get details for a specific conjunction event.
        
        Args:
            conjunction_id: ID of the conjunction event
            
        Returns:
            Conjunction event details
        """
        return self._make_request("GET", f"/api/v1/conjunctions/{conjunction_id}")
    
    def get_cyber_threats(
        self,
        spacecraft_id: int,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        severity: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get cyber threats for a spacecraft.
        
        Args:
            spacecraft_id: ID of the spacecraft
            start_time: Start time in ISO 8601 format
            end_time: End time in ISO 8601 format
            severity: Filter by severity (low, medium, high, critical)
            page: Page number for pagination
            limit: Number of items per page
            
        Returns:
            Dictionary containing cyber threat data and pagination metadata
        """
        params = {
            "page": page,
            "limit": limit
        }
        
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if severity:
            params["severity"] = severity
        
        return self._make_request(
            "GET", 
            f"/api/v1/spacecraft/{spacecraft_id}/cyber-threats", 
            params=params
        )
    
    def get_stability_data(
        self,
        spacecraft_id: Optional[int] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get stability data.
        
        Args:
            spacecraft_id: Filter by spacecraft ID
            start_time: Start time in ISO 8601 format
            end_time: End time in ISO 8601 format
            page: Page number for pagination
            limit: Number of items per page
            
        Returns:
            Dictionary containing stability data and pagination metadata
        """
        params = {
            "page": page,
            "limit": limit
        }
        
        if spacecraft_id:
            params["spacecraft_id"] = spacecraft_id
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        
        return self._make_request("GET", "/api/v1/stability/data", params=params)
    
    def get_telemetry_data(
        self,
        spacecraft_id: int,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        subsystem: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get telemetry data for a spacecraft.
        
        Args:
            spacecraft_id: ID of the spacecraft
            start_time: Start time in ISO 8601 format
            end_time: End time in ISO 8601 format
            subsystem: Filter by subsystem (power, thermal, attitude, communications)
            page: Page number for pagination
            limit: Number of items per page
            
        Returns:
            Dictionary containing telemetry data and pagination metadata
        """
        params = {
            "page": page,
            "limit": limit
        }
        
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if subsystem:
            params["subsystem"] = subsystem
        
        return self._make_request(
            "GET", 
            f"/api/v1/spacecraft/{spacecraft_id}/telemetry", 
            params=params
        )
    
    def create_webhook(
        self,
        url: str,
        events: List[str],
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a webhook subscription.
        
        Args:
            url: Webhook URL
            events: List of event types to subscribe to
            secret: Secret for webhook signature verification
            
        Returns:
            Created webhook details
        """
        data = {
            "url": url,
            "events": events
        }
        
        if secret:
            data["secret"] = secret
        
        return self._make_request("POST", "/api/v1/webhooks", data=data)


def main():
    """Example usage of the AstroShield API client."""
    # Create client instance
    client = AstroShieldClient(
        base_url="http://localhost:8000",
        username="user@example.com",
        password="password123"
    )
    
    try:
        # Check API health
        health = client.get_health()
        print(f"API Health: {health}")
        
        # List spacecraft
        spacecraft_list = client.list_spacecraft(status="active")
        print(f"Found {spacecraft_list['meta']['total']} active spacecraft")
        
        # If there are spacecraft, get details for the first one
        if spacecraft_list["data"]:
            spacecraft = spacecraft_list["data"][0]
            spacecraft_id = spacecraft["id"]
            
            # Get detailed information
            spacecraft_details = client.get_spacecraft(spacecraft_id)
            print(f"Spacecraft details: {json.dumps(spacecraft_details, indent=2)}")
            
            # Get cyber threats for this spacecraft
            now = datetime.now()
            one_month_ago = now - timedelta(days=30)
            
            cyber_threats = client.get_cyber_threats(
                spacecraft_id=spacecraft_id,
                start_time=one_month_ago.isoformat(),
                end_time=now.isoformat(),
                severity="high"
            )
            
            print(f"Found {cyber_threats['meta']['total']} high severity cyber threats")
            
            # Get telemetry data
            telemetry = client.get_telemetry_data(
                spacecraft_id=spacecraft_id,
                start_time=one_month_ago.isoformat(),
                end_time=now.isoformat(),
                subsystem="power"
            )
            
            print(f"Found {telemetry['meta']['total']} telemetry records")
        
        # Create a new spacecraft
        new_spacecraft = {
            "name": "Example Satellite",
            "norad_id": 12345,
            "status": "active",
            "orbit_type": "GEO",
            "launch_date": "2023-01-01T00:00:00Z",
            "orbital_parameters": {
                "semi_major_axis": 42164,
                "eccentricity": 0.0002,
                "inclination": 0.1,
                "raan": 95.5,
                "argument_of_perigee": 270,
                "mean_anomaly": 0,
                "epoch": "2023-05-01T12:00:00Z"
            },
            "physical_parameters": {
                "mass": 5000,
                "length": 15,
                "width": 3,
                "height": 3,
                "cross_section": 45
            }
        }
        
        created = client.create_spacecraft(new_spacecraft)
        print(f"Created new spacecraft with ID: {created['id']}")
        
        # Update the spacecraft
        update_data = {
            "status": "inactive",
            "orbital_parameters": {
                "semi_major_axis": 42165,
                "eccentricity": 0.0003
            }
        }
        
        updated = client.update_spacecraft(created["id"], update_data)
        print(f"Updated spacecraft status to: {updated['status']}")
        
        # Delete the spacecraft
        client.delete_spacecraft(created["id"])
        print(f"Deleted spacecraft with ID: {created['id']}")
        
        # Create a webhook
        webhook = client.create_webhook(
            url="https://example.com/webhook",
            events=["conjunction.detected", "cyber_threat.detected"],
            secret="your-webhook-secret"
        )
        
        print(f"Created webhook with ID: {webhook['id']}")
        
    except requests.exceptions.HTTPError as e:
        print(f"API request failed: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 