# AstroShield Sample Data

This directory contains sample data files that represent the various message types used in the AstroShield platform. These samples are provided to help developers understand the data structure, test their integration code, and validate their implementations without requiring access to the live data streams.

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
| `ss3.launch.detection.sample.json` | Launch detection events with trajectory information | Command & Control (SS3) | `schemas/ss3.launch.detection.schema.json` |
| `ss4.ccdm.detection.sample.json` | CCDM (Camouflage, Concealment, Deception, Maneuvering) detections | CCDM Detection (SS4) | `schemas/ss4.ccdm.detection.schema.json` |
| `ss5.conjunction.events.sample.json` | Space object conjunction (close approach) events | Hostility Monitoring (SS5) | `schemas/ss5.conjunction.events.schema.json` |
| `ss6.threat.assessment.sample.json` | Threat assessments based on detected events | Threat Assessment (SS6) | `schemas/ss6.threat.assessment.schema.json` |

## Message Traceability

The sample data demonstrates the message traceability feature of AstroShield. You can follow the flow of information through the system by tracing:

1. The `traceId` field, which remains constant throughout a processing chain
2. The `parentMessageIds` field, which references the source messages that led to the current message

For example, a threat assessment message in `ss6.threat.assessment.sample.json` may reference a CCDM detection message from `ss4.ccdm.detection.sample.json` in its `parentMessageIds` field.

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
2. State vectors (`ss2.data.state-vector.sample.json`) represent the processed positional data of space objects
3. These state vectors are used to detect conjunctions (`ss5.conjunction.events.sample.json`) and CCDM activities (`ss4.ccdm.detection.sample.json`)
4. Launch detections (`ss3.launch.detection.sample.json`) identify new objects entering space
5. All of these events feed into threat assessments (`ss6.threat.assessment.sample.json`) which provide actionable intelligence

## Notes on Data Quality

These samples are representative of the data structure but have been simplified in some ways:
- Actual operational data may contain additional fields not shown in these samples
- Some sensitive fields may use different values in production
- The volume of real data is significantly higher than these samples

For the most accurate representation, refer to the schema files in the `schemas/` directory. 