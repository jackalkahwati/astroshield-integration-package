# AstroShield Integration Package

This integration package provides all the necessary resources for integrating with AstroShield's APIs and Kafka streams. It includes API specifications, message schemas, example code, and configuration templates to help you quickly connect to and utilize AstroShield's services.

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

## Available Kafka Topics

| Topic | Description | Schema |
|-------|-------------|--------|
| `ss5.launch.prediction` | Predictions of upcoming launches | [Schema](schemas/ss5.launch.prediction.schema.json) |
| `ss5.telemetry.data` | Telemetry data from spacecraft | [Schema](schemas/ss5.telemetry.data.schema.json) |
| `ss5.conjunction.events` | Conjunction events between spacecraft | [Schema](schemas/ss5.conjunction.events.schema.json) |
| `ss5.cyber.threats` | Cyber threat notifications | [Schema](schemas/ss5.cyber.threats.schema.json) |

## Support

If you encounter any issues or have questions about integrating with AstroShield, please contact our support team:

- Email: integration-support@astroshield.com
- Support Portal: https://support.astroshield.com
- Documentation: https://docs.astroshield.com

## Version Information

- Integration Package Version: 1.0.0
- API Version: v1
- Last Updated: 2023-06-01 