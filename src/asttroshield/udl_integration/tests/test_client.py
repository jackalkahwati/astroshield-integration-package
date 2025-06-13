"""
Tests for the UDL API client.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from asttroshield.udl_integration.client import UDLClient


class TestUDLClient(unittest.TestCase):
    """Tests for the UDL API client."""

    @patch("asttroshield.udl_integration.client.requests.Session")
    def test_init(self, mock_session):
        """Test client initialization."""
        client = UDLClient(
            base_url="https://test-udl.com",
            api_key="test-api-key",
            username="test-user",
            password="test-pass",
        )
        
        self.assertEqual(client.base_url, "https://test-udl.com")
        self.assertEqual(client.api_key, "test-api-key")
        self.assertEqual(client.username, "test-user")
        self.assertEqual(client.password, "test-pass")
        self.assertIsNone(client.token)
        self.assertEqual(client.token_expiry, 0)

    @patch("asttroshield.udl_integration.client.requests.Session")
    def test_get_auth_header_with_api_key(self, mock_session):
        """Test getting auth header with API key."""
        client = UDLClient(api_key="test-api-key")
        
        headers = client._get_auth_header()
        
        self.assertEqual(headers, {"X-API-Key": "test-api-key"})

    @patch("asttroshield.udl_integration.client.requests.Session")
    def test_refresh_token(self, mock_session):
        """Test refreshing the authentication token."""
        # Mock the session post method
        mock_response = MagicMock()
        mock_response.json.return_value = {"token": "test-token", "expires_in": 3600}
        mock_session.return_value.post.return_value = mock_response
        
        client = UDLClient(username="test-user", password="test-pass")
        client._refresh_token()
        
        # Check that the post method was called with the right arguments
        mock_session.return_value.post.assert_called_once_with(
            "https://unifieddatalibrary.com/auth/token",
            json={"username": "test-user", "password": "test-pass"},
            timeout=30,
        )
        
        # Check that the token was updated
        self.assertEqual(client.token, "test-token")
        
    @patch("asttroshield.udl_integration.client.requests.Session")
    def test_make_request(self, mock_session):
        """Test making a request to the UDL API."""
        # Mock the session request method
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "1", "name": "test"}]
        mock_session.return_value.request.return_value = mock_response
        
        client = UDLClient(api_key="test-api-key")
        response = client._make_request("GET", "/test-endpoint", params={"param": "value"})
        
        # Check that the request method was called with the right arguments
        mock_session.return_value.request.assert_called_once_with(
            "GET",
            "https://unifieddatalibrary.com/test-endpoint",
            headers={"X-API-Key": "test-api-key"},
            params={"param": "value"},
            timeout=30,
        )
        
        # Check that the response was returned
        self.assertEqual(response, mock_response)
        
    @patch.object(UDLClient, "_make_request")
    def test_get_state_vectors(self, mock_make_request):
        """Test getting state vectors."""
        # Mock the _make_request method
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": "1", "name": "test"}]
        mock_make_request.return_value = mock_response
        
        client = UDLClient()
        result = client.get_state_vectors("2023-01-01T00:00:00Z")
        
        # Check that _make_request was called with the right arguments
        mock_make_request.assert_called_once_with(
            "GET",
            "/udl/statevector",
            params={"epoch": "2023-01-01T00:00:00Z"},
        )
        
        # Check that the result is correct
        self.assertEqual(result, [{"id": "1", "name": "test"}])

    @patch.object(UDLClient, "_make_request")
    def test_get_conjunctions(self, mock_make_request):
        """Test getting conjunctions."""
        # Mock the _make_request method
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": "1", "name": "test"}]
        mock_make_request.return_value = mock_response
        
        client = UDLClient()
        result = client.get_conjunctions(param="value")
        
        # Check that _make_request was called with the right arguments
        mock_make_request.assert_called_once_with(
            "GET",
            "/udl/conjunction",
            params={"param": "value"},
        )
        
        # Check that the result is correct
        self.assertEqual(result, [{"id": "1", "name": "test"}])

    @patch.object(UDLClient, "_make_request")
    def test_get_launch_events(self, mock_make_request):
        """Test getting launch events."""
        # Mock the _make_request method
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": "1", "name": "test"}]
        mock_make_request.return_value = mock_response
        
        client = UDLClient()
        result = client.get_launch_events("2023-01-01T00:00:00Z", param="value")
        
        # Check that _make_request was called with the right arguments
        mock_make_request.assert_called_once_with(
            "GET",
            "/udl/launchevent",
            params={"msgCreateDate": "2023-01-01T00:00:00Z", "param": "value"},
        )
        
        # Check that the result is correct
        self.assertEqual(result, [{"id": "1", "name": "test"}])


if __name__ == "__main__":
    unittest.main() 