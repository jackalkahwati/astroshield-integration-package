#!/usr/bin/env python3
"""
CCDM Detection Consumer Example

This example demonstrates how to consume CCDM detection messages from the AstroShield Kafka stream
and process them for integration with other systems.
"""

import json
import uuid
import logging
from datetime import datetime
from confluent_kafka import Consumer, Producer, KafkaError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Kafka configuration
KAFKA_CONFIG = {
    'bootstrap.servers': 'kafka.astroshield.com:9093',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': 'your-username',  # Replace with your username
    'sasl.password': 'your-password',  # Replace with your password
    'group.id': 'ccdm-consumer-example',
    'auto.offset.reset': 'earliest'
}

# Topic to consume from
CCDM_TOPIC = 'ss4.ccdm.detection'

# Topic to produce to (for demonstration)
ASSESSMENT_TOPIC = 'ss6.threat.assessment'

def delivery_report(err, msg):
    """Callback for message delivery reports."""
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def analyze_ccdm_detection(detection):
    """
    Analyze a CCDM detection and generate a threat assessment.
    This is a simplified example - in a real application, you would implement
    more sophisticated analysis.
    """
    # Extract key information from the detection
    object_id = detection['payload']['objectId']
    ccdm_type = detection['payload']['ccdmType']
    confidence = detection['payload']['confidence']
    
    # Simple logic to determine threat level based on CCDM type and confidence
    threat_level = "LOW"
    if ccdm_type in ["DECEPTION", "MANEUVERING"]:
        if confidence > 0.8:
            threat_level = "HIGH"
        elif confidence > 0.5:
            threat_level = "MEDIUM"
    
    # Generate a threat assessment
    assessment = {
        "header": {
            "messageId": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "source": "ccdm-consumer-example",
            "messageType": "threat.assessment",
            "traceId": detection['header']['traceId'],
            "parentMessageIds": [detection['header']['messageId']]
        },
        "payload": {
            "assessmentId": str(uuid.uuid4()),
            "objectId": object_id,
            "assessmentTime": datetime.utcnow().isoformat(),
            "threatLevel": threat_level,
            "confidence": min(confidence + 0.1, 1.0),  # Slightly adjust confidence
            "source": "CCDM_ANALYSIS",
            "description": f"Threat assessment based on {ccdm_type} detection",
            "relatedDetections": [
                {
                    "detectionId": detection['payload']['detectionId'],
                    "detectionType": "CCDM",
                    "weight": 1.0
                }
            ],
            "recommendedActions": generate_recommendations(ccdm_type, threat_level)
        }
    }
    
    return assessment

def generate_recommendations(ccdm_type, threat_level):
    """Generate recommended actions based on CCDM type and threat level."""
    recommendations = []
    
    if threat_level == "HIGH":
        recommendations.append("Increase monitoring frequency")
        recommendations.append("Alert space operations center")
        
        if ccdm_type == "MANEUVERING":
            recommendations.append("Predict possible trajectories")
            recommendations.append("Assess potential conjunction risks")
        elif ccdm_type == "DECEPTION":
            recommendations.append("Verify object identity through multiple sensors")
            recommendations.append("Cross-reference with intelligence sources")
    
    elif threat_level == "MEDIUM":
        recommendations.append("Continue monitoring")
        recommendations.append("Schedule follow-up observations")
    
    else:  # LOW
        recommendations.append("Maintain normal monitoring schedule")
    
    return recommendations

def process_message(detection, producer=None):
    """Process a CCDM detection message and optionally produce a threat assessment."""
    try:
        # Log the detection
        logger.info(f"Processing CCDM detection: {detection['payload']['detectionId']}")
        logger.info(f"  Object: {detection['payload']['objectId']}")
        logger.info(f"  Type: {detection['payload']['ccdmType']}")
        logger.info(f"  Confidence: {detection['payload']['confidence']}")
        
        # Analyze the detection
        assessment = analyze_ccdm_detection(detection)
        
        # If a producer was provided, send the assessment to Kafka
        if producer:
            producer.produce(
                ASSESSMENT_TOPIC,
                key=assessment['payload']['objectId'],
                value=json.dumps(assessment).encode('utf-8'),
                callback=delivery_report
            )
            producer.flush()
        
        return assessment
    
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return None

def main():
    """Main function to run the CCDM consumer."""
    # Create Consumer instance
    consumer = Consumer(KAFKA_CONFIG)
    
    # Create Producer instance (for demonstration)
    producer_config = KAFKA_CONFIG.copy()
    producer_config.pop('group.id', None)
    producer_config.pop('auto.offset.reset', None)
    producer = Producer(producer_config)
    
    try:
        # Subscribe to topic
        consumer.subscribe([CCDM_TOPIC])
        logger.info(f"Subscribed to {CCDM_TOPIC}")
        
        # Process messages
        while True:
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.info(f"Reached end of partition {msg.partition()}")
                else:
                    logger.error(f"Error: {msg.error()}")
            else:
                try:
                    # Parse the message
                    detection = json.loads(msg.value().decode('utf-8'))
                    
                    # Process the detection
                    process_message(detection, producer)
                    
                except json.JSONDecodeError:
                    logger.error("Failed to parse message as JSON")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    
    finally:
        # Close down consumer and producer
        consumer.close()
        logger.info("Consumer closed")

if __name__ == "__main__":
    main() 