"""
UDL API Client

This module provides a client for interacting with the Unified Data Library (UDL) APIs.
"""

import json
import logging
import os
import time
import base64
from typing import Dict, List, Optional, Union, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class UDLClient:
    """Client for interacting with the Unified Data Library (UDL) APIs."""

    def __init__(
        self,
        base_url: str = "https://unifieddatalibrary.com",
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize the UDL API client.

        Args:
            base_url: The base URL for the UDL API.
            api_key: API key for authentication.
            username: Username for authentication.
            password: Password for authentication.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
        """
        self.base_url = base_url
        self.api_key = api_key or os.environ.get("UDL_API_KEY")
        self.username = username or os.environ.get("UDL_USERNAME")
        self.password = password or os.environ.get("UDL_PASSWORD")
        self.timeout = timeout
        self.token = None
        self.token_expiry = 0

        # Set up session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get_auth_header(self) -> Dict[str, str]:
        """
        Get the authentication header for API requests.

        Returns:
            Dict containing the authentication header.
        """
        if self.api_key:
            return {"X-API-Key": self.api_key}
        
        # Use Basic Authentication when username/password are provided
        if self.username and self.password:
            auth_str = f"{self.username}:{self.password}"
            auth_bytes = auth_str.encode('ascii')
            base64_bytes = base64.b64encode(auth_bytes)
            base64_auth = base64_bytes.decode('ascii')
            return {"Authorization": f"Basic {base64_auth}"}
        
        # If no authentication method is available
        return {}

    def _refresh_token(self) -> None:
        """
        Refresh the authentication token.
        Note: This method is kept for backward compatibility but is not used
        as we're now using Basic Authentication.
        """
        if not self.username or not self.password:
            raise ValueError("Username and password are required for token authentication")
        
        auth_url = f"{self.base_url}/auth/token"
        response = self.session.post(
            auth_url,
            json={"username": self.username, "password": self.password},
            timeout=self.timeout,
        )
        response.raise_for_status()
        
        auth_data = response.json()
        self.token = auth_data["token"]
        # Set token expiry to 5 minutes before actual expiry
        self.token_expiry = time.time() + auth_data.get("expires_in", 3600) - 300

    def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> requests.Response:
        """
        Make an HTTP request to the UDL API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop("headers", {})
        headers.update(self._get_auth_header())
        
        # Add default timeout if not specified
        if "timeout" not in kwargs:
            kwargs["timeout"] = self.timeout
        
        response = self.session.request(method, url, headers=headers, **kwargs)
        
        # Log request details for debugging
        logger.debug(
            f"UDL API request: {method} {url}, Status: {response.status_code}"
        )
        
        # Raise exception for error status codes
        response.raise_for_status()
        
        return response

    def get_state_vectors(
        self, epoch: str, **query_params
    ) -> List[Dict[str, Any]]:
        """
        Get state vectors for a specific epoch.

        Args:
            epoch: Time of validity for state vector in ISO 8601 UTC datetime format
            **query_params: Additional query parameters

        Returns:
            List of state vector objects
        """
        params = {"epoch": epoch, **query_params}
        response = self._make_request("GET", "/udl/statevector", params=params)
        return response.json()

    def get_conjunctions(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get conjunction data.

        Args:
            **query_params: Query parameters

        Returns:
            List of conjunction objects
        """
        response = self._make_request("GET", "/udl/conjunction", params=query_params)
        return response.json()

    def get_launch_events(self, msg_create_date: str, **query_params) -> List[Dict[str, Any]]:
        """
        Get launch event data.

        Args:
            msg_create_date: Timestamp of the originating message in ISO8601 UTC format
            **query_params: Additional query parameters

        Returns:
            List of launch event objects
        """
        params = {"msgCreateDate": msg_create_date, **query_params}
        response = self._make_request("GET", "/udl/launchevent", params=params)
        return response.json()

    def get_tracks(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get track data.

        Args:
            **query_params: Query parameters

        Returns:
            List of track objects
        """
        response = self._make_request("GET", "/udl/track", params=query_params)
        return response.json()

    def get_orbit_determination(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get orbit determination data.

        Args:
            **query_params: Query parameters

        Returns:
            List of orbit determination objects
        """
        response = self._make_request("GET", "/udl/orbitdetermination", params=query_params)
        return response.json()

    def get_observations(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get observation data.

        Args:
            **query_params: Query parameters

        Returns:
            List of observation objects
        """
        response = self._make_request("GET", "/udl/observation", params=query_params)
        return response.json()

    def get_onorbit_objects(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get on-orbit object data.

        Args:
            **query_params: Query parameters

        Returns:
            List of on-orbit object data
        """
        response = self._make_request("GET", "/udl/onorbit", params=query_params)
        return response.json()

    # Additional UDL API Methods

    def get_ephemeris(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get ephemeris data for predicting positions of objects.

        Args:
            **query_params: Query parameters (object_id, start_time, end_time, etc.)

        Returns:
            List of ephemeris objects
        """
        response = self._make_request("GET", "/udl/ephemeris", params=query_params)
        return response.json()

    def get_maneuvers(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get spacecraft maneuver data.

        Args:
            **query_params: Query parameters (object_id, start_time, end_time, etc.)

        Returns:
            List of maneuver objects
        """
        response = self._make_request("GET", "/udl/maneuver", params=query_params)
        return response.json()

    def get_sensor_data(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get sensor information and capabilities.

        Args:
            **query_params: Query parameters (sensor_id, type, etc.)

        Returns:
            List of sensor objects
        """
        response = self._make_request("GET", "/udl/sensor", params=query_params)
        return response.json()

    def get_sensor_tasking(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get sensor tasking requests and status.

        Args:
            **query_params: Query parameters (sensor_id, object_id, status, etc.)

        Returns:
            List of sensor tasking objects
        """
        response = self._make_request("GET", "/udl/sensor-tasking", params=query_params)
        return response.json()

    def create_sensor_tasking(self, tasking_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new sensor tasking request.

        Args:
            tasking_data: Sensor tasking request data

        Returns:
            Created sensor tasking object
        """
        response = self._make_request("POST", "/udl/sensor-tasking", json=tasking_data)
        return response.json()

    def get_site_data(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get ground station and facility information.

        Args:
            **query_params: Query parameters (site_id, country, etc.)

        Returns:
            List of site objects
        """
        response = self._make_request("GET", "/udl/site", params=query_params)
        return response.json()

    def get_weather_data(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get weather data affecting space operations.

        Args:
            **query_params: Query parameters (location, time, etc.)

        Returns:
            List of weather data objects
        """
        response = self._make_request("GET", "/udl/weather", params=query_params)
        return response.json()

    def get_elset_data(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get two-line element sets for orbital objects.

        Args:
            **query_params: Query parameters (object_id, epoch, etc.)

        Returns:
            List of ELSET objects
        """
        response = self._make_request("GET", "/udl/elset", params=query_params)
        return response.json()

    def get_rf_data(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get radio frequency data.

        Args:
            **query_params: Query parameters (frequency, object_id, etc.)

        Returns:
            List of RF data objects
        """
        response = self._make_request("GET", "/udl/rf", params=query_params)
        return response.json()

    def get_earth_orientation_parameters(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get Earth orientation parameters.

        Args:
            **query_params: Query parameters (date, etc.)

        Returns:
            List of Earth orientation parameter objects
        """
        response = self._make_request("GET", "/udl/earth-orientation-parameters", params=query_params)
        return response.json()

    def get_solar_geomagnetic_data(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get solar and geomagnetic data.

        Args:
            **query_params: Query parameters (date, type, etc.)

        Returns:
            List of solar/geomagnetic data objects
        """
        response = self._make_request("GET", "/udl/solar-geomagnetic", params=query_params)
        return response.json()

    def get_star_catalog(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get star catalog information.

        Args:
            **query_params: Query parameters (magnitude, ra, dec, etc.)

        Returns:
            List of star catalog entries
        """
        response = self._make_request("GET", "/udl/star-catalog", params=query_params)
        return response.json()

    def get_tdoa_fdoa(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get Time Difference of Arrival (TDOA) and Frequency Difference of Arrival (FDOA) data.

        Args:
            **query_params: Query parameters

        Returns:
            List of TDOA/FDOA data objects
        """
        response = self._make_request("GET", "/udl/tdoa-fdoa", params=query_params)
        return response.json()

    def get_cyber_threats(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get cyber threat notifications.

        Args:
            **query_params: Query parameters (severity, target, etc.)

        Returns:
            List of cyber threat objects
        """
        response = self._make_request("GET", "/udl/cyber-threats", params=query_params)
        return response.json()

    def get_link_status(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get link status information.

        Args:
            **query_params: Query parameters (object_id, etc.)

        Returns:
            List of link status objects
        """
        response = self._make_request("GET", "/udl/link-status", params=query_params)
        return response.json()

    def get_comm_data(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get communications data.

        Args:
            **query_params: Query parameters (object_id, frequency, etc.)

        Returns:
            List of communications data objects
        """
        response = self._make_request("GET", "/udl/comm", params=query_params)
        return response.json()

    def get_mission_ops_data(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get mission operations data.

        Args:
            **query_params: Query parameters (mission_id, etc.)

        Returns:
            List of mission operations objects
        """
        response = self._make_request("GET", "/udl/mission-ops", params=query_params)
        return response.json()

    def get_vessel_data(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get vessel tracking data.

        Args:
            **query_params: Query parameters (vessel_id, location, etc.)

        Returns:
            List of vessel objects
        """
        response = self._make_request("GET", "/udl/vessel", params=query_params)
        return response.json()

    def get_aircraft_data(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get aircraft tracking data.

        Args:
            **query_params: Query parameters (aircraft_id, location, etc.)

        Returns:
            List of aircraft objects
        """
        response = self._make_request("GET", "/udl/aircraft", params=query_params)
        return response.json()

    def get_ground_imagery(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get ground imagery data.

        Args:
            **query_params: Query parameters (location, date, etc.)

        Returns:
            List of ground imagery objects
        """
        response = self._make_request("GET", "/udl/ground-imagery", params=query_params)
        return response.json()

    def get_sky_imagery(self, **query_params) -> List[Dict[str, Any]]:
        """
        Get sky imagery data.

        Args:
            **query_params: Query parameters (location, date, etc.)

        Returns:
            List of sky imagery objects
        """
        response = self._make_request("GET", "/udl/sky-imagery", params=query_params)
        return response.json()

    def get_video_streaming(self, **query_params) -> Dict[str, Any]:
        """
        Get video streaming information.

        Args:
            **query_params: Query parameters (source_id, etc.)

        Returns:
            Video streaming information
        """
        response = self._make_request("GET", "/udl/video-streaming", params=query_params)
        return response.json() 