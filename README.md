# AstroShield Integration Package

This integration package provides all the necessary resources for integrating with AstroShield's APIs and Kafka streams. It includes API specifications, message schemas, example code, and configuration templates to help you quickly connect to and utilize AstroShield's services.

## Table of Contents
- [Package Contents](#package-contents)
- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [Available Kafka Topics](#available-kafka-topics)
- [System Architecture](#system-architecture)
- [Message Traceability](#message-traceability)
- [Integration Best Practices](#integration-best-practices)
- [Troubleshooting](#troubleshooting)
- [Support](#support)
- [Version Information](#version-information)
- [License](#license)
- [UDL Integration](#udl-integration)

## Package Contents

- **API Documentation**
  - OpenAPI 3.0 specification (`api/openapi.yaml`)
  - Postman collection (`postman/AstroShield_API.postman_collection.json`)
  - Postman environment (`postman/AstroShield_API.postman_environment.json`)

- **Kafka Message Schemas**
  - JSON Schema definitions for all Kafka topics (`schemas/`)
  - Example messages for each topic

- **Example Code**
  - Python examples for API integration (`examples/python/`)
  - Java examples for Kafka consumer integration (`examples/java/`)
  - JavaScript examples for Kafka producer integration (`examples/javascript/`)
  - UDL Secure Messaging integration examples (`examples/udl_integration_example.py`)

- **Configuration Templates**
  - Kafka client configuration (`config/kafka-client.properties`)
  
- **UDL Integration**
  - UDL API client
  - UDL Secure Messaging client for real-time data streaming
  - Data transformers for UDL to AstroShield format conversion
  - Continuous integration components

## Getting Started

### Prerequisites
- API credentials (contact jack@lattis.io to obtain)
- Kafka cluster access (provided with your subscription)
- One of the following development environments:
  - Python 3.8+
  - Java 11+
  - Node.js 14+
- UDL credentials (for UDL integration features)

### API Integration

1. Review the OpenAPI specification in `api/openapi.yaml` to understand the available endpoints, request/response formats, and authentication requirements.

2. Import the Postman collection and environment from the `postman/` directory to quickly test the API endpoints.

3. Use the Python example in `examples/python/api_client.py` as a reference for implementing your own API client.

### Kafka Integration

1. Review the JSON Schema definitions in the `schemas/` directory to understand the structure of messages for each Kafka topic.

2. Configure your Kafka client using the template in `config/kafka-client.properties`. Replace the placeholder values with your actual credentials provided by AstroShield.

3. Use the example code in `examples/java/` and `examples/javascript/` as a reference for implementing your own Kafka consumers and producers.

## Authentication

### API Authentication

The AstroShield API supports two authentication methods:

1. **JWT Authentication**: Obtain a JWT token by sending a POST request to `/auth/token` with your username and password. Include the token in the `Authorization` header of subsequent requests as `Bearer <token>`.

2. **API Key Authentication**: Include your API key in the `X-API-Key` header of each request.

### Kafka Authentication

Kafka connections use SASL/PLAIN authentication over SSL. Configure your Kafka client with the following:

- Security protocol: `SASL_SSL`
- SASL mechanism: `PLAIN`
- SASL JAAS config: Username and password provided by AstroShield

Example configuration:
```properties
bootstrap.servers=kafka.astroshield.com:9093
security.protocol=SASL_SSL
sasl.mechanism=PLAIN
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="your-username" password="your-password";
```

## Available Kafka Topics

| Topic | Description | Schema | Subsystem |
|-------|-------------|--------|-----------|
| `ss0.sensor.heartbeat` | Sensor health monitoring data | [Schema](schemas/ss0.sensor.heartbeat.schema.json) | Subsystem 0 (Data Ingestion) |
| `ss2.data.state-vector` | Spacecraft state vectors | [Schema](schemas/ss2.data.state-vector.schema.json) | Subsystem 2 (State Estimation) |
| `ss4.ccdm.detection` | CCDM behavior detection | [Schema](schemas/ss4.ccdm.detection.schema.json) | Subsystem 4 (CCDM) |
| `ss5.launch.prediction` | Predictions of upcoming launches | [Schema](schemas/ss5.launch.prediction.schema.json) | Subsystem 5 (Hostility Monitoring) |
| `ss5.telemetry.data` | Telemetry data from spacecraft | [Schema](schemas/ss5.telemetry.data.schema.json) | Subsystem 5 (Hostility Monitoring) |
| `ss5.conjunction.events` | Conjunction events between spacecraft | [Schema](schemas/ss5.conjunction.events.schema.json) | Subsystem 5 (Hostility Monitoring) |
| `ss5.cyber.threats` | Cyber threat notifications | [Schema](schemas/ss5.cyber.threats.schema.json) | Subsystem 5 (Hostility Monitoring) |

## System Architecture

AstroShield is organized into a modular subsystem architecture that enables distributed processing and scalability. Each subsystem focuses on specific aspects of space domain awareness:

### Subsystem 0: Data Ingestion
Responsible for ingesting data from various sensors and external sources. This subsystem handles the initial processing of raw data and makes it available to other subsystems through Kafka topics.

### Subsystem 1: Target Modeling
Maintains a database of known space objects, their capabilities, and characteristics. This subsystem provides reference data for object identification and threat assessment.

### Subsystem 2: State Estimation
Performs orbit determination, correlation, maneuver detection, and propagation. This subsystem is responsible for maintaining accurate state vectors for tracked objects and predicting their future positions.

### Subsystem 3: Command and Control (C2)
Handles sensor tasking and orchestration to optimize observation collection. This subsystem prioritizes objects for tracking based on inputs from other subsystems.

### Subsystem 4: CCDM Detection
Focuses on detecting Camouflage, Concealment, Deception, and Maneuvering behaviors. This subsystem analyzes pattern-of-life violations and anomalous behaviors that might indicate hostile intent.

### Subsystem 5: Hostility Monitoring
Monitors for potential threats, including conjunction events, cyber threats, and launch predictions. This subsystem provides early warning of potential hostile activities.

### Subsystem 6: Threat Assessment
Integrates data from all other subsystems to provide comprehensive threat assessments and recommended actions.

## Message Traceability

AstroShield implements message traceability to track the lineage of information as it flows through the system. This enables users to understand how detections, alerts, and assessments were derived from raw data.

### Traceability Headers

All Kafka messages include traceability information in their headers:

- `traceId`: A unique identifier that follows the processing chain across multiple messages
- `parentMessageIds`: References to previous messages that contributed to the current message

### Implementing Traceability

When consuming messages and producing new ones based on that data:

1. Extract the `traceId` from the incoming message
2. Use the same `traceId` in your outgoing message
3. Add the `messageId` of the incoming message to the `parentMessageIds` array in your outgoing message

Example in Python:
```python
def process_message(incoming_message):
    # Process the message data
    result = analyze_data(incoming_message['payload'])
    
    # Create a new message with traceability
    outgoing_message = {
        'header': {
            'messageId': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'my-application',
            'messageType': 'my-message-type',
            'traceId': incoming_message['header']['traceId'],
            'parentMessageIds': [incoming_message['header']['messageId']]
        },
        'payload': result
    }
    
    return outgoing_message
```

## Integration Best Practices

### API Integration
- Implement proper error handling and retry logic
- Cache responses when appropriate to reduce API calls
- Use connection pooling for better performance
- Set reasonable timeouts for API requests
- Implement rate limiting in your client to avoid hitting API limits

### Kafka Integration
- Use consumer groups for scalable message processing
- Implement proper error handling for message processing
- Consider using a dead-letter queue for failed messages
- Monitor consumer lag to ensure timely processing
- Implement idempotent processing to handle duplicate messages

### Security Best Practices
- Store API keys and credentials securely (use environment variables or a secrets manager)
- Rotate API keys regularly (recommended every 90 days)
- Use TLS for all communications
- Implement proper access controls for your integration
- Audit and log all API calls and Kafka message processing

## Troubleshooting

### Common API Issues

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| 401 Unauthorized | Invalid or expired token | Refresh your JWT token or check API key |
| 403 Forbidden | Insufficient permissions | Contact jack@lattis.io to update permissions |
| 429 Too Many Requests | Rate limit exceeded | Implement backoff and retry logic |
| 5xx Server Error | Server-side issue | Retry with exponential backoff |

### Common Kafka Issues

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| Connection failures | Network or authentication issues | Check credentials and network connectivity |
| Consumer lag | Slow processing or high message volume | Scale consumers or optimize processing |
| Deserialization errors | Schema mismatch | Verify message format against schema |
| Offset commit failures | Broker connectivity issues | Implement proper error handling |

## Support

If you encounter any issues or have questions about integrating with AstroShield, please contact:

- Email: jack@lattis.io
- Response Time: Within 24 hours
- For urgent issues: Include "URGENT" in the email subject

## Version Information

- Integration Package Version: 1.0.0
- API Version: v1
- Last Updated: 2024-03-12

## License

This software is proprietary and confidential. See the [LICENSE](LICENSE) file for details.

Copyright (c) 2024 Stardrive Inc. All Rights Reserved. 

## UDL Integration

The AstroShield Integration Package includes a powerful integration with the Unified Data Library (UDL) APIs for space situational awareness data. This integration supports both the REST API for polling-based data retrieval and the Secure Messaging API for real-time streaming.

### Authentication

The UDL client supports three authentication methods:

1. **API Key Authentication**: Set the `UDL_API_KEY` environment variable or pass the `api_key` parameter to the client constructor.
2. **Basic Authentication**: Set the `UDL_USERNAME` and `UDL_PASSWORD` environment variables or pass the `username` and `password` parameters to the client constructor.
3. **Token Authentication**: This method is currently not working with the UDL API.

For most users, Basic Authentication is the recommended method.

### Secure Messaging API

The Secure Messaging API provides real-time streaming access to UDL data. To use this feature:

1. **Request Access**: Special authorization is required for the Secure Messaging API. Contact the UDL team to request access by filling out the Secure Messaging Access Form.
2. **Enable in Configuration**: Set `use_secure_messaging=True` when initializing the `UDLIntegration` class.

Without proper authorization, attempts to access the Secure Messaging API will result in 403 Forbidden errors.

### Basic Usage

```python
from asttroshield.udl_integration import UDLClient, UDLMessagingClient, UDLIntegration

# Standard REST API client
client = UDLClient(
    username="your-username",
    password="your-password"
)

# Secure Messaging client (requires special authorization)
messaging_client = UDLMessagingClient(
    username="your-username",
    password="your-password"
)

# Complete integration with Kafka
integration = UDLIntegration(
    udl_username="your-username",
    udl_password="your-password",
    kafka_bootstrap_servers="kafka:9092",
    use_secure_messaging=True  # Enable if you have authorization
)

# Process specific data types
integration.process_state_vectors(epoch="now")
integration.process_conjunctions()

# Stream data in real-time (requires Secure Messaging authorization)
integration.stream_topic("statevector", transform_state_vector, "astroshield-statevectors")
```

For more detailed information, examples, and usage, refer to the documentation in the `src/asttroshield/udl_integration/README.md` file. The integration package provides a comprehensive solution for integrating UDL data with your AstroShield Kafka topics and includes extensive examples and documentation to help you get started quickly. 