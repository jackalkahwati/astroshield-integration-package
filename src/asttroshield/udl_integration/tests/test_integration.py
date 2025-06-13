"""
Tests for the UDL integration module.
"""

import unittest
from unittest.mock import patch, MagicMock, call

from asttroshield.udl_integration.integration import (
    UDLIntegration, 
    UDLIntegrationError,
    setup_logging
)


class TestUDLIntegration(unittest.TestCase):
    """Tests for the UDL integration module."""
    
    @patch("asttroshield.udl_integration.integration.UDLClient")
    @patch("asttroshield.udl_integration.integration.KafkaProducer")
    @patch("asttroshield.udl_integration.integration.setup_logging")
    def test_init(self, mock_setup_logging, mock_kafka_producer, mock_udl_client):
        """Test initializing the UDL integration."""
        # Arrange
        udl_base_url = "https://udl.example.com"
        udl_api_key = "test-api-key"
        kafka_bootstrap_servers = ["localhost:9092"]
        kafka_client_id = "test-client"
        
        # Act
        integration = UDLIntegration(
            udl_base_url=udl_base_url,
            udl_api_key=udl_api_key,
            kafka_bootstrap_servers=kafka_bootstrap_servers,
            kafka_client_id=kafka_client_id,
        )
        
        # Assert
        mock_setup_logging.assert_called_once()
        mock_udl_client.assert_called_once_with(
            base_url=udl_base_url,
            api_key=udl_api_key,
        )
        mock_kafka_producer.assert_called_once_with(
            bootstrap_servers=kafka_bootstrap_servers,
            client_id=kafka_client_id,
        )
        self.assertEqual(integration.udl_client, mock_udl_client.return_value)
        self.assertEqual(integration.kafka_producer, mock_kafka_producer.return_value)
        self.assertEqual(integration.poll_interval, 60)
        self.assertFalse(integration.running)
    
    @patch("asttroshield.udl_integration.integration.UDLClient")
    @patch("asttroshield.udl_integration.integration.KafkaProducer")
    @patch("asttroshield.udl_integration.integration.setup_logging")
    def test_init_with_custom_poll_interval(self, mock_setup_logging, mock_kafka_producer, mock_udl_client):
        """Test initializing the UDL integration with a custom poll interval."""
        # Arrange
        udl_base_url = "https://udl.example.com"
        udl_api_key = "test-api-key"
        kafka_bootstrap_servers = ["localhost:9092"]
        kafka_client_id = "test-client"
        poll_interval = 120
        
        # Act
        integration = UDLIntegration(
            udl_base_url=udl_base_url,
            udl_api_key=udl_api_key,
            kafka_bootstrap_servers=kafka_bootstrap_servers,
            kafka_client_id=kafka_client_id,
            poll_interval=poll_interval,
        )
        
        # Assert
        self.assertEqual(integration.poll_interval, poll_interval)
    
    @patch("asttroshield.udl_integration.integration.UDLClient")
    @patch("asttroshield.udl_integration.integration.KafkaProducer")
    @patch("asttroshield.udl_integration.integration.setup_logging")
    @patch("asttroshield.udl_integration.integration.transform_state_vector")
    def test_process_state_vectors(self, mock_transform_sv, mock_setup_logging, mock_kafka_producer, mock_udl_client):
        """Test processing state vectors."""
        # Arrange
        mock_udl_client_instance = mock_udl_client.return_value
        mock_kafka_producer_instance = mock_kafka_producer.return_value
        
        # Mock UDL client to return some state vectors
        state_vectors = [
            {"satno": 12345, "objectName": "SV1"},
            {"satno": 67890, "objectName": "SV2"},
        ]
        mock_udl_client_instance.fetch_state_vectors.return_value = state_vectors
        
        # Mock transform_state_vector to return transformed data
        transformed_state_vectors = [
            {
                "header": {"messageId": "sv1"},
                "payload": {"objectId": "SATCAT-12345"}
            },
            {
                "header": {"messageId": "sv2"},
                "payload": {"objectId": "SATCAT-67890"}
            },
        ]
        mock_transform_sv.side_effect = transformed_state_vectors
        
        integration = UDLIntegration(
            udl_base_url="https://udl.example.com",
            udl_api_key="test-api-key",
            kafka_bootstrap_servers=["localhost:9092"],
            kafka_client_id="test-client",
        )
        
        # Act
        result = integration.process_state_vectors()
        
        # Assert
        mock_udl_client_instance.fetch_state_vectors.assert_called_once()
        mock_transform_sv.assert_has_calls([
            call(state_vectors[0]),
            call(state_vectors[1]),
        ])
        mock_kafka_producer_instance.send_state_vector.assert_has_calls([
            call(transformed_state_vectors[0]),
            call(transformed_state_vectors[1]),
        ])
        self.assertEqual(result, 2)
    
    @patch("asttroshield.udl_integration.integration.UDLClient")
    @patch("asttroshield.udl_integration.integration.KafkaProducer")
    @patch("asttroshield.udl_integration.integration.setup_logging")
    @patch("asttroshield.udl_integration.integration.transform_conjunction")
    def test_process_conjunctions(self, mock_transform_conj, mock_setup_logging, mock_kafka_producer, mock_udl_client):
        """Test processing conjunctions."""
        # Arrange
        mock_udl_client_instance = mock_udl_client.return_value
        mock_kafka_producer_instance = mock_kafka_producer.return_value
        
        # Mock UDL client to return some conjunctions
        conjunctions = [
            {
                "object1": {"satno": 12345, "objectName": "SAT1"},
                "object2": {"satno": 67890, "objectName": "SAT2"},
                "tca": "2023-01-01T00:00:00Z",
            },
            {
                "object1": {"satno": 11111, "objectName": "SAT3"},
                "object2": {"satno": 22222, "objectName": "SAT4"},
                "tca": "2023-01-02T00:00:00Z",
            },
        ]
        mock_udl_client_instance.fetch_conjunctions.return_value = conjunctions
        
        # Mock transform_conjunction to return transformed data
        transformed_conjunctions = [
            {
                "header": {"messageId": "conj1"},
                "payload": {"conjunctionId": "conj-id-1"}
            },
            {
                "header": {"messageId": "conj2"},
                "payload": {"conjunctionId": "conj-id-2"}
            },
        ]
        mock_transform_conj.side_effect = transformed_conjunctions
        
        integration = UDLIntegration(
            udl_base_url="https://udl.example.com",
            udl_api_key="test-api-key",
            kafka_bootstrap_servers=["localhost:9092"],
            kafka_client_id="test-client",
        )
        
        # Act
        result = integration.process_conjunctions()
        
        # Assert
        mock_udl_client_instance.fetch_conjunctions.assert_called_once()
        mock_transform_conj.assert_has_calls([
            call(conjunctions[0]),
            call(conjunctions[1]),
        ])
        mock_kafka_producer_instance.send_conjunction.assert_has_calls([
            call(transformed_conjunctions[0]),
            call(transformed_conjunctions[1]),
        ])
        self.assertEqual(result, 2)
    
    @patch("asttroshield.udl_integration.integration.UDLClient")
    @patch("asttroshield.udl_integration.integration.KafkaProducer")
    @patch("asttroshield.udl_integration.integration.setup_logging")
    @patch("asttroshield.udl_integration.integration.transform_launch_event")
    def test_process_launch_events(self, mock_transform_launch, mock_setup_logging, mock_kafka_producer, mock_udl_client):
        """Test processing launch events."""
        # Arrange
        mock_udl_client_instance = mock_udl_client.return_value
        mock_kafka_producer_instance = mock_kafka_producer.return_value
        
        # Mock UDL client to return some launch events
        launch_events = [
            {
                "launchSite": {"name": "Cape Canaveral"},
                "launchTime": "2023-01-01T00:00:00Z",
            },
            {
                "launchSite": {"name": "Baikonur"},
                "launchTime": "2023-01-02T00:00:00Z",
            },
        ]
        mock_udl_client_instance.fetch_launch_events.return_value = launch_events
        
        # Mock transform_launch_event to return transformed data
        transformed_launch_events = [
            {
                "header": {"messageId": "launch1"},
                "payload": {"detectionId": "launch-id-1"}
            },
            {
                "header": {"messageId": "launch2"},
                "payload": {"detectionId": "launch-id-2"}
            },
        ]
        mock_transform_launch.side_effect = transformed_launch_events
        
        integration = UDLIntegration(
            udl_base_url="https://udl.example.com",
            udl_api_key="test-api-key",
            kafka_bootstrap_servers=["localhost:9092"],
            kafka_client_id="test-client",
        )
        
        # Act
        result = integration.process_launch_events()
        
        # Assert
        mock_udl_client_instance.fetch_launch_events.assert_called_once()
        mock_transform_launch.assert_has_calls([
            call(launch_events[0]),
            call(launch_events[1]),
        ])
        mock_kafka_producer_instance.send_launch_event.assert_has_calls([
            call(transformed_launch_events[0]),
            call(transformed_launch_events[1]),
        ])
        self.assertEqual(result, 2)
    
    @patch("asttroshield.udl_integration.integration.UDLClient")
    @patch("asttroshield.udl_integration.integration.KafkaProducer")
    @patch("asttroshield.udl_integration.integration.setup_logging")
    @patch("asttroshield.udl_integration.integration.time")
    def test_run_once(self, mock_time, mock_setup_logging, mock_kafka_producer, mock_udl_client):
        """Test running the integration process once."""
        # Arrange
        integration = UDLIntegration(
            udl_base_url="https://udl.example.com",
            udl_api_key="test-api-key",
            kafka_bootstrap_servers=["localhost:9092"],
            kafka_client_id="test-client",
        )
        
        # Mock the process methods
        integration.process_state_vectors = MagicMock(return_value=10)
        integration.process_conjunctions = MagicMock(return_value=5)
        integration.process_launch_events = MagicMock(return_value=2)
        
        # Act
        result = integration.run_once()
        
        # Assert
        integration.process_state_vectors.assert_called_once()
        integration.process_conjunctions.assert_called_once()
        integration.process_launch_events.assert_called_once()
        self.assertEqual(result, {"state_vectors": 10, "conjunctions": 5, "launch_events": 2})
    
    @patch("asttroshield.udl_integration.integration.UDLClient")
    @patch("asttroshield.udl_integration.integration.KafkaProducer")
    @patch("asttroshield.udl_integration.integration.setup_logging")
    @patch("asttroshield.udl_integration.integration.time")
    def test_run_loop_with_iteration_count(self, mock_time, mock_setup_logging, mock_kafka_producer, mock_udl_client):
        """Test running the integration process in a loop with a fixed number of iterations."""
        # Arrange
        integration = UDLIntegration(
            udl_base_url="https://udl.example.com",
            udl_api_key="test-api-key",
            kafka_bootstrap_servers=["localhost:9092"],
            kafka_client_id="test-client",
        )
        
        # Mock the run_once method
        integration.run_once = MagicMock(return_value={
            "state_vectors": 10,
            "conjunctions": 5,
            "launch_events": 2,
        })
        
        # Act
        integration.run(iterations=3)
        
        # Assert
        self.assertEqual(integration.run_once.call_count, 3)
        mock_time.sleep.assert_has_calls([
            call(integration.poll_interval),
            call(integration.poll_interval),
        ])
    
    @patch("asttroshield.udl_integration.integration.UDLClient")
    @patch("asttroshield.udl_integration.integration.KafkaProducer")
    @patch("asttroshield.udl_integration.integration.setup_logging")
    @patch("asttroshield.udl_integration.integration.time")
    def test_run_loop_with_keyboard_interrupt(self, mock_time, mock_setup_logging, mock_kafka_producer, mock_udl_client):
        """Test handling keyboard interrupt when running the integration process in a loop."""
        # Arrange
        integration = UDLIntegration(
            udl_base_url="https://udl.example.com",
            udl_api_key="test-api-key",
            kafka_bootstrap_servers=["localhost:9092"],
            kafka_client_id="test-client",
        )
        
        # Mock the run_once method to raise KeyboardInterrupt after first call
        integration.run_once = MagicMock(side_effect=[
            {"state_vectors": 10, "conjunctions": 5, "launch_events": 2},
            KeyboardInterrupt,
        ])
        
        # Act
        integration.run()
        
        # Assert
        self.assertEqual(integration.run_once.call_count, 2)
        mock_time.sleep.assert_called_once_with(integration.poll_interval)
        self.assertFalse(integration.running)

    @patch("asttroshield.udl_integration.integration.UDLClient")
    @patch("asttroshield.udl_integration.integration.KafkaProducer")
    @patch("asttroshield.udl_integration.integration.setup_logging")
    def test_stop(self, mock_setup_logging, mock_kafka_producer, mock_udl_client):
        """Test stopping the integration process."""
        # Arrange
        integration = UDLIntegration(
            udl_base_url="https://udl.example.com",
            udl_api_key="test-api-key",
            kafka_bootstrap_servers=["localhost:9092"],
            kafka_client_id="test-client",
        )
        integration.running = True
        
        # Act
        integration.stop()
        
        # Assert
        self.assertFalse(integration.running)

    @patch("asttroshield.udl_integration.integration.UDLClient")
    @patch("asttroshield.udl_integration.integration.KafkaProducer")
    @patch("asttroshield.udl_integration.integration.setup_logging")
    def test_close(self, mock_setup_logging, mock_kafka_producer, mock_udl_client):
        """Test closing the integration resources."""
        # Arrange
        mock_kafka_producer_instance = mock_kafka_producer.return_value
        
        integration = UDLIntegration(
            udl_base_url="https://udl.example.com",
            udl_api_key="test-api-key",
            kafka_bootstrap_servers=["localhost:9092"],
            kafka_client_id="test-client",
        )
        integration.running = True
        
        # Act
        integration.close()
        
        # Assert
        self.assertFalse(integration.running)
        mock_kafka_producer_instance.close.assert_called_once()
    
    @patch("asttroshield.udl_integration.integration.logging")
    def test_setup_logging(self, mock_logging):
        """Test setting up logging."""
        # Act
        setup_logging()
        
        # Assert
        mock_logging.basicConfig.assert_called_once()
        self.assertEqual(mock_logging.basicConfig.call_args[1]["level"], mock_logging.INFO)


if __name__ == "__main__":
    unittest.main() 