# AstroShield Integration Package Configuration Reference

This document provides detailed information about all configuration options available in the AstroShield Integration Package. Configuration can be provided through environment variables or a `.env` file.

## Configuration Methods

### Environment Variables

You can set these configuration values directly as environment variables in your deployment environment.

### .env File

For local development, you can create a `.env` file in the root directory of the project. An example file (`.env.example`) is provided as a template.

```bash
# Copy the example file
cp .env.example .env

# Edit the file with your own settings
nano .env
```

## Configuration Categories

- [General Settings](#general-settings)
- [Kafka Configuration](#kafka-configuration)
- [Vantiq Integration](#vantiq-integration)
- [UDL Integration](#udl-integration)
- [Weather Service Integration](#weather-service-integration)
- [Database Configuration](#database-configuration)
- [Redis Configuration](#redis-configuration)
- [Error Handling and Monitoring](#error-handling-and-monitoring)
- [Feature Flags](#feature-flags)

## General Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|:--------:|
| `NODE_ENV` | Environment mode (`development`, `production`, `test`) | `development` | No |
| `LOG_LEVEL` | Logging level (`debug`, `info`, `warn`, `error`) | `info` | No |
| `CORRELATION_ID_HEADER` | HTTP header name for correlation ID | `x-correlation-id` | No |
| `REQUEST_TIMEOUT` | Default timeout for HTTP requests (ms) | `30000` | No |

## Kafka Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|:--------:|
| `KAFKA_BOOTSTRAP_SERVERS` | Comma-separated list of Kafka bootstrap servers | - | Yes |
| `KAFKA_CLIENT_ID` | Client ID for Kafka connections | `astroshield-integration` | No |
| `KAFKA_GROUP_ID` | Consumer group ID for Kafka consumers | `astroshield-integration-group` | No |
| `KAFKA_CONNECTION_TIMEOUT` | Connection timeout for Kafka (ms) | `10000` | No |
| `KAFKA_REQUEST_TIMEOUT` | Request timeout for Kafka operations (ms) | `30000` | No |
| `KAFKA_RETRY_MAX_RETRIES` | Maximum number of retries for Kafka operations | `5` | No |
| `KAFKA_AUTO_OFFSET_RESET` | Initial offset when no committed offset exists (`earliest`, `latest`) | `earliest` | No |

### Secure Kafka Connection

For secure Kafka connections, these additional variables are required:

| Variable | Description | Default | Required |
|----------|-------------|---------|:--------:|
| `KAFKA_SASL_MECHANISM` | SASL mechanism (`plain`, `scram-sha-256`, `scram-sha-512`) | - | For secure connections |
| `KAFKA_SASL_USERNAME` | SASL username | - | For secure connections |
| `KAFKA_SASL_PASSWORD` | SASL password | - | For secure connections |
| `KAFKA_SSL_ENABLED` | Enable SSL connections to Kafka | `false` | No |
| `KAFKA_SSL_CA_CERT_PATH` | Path to CA certificate file for SSL | - | If SSL enabled |

## Vantiq Integration

| Variable | Description | Default | Required |
|----------|-------------|---------|:--------:|
| `VANTIQ_API_URL` | Vantiq API URL | - | Yes |
| `VANTIQ_CLIENT_ID` | Vantiq OAuth2 client ID | - | Yes |
| `VANTIQ_CLIENT_SECRET` | Vantiq OAuth2 client secret | - | Yes |
| `VANTIQ_USERNAME` | Vantiq username | - | Yes |
| `VANTIQ_PASSWORD` | Vantiq password | - | Yes |
| `VANTIQ_TOKEN_REFRESH_INTERVAL` | Interval for token refresh (ms) | `3600000` | No |
| `VANTIQ_REQUEST_TIMEOUT` | Timeout for Vantiq API requests (ms) | `10000` | No |

## UDL Integration

| Variable | Description | Default | Required |
|----------|-------------|---------|:--------:|
| `UDL_API_URL` | UDL API base URL | - | Yes |
| `UDL_API_KEY` | UDL API key | - | Yes* |
| `UDL_USERNAME` | UDL username | - | Yes* |
| `UDL_PASSWORD` | UDL password | - | Yes* |
| `UDL_USE_SECURE_MESSAGING` | Enable UDL secure messaging | `false` | No |
| `UDL_SECURE_MESSAGING_URL` | UDL secure messaging WebSocket URL | - | For secure messaging |
| `UDL_REQUEST_TIMEOUT` | Timeout for UDL API requests (ms) | `15000` | No |

*Either API key or username/password authentication is required

## Weather Service Integration

| Variable | Description | Default | Required |
|----------|-------------|---------|:--------:|
| `WEATHER_SERVICE_URL` | Weather service API URL | - | Yes |
| `WEATHER_SERVICE_API_KEY` | Weather service API key | - | Yes |
| `WEATHER_SERVICE_REQUEST_TIMEOUT` | Timeout for weather service requests (ms) | `5000` | No |

## Database Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|:--------:|
| `MONGODB_URI` | MongoDB connection URI | - | Yes |
| `MONGODB_USE_SSL` | Enable SSL for MongoDB connections | `false` | No |
| `MONGODB_POOL_SIZE` | MongoDB connection pool size | `10` | No |
| `MONGODB_RETRY_WRITES` | Enable retryable writes for MongoDB | `true` | No |

## Redis Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|:--------:|
| `REDIS_URI` | Redis connection URI | - | Yes |
| `REDIS_PREFIX` | Key prefix for Redis cache | `astroshield:` | No |
| `REDIS_CACHE_TTL` | Default TTL for cache entries (seconds) | `3600` | No |

## Error Handling and Monitoring

| Variable | Description | Default | Required |
|----------|-------------|---------|:--------:|
| `ERROR_RETRY_LIMIT` | Maximum number of retries for failed operations | `3` | No |
| `ERROR_RETRY_DELAY` | Delay between retries (ms) | `1000` | No |
| `DEAD_LETTER_TOPIC` | Kafka topic for dead-letter messages | `astroshield.dead-letter` | No |
| `ENABLE_PERFORMANCE_METRICS` | Enable collection of performance metrics | `true` | No |
| `METRICS_REPORTING_INTERVAL` | Interval for reporting metrics (ms) | `60000` | No |

## Feature Flags

| Variable | Description | Default | Required |
|----------|-------------|---------|:--------:|
| `FEATURE_CIRCUIT_BREAKER` | Enable circuit breaker pattern for external services | `true` | No |
| `FEATURE_RATE_LIMITING` | Enable rate limiting for external API calls | `true` | No |
| `FEATURE_SCHEMA_VALIDATION` | Enable schema validation for messages | `true` | No |
| `FEATURE_CACHED_TRANSFORMATIONS` | Enable caching of transformation results | `true` | No |

## Example Configuration

Here's a minimal example configuration for connecting to Vantiq and Kafka:

```bash
# General Settings
NODE_ENV=production
LOG_LEVEL=info

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=kafka-1.example.com:9092,kafka-2.example.com:9092
KAFKA_CLIENT_ID=my-astroshield-service
KAFKA_GROUP_ID=my-consumer-group

# Vantiq Integration
VANTIQ_API_URL=https://my-vantiq-instance.example.com/api/v1
VANTIQ_CLIENT_ID=my-client-id
VANTIQ_CLIENT_SECRET=my-client-secret
VANTIQ_USERNAME=my-username
VANTIQ_PASSWORD=my-password

# Database Configuration
MONGODB_URI=mongodb://user:password@mongodb.example.com:27017/astroshield
```

## Configuration Validation

On startup, the integration package validates all required configuration values and provides clear error messages if any are missing or invalid. Optional values that are not provided will use their default values.

## Secure Configuration Management

For production deployments, we recommend:

1. Using environment variables instead of `.env` files
2. Using a secrets management solution like Kubernetes Secrets, AWS Secrets Manager, or HashiCorp Vault
3. Rotating all credentials regularly
4. Limiting access to configuration values to authorized personnel only 