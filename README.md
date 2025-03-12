# AstroShield Integration Package

This integration package provides all the necessary resources for integrating with AstroShield's APIs and Kafka streams. It includes API specifications, message schemas, example code, and configuration templates to help you quickly connect to and utilize AstroShield's services.

## Table of Contents
- [Package Contents](#package-contents)
- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [Available Kafka Topics](#available-kafka-topics)
- [Integration Best Practices](#integration-best-practices)
- [Troubleshooting](#troubleshooting)
- [Support](#support)
- [Version Information](#version-information)
- [License](#license)

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

- **Configuration Templates**
  - Kafka client configuration (`config/kafka-client.properties`)

## Getting Started

### Prerequisites
- API credentials (contact jack@lattis.io to obtain)
- Kafka cluster access (provided with your subscription)
- One of the following development environments:
  - Python 3.8+
  - Java 11+
  - Node.js 14+

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

| Topic | Description | Schema |
|-------|-------------|--------|
| `ss0.sensor.heartbeat` | Sensor health monitoring data | [Schema](schemas/ss0.sensor.heartbeat.schema.json) |
| `ss2.data.state-vector` | Spacecraft state vectors | [Schema](schemas/ss2.data.state-vector.schema.json) |
| `ss5.launch.prediction` | Predictions of upcoming launches | [Schema](schemas/ss5.launch.prediction.schema.json) |
| `ss5.telemetry.data` | Telemetry data from spacecraft | [Schema](schemas/ss5.telemetry.data.schema.json) |
| `ss5.conjunction.events` | Conjunction events between spacecraft | [Schema](schemas/ss5.conjunction.events.schema.json) |
| `ss5.cyber.threats` | Cyber threat notifications | [Schema](schemas/ss5.cyber.threats.schema.json) |

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