# AstroShield Sample Data

This directory contains sample data for testing AstroShield integration. Each file represents a different message type from the AstroShield Kafka topics.

## Object Identification Standard

Throughout the AstroShield platform, space objects are identified using two standard identifiers:

1. **objectId** - String identifier with format `SATCAT-{number}` (e.g., `SATCAT-25544`), allowing for custom prefixes for different catalogs.
2. **noradId** - Integer value representing the NORAD Catalog Number (e.g., `25544`), directly compatible with existing satellite tracking systems.

Both identifiers are included in all messages that reference space objects, ensuring compatibility with various systems and providing a consistent way to cross-reference objects across different data sources.

## Files Included

### State Vectors (`ss2.data.state-vector.sample.json`)
Contains state vector data for multiple objects, including position, velocity, and covariance information. Enhanced with track information, correlation scores, state estimation methods, and catalog references. Includes examples of both well-tracked objects and uncorrelated tracks (UCTs).

### Conjunction Events (`ss5.conjunction.events.sample.json`)
Details potential conjunction events between space objects, including miss distance, probability of collision, and risk assessments.

### CCDM Detections (`ss4.ccdm.detection.sample.json`)
Contains Command, Control, and Decision Making (CCDM) detection events, identifying behaviors such as maneuvers, signal emissions, or anomalous activities.

### Response Recommendations (`ss6.response-recommendation.sample.json`) 
Provides actionable response recommendations for both on-orbit threats and launch events, including detailed course of action recommendations, alternative options, and tactics, techniques, and procedures (TTPs). Replaces the legacy threat assessment format with the more comprehensive response recommendation format used by Subsystem 6.

### Sensor Heartbeats (`ss0.sensor.heartbeat.sample.json`)
Regular status updates from various sensors in the network, including health metrics, operational status, and coverage information.

### Launch Detections (`ss0.launch.detection.sample.json`)
Information about detected launch events, including launch site, vehicle type, trajectory, and predicted target orbit.

## Message Structure

All messages follow a standardized format with a header section and a payload section. The header contains metadata like messageId, timestamp, source, messageType, traceId, and parentMessageIds for traceability. The payload contains the actual data specific to the message type.

## Usage

These sample files can be used for:
- Testing integration with the AstroShield Kafka streams
- Developing message processing applications
- Understanding the data structure and content
- Creating mock services for development and testing

## Data Quality Notes

The sample data is representative of real-world scenarios but has been generated for demonstration purposes. Specific values, object identifiers, and timestamps are fictional but structured in a way that mimics operational data.

## Subsystem Alignments

The sample data files are aligned with specific AstroShield subsystems:

### Subsystem 2 - State Estimation
The state vector sample (`ss2.data.state-vector.sample.json`) demonstrates Subsystem 2's capabilities for:
- Maintaining an internal catalog of active objects
- Correlating observations against known objects
- Processing uncorrelated tracks (UCTs) to identify new objects
- Serving current state information for any Resident Space Object

### Subsystem 6 - Response Recommendation
The response recommendation sample (`ss6.response-recommendation.sample.json`) demonstrates Subsystem 6's capabilities for:
- Providing timely, continuously updated recommendations
- Offering prioritized lists of courses of action (COAs)
- Including associated tactics, techniques, and procedures (TTPs)
- Processing both launch events and on-orbit threat detections

## Overview

Each sample file contains an array of JSON messages that follow the standardized message format used throughout the AstroShield platform. All messages include:

1. A `header` section with metadata about the message
2. A `payload` section with the actual data content

The header includes fields such as:
- `messageId`: A unique identifier for the message
- `timestamp`: When the message was created
- `source`: The subsystem that generated the message
- `messageType`: The type of message
- `traceId`: A unique identifier for tracing message flows
- `parentMessageIds`: References to parent messages (when applicable)

## Available Sample Files

| File | Description | Subsystem | Schema |
|------|-------------|-----------|--------|
| `ss0.sensor.heartbeat.sample.json` | Sensor status and health information | Data Ingestion (SS0) | `schemas/ss0.sensor.heartbeat.schema.json` |
| `ss2.data.state-vector.sample.json` | Space object state vectors with position and velocity | State Estimation (SS2) | `schemas/ss2.data.state-vector.schema.json` |
| `ss0.launch.detection.sample.json` | Launch detection events with trajectory information | Data Ingestion (SS0) | `schemas/ss0.launch.detection.schema.json` |
| `ss4.ccdm.detection.sample.json` | CCDM (Camouflage, Concealment, Deception, Maneuvering) detections | CCDM Detection (SS4) | `schemas/ss4.ccdm.detection.schema.json` |
| `ss5.conjunction.events.sample.json` | Space object conjunction (close approach) events | Hostility Monitoring (SS5) | `schemas/ss5.conjunction.events.schema.json` |
| `ss6.response-recommendation.sample.json` | Response recommendations for various threats | Response Recommendation (SS6) | `schemas/ss6.response-recommendation.schema.json` |

## Message Traceability

The sample data demonstrates the message traceability feature of AstroShield. You can follow the flow of information through the system by tracing:

1. The `traceId` field, which remains constant throughout a processing chain
2. The `parentMessageIds` field, which references the source messages that led to the current message

For example, a response recommendation message in `ss6.response-recommendation.sample.json` references a CCDM detection message from `ss4.ccdm.detection.sample.json` in its `parentMessageIds` field.

## Using the Sample Data

### For Testing

These sample files can be used to test your integration code without connecting to the live Kafka streams:

```python
import json

# Load sample data
with open('sample_data/ss4.ccdm.detection.sample.json', 'r') as f:
    ccdm_samples = json.load(f)

# Process each message
for message in ccdm_samples:
    # Your processing logic here
    process_ccdm_detection(message)
```

### For Kafka Integration Testing

You can use these samples to populate a test Kafka cluster:

```python
from confluent_kafka import Producer
import json

# Configure the producer
producer = Producer({
    'bootstrap.servers': 'localhost:9092'
})

# Load sample data
with open('sample_data/ss5.conjunction.events.sample.json', 'r') as f:
    conjunction_samples = json.load(f)

# Publish to Kafka
for message in conjunction_samples:
    producer.produce(
        'ss5.conjunction.events', 
        key=message['header']['messageId'],
        value=json.dumps(message)
    )
    producer.flush()
```

### For Schema Validation

You can validate your own generated messages against these samples to ensure compatibility:

```python
import json
import jsonschema

# Load schema
with open('schemas/ss2.data.state-vector.schema.json', 'r') as f:
    schema = json.load(f)

# Load sample for reference
with open('sample_data/ss2.data.state-vector.sample.json', 'r') as f:
    samples = json.load(f)

# Your message
my_message = create_state_vector_message()

# Validate
jsonschema.validate(my_message, schema)
```

## Data Relationships

The sample data files contain related messages that demonstrate the flow of information through the AstroShield system:

1. Sensor heartbeats (`ss0.sensor.heartbeat.sample.json`) provide status information about the sensors that collect raw data
2. State vectors (`ss2.data.state-vector.sample.json`) represent the processed positional data of space objects, including UCT processing results
3. These state vectors are used to detect conjunctions (`ss5.conjunction.events.sample.json`) and CCDM activities (`ss4.ccdm.detection.sample.json`)
4. Launch detections (`ss0.launch.detection.sample.json`) identify new objects entering space
5. All of these events feed into response recommendations (`ss6.response-recommendation.sample.json`) which provide actionable intelligence and courses of action

## Notes on Data Quality

These samples are representative of the data structure but have been simplified in some ways:
- Actual operational data may contain additional fields not shown in these samples
- Some sensitive fields may use different values in production
- The volume of real data is significantly higher than these samples

For the most accurate representation, refer to the schema files in the `schemas/` directory. 