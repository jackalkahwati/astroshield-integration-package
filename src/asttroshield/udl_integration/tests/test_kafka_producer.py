"""
Tests for the Kafka producer component.
"""

import json
import unittest
from unittest.mock import patch, MagicMock

from asttroshield.udl_integration.kafka_producer import KafkaProducer, KafkaProducerError


class TestKafkaProducer(unittest.TestCase):
    """Tests for the Kafka producer component."""

    @patch("asttroshield.udl_integration.kafka_producer.KafkaProducer", autospec=True)
    def test_init(self, mock_kafka_producer):
        """Test initializing the Kafka producer."""
        # Arrange
        bootstrap_servers = ["localhost:9092"]
        client_id = "test-client"
        
        # Act
        producer = KafkaProducer(bootstrap_servers, client_id)
        
        # Assert
        mock_kafka_producer.assert_called_once_with(
            bootstrap_servers=bootstrap_servers,
            client_id=client_id,
            value_serializer=producer._serialize_value,
            key_serializer=producer._serialize_key,
            acks="all",
            retries=5,
            retry_backoff_ms=500,
        )

    @patch("asttroshield.udl_integration.kafka_producer.KafkaProducer", autospec=True)
    def test_serialize_value(self, mock_kafka_producer):
        """Test serializing message values."""
        # Arrange
        producer = KafkaProducer(["localhost:9092"], "test-client")
        message = {"key": "value"}
        
        # Act
        result = producer._serialize_value(message)
        
        # Assert
        self.assertEqual(result, json.dumps(message).encode("utf-8"))

    @patch("asttroshield.udl_integration.kafka_producer.KafkaProducer", autospec=True)
    def test_serialize_key(self, mock_kafka_producer):
        """Test serializing message keys."""
        # Arrange
        producer = KafkaProducer(["localhost:9092"], "test-client")
        key = "test-key"
        
        # Act
        result = producer._serialize_key(key)
        
        # Assert
        self.assertEqual(result, key.encode("utf-8"))

    @patch("asttroshield.udl_integration.kafka_producer.KafkaProducer", autospec=True)
    def test_send_message_success(self, mock_kafka_producer):
        """Test sending a message successfully."""
        # Arrange
        mock_instance = mock_kafka_producer.return_value
        future = MagicMock()
        future.get.return_value = MagicMock(topic="test-topic", partition=0, offset=1)
        mock_instance.send.return_value = future
        
        producer = KafkaProducer(["localhost:9092"], "test-client")
        topic = "test-topic"
        message = {"key": "value"}
        key = "test-key"
        
        # Act
        result = producer.send_message(topic, message, key)
        
        # Assert
        mock_instance.send.assert_called_once_with(
            topic=topic, value=message, key=key
        )
        self.assertEqual(result, {"topic": "test-topic", "partition": 0, "offset": 1})

    @patch("asttroshield.udl_integration.kafka_producer.KafkaProducer", autospec=True)
    def test_send_message_error(self, mock_kafka_producer):
        """Test handling errors when sending a message."""
        # Arrange
        mock_instance = mock_kafka_producer.return_value
        future = MagicMock()
        future.get.side_effect = Exception("Kafka error")
        mock_instance.send.return_value = future
        
        producer = KafkaProducer(["localhost:9092"], "test-client")
        topic = "test-topic"
        message = {"key": "value"}
        
        # Act & Assert
        with self.assertRaises(KafkaProducerError):
            producer.send_message(topic, message)

    @patch("asttroshield.udl_integration.kafka_producer.KafkaProducer", autospec=True)
    def test_send_state_vector(self, mock_kafka_producer):
        """Test sending a state vector message."""
        # Arrange
        mock_instance = mock_kafka_producer.return_value
        future = MagicMock()
        future.get.return_value = MagicMock(topic="state-vectors", partition=0, offset=1)
        mock_instance.send.return_value = future
        
        producer = KafkaProducer(["localhost:9092"], "test-client")
        state_vector = {
            "header": {
                "messageId": "test-id",
                "messageType": "ss2.state.vector"
            },
            "payload": {
                "objectId": "SATCAT-12345"
            }
        }
        
        # Act
        result = producer.send_state_vector(state_vector)
        
        # Assert
        mock_instance.send.assert_called_once_with(
            topic="state-vectors", 
            value=state_vector, 
            key="SATCAT-12345"
        )
        self.assertEqual(result, {"topic": "state-vectors", "partition": 0, "offset": 1})

    @patch("asttroshield.udl_integration.kafka_producer.KafkaProducer", autospec=True)
    def test_send_conjunction(self, mock_kafka_producer):
        """Test sending a conjunction message."""
        # Arrange
        mock_instance = mock_kafka_producer.return_value
        future = MagicMock()
        future.get.return_value = MagicMock(topic="conjunctions", partition=0, offset=1)
        mock_instance.send.return_value = future
        
        producer = KafkaProducer(["localhost:9092"], "test-client")
        conjunction = {
            "header": {
                "messageId": "test-id",
                "messageType": "ss5.conjunction.event"
            },
            "payload": {
                "conjunctionId": "conj-id",
                "primaryObject": {
                    "objectId": "SATCAT-12345"
                }
            }
        }
        
        # Act
        result = producer.send_conjunction(conjunction)
        
        # Assert
        mock_instance.send.assert_called_once_with(
            topic="conjunctions", 
            value=conjunction, 
            key="conj-id"
        )
        self.assertEqual(result, {"topic": "conjunctions", "partition": 0, "offset": 1})

    @patch("asttroshield.udl_integration.kafka_producer.KafkaProducer", autospec=True)
    def test_send_launch_event(self, mock_kafka_producer):
        """Test sending a launch event message."""
        # Arrange
        mock_instance = mock_kafka_producer.return_value
        future = MagicMock()
        future.get.return_value = MagicMock(topic="launch-events", partition=0, offset=1)
        mock_instance.send.return_value = future
        
        producer = KafkaProducer(["localhost:9092"], "test-client")
        launch_event = {
            "header": {
                "messageId": "test-id",
                "messageType": "ss0.launch.detection"
            },
            "payload": {
                "detectionId": "launch-id"
            }
        }
        
        # Act
        result = producer.send_launch_event(launch_event)
        
        # Assert
        mock_instance.send.assert_called_once_with(
            topic="launch-events", 
            value=launch_event, 
            key="launch-id"
        )
        self.assertEqual(result, {"topic": "launch-events", "partition": 0, "offset": 1})

    @patch("asttroshield.udl_integration.kafka_producer.KafkaProducer", autospec=True)
    def test_close(self, mock_kafka_producer):
        """Test closing the Kafka producer."""
        # Arrange
        mock_instance = mock_kafka_producer.return_value
        producer = KafkaProducer(["localhost:9092"], "test-client")
        
        # Act
        producer.close()
        
        # Assert
        mock_instance.close.assert_called_once()


if __name__ == "__main__":
    unittest.main() 