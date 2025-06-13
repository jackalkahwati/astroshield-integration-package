"""
Tests for the UDL Secure Messaging client.
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
import threading
import time
import datetime

from ..messaging_client import UDLMessagingClient


class TestUDLMessagingClient(unittest.TestCase):
    """Test cases for the UDLMessagingClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = UDLMessagingClient(
            base_url="https://example.com",
            username="testuser",
            password="testpass",
            timeout=1,
            max_retries=0,
            sample_period=0.01,  # Fast sample period for tests
        )

    @patch('requests.Session')
    def test_init(self, mock_session):
        """Test the initialization of the client."""
        client = UDLMessagingClient(
            base_url="https://example.com",
            username="testuser",
            password="testpass"
        )
        
        # Check that session was created and auth was set
        mock_session.assert_called_once()
        session_instance = mock_session.return_value
        self.assertEqual(session_instance.auth, ("testuser", "testpass"))

    @patch('requests.Session')
    def test_list_topics(self, mock_session):
        """Test listing topics."""
        # Set up mock response
        mock_response = Mock()
        mock_response.json.return_value = [
            {"name": "topic1", "partitions": 1},
            {"name": "topic2", "partitions": 2}
        ]
        mock_response.status_code = 200
        
        session_instance = mock_session.return_value
        session_instance.get.return_value = mock_response
        
        # Call the method
        result = self.client.list_topics()
        
        # Verify the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "topic1")
        self.assertEqual(result[1]["name"], "topic2")
        
        # Verify API call
        session_instance.get.assert_called_once_with(
            "https://example.com/sm/listTopics",
            timeout=1,
            verify=True
        )

    @patch('requests.Session')
    def test_describe_topic(self, mock_session):
        """Test describing a topic."""
        # Set up mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "topic1", 
            "partitions": 1,
            "config": {"retention.ms": "604800000"}
        }
        mock_response.status_code = 200
        
        session_instance = mock_session.return_value
        session_instance.get.return_value = mock_response
        
        # Call the method
        result = self.client.describe_topic("topic1")
        
        # Verify the result
        self.assertEqual(result["name"], "topic1")
        self.assertEqual(result["partitions"], 1)
        
        # Verify API call
        session_instance.get.assert_called_once_with(
            "https://example.com/sm/describeTopic/topic1/0",
            timeout=1,
            verify=True
        )

    @patch('requests.Session')
    def test_get_latest_offset(self, mock_session):
        """Test getting the latest offset."""
        # Set up mock response
        mock_response = Mock()
        mock_response.text = "42"
        mock_response.status_code = 200
        
        session_instance = mock_session.return_value
        session_instance.get.return_value = mock_response
        
        # Call the method
        result = self.client.get_latest_offset("topic1")
        
        # Verify the result
        self.assertEqual(result, 42)
        
        # Verify API call
        session_instance.get.assert_called_once_with(
            "https://example.com/sm/getLatestOffset/topic1/0",
            timeout=1,
            verify=True
        )

    @patch('requests.Session')
    def test_get_messages(self, mock_session):
        """Test getting messages."""
        # Set up mock response
        mock_response = Mock()
        mock_response.json.return_value = [
            {"key": "key1", "value": "value1", "timestamp": 1234567890},
            {"key": "key2", "value": "value2", "timestamp": 1234567891}
        ]
        mock_response.status_code = 200
        mock_response.headers = {"KAFKA_NEXT_OFFSET": "43"}
        
        session_instance = mock_session.return_value
        session_instance.get.return_value = mock_response
        
        # Call the method
        messages, next_offset = self.client.get_messages("topic1", offset=42)
        
        # Verify the result
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["key"], "key1")
        self.assertEqual(messages[1]["key"], "key2")
        self.assertEqual(next_offset, 43)
        
        # Verify API call
        session_instance.get.assert_called_once_with(
            "https://example.com/sm/getMessages/topic1/0/42",
            params={},
            timeout=1,
            verify=True
        )

    @patch('requests.Session')
    def test_get_messages_with_params(self, mock_session):
        """Test getting messages with query parameters."""
        # Set up mock response
        mock_response = Mock()
        mock_response.json.return_value = [{"key": "key1", "value": "value1"}]
        mock_response.status_code = 200
        mock_response.headers = {"KAFKA_NEXT_OFFSET": "43"}
        
        session_instance = mock_session.return_value
        session_instance.get.return_value = mock_response
        
        # Call the method with query params
        query_params = {"filter": "someFilter", "limit": "10"}
        messages, next_offset = self.client.get_messages("topic1", offset=42, query_params=query_params)
        
        # Verify API call includes params
        session_instance.get.assert_called_once_with(
            "https://example.com/sm/getMessages/topic1/0/42",
            params=query_params,
            timeout=1,
            verify=True
        )

    @patch('requests.Session')
    def test_consumer_thread(self, mock_session):
        """Test the consumer thread functionality."""
        # Set up mock responses for multiple calls
        mock_response1 = Mock()
        mock_response1.json.return_value = [{"key": "key1", "value": "value1"}]
        mock_response1.status_code = 200
        mock_response1.headers = {"KAFKA_NEXT_OFFSET": "43"}
        
        mock_response2 = Mock()
        mock_response2.json.return_value = []  # Empty response for the second call
        mock_response2.status_code = 200
        mock_response2.headers = {"KAFKA_NEXT_OFFSET": "43"}
        
        session_instance = mock_session.return_value
        session_instance.get.side_effect = [mock_response1, mock_response2]
        
        # Set up a callback function
        callback_results = []
        def test_callback(messages):
            callback_results.extend(messages)
        
        # Start the consumer
        self.client.start_consumer("topic1", test_callback, start_from_latest=False)
        
        # Let it run for a short time
        time.sleep(0.05)
        
        # Stop the consumer
        self.client.stop_consumer("topic1")
        
        # Verify callback was called with the messages
        self.assertEqual(len(callback_results), 1)
        self.assertEqual(callback_results[0]["key"], "key1")
        
        # Verify the consumer was properly tracked and stopped
        self.assertNotIn("topic1:0", self.client._consumers)

    def test_stop_all_consumers(self):
        """Test stopping all consumers."""
        # Create mock consumer threads
        mock_thread1 = Mock()
        mock_thread2 = Mock()
        
        # Add them to the client
        self.client._consumers = {
            "topic1:0": mock_thread1,
            "topic2:0": mock_thread2
        }
        
        # Set the stop event
        self.client._stop_event = Mock()
        
        # Call the method
        self.client.stop_all_consumers()
        
        # Verify stop event was set
        self.client._stop_event.set.assert_called_once()
        
        # Verify the consumers dict was cleared
        self.assertEqual(len(self.client._consumers), 0)


if __name__ == '__main__':
    unittest.main() 