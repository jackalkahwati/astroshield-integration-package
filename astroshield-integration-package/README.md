# AstroShield Integration Package

A comprehensive integration package for connecting AstroShield with external systems including Vantiq, UDL, and Weather Services for space situational awareness and threat assessment.

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D16.0.0-brightgreen.svg)](https://nodejs.org/en/)

## Overview

AstroShield Integration Package provides a robust set of tools and utilities for seamless data exchange between AstroShield's space situational awareness platform and various external systems. The package includes data transformers, validators, messaging infrastructure, and monitoring capabilities to ensure reliable and secure communication.

## Key Features

- **Message Transformation**: Convert between internal and external message formats
- **Data Validation**: Ensure message integrity and format compliance
- **Kafka Integration**: Reliable message streaming with Kafka
- **External System Connectors**: Pre-built integrations with Vantiq, UDL, and Weather Services
- **Monitoring and Alerting**: Track integration health and performance
- **Error Handling**: Sophisticated retry and recovery mechanisms
- **Authentication**: Secure OAuth2-based authentication with all external systems

## System Architecture

AstroShield Integration Package serves as the communication layer between the core AstroShield subsystems and external services:

```
┌───────────────────────────────────────────────────────────────┐
│                     AstroShield Core                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │ Data        │  │ Target      │  │ Threat Assessment   │   │
│  │ Ingestion   │  │ Modeling    │  │ & Command Control   │   │
│  └─────────────┘  └─────────────┘  └─────────────────────┘   │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                 AstroShield Integration Package                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
│  │ Message     │  │ Validation  │  │ Kafka Streaming     │   │
│  │ Transformers│  │ & Security  │  │ & Error Handling    │   │
│  └─────────────┘  └─────────────┘  └─────────────────────┘   │
└───────┬───────────────────┬───────────────────┬──────────────┘
        │                   │                   │
┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
│   Vantiq      │   │   UDL API     │   │  Weather      │
│   Platform    │   │   Services    │   │  Services     │
└───────────────┘   └───────────────┘   └───────────────┘
```

## Quick Start

### Prerequisites

- Node.js 16.x or later
- Docker and Docker Compose for local development

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/astroshield/integration-package.git
   cd integration-package
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up the local development environment:
   ```bash
   docker-compose up -d
   ```

4. Configure the integration package:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Start the integration services:
   ```bash
   npm start
   ```

### Configuration

The integration package is configured through environment variables or a `.env` file. Key configuration options include:

- `KAFKA_BOOTSTRAP_SERVERS`: Comma-separated list of Kafka bootstrap servers
- `VANTIQ_API_URL`: URL for the Vantiq API
- `VANTIQ_CLIENT_ID`: Client ID for Vantiq OAuth2 authentication
- `UDL_API_URL`: URL for the UDL API
- `WEATHER_SERVICE_URL`: URL for the Weather Service API
- `MONGODB_URI`: MongoDB connection string

For a complete list of configuration options, see the [Configuration Documentation](docs/CONFIGURATION.md).

## Development

### Running Tests

```bash
# Run unit tests
npm test

# Run integration tests (requires Docker services)
npm run test:integration

# Run all tests
npm run test:all
```

### Building for Production

```bash
npm run build
```

The build artifacts will be stored in the `dist/` directory.

### Linting and Code Style

```bash
# Run ESLint
npm run lint

# Run ESLint with auto-fix
npm run lint:fix
```

## Documentation

- [API Documentation](docs/API.md)
- [Message Formats](docs/MESSAGE_FORMATS.md)
- [Configuration Reference](docs/CONFIGURATION.md)
- [Version Compatibility](docs/VERSION_COMPATIBILITY.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support, please open an issue on the GitHub repository or contact AstroShield support at support@astroshield.com. 