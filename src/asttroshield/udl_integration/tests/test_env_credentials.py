"""
Tests for loading UDL credentials from .env file.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from asttroshield.udl_integration.client import UDLClient


class TestEnvCredentials(unittest.TestCase):
    """Tests for loading UDL credentials from environment variables."""

    def test_env_variables_loaded(self):
        """Test that UDL environment variables are properly loaded from .env."""
        # Verify UDL environment variables were loaded
        self.assertIsNotNone(os.environ.get("UDL_USERNAME"), "UDL_USERNAME not found in environment")
        self.assertIsNotNone(os.environ.get("UDL_PASSWORD"), "UDL_PASSWORD not found in environment")
        self.assertIsNotNone(os.environ.get("UDL_BASE_URL"), "UDL_BASE_URL not found in environment")
        
        # Verify the expected values
        self.assertEqual(os.environ.get("UDL_USERNAME"), "jack.al-kahwati")
        self.assertEqual(os.environ.get("UDL_PASSWORD"), "qaBku2-hinqeg-comhap")
        self.assertEqual(os.environ.get("UDL_BASE_URL"), "https://unifieddatalibrary.com/udl/api/v1")
    
    @patch("asttroshield.udl_integration.client.requests.Session")
    def test_client_loads_env_credentials(self, mock_session):
        """Test that UDLClient correctly loads credentials from environment variables."""
        # Create a UDLClient without explicitly providing credentials
        client = UDLClient()
        
        # Check that the client loaded the credentials from environment
        self.assertEqual(client.username, "jack.al-kahwati")
        self.assertEqual(client.password, "qaBku2-hinqeg-comhap")
        self.assertEqual(client.base_url, "https://unifieddatalibrary.com/udl/api/v1")
    
    @patch("asttroshield.udl_integration.client.requests.Session")
    def test_auth_header_with_env_credentials(self, mock_session):
        """Test that authentication headers are properly created with env credentials."""
        # Mock the token refresh method
        mock_response = MagicMock()
        mock_response.json.return_value = {"token": "test-token", "expires_in": 3600}
        mock_session.return_value.post.return_value = mock_response
        
        # Create client and get auth header
        client = UDLClient()
        
        # Force token refresh and get auth header
        client._refresh_token()
        headers = client._get_auth_header()
        
        # Verify the session was called with the correct credentials
        mock_session.return_value.post.assert_called_once()
        call_args = mock_session.return_value.post.call_args[0]
        call_kwargs = mock_session.return_value.post.call_args[1]
        
        # Check that the auth endpoint was called with credentials from .env
        self.assertIn("auth", call_args[0])
        self.assertEqual(call_kwargs["json"]["username"], "jack.al-kahwati")
        self.assertEqual(call_kwargs["json"]["password"], "qaBku2-hinqeg-comhap")
        
        # Check that the auth header has the token
        self.assertEqual(headers, {"Authorization": "Bearer test-token"})


if __name__ == "__main__":
    unittest.main() 