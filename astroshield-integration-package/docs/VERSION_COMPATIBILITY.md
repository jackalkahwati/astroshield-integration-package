# AstroShield Integration Package Version Compatibility

This document outlines the compatibility matrix between the AstroShield Integration Package versions and dependent systems.

## Version Compatibility Matrix

| AstroShield Version | Vantiq API | UDL API | Weather Service | Kafka | Node.js | MongoDB |
|---------------------|------------|---------|-----------------|-------|---------|---------|
| 1.0.0               | 2.1.x      | 3.5.x   | 1.2.x           | 3.3.x | 16.x-18.x | 5.0-6.0 |
| 0.9.0               | 2.0.x      | 3.4.x   | 1.1.x           | 3.2.x | 16.x-18.x | 5.0-6.0 |
| 0.8.0               | 1.9.x      | 3.3.x   | 1.0.x           | 3.1.x | 16.x    | 5.0     |
| 0.7.0               | 1.8.x      | 3.2.x   | 1.0.x           | 3.0.x | 14.x-16.x | 4.4-5.0 |

## System Requirements

### Operating Systems
- **Supported**: Linux (Ubuntu 20.04+, CentOS 8+), macOS 11.0+
- **Experimental**: Windows 10+ with WSL2

### Hardware Requirements
- **Minimum**: 4 CPU cores, 8GB RAM, 20GB storage
- **Recommended**: 8+ CPU cores, 16GB+ RAM, 50GB+ SSD storage

### Network Requirements
- Outbound access to Vantiq, UDL, and Weather Service endpoints
- Low-latency connection (<100ms RTT) for real-time operations

## Breaking Changes

### 1.0.0 → 0.9.0
- Authentication mechanism updated to use OAuth2 (not backward compatible with token-based auth)
- Kafka message format changes in maneuver detection events

### 0.9.0 → 0.8.0
- UDL API endpoint structure changes
- Schema changes for observation window messages

### 0.8.0 → 0.7.0
- Weather service integration completely refactored
- Configuration file format changes

## Upgrade Recommendations

When upgrading between versions with breaking changes, please follow these steps:

1. Back up all configuration files and custom code
2. Review breaking changes for the target version
3. Update dependent systems to compatible versions
4. Deploy the new version in a staging environment first
5. Run the compatibility verification suite (`npm run compatibility:check`)
6. Update any custom code to match new APIs
7. Deploy to production during a maintenance window

## Deprecation Notices

### Upcoming in 1.1.0
- The legacy `sendLegacyMessage()` method will be removed
- Support for Node.js 16.x will be deprecated
- MongoDB 5.0 will become the minimum supported version

## Support Policy

- Each version receives full support for 6 months after release
- Critical security patches may be released for up to 12 months
- For versions older than 12 months, upgrade to a supported version is required

## Core Compatibility

| AstroShield Version | Node.js       | Kafka          | Vantiq         | MongoDB        | Redis          |
|---------------------|---------------|----------------|----------------|----------------|----------------|
| 1.0.0               | 16.x, 18.x    | 2.8.0 - 3.4.0  | 1.30.x - 1.33.x| 5.0.x - 6.0.x  | 6.2.x - 7.0.x  |
| 0.9.0               | 16.x          | 2.8.0 - 3.3.0  | 1.30.x - 1.32.x| 5.0.x          | 6.2.x          |
| 0.8.0               | 14.x, 16.x    | 2.7.0 - 3.2.0  | 1.29.x - 1.31.x| 4.4.x - 5.0.x  | 6.0.x - 6.2.x  |

## Browser Compatibility (Dashboard)

| AstroShield Version | Chrome        | Firefox        | Safari         | Edge           |
|---------------------|---------------|----------------|----------------|----------------|
| 1.0.0               | 90+           | 88+            | 14+            | 90+            |
| 0.9.0               | 88+           | 86+            | 14+            | 88+            |
| 0.8.0               | 85+           | 84+            | 13+            | 85+            |

## API Compatibility

| AstroShield Version | API Version    | Breaking Changes from Previous Version |
|---------------------|----------------|----------------------------------------|
| 1.0.0               | v2             | New authentication flow, restructured response objects |
| 0.9.0               | v1.1           | Added pagination to object listings |
| 0.8.0               | v1             | Initial stable API release |

## Third-Party Integration Compatibility

| AstroShield Version | Space-Track API | AGI STK       | NORAD TLEs     | SPICE          |
|---------------------|-----------------|---------------|----------------|----------------|
| 1.0.0               | v2.3            | 12.x, 11.x    | Format 3       | N0066          |
| 0.9.0               | v2.2            | 11.x          | Format 3       | N0066          |
| 0.8.0               | v2.1            | 11.x          | Format 2, 3    | N0065          |

## Notes

- **Node.js**: We recommend using LTS versions of Node.js for production environments.
- **Kafka**: Versions listed are for Kafka server. Client libraries should match server versions.
- **Vantiq**: Integration tested with listed Vantiq platform versions.
- **Browser Support**: Versions listed are minimum supported versions. Latest versions are always recommended.
- **API Versions**: Each AstroShield release supports specific API versions. When upgrading, check for breaking changes.

## Recommended Setup

For optimal performance and compatibility, we recommend:
- Node.js 18.x LTS
- Kafka 3.4.0
- Vantiq 1.33.x
- MongoDB 6.0
- Redis 7.0

Please report any compatibility issues to the AstroShield support team. 