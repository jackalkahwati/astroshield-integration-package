# AstroShield Integration Quick Start Guide

This guide provides step-by-step instructions to quickly get started with the AstroShield integration package. Follow these steps to set up your environment and begin integrating with AstroShield's APIs and Kafka streams.

## Prerequisites

- Python 3.8+ (for API examples)
- Java 11+ (for Kafka Java examples)
- Node.js 14+ (for Kafka JavaScript examples)
- Access credentials for AstroShield services (contact your AstroShield representative)

## 1. Set Up Your Environment

### Clone or Download the Integration Package

```bash
# If using Git
git clone https://github.com/astroshield/integration-package.git
cd integration-package

# Or extract the provided ZIP file
unzip astroshield-integration-package.zip
cd integration-package
```

### Install Dependencies

#### For Python Examples

```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install requests
```

#### For Java Examples

```bash
# Using Maven
cd examples/java
mvn clean install
```

#### For JavaScript Examples

```bash
# Using npm
cd examples/javascript
npm install node-rdkafka uuid
```

## 2. Configure Your Credentials

### API Credentials

Create a `.env` file in the root directory with your API credentials:

```
ASTROSHIELD_USERNAME=your-username
ASTROSHIELD_PASSWORD=your-password
ASTROSHIELD_API_KEY=your-api-key  # Optional, if using API key authentication
```

### Kafka Credentials

Edit the `config/kafka-client.properties` file and replace the placeholder values with your actual credentials:

```properties
# Replace these values
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="your-username" password="your-password";
```

## 3. Test the API Connection

Run the Python API client example to verify your connection to the AstroShield API:

```bash
cd examples/python
python api_client.py
```

If successful, you should see output showing the API health status and other information.

## 4. Test the Kafka Connection

### Using Java

```bash
cd examples/java
# Compile and run the Kafka consumer example
javac -cp "path/to/dependencies/*" KafkaConsumerExample.java
java -cp ".:path/to/dependencies/*" com.astroshield.examples.KafkaConsumerExample
```

### Using JavaScript

```bash
cd examples/javascript
node kafka-producer.js
```

## 5. Explore the API with Postman

1. Import the Postman collection from `postman/AstroShield_API.postman_collection.json`
2. Import the environment from `postman/AstroShield_API.postman_environment.json`
3. Update the environment variables with your credentials
4. Test the endpoints in the collection

## 6. Understand the Message Schemas

Review the JSON Schema files in the `schemas/` directory to understand the structure of messages for each Kafka topic:

- `ss5.launch.prediction.schema.json`: Schema for launch prediction messages
- `ss5.telemetry.data.schema.json`: Schema for telemetry data messages
- `ss5.conjunction.events.schema.json`: Schema for conjunction event messages
- `ss5.cyber.threats.schema.json`: Schema for cyber threat messages

## 7. Implement Your Integration

Use the provided examples as a starting point for your own integration:

1. Modify the API client to call the endpoints relevant to your use case
2. Adapt the Kafka consumers and producers to process the topics you're interested in
3. Implement your business logic to handle the data from AstroShield

## 8. Monitor and Troubleshoot

- Check the logs from your applications for any errors
- Verify that your Kafka consumers are receiving messages
- Ensure that your API requests are returning the expected responses

## Next Steps

- Review the full documentation in the `README.md` file
- Explore the OpenAPI specification in `api/openapi.yaml` for detailed API information
- Contact AstroShield support if you encounter any issues:
  - Email: integration-support@astroshield.com
  - Support Portal: https://support.astroshield.com

## Common Issues and Solutions

### API Connection Issues

- **401 Unauthorized**: Check your credentials and ensure they are correctly set in your environment
- **403 Forbidden**: Verify that your account has the necessary permissions
- **Connection Timeout**: Check your network configuration and firewall settings

### Kafka Connection Issues

- **Authentication Failed**: Verify your Kafka credentials in the properties file
- **Connection Refused**: Check that you have network access to the Kafka brokers
- **Topic Not Found**: Ensure you're using the correct topic names and have the necessary permissions

### Schema Validation Errors

- Ensure your messages conform to the JSON Schema definitions
- Check for required fields and correct data types
- Validate your messages against the schemas before sending them 