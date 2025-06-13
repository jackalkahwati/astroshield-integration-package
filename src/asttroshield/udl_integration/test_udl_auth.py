#!/usr/bin/env python3
"""
Test script for UDL authentication.

This script tests UDL authentication using credentials from the .env file.
It attempts to make a simple API call to verify authentication works.
"""

import logging
import os
import sys

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from asttroshield.udl_integration.client import UDLClient


def test_udl_auth():
    """Test UDL authentication using credentials from .env file."""
    logger.info("Testing UDL authentication with credentials from .env")
    
    # Log environment variable status (without revealing full credentials)
    username = os.environ.get("UDL_USERNAME", "")
    password = os.environ.get("UDL_PASSWORD", "")
    base_url = os.environ.get("UDL_BASE_URL", "")
    
    logger.info(f"UDL_USERNAME: {'✓' if username else '✗'} (value: {username[:2]}{'*' * (len(username) - 4)}{username[-2:] if len(username) > 3 else ''})")
    logger.info(f"UDL_PASSWORD: {'✓' if password else '✗'} (length: {len(password)})")
    logger.info(f"UDL_BASE_URL: {'✓' if base_url else '✗'} (value: {base_url})")
    
    if not (username and password):
        logger.error("Required environment variables not found. Please check your .env file.")
        return False
    
    try:
        # Initialize the UDL client (it will use the environment variables)
        client = UDLClient()
        
        # Try to make a simple API call to test authentication
        logger.info("Attempting to retrieve state vectors from UDL")
        state_vectors = client.get_state_vectors(limit=1)
        
        if state_vectors:
            logger.info(f"Successfully retrieved {len(state_vectors)} state vector(s) from UDL")
            logger.info("Authentication successful!")
            return True
        else:
            logger.warning("No state vectors retrieved. API call worked but no data was returned.")
            logger.info("Authentication successful, but no data available.")
            return True
            
    except Exception as e:
        logger.error(f"Error authenticating with UDL: {e}")
        return False


if __name__ == "__main__":
    success = test_udl_auth()
    sys.exit(0 if success else 1) 