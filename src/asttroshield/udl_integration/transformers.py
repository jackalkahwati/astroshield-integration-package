"""
UDL Data Transformers

This module provides functions for transforming UDL API data to AstroShield format.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Union


def generate_message_id(prefix: str = "msg") -> str:
    """
    Generate a unique message ID for AstroShield messages.
    
    Args:
        prefix: Prefix for the message ID
        
    Returns:
        A unique message ID string
    """
    return f"{prefix}-{uuid.uuid4()}"


def transform_state_vector(udl_state_vector: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a UDL state vector to AstroShield format.
    
    Args:
        udl_state_vector: State vector data from UDL
        
    Returns:
        State vector in AstroShield format
    """
    # Extract object identifiers
    object_id = f"SATCAT-{udl_state_vector.get('satno', 'UNKNOWN')}"
    norad_id = udl_state_vector.get('satno')
    object_name = udl_state_vector.get('objectName', 'UNKNOWN')
    
    # Extract position and velocity
    position = {
        "x": udl_state_vector.get('x', 0.0),
        "y": udl_state_vector.get('y', 0.0),
        "z": udl_state_vector.get('z', 0.0)
    }
    
    velocity = {
        "x": udl_state_vector.get('xDot', 0.0),
        "y": udl_state_vector.get('yDot', 0.0),
        "z": udl_state_vector.get('zDot', 0.0)
    }
    
    # Create covariance matrix (if available)
    covariance = None
    if all(key in udl_state_vector for key in ['covarianceMatrix']):
        cov_matrix = udl_state_vector.get('covarianceMatrix', [])
        if cov_matrix:
            covariance = [
                [cov_matrix[0], cov_matrix[1], cov_matrix[2], cov_matrix[3], cov_matrix[4], cov_matrix[5]],
                [cov_matrix[1], cov_matrix[6], cov_matrix[7], cov_matrix[8], cov_matrix[9], cov_matrix[10]],
                [cov_matrix[2], cov_matrix[7], cov_matrix[11], cov_matrix[12], cov_matrix[13], cov_matrix[14]],
                [cov_matrix[3], cov_matrix[8], cov_matrix[12], cov_matrix[15], cov_matrix[16], cov_matrix[17]],
                [cov_matrix[4], cov_matrix[9], cov_matrix[13], cov_matrix[16], cov_matrix[18], cov_matrix[19]],
                [cov_matrix[5], cov_matrix[10], cov_matrix[14], cov_matrix[17], cov_matrix[19], cov_matrix[20]]
            ]
    
    # If covariance is not available, create a default one
    if not covariance:
        covariance = [
            [0.0001, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0001, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0001, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.000001, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.000001, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.000001]
        ]
    
    # Extract metadata
    metadata = {
        "source": udl_state_vector.get('source', 'UDL'),
        "dataQuality": "MEDIUM",
        "orbitType": determine_orbit_type(position),
    }
    
    # Add track info if available
    if 'trackId' in udl_state_vector:
        metadata["trackInfo"] = {
            "trackId": udl_state_vector.get('trackId', f"track-{uuid.uuid4()}"),
            "correlationScore": udl_state_vector.get('correlationScore', 0.8),
            "correlationMethod": "PROBABILISTIC",
            "observationCount": udl_state_vector.get('observationCount', 1),
            "observationSources": [udl_state_vector.get('source', 'UDL')]
        }
    
    # Add state estimation info
    metadata["stateEstimationInfo"] = {
        "estimationMethod": udl_state_vector.get('estimationMethod', 'KALMAN_FILTER'),
        "propagationMethod": udl_state_vector.get('propagationMethod', 'SGP4'),
        "lastPropagationTime": udl_state_vector.get('epoch', datetime.utcnow().isoformat() + 'Z'),
        "catalogEntry": {
            "catalogId": "UDL-CATALOG",
            "entryId": f"UDLCAT-{norad_id}" if norad_id else f"UDLCAT-UNKNOWN-{uuid.uuid4().hex[:8]}",
            "lastUpdateTime": datetime.utcnow().isoformat() + 'Z',
            "entryStatus": "ACTIVE"
        }
    }
    
    # Create message ID and timestamp
    message_id = generate_message_id("sv")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create the AstroShield state vector message
    astroshield_state_vector = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss2.state.vector",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "stateVectorId": message_id,
            "objectId": object_id,
            "noradId": norad_id,
            "objectName": object_name,
            "epoch": udl_state_vector.get('epoch', timestamp),
            "referenceFrame": udl_state_vector.get('referenceFrame', 'GCRF'),
            "position": position,
            "velocity": velocity,
            "covariance": covariance,
            "metadata": metadata
        }
    }
    
    return astroshield_state_vector


def transform_conjunction(udl_conjunction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a UDL conjunction to AstroShield format.
    
    Args:
        udl_conjunction: Conjunction data from UDL
        
    Returns:
        Conjunction in AstroShield format
    """
    # Extract object identifiers
    primary_object_id = f"SATCAT-{udl_conjunction.get('object1', {}).get('satno', 'UNKNOWN')}"
    primary_norad_id = udl_conjunction.get('object1', {}).get('satno')
    primary_object_name = udl_conjunction.get('object1', {}).get('objectName', 'UNKNOWN')
    
    secondary_object_id = f"SATCAT-{udl_conjunction.get('object2', {}).get('satno', 'UNKNOWN')}"
    secondary_norad_id = udl_conjunction.get('object2', {}).get('satno')
    secondary_object_name = udl_conjunction.get('object2', {}).get('objectName', 'UNKNOWN')
    
    # Extract conjunction details
    tca = udl_conjunction.get('tca', datetime.utcnow().isoformat() + 'Z')
    miss_distance = udl_conjunction.get('missDistance', 0.0)
    relative_velocity = udl_conjunction.get('relVelMag', 0.0)
    probability_of_collision = udl_conjunction.get('collisionProb', 0.0)
    
    # Determine risk level based on miss distance and probability
    risk_level = determine_risk_level(miss_distance, probability_of_collision)
    
    # Create message ID and timestamp
    message_id = generate_message_id("conj")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create the AstroShield conjunction message
    astroshield_conjunction = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss5.conjunction.event",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "conjunctionId": message_id,
            "detectionTime": timestamp,
            "primaryObject": {
                "objectId": primary_object_id,
                "noradId": primary_norad_id,
                "objectName": primary_object_name,
                "stateVectorId": udl_conjunction.get('idStateVector1', f"sv-{uuid.uuid4()}")
            },
            "secondaryObject": {
                "objectId": secondary_object_id,
                "noradId": secondary_norad_id,
                "objectName": secondary_object_name,
                "stateVectorId": udl_conjunction.get('idStateVector2', f"sv-{uuid.uuid4()}")
            },
            "timeOfClosestApproach": tca,
            "missDistance": {
                "value": miss_distance / 1000.0,  # Convert to km
                "units": "km"
            },
            "relativeVelocity": {
                "value": relative_velocity / 1000.0,  # Convert to km/s
                "units": "km/s"
            },
            "probabilityOfCollision": probability_of_collision,
            "riskLevel": risk_level,
            "riskAssessment": {
                "impactEnergy": {
                    "value": calculate_impact_energy(primary_norad_id, secondary_norad_id, relative_velocity),
                    "units": "kJ"
                },
                "expectedDebrisCount": calculate_debris_count(primary_norad_id, secondary_norad_id),
                "consequenceRating": determine_consequence_rating(primary_norad_id, secondary_norad_id)
            },
            "timeToClosestApproach": {
                "value": calculate_time_to_closest_approach(tca),
                "units": "hours"
            },
            "mitigationOptions": generate_mitigation_options(
                primary_object_id, 
                primary_object_name, 
                secondary_object_id, 
                secondary_object_name
            )
        }
    }
    
    return astroshield_conjunction


def transform_launch_event(udl_launch_event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a UDL launch event to AstroShield format.
    
    Args:
        udl_launch_event: Launch event data from UDL
        
    Returns:
        Launch event in AstroShield format
    """
    # Extract launch details
    launch_site = udl_launch_event.get('launchSite', {})
    launch_vehicle = udl_launch_event.get('launchVehicle', {})
    
    # Create message ID and timestamp
    message_id = generate_message_id("lnch")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create the AstroShield launch detection message
    astroshield_launch = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss0.launch.detection",
            "traceId": f"trace-{uuid.uuid4()}"
        },
        "payload": {
            "detectionId": message_id,
            "detectionTime": timestamp,
            "launchSite": {
                "name": launch_site.get('name', 'UNKNOWN'),
                "country": launch_site.get('country', 'UNKNOWN'),
                "coordinates": {
                    "latitude": launch_site.get('latitude', 0.0),
                    "longitude": launch_site.get('longitude', 0.0),
                    "altitude": launch_site.get('altitude', 0.0)
                }
            },
            "launchVehicle": {
                "type": launch_vehicle.get('type', 'UNKNOWN'),
                "configuration": launch_vehicle.get('configuration', 'UNKNOWN'),
                "confidence": 0.8
            },
            "launchTime": {
                "estimated": udl_launch_event.get('launchTime', timestamp),
                "confidence": 0.8
            },
            "trajectory": {
                "initialAzimuth": udl_launch_event.get('initialAzimuth', 0.0),
                "initialElevation": udl_launch_event.get('initialElevation', 0.0),
                "estimatedStages": udl_launch_event.get('estimatedStages', 1),
                "estimatedPayloadCount": udl_launch_event.get('estimatedPayloadCount', 1)
            },
            "detectionMethod": {
                "primary": udl_launch_event.get('detectionMethod', 'RADAR'),
                "supporting": udl_launch_event.get('supportingDetectionMethods', [])
            },
            "predictedTargetOrbit": {
                "type": udl_launch_event.get('orbitType', 'LEO'),
                "semiMajorAxis": udl_launch_event.get('semiMajorAxis', 6778.0),
                "eccentricity": udl_launch_event.get('eccentricity', 0.0015),
                "inclination": udl_launch_event.get('inclination', 51.6),
                "raan": udl_launch_event.get('raan', 0.0),
                "argumentOfPerigee": udl_launch_event.get('argumentOfPerigee', 0.0)
            },
            "assessedPurpose": {
                "category": udl_launch_event.get('purpose', 'UNKNOWN'),
                "description": udl_launch_event.get('description', 'Unknown purpose'),
                "confidence": 0.7
            },
            "relatedObjects": []
        }
    }
    
    return astroshield_launch


# Helper functions

def determine_orbit_type(position: Dict[str, float]) -> str:
    """
    Determine the orbit type based on position.
    
    Args:
        position: Position vector
        
    Returns:
        Orbit type (LEO, MEO, GEO, HEO)
    """
    # Calculate distance from Earth center
    distance = (position["x"]**2 + position["y"]**2 + position["z"]**2)**0.5
    
    if distance < 8000:  # Less than 2000 km altitude
        return "LEO"
    elif distance < 25000:  # Less than 20000 km altitude
        return "MEO"
    elif 35000 < distance < 45000:  # Near geostationary altitude
        return "GEO"
    else:
        return "HEO"


def determine_risk_level(miss_distance: float, probability: float) -> str:
    """
    Determine the risk level based on miss distance and probability.
    
    Args:
        miss_distance: Miss distance in meters
        probability: Probability of collision
        
    Returns:
        Risk level (LOW, MEDIUM, HIGH, CRITICAL)
    """
    if probability > 1e-3:
        return "CRITICAL"
    elif probability > 1e-4:
        return "HIGH"
    elif probability > 1e-5 or miss_distance < 1000:
        return "MEDIUM"
    else:
        return "LOW"


def calculate_impact_energy(primary_id: Optional[int], secondary_id: Optional[int], rel_velocity: float) -> float:
    """
    Calculate the impact energy for a collision.
    
    Args:
        primary_id: NORAD ID of primary object
        secondary_id: NORAD ID of secondary object
        rel_velocity: Relative velocity in m/s
        
    Returns:
        Impact energy in kJ
    """
    # This is a simplified calculation
    # In a real implementation, you would look up the mass of the objects
    primary_mass = 1000.0  # Default to 1000 kg
    secondary_mass = 100.0  # Default to 100 kg
    
    # Calculate kinetic energy: 0.5 * m * v^2
    # Convert to kJ (divide by 1000)
    return 0.5 * (primary_mass * secondary_mass / (primary_mass + secondary_mass)) * (rel_velocity**2) / 1000.0


def calculate_debris_count(primary_id: Optional[int], secondary_id: Optional[int]) -> int:
    """
    Estimate the number of debris pieces from a collision.
    
    Args:
        primary_id: NORAD ID of primary object
        secondary_id: NORAD ID of secondary object
        
    Returns:
        Estimated number of debris pieces
    """
    # This is a placeholder implementation
    # In a real implementation, you would use a debris model
    return 500


def determine_consequence_rating(primary_id: Optional[int], secondary_id: Optional[int]) -> str:
    """
    Determine the consequence rating for a collision.
    
    Args:
        primary_id: NORAD ID of primary object
        secondary_id: NORAD ID of secondary object
        
    Returns:
        Consequence rating (MINOR, MODERATE, SEVERE, CATASTROPHIC)
    """
    # This is a placeholder implementation
    # In a real implementation, you would consider the importance of the objects
    return "SEVERE"


def calculate_time_to_closest_approach(tca: str) -> float:
    """
    Calculate the time to closest approach in hours.
    
    Args:
        tca: Time of closest approach in ISO format
        
    Returns:
        Time to closest approach in hours
    """
    tca_dt = datetime.fromisoformat(tca.replace('Z', '+00:00'))
    now = datetime.utcnow()
    
    # Calculate the difference in hours
    delta = tca_dt - now
    hours = delta.total_seconds() / 3600.0
    
    return max(0.0, hours)  # Don't return negative values


def generate_mitigation_options(
    primary_id: str, 
    primary_name: str, 
    secondary_id: str, 
    secondary_name: str
) -> List[Dict[str, Any]]:
    """
    Generate mitigation options for a conjunction.
    
    Args:
        primary_id: ID of primary object
        primary_name: Name of primary object
        secondary_id: ID of secondary object
        secondary_name: Name of secondary object
        
    Returns:
        List of mitigation options
    """
    # This is a placeholder implementation
    # In a real implementation, you would generate options based on the objects
    options = [
        {
            "optionId": f"mit-{uuid.uuid4().hex[:8]}-1",
            "description": f"{primary_name} perform avoidance maneuver",
            "deltaV": 0.12,
            "executionTime": (datetime.utcnow().replace(microsecond=0) + 
                             datetime.timedelta(hours=12)).isoformat() + 'Z'
        }
    ]
    
    # Add a second option if the secondary object is not debris
    if "DEBRIS" not in secondary_name.upper():
        options.append({
            "optionId": f"mit-{uuid.uuid4().hex[:8]}-2",
            "description": f"Request {secondary_name} maneuver",
            "notes": f"Coordination with operator of {secondary_name} required"
        })
    
    return options


# Additional transformer functions

def transform_track(udl_track: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a UDL track to AstroShield format.
    
    Args:
        udl_track: Track data from UDL
        
    Returns:
        Track in AstroShield format
    """
    # Extract track identifiers
    track_id = udl_track.get('trackId', f"track-{uuid.uuid4()}")
    object_id = f"SATCAT-{udl_track.get('satno', 'UNKNOWN')}"
    norad_id = udl_track.get('satno')
    object_name = udl_track.get('objectName', 'UNKNOWN')
    
    # Create message ID and timestamp
    message_id = generate_message_id("track")
    timestamp = datetime.utcnow().isoformat() + 'Z'

    # Extract observation metadata
    sensor_id = udl_track.get('sensorId', 'UNKNOWN')
    observation_count = udl_track.get('observationCount', 1)
    observation_start = udl_track.get('observationStart', timestamp)
    observation_end = udl_track.get('observationEnd', timestamp)
    
    # Create the AstroShield track message
    astroshield_track = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss1.track.detection",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "trackId": track_id,
            "objectId": object_id,
            "noradId": norad_id,
            "objectName": object_name,
            "detectionTime": timestamp,
            "trackQuality": udl_track.get('trackQuality', 'MEDIUM'),
            "trackType": udl_track.get('trackType', 'RADAR'),
            "sensorInfo": {
                "sensorId": sensor_id,
                "sensorName": udl_track.get('sensorName', f"Sensor-{sensor_id}"),
                "sensorType": udl_track.get('sensorType', 'RADAR'),
                "sensorLocation": {
                    "latitude": udl_track.get('sensorLatitude', 0.0),
                    "longitude": udl_track.get('sensorLongitude', 0.0),
                    "altitude": udl_track.get('sensorAltitude', 0.0),
                }
            },
            "observationStats": {
                "observationCount": observation_count,
                "startTime": observation_start,
                "endTime": observation_end,
                "trackDuration": {
                    "value": calculate_track_duration(observation_start, observation_end),
                    "units": "seconds"
                }
            },
            "trackState": udl_track.get('trackState', 'ACTIVE'),
            "confidence": udl_track.get('confidence', 0.8),
            "stateVectorId": udl_track.get('stateVectorId', f"sv-{uuid.uuid4()}")
        }
    }
    
    return astroshield_track


def transform_ephemeris(udl_ephemeris: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a UDL ephemeris to AstroShield format.
    
    Args:
        udl_ephemeris: Ephemeris data from UDL
        
    Returns:
        Ephemeris in AstroShield format
    """
    # Extract object identifiers
    object_id = f"SATCAT-{udl_ephemeris.get('satno', 'UNKNOWN')}"
    norad_id = udl_ephemeris.get('satno')
    object_name = udl_ephemeris.get('objectName', 'UNKNOWN')
    
    # Extract ephemeris data points
    ephemeris_points = udl_ephemeris.get('ephemerisPoints', [])
    transformed_points = []
    
    for point in ephemeris_points:
        transformed_points.append({
            "epoch": point.get('epoch', ''),
            "position": {
                "x": point.get('x', 0.0),
                "y": point.get('y', 0.0),
                "z": point.get('z', 0.0)
            },
            "velocity": {
                "x": point.get('xDot', 0.0),
                "y": point.get('yDot', 0.0),
                "z": point.get('zDot', 0.0)
            }
        })
    
    # Create message ID and timestamp
    message_id = generate_message_id("ephem")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create the AstroShield ephemeris message
    astroshield_ephemeris = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss2.ephemeris",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "ephemerisId": message_id,
            "objectId": object_id,
            "noradId": norad_id,
            "objectName": object_name,
            "startTime": udl_ephemeris.get('startTime', timestamp),
            "endTime": udl_ephemeris.get('endTime', timestamp),
            "referenceFrame": udl_ephemeris.get('referenceFrame', 'GCRF'),
            "propagationMethod": udl_ephemeris.get('propagationMethod', 'SGP4'),
            "stepSize": {
                "value": udl_ephemeris.get('stepSize', 60),
                "units": "seconds"
            },
            "ephemerisPoints": transformed_points,
            "metadata": {
                "source": udl_ephemeris.get('source', 'UDL'),
                "generationTime": timestamp,
                "propagationParameters": udl_ephemeris.get('propagationParameters', {})
            }
        }
    }
    
    return astroshield_ephemeris


def transform_maneuver(udl_maneuver: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a UDL maneuver to AstroShield format.
    
    Args:
        udl_maneuver: Maneuver data from UDL
        
    Returns:
        Maneuver in AstroShield format
    """
    # Extract object identifiers
    object_id = f"SATCAT-{udl_maneuver.get('satno', 'UNKNOWN')}"
    norad_id = udl_maneuver.get('satno')
    object_name = udl_maneuver.get('objectName', 'UNKNOWN')
    
    # Create message ID and timestamp
    message_id = generate_message_id("mnvr")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Extract maneuver details
    maneuver_start = udl_maneuver.get('startTime', timestamp)
    maneuver_end = udl_maneuver.get('endTime', timestamp)
    delta_v = udl_maneuver.get('deltaV', 0.0)
    
    # Create the AstroShield maneuver message
    astroshield_maneuver = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss2.maneuver.detection",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "maneuverId": message_id,
            "objectId": object_id,
            "noradId": norad_id,
            "objectName": object_name,
            "detectionTime": timestamp,
            "maneuverStart": maneuver_start,
            "maneuverEnd": maneuver_end,
            "duration": {
                "value": calculate_maneuver_duration(maneuver_start, maneuver_end),
                "units": "seconds"
            },
            "maneuverType": udl_maneuver.get('maneuverType', 'UNKNOWN'),
            "deltaV": {
                "value": delta_v,
                "units": "m/s"
            },
            "deltaVVector": {
                "x": udl_maneuver.get('deltaVx', 0.0),
                "y": udl_maneuver.get('deltaVy', 0.0),
                "z": udl_maneuver.get('deltaVz', 0.0)
            },
            "preManeuverState": {
                "stateVectorId": udl_maneuver.get('preManeuverStateVectorId', f"sv-{uuid.uuid4()}"),
                "orbitType": udl_maneuver.get('preManeuverOrbitType', 'UNKNOWN')
            },
            "postManeuverState": {
                "stateVectorId": udl_maneuver.get('postManeuverStateVectorId', f"sv-{uuid.uuid4()}"),
                "orbitType": udl_maneuver.get('postManeuverOrbitType', 'UNKNOWN')
            },
            "detectionMethod": udl_maneuver.get('detectionMethod', 'STATISTICAL'),
            "confidence": udl_maneuver.get('confidence', 0.8),
            "purpose": udl_maneuver.get('purpose', 'UNKNOWN'),
            "metadata": {
                "source": udl_maneuver.get('source', 'UDL'),
                "detector": udl_maneuver.get('detector', 'UDL_MANEUVER_DETECTOR'),
                "anomalyScore": udl_maneuver.get('anomalyScore', 0.0)
            }
        }
    }
    
    return astroshield_maneuver


def transform_observation(udl_observation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a UDL observation to AstroShield format.
    
    Args:
        udl_observation: Observation data from UDL
        
    Returns:
        Observation in AstroShield format
    """
    # Extract observation details
    sensor_id = udl_observation.get('sensorId', 'UNKNOWN')
    observation_time = udl_observation.get('observationTime', datetime.utcnow().isoformat() + 'Z')
    
    # Create message ID and timestamp
    message_id = generate_message_id("obs")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create the AstroShield observation message
    astroshield_observation = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss0.observation",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "observationId": message_id,
            "observationTime": observation_time,
            "sensorInfo": {
                "sensorId": sensor_id,
                "sensorName": udl_observation.get('sensorName', f"Sensor-{sensor_id}"),
                "sensorType": udl_observation.get('sensorType', 'RADAR'),
                "sensorMode": udl_observation.get('sensorMode', 'TRACKING'),
                "sensorLocation": {
                    "latitude": udl_observation.get('sensorLatitude', 0.0),
                    "longitude": udl_observation.get('sensorLongitude', 0.0),
                    "altitude": udl_observation.get('sensorAltitude', 0.0),
                }
            },
            "measurements": {
                "type": udl_observation.get('measurementType', 'RANGE_ANGLE'),
                "data": udl_observation.get('measurementData', {}),
                "uncertainties": udl_observation.get('measurementUncertainties', {})
            },
            "targetInfo": {
                "targetId": udl_observation.get('targetId', 'UNKNOWN'),
                "targetType": udl_observation.get('targetType', 'SPACE_OBJECT'),
                "trackId": udl_observation.get('trackId', None)
            },
            "processingInfo": {
                "processingLevel": udl_observation.get('processingLevel', 'RAW'),
                "calibrationApplied": udl_observation.get('calibrationApplied', False),
                "noiseReductionApplied": udl_observation.get('noiseReductionApplied', False)
            },
            "metadata": {
                "source": udl_observation.get('source', 'UDL'),
                "quality": udl_observation.get('quality', 'MEDIUM'),
                "observationCampaign": udl_observation.get('observationCampaign', None)
            }
        }
    }
    
    return astroshield_observation


def transform_sensor(udl_sensor: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform UDL sensor data to AstroShield format.
    
    Args:
        udl_sensor: Sensor data from UDL
        
    Returns:
        Sensor in AstroShield format
    """
    # Extract sensor details
    sensor_id = udl_sensor.get('sensorId', f"sensor-{uuid.uuid4().hex[:8]}")
    
    # Create message ID and timestamp
    message_id = generate_message_id("sens")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create the AstroShield sensor message
    astroshield_sensor = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss0.sensor.info",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "sensorId": sensor_id,
            "sensorName": udl_sensor.get('sensorName', f"Sensor-{sensor_id}"),
            "sensorType": udl_sensor.get('sensorType', 'RADAR'),
            "location": {
                "latitude": udl_sensor.get('latitude', 0.0),
                "longitude": udl_sensor.get('longitude', 0.0),
                "altitude": udl_sensor.get('altitude', 0.0),
                "siteName": udl_sensor.get('siteName', 'UNKNOWN'),
                "country": udl_sensor.get('country', 'UNKNOWN')
            },
            "capabilities": {
                "frequency": {
                    "min": udl_sensor.get('minFrequency', 0.0),
                    "max": udl_sensor.get('maxFrequency', 0.0),
                    "units": "MHz"
                },
                "power": {
                    "value": udl_sensor.get('power', 0.0),
                    "units": "kW"
                },
                "range": {
                    "min": udl_sensor.get('minRange', 0.0),
                    "max": udl_sensor.get('maxRange', 0.0),
                    "units": "km"
                },
                "fieldOfView": {
                    "azimuth": {
                        "min": udl_sensor.get('minAzimuth', 0.0),
                        "max": udl_sensor.get('maxAzimuth', 360.0),
                        "units": "degrees"
                    },
                    "elevation": {
                        "min": udl_sensor.get('minElevation', 0.0),
                        "max": udl_sensor.get('maxElevation', 90.0),
                        "units": "degrees"
                    }
                },
                "accuracy": {
                    "range": udl_sensor.get('rangeAccuracy', 0.0),
                    "angle": udl_sensor.get('angleAccuracy', 0.0),
                    "velocity": udl_sensor.get('velocityAccuracy', 0.0)
                },
                "supportedModes": udl_sensor.get('supportedModes', ["TRACKING", "SURVEY"]),
                "maxTrackables": udl_sensor.get('maxTrackables', 100)
            },
            "status": {
                "operationalStatus": udl_sensor.get('operationalStatus', 'ACTIVE'),
                "lastMaintenance": udl_sensor.get('lastMaintenance', timestamp),
                "healthScore": udl_sensor.get('healthScore', 1.0),
                "availabilityPercent": udl_sensor.get('availabilityPercent', 99.0)
            },
            "metadata": {
                "owner": udl_sensor.get('owner', 'UNKNOWN'),
                "classification": udl_sensor.get('classification', 'UNCLASSIFIED'),
                "dataSharing": udl_sensor.get('dataSharing', 'FULL'),
                "lastUpdated": timestamp
            }
        }
    }
    
    return astroshield_sensor


def transform_orbit_determination(udl_orbit_determination: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform UDL orbit determination data to AstroShield format.
    
    Args:
        udl_orbit_determination: Orbit determination data from UDL
        
    Returns:
        Orbit determination in AstroShield format
    """
    # Extract object identifiers
    object_id = f"SATCAT-{udl_orbit_determination.get('satno', 'UNKNOWN')}"
    norad_id = udl_orbit_determination.get('satno')
    object_name = udl_orbit_determination.get('objectName', 'UNKNOWN')
    
    # Create message ID and timestamp
    message_id = generate_message_id("orb")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Extract orbital elements
    semi_major_axis = udl_orbit_determination.get('semiMajorAxis', 0.0)
    eccentricity = udl_orbit_determination.get('eccentricity', 0.0)
    inclination = udl_orbit_determination.get('inclination', 0.0)
    raan = udl_orbit_determination.get('raan', 0.0)
    arg_of_perigee = udl_orbit_determination.get('argOfPerigee', 0.0)
    mean_anomaly = udl_orbit_determination.get('meanAnomaly', 0.0)
    
    # Create the AstroShield orbit determination message
    astroshield_orbit_determination = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss2.orbit.determination",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "orbitDeterminationId": message_id,
            "objectId": object_id,
            "noradId": norad_id,
            "objectName": object_name,
            "epoch": udl_orbit_determination.get('epoch', timestamp),
            "referenceFrame": udl_orbit_determination.get('referenceFrame', 'GCRF'),
            "orbitalElements": {
                "semiMajorAxis": {
                    "value": semi_major_axis,
                    "units": "km"
                },
                "eccentricity": eccentricity,
                "inclination": {
                    "value": inclination,
                    "units": "degrees"
                },
                "raan": {
                    "value": raan,
                    "units": "degrees"
                },
                "argOfPerigee": {
                    "value": arg_of_perigee,
                    "units": "degrees"
                },
                "meanAnomaly": {
                    "value": mean_anomaly,
                    "units": "degrees"
                }
            },
            "derivedParameters": {
                "period": {
                    "value": calculate_orbital_period(semi_major_axis),
                    "units": "minutes"
                },
                "apogee": {
                    "value": calculate_apogee(semi_major_axis, eccentricity),
                    "units": "km"
                },
                "perigee": {
                    "value": calculate_perigee(semi_major_axis, eccentricity),
                    "units": "km"
                },
                "orbitType": determine_orbit_type_from_elements(semi_major_axis, eccentricity),
                "meanMotion": {
                    "value": calculate_mean_motion(semi_major_axis),
                    "units": "revs/day"
                }
            },
            "correlationInfo": {
                "observations": udl_orbit_determination.get('observationCount', 0),
                "observationArcs": udl_orbit_determination.get('observationArcs', 1),
                "observationSpan": {
                    "value": udl_orbit_determination.get('observationSpan', 0.0),
                    "units": "days"
                },
                "residualRms": udl_orbit_determination.get('residualRms', 0.0),
                "covarianceAvailable": udl_orbit_determination.get('covarianceAvailable', False)
            },
            "metadata": {
                "source": udl_orbit_determination.get('source', 'UDL'),
                "orbitalModel": udl_orbit_determination.get('orbitalModel', 'SGP4'),
                "quality": udl_orbit_determination.get('quality', 'MEDIUM'),
                "determiniationMethod": udl_orbit_determination.get('determiniationMethod', 'BATCH_LEAST_SQUARES')
            }
        }
    }
    
    if udl_orbit_determination.get('covarianceMatrix'):
        astroshield_orbit_determination["payload"]["covariance"] = udl_orbit_determination.get('covarianceMatrix')
    
    return astroshield_orbit_determination


def transform_elset(udl_elset: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform UDL ELSET data to AstroShield format.
    
    Args:
        udl_elset: ELSET data from UDL
        
    Returns:
        ELSET in AstroShield format
    """
    # Extract object identifiers
    object_id = f"SATCAT-{udl_elset.get('satno', 'UNKNOWN')}"
    norad_id = udl_elset.get('satno')
    object_name = udl_elset.get('objectName', 'UNKNOWN')
    
    # Create message ID and timestamp
    message_id = generate_message_id("elset")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Extract TLE lines
    line1 = udl_elset.get('line1', '')
    line2 = udl_elset.get('line2', '')
    
    # Create the AstroShield ELSET message
    astroshield_elset = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss2.elset",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "elsetId": message_id,
            "objectId": object_id,
            "noradId": norad_id,
            "objectName": object_name,
            "epoch": udl_elset.get('epoch', timestamp),
            "tle": {
                "line1": line1,
                "line2": line2
            },
            "meanElements": {
                "epoch": udl_elset.get('epoch', timestamp),
                "meanMotion": {
                    "value": udl_elset.get('meanMotion', 0.0),
                    "units": "revs/day"
                },
                "eccentricity": udl_elset.get('eccentricity', 0.0),
                "inclination": {
                    "value": udl_elset.get('inclination', 0.0),
                    "units": "degrees"
                },
                "raan": {
                    "value": udl_elset.get('raan', 0.0),
                    "units": "degrees"
                },
                "argOfPerigee": {
                    "value": udl_elset.get('argOfPerigee', 0.0),
                    "units": "degrees"
                },
                "meanAnomaly": {
                    "value": udl_elset.get('meanAnomaly', 0.0),
                    "units": "degrees"
                },
                "bstar": udl_elset.get('bstar', 0.0),
                "revolutionNumber": udl_elset.get('revolutionNumber', 0)
            },
            "source": udl_elset.get('source', 'UDL'),
            "elsetNumber": udl_elset.get('elsetNumber', 0),
            "classification": udl_elset.get('classification', 'UNCLASSIFIED'),
            "meanElementTheory": udl_elset.get('meanElementTheory', 'SGP4')
        }
    }
    
    return astroshield_elset


def transform_weather(udl_weather: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform UDL weather data to AstroShield format.
    
    Args:
        udl_weather: Weather data from UDL
        
    Returns:
        Weather in AstroShield format
    """
    # Create message ID and timestamp
    message_id = generate_message_id("wthr")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create the AstroShield weather message
    astroshield_weather = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss0.weather",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "weatherId": message_id,
            "observationTime": udl_weather.get('observationTime', timestamp),
            "location": {
                "latitude": udl_weather.get('latitude', 0.0),
                "longitude": udl_weather.get('longitude', 0.0),
                "altitude": udl_weather.get('altitude', 0.0),
                "locationName": udl_weather.get('locationName', 'UNKNOWN')
            },
            "conditions": {
                "temperature": {
                    "value": udl_weather.get('temperature', 0.0),
                    "units": "celsius"
                },
                "humidity": {
                    "value": udl_weather.get('humidity', 0.0),
                    "units": "percent"
                },
                "pressure": {
                    "value": udl_weather.get('pressure', 1013.25),
                    "units": "hPa"
                },
                "windSpeed": {
                    "value": udl_weather.get('windSpeed', 0.0),
                    "units": "m/s"
                },
                "windDirection": {
                    "value": udl_weather.get('windDirection', 0.0),
                    "units": "degrees"
                },
                "clouds": {
                    "coverage": udl_weather.get('cloudCoverage', 0.0),
                    "type": udl_weather.get('cloudType', 'CLEAR'),
                    "ceiling": {
                        "value": udl_weather.get('cloudCeiling', 0.0),
                        "units": "meters"
                    }
                },
                "visibility": {
                    "value": udl_weather.get('visibility', 10.0),
                    "units": "km"
                },
                "precipitation": {
                    "type": udl_weather.get('precipitationType', 'NONE'),
                    "intensity": udl_weather.get('precipitationIntensity', 0.0),
                    "units": "mm/hr"
                }
            },
            "spaceWeather": {
                "kpIndex": udl_weather.get('kpIndex', 0.0),
                "solarFlux": udl_weather.get('solarFlux', 0.0),
                "sunspotNumber": udl_weather.get('sunspotNumber', 0),
                "solarWindSpeed": {
                    "value": udl_weather.get('solarWindSpeed', 0.0),
                    "units": "km/s"
                },
                "solarWindDensity": udl_weather.get('solarWindDensity', 0.0)
            },
            "forecasts": udl_weather.get('forecasts', []),
            "operationalImpact": {
                "impactRating": udl_weather.get('impactRating', 'NONE'),
                "impactDetails": udl_weather.get('impactDetails', ''),
                "recommendations": udl_weather.get('recommendations', [])
            }
        }
    }
    
    return astroshield_weather


# Helper functions

def calculate_track_duration(start_time: str, end_time: str) -> float:
    """
    Calculate the duration of a track in seconds.
    
    Args:
        start_time: Start time in ISO format
        end_time: End time in ISO format
        
    Returns:
        Duration in seconds
    """
    try:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        return (end - start).total_seconds()
    except:
        return 0.0


def calculate_maneuver_duration(start_time: str, end_time: str) -> float:
    """
    Calculate the duration of a maneuver in seconds.
    
    Args:
        start_time: Start time in ISO format
        end_time: End time in ISO format
        
    Returns:
        Duration in seconds
    """
    try:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        return (end - start).total_seconds()
    except:
        return 0.0


def calculate_orbital_period(semi_major_axis: float) -> float:
    """
    Calculate the orbital period from semi-major axis.
    
    Args:
        semi_major_axis: Semi-major axis in km
        
    Returns:
        Orbital period in minutes
    """
    # Earth gravitational parameter in km^3/s^2
    mu = 398600.4418
    
    # Period = 2π * sqrt(a^3/μ)
    try:
        return 2 * 3.14159265359 * (semi_major_axis ** 3 / mu) ** 0.5 / 60.0
    except:
        return 0.0


def calculate_apogee(semi_major_axis: float, eccentricity: float) -> float:
    """
    Calculate the apogee from semi-major axis and eccentricity.
    
    Args:
        semi_major_axis: Semi-major axis in km
        eccentricity: Eccentricity (dimensionless)
        
    Returns:
        Apogee in km
    """
    try:
        return semi_major_axis * (1 + eccentricity)
    except:
        return 0.0


def calculate_perigee(semi_major_axis: float, eccentricity: float) -> float:
    """
    Calculate the perigee from semi-major axis and eccentricity.
    
    Args:
        semi_major_axis: Semi-major axis in km
        eccentricity: Eccentricity (dimensionless)
        
    Returns:
        Perigee in km
    """
    try:
        return semi_major_axis * (1 - eccentricity)
    except:
        return 0.0


def calculate_mean_motion(semi_major_axis: float) -> float:
    """
    Calculate the mean motion from semi-major axis.
    
    Args:
        semi_major_axis: Semi-major axis in km
        
    Returns:
        Mean motion in revs/day
    """
    # Earth gravitational parameter in km^3/s^2
    mu = 398600.4418
    
    # Mean motion = sqrt(μ/a^3) * (86400 / 2π) [revs/day]
    try:
        return (mu / semi_major_axis ** 3) ** 0.5 * 86400 / (2 * 3.14159265359)
    except:
        return 0.0


def determine_orbit_type_from_elements(semi_major_axis: float, eccentricity: float) -> str:
    """
    Determine the orbit type from orbital elements.
    
    Args:
        semi_major_axis: Semi-major axis in km
        eccentricity: Eccentricity (dimensionless)
        
    Returns:
        Orbit type string
    """
    # Earth radius in km
    earth_radius = 6378.137
    
    # Calculate perigee and apogee
    perigee = calculate_perigee(semi_major_axis, eccentricity)
    apogee = calculate_apogee(semi_major_axis, eccentricity)
    
    # Determine orbit type based on apogee and perigee
    if perigee < earth_radius:
        return "DECAYING"
    elif apogee < earth_radius + 2000:
        return "LEO"
    elif apogee < earth_radius + 35786:
        return "MEO"
    elif 35586 < apogee < 35986 and eccentricity < 0.01:
        return "GEO"
    elif apogee > earth_radius + 35786:
        if eccentricity > 0.3:
            return "HEO"
        else:
            return "SUPER_GEO"
    else:
        return "UNKNOWN"


def transform_cyber_threat(udl_cyber_threat: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform UDL cyber threat data to AstroShield format.
    
    Args:
        udl_cyber_threat: Cyber threat data from UDL
        
    Returns:
        Cyber threat in AstroShield format
    """
    # Create message ID and timestamp
    message_id = generate_message_id("cyber")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create the AstroShield cyber threat message
    astroshield_cyber_threat = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss0.cyber.threat",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "threatId": udl_cyber_threat.get('threatId', message_id),
            "detectionTime": udl_cyber_threat.get('detectionTime', timestamp),
            "reportTime": udl_cyber_threat.get('reportTime', timestamp),
            "severity": udl_cyber_threat.get('severity', 'MEDIUM'),
            "confidence": udl_cyber_threat.get('confidence', 'MEDIUM'),
            "source": {
                "ipAddress": udl_cyber_threat.get('sourceIp', 'UNKNOWN'),
                "geolocation": udl_cyber_threat.get('sourceGeolocation', 'UNKNOWN'),
                "actorType": udl_cyber_threat.get('actorType', 'UNKNOWN'),
                "actorName": udl_cyber_threat.get('actorName', 'UNKNOWN'),
                "attribution": udl_cyber_threat.get('attribution', 'UNKNOWN')
            },
            "target": {
                "system": udl_cyber_threat.get('targetSystem', 'UNKNOWN'),
                "ipAddress": udl_cyber_threat.get('targetIp', 'UNKNOWN'),
                "location": udl_cyber_threat.get('targetLocation', 'UNKNOWN'),
                "assetType": udl_cyber_threat.get('assetType', 'UNKNOWN'),
                "vulnerability": udl_cyber_threat.get('vulnerability', 'UNKNOWN')
            },
            "attack": {
                "type": udl_cyber_threat.get('attackType', 'UNKNOWN'),
                "vector": udl_cyber_threat.get('attackVector', 'UNKNOWN'),
                "phase": udl_cyber_threat.get('attackPhase', 'UNKNOWN'),
                "technique": udl_cyber_threat.get('attackTechnique', 'UNKNOWN'),
                "indicators": udl_cyber_threat.get('indicators', []),
                "signatureId": udl_cyber_threat.get('signatureId', 'UNKNOWN')
            },
            "impact": {
                "operationalStatus": udl_cyber_threat.get('operationalStatus', 'NORMAL'),
                "dataCompromise": udl_cyber_threat.get('dataCompromise', False),
                "serviceDisruption": udl_cyber_threat.get('serviceDisruption', False),
                "systemCompromise": udl_cyber_threat.get('systemCompromise', False)
            },
            "mitigationStatus": udl_cyber_threat.get('mitigationStatus', 'PENDING'),
            "mitigationActions": udl_cyber_threat.get('mitigationActions', []),
            "notes": udl_cyber_threat.get('notes', '')
        }
    }
    
    return astroshield_cyber_threat


def transform_link_status(udl_link_status: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform UDL link status data to AstroShield format.
    
    Args:
        udl_link_status: Link status data from UDL
        
    Returns:
        Link status in AstroShield format
    """
    # Create message ID and timestamp
    message_id = generate_message_id("link")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create the AstroShield link status message
    astroshield_link_status = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss0.link.status",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "linkId": udl_link_status.get('linkId', message_id),
            "objectId": udl_link_status.get('objectId', 'UNKNOWN'),
            "objectName": udl_link_status.get('objectName', 'UNKNOWN'),
            "linkType": udl_link_status.get('linkType', 'UNKNOWN'),
            "statusTime": udl_link_status.get('statusTime', timestamp),
            "status": udl_link_status.get('status', 'UNKNOWN'),
            "signalStrength": {
                "value": udl_link_status.get('signalStrength', 0.0),
                "units": "dBm"
            },
            "signalToNoiseRatio": {
                "value": udl_link_status.get('signalToNoiseRatio', 0.0),
                "units": "dB"
            },
            "bitErrorRate": udl_link_status.get('bitErrorRate', 0.0),
            "dataRate": {
                "value": udl_link_status.get('dataRate', 0.0),
                "units": "bps"
            },
            "frequency": {
                "value": udl_link_status.get('frequency', 0.0),
                "units": "MHz"
            },
            "bandwidth": {
                "value": udl_link_status.get('bandwidth', 0.0),
                "units": "MHz"
            },
            "modulation": udl_link_status.get('modulation', 'UNKNOWN'),
            "encoding": udl_link_status.get('encoding', 'UNKNOWN'),
            "groundStation": {
                "id": udl_link_status.get('groundStationId', 'UNKNOWN'),
                "name": udl_link_status.get('groundStationName', 'UNKNOWN'),
                "location": udl_link_status.get('groundStationLocation', {})
            },
            "interference": {
                "detected": udl_link_status.get('interferenceDetected', False),
                "type": udl_link_status.get('interferenceType', 'NONE'),
                "source": udl_link_status.get('interferenceSource', 'UNKNOWN'),
                "level": udl_link_status.get('interferenceLevel', 0.0)
            },
            "nextContactTime": udl_link_status.get('nextContactTime', '')
        }
    }
    
    return astroshield_link_status


def transform_comm_data(udl_comm_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform UDL communications data to AstroShield format.
    
    Args:
        udl_comm_data: Communications data from UDL
        
    Returns:
        Communications data in AstroShield format
    """
    # Create message ID and timestamp
    message_id = generate_message_id("comm")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create the AstroShield communications data message
    astroshield_comm_data = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss0.comm.data",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "communicationId": udl_comm_data.get('communicationId', message_id),
            "timestamp": udl_comm_data.get('timestamp', timestamp),
            "transmitter": {
                "id": udl_comm_data.get('transmitterId', 'UNKNOWN'),
                "type": udl_comm_data.get('transmitterType', 'UNKNOWN'),
                "name": udl_comm_data.get('transmitterName', 'UNKNOWN'),
                "location": udl_comm_data.get('transmitterLocation', {})
            },
            "receiver": {
                "id": udl_comm_data.get('receiverId', 'UNKNOWN'),
                "type": udl_comm_data.get('receiverType', 'UNKNOWN'),
                "name": udl_comm_data.get('receiverName', 'UNKNOWN'),
                "location": udl_comm_data.get('receiverLocation', {})
            },
            "frequency": {
                "value": udl_comm_data.get('frequency', 0.0),
                "units": "MHz"
            },
            "bandType": udl_comm_data.get('bandType', 'UNKNOWN'),
            "bandwidth": {
                "value": udl_comm_data.get('bandwidth', 0.0),
                "units": "MHz"
            },
            "signalType": udl_comm_data.get('signalType', 'UNKNOWN'),
            "modulation": udl_comm_data.get('modulation', 'UNKNOWN'),
            "encoding": udl_comm_data.get('encoding', 'UNKNOWN'),
            "dataRate": {
                "value": udl_comm_data.get('dataRate', 0.0),
                "units": "bps"
            },
            "transmissionPower": {
                "value": udl_comm_data.get('transmissionPower', 0.0),
                "units": "dBW"
            },
            "duration": {
                "value": udl_comm_data.get('duration', 0.0),
                "units": "seconds"
            },
            "classification": udl_comm_data.get('classification', 'UNCLASSIFIED'),
            "purpose": udl_comm_data.get('purpose', 'UNKNOWN'),
            "contentType": udl_comm_data.get('contentType', 'UNKNOWN'),
            "contentSize": {
                "value": udl_comm_data.get('contentSize', 0.0),
                "units": "bytes"
            }
        }
    }
    
    return astroshield_comm_data


def transform_mission_ops(udl_mission_ops: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform UDL mission operations data to AstroShield format.
    
    Args:
        udl_mission_ops: Mission operations data from UDL
        
    Returns:
        Mission operations data in AstroShield format
    """
    # Create message ID and timestamp
    message_id = generate_message_id("ops")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create the AstroShield mission operations data message
    astroshield_mission_ops = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss0.mission.ops",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "operationId": udl_mission_ops.get('operationId', message_id),
            "missionId": udl_mission_ops.get('missionId', 'UNKNOWN'),
            "missionName": udl_mission_ops.get('missionName', 'UNKNOWN'),
            "type": udl_mission_ops.get('type', 'UNKNOWN'),
            "status": udl_mission_ops.get('status', 'UNKNOWN'),
            "startTime": udl_mission_ops.get('startTime', timestamp),
            "endTime": udl_mission_ops.get('endTime', ''),
            "assets": udl_mission_ops.get('assets', []),
            "personnel": udl_mission_ops.get('personnel', []),
            "location": udl_mission_ops.get('location', {}),
            "activities": udl_mission_ops.get('activities', []),
            "dependencies": udl_mission_ops.get('dependencies', []),
            "priority": udl_mission_ops.get('priority', 'MEDIUM'),
            "classification": udl_mission_ops.get('classification', 'UNCLASSIFIED'),
            "notes": udl_mission_ops.get('notes', ''),
            "results": udl_mission_ops.get('results', {}),
            "anomalies": udl_mission_ops.get('anomalies', [])
        }
    }
    
    return astroshield_mission_ops


def transform_vessel(udl_vessel: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform UDL vessel data to AstroShield format.
    
    Args:
        udl_vessel: Vessel data from UDL
        
    Returns:
        Vessel data in AstroShield format
    """
    # Create message ID and timestamp
    message_id = generate_message_id("vessel")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create the AstroShield vessel data message
    astroshield_vessel = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss0.vessel",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "vesselId": udl_vessel.get('vesselId', message_id),
            "mmsi": udl_vessel.get('mmsi', 'UNKNOWN'),
            "imo": udl_vessel.get('imo', 'UNKNOWN'),
            "callsign": udl_vessel.get('callsign', 'UNKNOWN'),
            "name": udl_vessel.get('name', 'UNKNOWN'),
            "type": udl_vessel.get('type', 'UNKNOWN'),
            "country": udl_vessel.get('country', 'UNKNOWN'),
            "flag": udl_vessel.get('flag', 'UNKNOWN'),
            "dimensions": {
                "length": udl_vessel.get('length', 0.0),
                "width": udl_vessel.get('width', 0.0),
                "draft": udl_vessel.get('draft', 0.0),
                "units": "meters"
            },
            "position": {
                "latitude": udl_vessel.get('latitude', 0.0),
                "longitude": udl_vessel.get('longitude', 0.0),
                "time": udl_vessel.get('positionTime', timestamp),
                "accuracy": udl_vessel.get('positionAccuracy', 'LOW')
            },
            "course": {
                "speed": udl_vessel.get('speed', 0.0),
                "heading": udl_vessel.get('heading', 0.0),
                "destination": udl_vessel.get('destination', 'UNKNOWN'),
                "eta": udl_vessel.get('eta', '')
            },
            "navigationStatus": udl_vessel.get('navigationStatus', 'UNKNOWN'),
            "lastPort": udl_vessel.get('lastPort', 'UNKNOWN'),
            "lastPortTime": udl_vessel.get('lastPortTime', ''),
            "classification": udl_vessel.get('classification', 'NORMAL'),
            "notes": udl_vessel.get('notes', '')
        }
    }
    
    return astroshield_vessel


def transform_aircraft(udl_aircraft: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform UDL aircraft data to AstroShield format.
    
    Args:
        udl_aircraft: Aircraft data from UDL
        
    Returns:
        Aircraft data in AstroShield format
    """
    # Create message ID and timestamp
    message_id = generate_message_id("aircraft")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create the AstroShield aircraft data message
    astroshield_aircraft = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss0.aircraft",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "aircraftId": udl_aircraft.get('aircraftId', message_id),
            "icao": udl_aircraft.get('icao', 'UNKNOWN'),
            "registration": udl_aircraft.get('registration', 'UNKNOWN'),
            "callsign": udl_aircraft.get('callsign', 'UNKNOWN'),
            "flightNumber": udl_aircraft.get('flightNumber', 'UNKNOWN'),
            "type": udl_aircraft.get('type', 'UNKNOWN'),
            "model": udl_aircraft.get('model', 'UNKNOWN'),
            "operator": udl_aircraft.get('operator', 'UNKNOWN'),
            "country": udl_aircraft.get('country', 'UNKNOWN'),
            "position": {
                "latitude": udl_aircraft.get('latitude', 0.0),
                "longitude": udl_aircraft.get('longitude', 0.0),
                "altitude": {
                    "value": udl_aircraft.get('altitude', 0.0),
                    "units": "feet"
                },
                "time": udl_aircraft.get('positionTime', timestamp),
                "accuracy": udl_aircraft.get('positionAccuracy', 'LOW')
            },
            "movement": {
                "groundSpeed": {
                    "value": udl_aircraft.get('groundSpeed', 0.0),
                    "units": "knots"
                },
                "heading": udl_aircraft.get('heading', 0.0),
                "verticalRate": {
                    "value": udl_aircraft.get('verticalRate', 0.0),
                    "units": "feet_per_minute"
                }
            },
            "route": {
                "origin": udl_aircraft.get('origin', 'UNKNOWN'),
                "destination": udl_aircraft.get('destination', 'UNKNOWN'),
                "departureTime": udl_aircraft.get('departureTime', ''),
                "arrivalTime": udl_aircraft.get('arrivalTime', '')
            },
            "squawk": udl_aircraft.get('squawk', 'UNKNOWN'),
            "flightStatus": udl_aircraft.get('flightStatus', 'UNKNOWN'),
            "classification": udl_aircraft.get('classification', 'NORMAL'),
            "notes": udl_aircraft.get('notes', '')
        }
    }
    
    return astroshield_aircraft


def transform_ground_imagery(udl_imagery: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform UDL ground imagery data to AstroShield format.
    
    Args:
        udl_imagery: Ground imagery data from UDL
        
    Returns:
        Ground imagery data in AstroShield format
    """
    # Create message ID and timestamp
    message_id = generate_message_id("img")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create the AstroShield ground imagery data message
    astroshield_imagery = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss0.ground.imagery",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "imageId": udl_imagery.get('imageId', message_id),
            "captureTime": udl_imagery.get('captureTime', timestamp),
            "sensor": {
                "id": udl_imagery.get('sensorId', 'UNKNOWN'),
                "type": udl_imagery.get('sensorType', 'UNKNOWN'),
                "name": udl_imagery.get('sensorName', 'UNKNOWN'),
                "platform": udl_imagery.get('platform', 'UNKNOWN')
            },
            "location": {
                "latitude": udl_imagery.get('centerLatitude', 0.0),
                "longitude": udl_imagery.get('centerLongitude', 0.0),
                "altitude": udl_imagery.get('altitude', 0.0),
                "boundingBox": udl_imagery.get('boundingBox', [])
            },
            "imageProperties": {
                "type": udl_imagery.get('imageType', 'OPTICAL'),
                "resolution": {
                    "value": udl_imagery.get('resolution', 0.0),
                    "units": "meters_per_pixel"
                },
                "bandInfo": udl_imagery.get('bandInfo', []),
                "format": udl_imagery.get('format', 'UNKNOWN'),
                "size": {
                    "width": udl_imagery.get('width', 0),
                    "height": udl_imagery.get('height', 0),
                    "units": "pixels"
                },
                "fileSize": {
                    "value": udl_imagery.get('fileSize', 0),
                    "units": "bytes"
                }
            },
            "imageMetadata": {
                "cloudCover": udl_imagery.get('cloudCover', 0.0),
                "sunElevation": udl_imagery.get('sunElevation', 0.0),
                "sunAzimuth": udl_imagery.get('sunAzimuth', 0.0),
                "offNadirAngle": udl_imagery.get('offNadirAngle', 0.0),
                "illumination": udl_imagery.get('illumination', 'DAY')
            },
            "dataUrl": udl_imagery.get('dataUrl', ''),
            "thumbnailUrl": udl_imagery.get('thumbnailUrl', ''),
            "classification": udl_imagery.get('classification', 'UNCLASSIFIED'),
            "detections": udl_imagery.get('detections', []),
            "notes": udl_imagery.get('notes', '')
        }
    }
    
    return astroshield_imagery


def transform_sky_imagery(udl_sky_imagery: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform UDL sky imagery data to AstroShield format.
    
    Args:
        udl_sky_imagery: Sky imagery data from UDL
        
    Returns:
        Sky imagery data in AstroShield format
    """
    # Create message ID and timestamp
    message_id = generate_message_id("sky")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create the AstroShield sky imagery data message
    astroshield_sky_imagery = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss0.sky.imagery",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "imageId": udl_sky_imagery.get('imageId', message_id),
            "captureTime": udl_sky_imagery.get('captureTime', timestamp),
            "sensor": {
                "id": udl_sky_imagery.get('sensorId', 'UNKNOWN'),
                "type": udl_sky_imagery.get('sensorType', 'UNKNOWN'),
                "name": udl_sky_imagery.get('sensorName', 'UNKNOWN'),
                "location": {
                    "latitude": udl_sky_imagery.get('sensorLatitude', 0.0),
                    "longitude": udl_sky_imagery.get('sensorLongitude', 0.0),
                    "altitude": udl_sky_imagery.get('sensorAltitude', 0.0)
                }
            },
            "fov": {
                "rightAscension": udl_sky_imagery.get('centerRa', 0.0),
                "declination": udl_sky_imagery.get('centerDec', 0.0),
                "width": udl_sky_imagery.get('fovWidth', 0.0),
                "height": udl_sky_imagery.get('fovHeight', 0.0),
                "units": "degrees"
            },
            "imageProperties": {
                "type": udl_sky_imagery.get('imageType', 'OPTICAL'),
                "resolution": {
                    "value": udl_sky_imagery.get('resolution', 0.0),
                    "units": "arcsec_per_pixel"
                },
                "exposure": {
                    "value": udl_sky_imagery.get('exposure', 0.0),
                    "units": "seconds"
                },
                "filter": udl_sky_imagery.get('filter', 'UNKNOWN'),
                "format": udl_sky_imagery.get('format', 'UNKNOWN'),
                "size": {
                    "width": udl_sky_imagery.get('width', 0),
                    "height": udl_sky_imagery.get('height', 0),
                    "units": "pixels"
                },
                "fileSize": {
                    "value": udl_sky_imagery.get('fileSize', 0),
                    "units": "bytes"
                }
            },
            "skyConditions": {
                "limitingMagnitude": udl_sky_imagery.get('limitingMagnitude', 0.0),
                "seeing": {
                    "value": udl_sky_imagery.get('seeing', 0.0),
                    "units": "arcsec"
                },
                "transparency": udl_sky_imagery.get('transparency', 0.0),
                "moonPhase": udl_sky_imagery.get('moonPhase', 0.0),
                "moonSeparation": udl_sky_imagery.get('moonSeparation', 0.0)
            },
            "dataUrl": udl_sky_imagery.get('dataUrl', ''),
            "thumbnailUrl": udl_sky_imagery.get('thumbnailUrl', ''),
            "classification": udl_sky_imagery.get('classification', 'UNCLASSIFIED'),
            "detections": udl_sky_imagery.get('detections', []),
            "notes": udl_sky_imagery.get('notes', '')
        }
    }
    
    return astroshield_sky_imagery


def transform_video_streaming(udl_streaming: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform UDL video streaming data to AstroShield format.
    
    Args:
        udl_streaming: Video streaming data from UDL
        
    Returns:
        Video streaming data in AstroShield format
    """
    # Create message ID and timestamp
    message_id = generate_message_id("video")
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Create the AstroShield video streaming data message
    astroshield_streaming = {
        "header": {
            "messageId": message_id,
            "timestamp": timestamp,
            "source": "udl_integration",
            "messageType": "ss0.video.streaming",
            "traceId": f"trace-{uuid.uuid4()}",
            "parentMessageIds": []
        },
        "payload": {
            "streamId": udl_streaming.get('streamId', message_id),
            "title": udl_streaming.get('title', 'UNKNOWN'),
            "description": udl_streaming.get('description', ''),
            "startTime": udl_streaming.get('startTime', timestamp),
            "endTime": udl_streaming.get('endTime', ''),
            "source": {
                "id": udl_streaming.get('sourceId', 'UNKNOWN'),
                "type": udl_streaming.get('sourceType', 'UNKNOWN'),
                "name": udl_streaming.get('sourceName', 'UNKNOWN'),
                "location": udl_streaming.get('sourceLocation', {})
            },
            "streamParameters": {
                "url": udl_streaming.get('url', ''),
                "protocol": udl_streaming.get('protocol', 'UNKNOWN'),
                "format": udl_streaming.get('format', 'UNKNOWN'),
                "codec": udl_streaming.get('codec', 'UNKNOWN'),
                "resolution": {
                    "width": udl_streaming.get('width', 0),
                    "height": udl_streaming.get('height', 0),
                    "units": "pixels"
                },
                "frameRate": {
                    "value": udl_streaming.get('frameRate', 0.0),
                    "units": "fps"
                },
                "bitRate": {
                    "value": udl_streaming.get('bitRate', 0.0),
                    "units": "kbps"
                }
            },
            "status": udl_streaming.get('status', 'OFFLINE'),
            "viewerCount": udl_streaming.get('viewerCount', 0),
            "classification": udl_streaming.get('classification', 'UNCLASSIFIED'),
            "accessControl": {
                "requiresAuthentication": udl_streaming.get('requiresAuthentication', True),
                "accessLevel": udl_streaming.get('accessLevel', 'RESTRICTED'),
                "authorizedGroups": udl_streaming.get('authorizedGroups', [])
            },
            "annotations": udl_streaming.get('annotations', []),
            "notes": udl_streaming.get('notes', '')
        }
    }
    
    return astroshield_streaming 