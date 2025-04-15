# Message Formats

This document describes the message formats used within the AstroShield Integration Package for communication with external systems and internal subsystems.

## Common Message Structure

All messages in the AstroShield Integration Package follow a common envelope structure:

```json
{
  "header": {
    "messageId": "string",       // Unique identifier for the message
    "correlationId": "string",   // ID for tracing message chains
    "source": "string",          // Source system/component
    "timestamp": "string",       // ISO-8601 format (YYYY-MM-DDTHH:MM:SS.sssZ)
    "messageType": "string",     // Type of message
    "version": "string"          // Message schema version
  },
  "payload": {
    // Message-specific content
  }
}
```

## Vantiq Message Formats

### Maneuver Detection

Message sent to Vantiq when a spacecraft maneuver is detected.

**Topic:** `astroshield.vantiq.maneuver`

```json
{
  "header": {
    "messageId": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "correlationId": "7ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "source": "astroshield.subsystem2",
    "timestamp": "2023-09-15T14:32:20.123Z",
    "messageType": "MANEUVER_DETECTION",
    "version": "1.0"
  },
  "payload": {
    "objectId": "string",                  // Object identifier
    "objectName": "string",                // Human-readable name
    "noradId": "string",                   // NORAD catalog ID
    "maneuverType": "string",              // Type of maneuver detected
    "confidenceScore": 0.95,               // Confidence level (0-1)
    "detectionTime": "2023-09-15T14:30:00.000Z", // When maneuver was detected
    "estimatedStartTime": "2023-09-15T14:28:30.000Z", // Estimated maneuver start
    "estimatedEndTime": "2023-09-15T14:29:45.000Z",   // Estimated maneuver end
    "deltaV": {                            // Velocity change
      "magnitude": 10.5,                   // Delta-V magnitude (m/s)
      "direction": {                       // Direction vector
        "x": 0.5,
        "y": 0.3,
        "z": -0.8
      }
    },
    "preManeuverState": {                  // State before maneuver
      "epoch": "2023-09-15T14:28:00.000Z",
      "position": {
        "x": 6378.0,                       // km in ECI frame
        "y": 0.0,
        "z": 0.0
      },
      "velocity": {
        "x": 0.0,                          // km/s in ECI frame
        "y": 7.7,
        "z": 0.0
      }
    },
    "postManeuverState": {                 // State after maneuver
      "epoch": "2023-09-15T14:30:00.000Z",
      "position": {
        "x": 6378.0,
        "y": 0.05,
        "z": 0.0
      },
      "velocity": {
        "x": 0.0,
        "y": 7.8,
        "z": 0.0
      }
    },
    "orbitChangeParameters": {             // Optional orbit change details
      "deltaInclination": 0.02,            // deg
      "deltaEccentricity": 0.001,
      "deltaSemiMajorAxis": 5.0,           // km
      "deltaRaan": 0.05                    // deg
    }
  }
}
```

### Object Details

Message containing detailed information about a space object.

**Topic:** `astroshield.vantiq.object`

```json
{
  "header": {
    "messageId": "8ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "correlationId": "7ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "source": "astroshield.subsystem1",
    "timestamp": "2023-09-15T14:32:22.456Z",
    "messageType": "OBJECT_DETAILS",
    "version": "1.0"
  },
  "payload": {
    "objectId": "string",
    "objectName": "string",
    "noradId": "string",
    "internationalDesignator": "string",  // International designator (launch year, number)
    "objectType": "string",               // PAYLOAD, ROCKET_BODY, DEBRIS, UNKNOWN
    "countryOfOrigin": "string",          // Country code
    "launchDate": "2021-03-15T00:00:00.000Z",
    "status": "string",                  // ACTIVE, INACTIVE, DECAYED
    "physicalProperties": {
      "mass": 1200.5,                    // kg, may be null if unknown
      "length": 5.2,                     // meters
      "width": 2.3,                      // meters
      "height": 2.1,                     // meters
      "rcs": 1.5                         // Radar Cross Section (m²)
    },
    "orbitParameters": {
      "epoch": "2023-09-15T12:00:00.000Z",
      "semiMajorAxis": 7000.0,           // km
      "eccentricity": 0.001,
      "inclination": 51.6,               // deg
      "raan": 235.7,                     // deg, Right Ascension of Ascending Node
      "argumentOfPerigee": 90.0,         // deg
      "meanAnomaly": 45.0,               // deg
      "period": 92.5,                    // minutes
      "apogee": 420.5,                   // km
      "perigee": 415.2                   // km
    },
    "lastUpdated": "2023-09-15T14:00:00.000Z",
    "updateSource": "string",            // Source of the latest update
    "notes": "string",                   // Additional information
    "tags": ["string"],                  // Array of classification tags
    "metadata": {                        // Additional extensible metadata
      "key1": "value1",
      "key2": "value2"
    }
  }
}
```

### Observation

Message containing observation data of a space object.

**Topic:** `astroshield.vantiq.observation`

```json
{
  "header": {
    "messageId": "9ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "correlationId": "7ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "source": "astroshield.subsystem0",
    "timestamp": "2023-09-15T14:32:25.789Z",
    "messageType": "OBSERVATION",
    "version": "1.0"
  },
  "payload": {
    "observationId": "string",
    "objectId": "string",                  // Object identifier, may be null if unidentified
    "noradId": "string",                   // NORAD catalog ID, may be null
    "sensorId": "string",                  // ID of the sensor that made the observation
    "sensorType": "string",                // RADAR, OPTICAL, RF, OTHER
    "observationTime": "2023-09-15T14:30:10.500Z",
    "observationType": "string",           // POSITION, ANGLE_ONLY, RANGE_DOPPLER, etc.
    "dataQuality": 0.85,                   // Quality score (0-1)
    "lightTime": 0.05,                     // Light time correction (s)
    "position": {                          // May be null depending on observation type
      "x": 6378.0,                         // km in specified frame
      "y": 0.0,
      "z": 0.0,
      "sigmaX": 0.1,                       // Uncertainty
      "sigmaY": 0.1,
      "sigmaZ": 0.1
    },
    "velocity": {                          // May be null depending on observation type
      "x": 0.0,                            // km/s in specified frame
      "y": 7.7,
      "z": 0.0,
      "sigmaX": 0.05,                      // Uncertainty
      "sigmaY": 0.05,
      "sigmaZ": 0.05
    },
    "angleOnly": {                         // May be null depending on observation type
      "rightAscension": 180.5,             // deg
      "declination": 23.4,                 // deg
      "sigmaRightAscension": 0.02,         // Uncertainty (deg)
      "sigmaDeclination": 0.02             // Uncertainty (deg)
    },
    "rangeDoppler": {                      // May be null depending on observation type
      "range": 1000.5,                     // km
      "rangeRate": 2.5,                    // km/s
      "sigmaRange": 0.05,                  // Uncertainty (km)
      "sigmaRangeRate": 0.01               // Uncertainty (km/s)
    },
    "referenceFrame": "string",            // ECI, ECEF, etc.
    "processingLevel": "string",           // RAW, CALIBRATED, CORRELATED
    "metaData": {                          // Additional extensible metadata
      "key1": "value1",
      "key2": "value2"
    }
  }
}
```

## UDL Message Formats

### State Vector

Message containing state vector data from UDL.

**Topic:** `astroshield.udl.state-vector`

```json
{
  "header": {
    "messageId": "aba7b810-9dad-11d1-80b4-00c04fd430c8",
    "correlationId": "bba7b810-9dad-11d1-80b4-00c04fd430c8",
    "source": "udl.api",
    "timestamp": "2023-09-15T14:32:30.123Z",
    "messageType": "STATE_VECTOR",
    "version": "1.0"
  },
  "payload": {
    "udlId": "string",                    // UDL identifier
    "noradId": "string",                  // NORAD catalog ID
    "objectName": "string",               // Human-readable name
    "epoch": "2023-09-15T14:30:00.000Z",  // Epoch of the state vector
    "frame": "string",                    // Reference frame (e.g., "ECI")
    "position": {
      "x": 6378.0,                        // km
      "y": 0.0,
      "z": 0.0
    },
    "velocity": {
      "x": 0.0,                           // km/s
      "y": 7.7,
      "z": 0.0
    },
    "covariance": [
      [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
      [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
      [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
      [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
      [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
      [0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
    ],
    "dataSource": "string",              // Source of the data
    "updateType": "string",              // ROUTINE, SPECIAL
    "metadata": {                        // Additional extensible metadata
      "key1": "value1",
      "key2": "value2"
    }
  }
}
```

### Conjunction Data

Message containing conjunction data from UDL.

**Topic:** `astroshield.udl.conjunction`

```json
{
  "header": {
    "messageId": "cba7b810-9dad-11d1-80b4-00c04fd430c8",
    "correlationId": "bba7b810-9dad-11d1-80b4-00c04fd430c8",
    "source": "udl.api",
    "timestamp": "2023-09-15T14:32:35.456Z",
    "messageType": "CONJUNCTION",
    "version": "1.0"
  },
  "payload": {
    "conjunctionId": "string",               // Unique ID for the conjunction
    "tca": "2023-09-16T12:30:45.000Z",       // Time of Closest Approach
    "missDistance": 1.5,                      // km
    "probability": 0.0001,                    // Probability of collision
    "primaryObject": {
      "objectId": "string",
      "noradId": "string",
      "objectName": "string",
      "objectType": "string",                // PAYLOAD, ROCKET_BODY, DEBRIS, UNKNOWN
      "position": {                          // Position at TCA
        "x": 6378.0,
        "y": 0.0,
        "z": 0.0
      },
      "velocity": {                          // Velocity at TCA
        "x": 0.0,
        "y": 7.7,
        "z": 0.0
      }
    },
    "secondaryObject": {
      "objectId": "string",
      "noradId": "string",
      "objectName": "string",
      "objectType": "string",
      "position": {
        "x": 6379.5,
        "y": 0.0,
        "z": 0.0
      },
      "velocity": {
        "x": 0.0,
        "y": -7.7,
        "z": 0.0
      }
    },
    "frame": "string",                       // Reference frame for positions and velocities
    "screeningCriteria": {                   // Criteria used for screening
      "minRange": 0.0,                       // km
      "timeWindow": 7,                       // days
      "screeningType": "string"
    },
    "dataSource": "string",                 // Source of the conjunction data
    "reportedTime": "2023-09-15T10:15:30.000Z", // When the conjunction was reported
    "metadata": {                           // Additional extensible metadata
      "key1": "value1",
      "key2": "value2"
    }
  }
}
```

## Weather Service Message Formats

### Space Weather Alert

Message containing space weather alert data.

**Topic:** `astroshield.weather.alert`

```json
{
  "header": {
    "messageId": "dba7b810-9dad-11d1-80b4-00c04fd430c8",
    "correlationId": "eba7b810-9dad-11d1-80b4-00c04fd430c8",
    "source": "weather.service",
    "timestamp": "2023-09-15T14:32:40.789Z",
    "messageType": "SPACE_WEATHER_ALERT",
    "version": "1.0"
  },
  "payload": {
    "alertId": "string",
    "alertType": "string",                   // SOLAR_FLARE, CME, GEOMAGNETIC_STORM, etc.
    "severity": "string",                    // MINOR, MODERATE, SEVERE, EXTREME
    "issueTime": "2023-09-15T14:30:00.000Z", // When the alert was issued
    "startTime": "2023-09-15T15:00:00.000Z", // When the event is expected to start
    "endTime": "2023-09-15T18:00:00.000Z",   // When the event is expected to end
    "description": "string",                 // Human-readable description
    "source": "string",                      // Source of the alert
    "affectedRegion": [                      // Array of affected regions
      {
        "type": "string",                    // LEO, MEO, GEO, etc.
        "coordinates": {
          "minLatitude": -90.0,              // deg
          "maxLatitude": 90.0,               // deg
          "minLongitude": -180.0,            // deg
          "maxLongitude": 180.0,             // deg
          "minAltitude": 200.0,              // km
          "maxAltitude": 36000.0             // km
        }
      }
    ],
    "parameters": {                          // Event-specific parameters
      "kpIndex": 7,                          // For geomagnetic storms
      "flareClass": "X1.5",                  // For solar flares
      "particleFlux": 1000.0,                // For radiation events
      "otherParameters": {
        "key1": "value1",
        "key2": "value2"
      }
    },
    "forecastConfidence": 0.85,              // Confidence level (0-1)
    "recommendedActions": [                  // Array of recommended actions
      "string"
    ],
    "url": "string",                         // URL for more information
    "metadata": {                            // Additional extensible metadata
      "key1": "value1",
      "key2": "value2"
    }
  }
}
```

### Space Weather Forecast

Message containing space weather forecast data.

**Topic:** `astroshield.weather.forecast`

```json
{
  "header": {
    "messageId": "fba7b810-9dad-11d1-80b4-00c04fd430c8",
    "correlationId": "eba7b810-9dad-11d1-80b4-00c04fd430c8",
    "source": "weather.service",
    "timestamp": "2023-09-15T14:32:45.123Z",
    "messageType": "SPACE_WEATHER_FORECAST",
    "version": "1.0"
  },
  "payload": {
    "forecastId": "string",
    "forecastType": "string",                // SOLAR, GEOMAGNETIC, RADIATION, etc.
    "issueTime": "2023-09-15T14:30:00.000Z", // When the forecast was issued
    "validFrom": "2023-09-15T15:00:00.000Z", // Start of forecast validity period
    "validTo": "2023-09-18T15:00:00.000Z",   // End of forecast validity period
    "description": "string",                 // Human-readable description
    "source": "string",                      // Source of the forecast
    "forecastEntries": [                     // Array of forecast time entries
      {
        "time": "2023-09-15T15:00:00.000Z", 
        "conditions": {
          "solarActivity": "string",         // LOW, MODERATE, HIGH, EXTREME
          "geomagneticActivity": "string",   // QUIET, UNSETTLED, ACTIVE, STORM
          "radiationEnvironment": "string",  // NORMAL, ELEVATED, ALERT
          "kpIndex": 3,
          "sunspotNumber": 50,
          "f10p7": 150.0,                    // Solar radio flux
          "energeticProtons": 10.0,          // pfu
          "electronFlux": 1000.0,            // electrons/cm²/day
          "otherParameters": {
            "key1": "value1",
            "key2": "value2"
          }
        },
        "probability": 0.75,                 // Probability of conditions occurring
        "confidence": 0.8                    // Confidence level (0-1)
      }
    ],
    "potentialImpacts": [                    // Array of potential impacts
      {
        "system": "string",                  // COMMUNICATIONS, POSITIONING, POWER, etc.
        "severity": "string",                // NONE, MINOR, MODERATE, SEVERE
        "description": "string"
      }
    ],
    "affectedRegion": [                      // Array of affected regions
      {
        "type": "string",                    // LEO, MEO, GEO, etc.
        "coordinates": {
          "minLatitude": -90.0,              // deg
          "maxLatitude": 90.0,               // deg
          "minLongitude": -180.0,            // deg
          "maxLongitude": 180.0,             // deg
          "minAltitude": 200.0,              // km
          "maxAltitude": 36000.0             // km
        }
      }
    ],
    "url": "string",                         // URL for more information
    "metadata": {                            // Additional extensible metadata
      "key1": "value1",
      "key2": "value2"
    }
  }
}
```

## Internal Message Formats

### Dead Letter Message

Message format for messages that could not be processed and are sent to the dead letter topic.

**Topic:** `astroshield.dead-letter`

```json
{
  "header": {
    "messageId": "0ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "correlationId": "1ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "source": "astroshield.integration",
    "timestamp": "2023-09-15T14:32:50.456Z",
    "messageType": "DEAD_LETTER",
    "version": "1.0"
  },
  "payload": {
    "originalTopic": "string",              // Original topic of the message
    "originalMessageId": "string",          // Message ID of the original message
    "errorCode": "string",                  // Error code
    "errorMessage": "string",               // Human-readable error message
    "errorTime": "2023-09-15T14:32:50.456Z", // Time when the error occurred
    "retryCount": 3,                        // Number of retry attempts
    "originalMessage": {                    // Original message that failed processing
      "header": {
        // Original message header
      },
      "payload": {
        // Original message payload
      }
    }
  }
}
```

### System Health Message

Message format for system health status reporting.

**Topic:** `astroshield.system.health`

```json
{
  "header": {
    "messageId": "2ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "correlationId": "3ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "source": "astroshield.integration",
    "timestamp": "2023-09-15T14:32:55.789Z",
    "messageType": "SYSTEM_HEALTH",
    "version": "1.0"
  },
  "payload": {
    "componentId": "string",                // ID of the reporting component
    "componentType": "string",              // Type of component
    "status": "string",                     // UP, DEGRADED, DOWN
    "uptimeSeconds": 3600,                  // Uptime in seconds
    "timestamp": "2023-09-15T14:32:55.789Z", // Time of health check
    "metrics": {                            // Component-specific metrics
      "messageProcessed": 1000,
      "messageErrors": 5,
      "avgProcessingTimeMs": 15.5,
      "cpuUsage": 0.3,                     // 0-1 scale
      "memoryUsage": 0.4,                  // 0-1 scale
      "otherMetrics": {
        "key1": "value1",
        "key2": "value2"
      }
    },
    "issues": [                            // Array of active issues, if any
      {
        "issueId": "string",
        "severity": "string",              // WARNING, ERROR, CRITICAL
        "message": "string",
        "startTime": "2023-09-15T14:30:00.000Z",
        "details": "string"
      }
    ],
    "dependencies": [                      // Status of dependencies
      {
        "name": "string",                  // Name of the dependency
        "type": "string",                  // DATABASE, API, KAFKA, etc.
        "status": "string",                // UP, DEGRADED, DOWN
        "lastCheckTime": "2023-09-15T14:32:50.000Z"
      }
    ]
  }
}
```

## Schema Validation

All messages are validated against JSON Schema definitions to ensure compliance with the expected formats. Schema validation is enabled by default and can be controlled using the `FEATURE_SCHEMA_VALIDATION` configuration parameter.

## Message Transformation

The AstroShield Integration Package provides transformation utilities to convert between internal message formats and the formats required by external systems. These transformers ensure that data is correctly mapped between systems while maintaining semantic integrity.

### Transformation Process

1. **Validation** - Incoming messages are validated against their schema
2. **Transformation** - Messages are transformed to the target format using system-specific transformers
3. **Enrichment** - Additional data may be added from reference data sources
4. **Validation** - Transformed messages are validated against the target schema
5. **Delivery** - Messages are delivered to the target system

## Message Correlation

To maintain traceability across systems, all messages include a `correlationId` in their header. This allows tracking of message chains as they flow through different systems and transformations. 

When creating a new message based on an existing one, the `correlationId` should be preserved to maintain the chain of related messages. 