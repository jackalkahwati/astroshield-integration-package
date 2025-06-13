"""
Tests for the UDL data transformers.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from asttroshield.udl_integration.transformers import (
    generate_message_id,
    transform_state_vector,
    transform_conjunction,
    transform_launch_event,
    transform_track,
    transform_ephemeris,
    transform_maneuver,
    transform_observation,
    transform_sensor,
    transform_orbit_determination,
    transform_elset,
    transform_weather,
    determine_orbit_type,
    determine_risk_level,
    calculate_impact_energy,
    calculate_debris_count,
    determine_consequence_rating,
    calculate_time_to_closest_approach,
    generate_mitigation_options,
    calculate_track_duration,
    calculate_maneuver_duration,
    calculate_orbital_period,
    calculate_apogee,
    calculate_perigee,
    calculate_mean_motion,
    determine_orbit_type_from_elements,
)


class TestTransformers(unittest.TestCase):
    """Tests for the UDL data transformers."""

    @patch("asttroshield.udl_integration.transformers.uuid.uuid4")
    def test_generate_message_id(self, mock_uuid4):
        """Test generating a message ID."""
        mock_uuid4.return_value = "test-uuid"
        
        result = generate_message_id("test")
        
        self.assertEqual(result, "test-test-uuid")

    @patch("asttroshield.udl_integration.transformers.uuid.uuid4")
    @patch("asttroshield.udl_integration.transformers.datetime")
    def test_transform_state_vector(self, mock_datetime, mock_uuid4):
        """Test transforming a UDL state vector to AstroShield format."""
        # Mock uuid4 and datetime
        mock_uuid4.return_value = "test-uuid"
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 0, 0, 0)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        udl_state_vector = {
            "satno": 12345,
            "objectName": "TEST-SAT",
            "epoch": "2023-01-01T00:00:00Z",
            "referenceFrame": "GCRF",
            "x": 1.0,
            "y": 2.0,
            "z": 3.0,
            "xDot": 4.0,
            "yDot": 5.0,
            "zDot": 6.0,
            "source": "TEST",
        }
        
        result = transform_state_vector(udl_state_vector)
        
        # Check header fields
        self.assertEqual(result["header"]["messageId"], "sv-test-uuid")
        self.assertEqual(result["header"]["timestamp"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["header"]["source"], "udl_integration")
        self.assertEqual(result["header"]["messageType"], "ss2.state.vector")
        self.assertEqual(result["header"]["traceId"], "trace-test-uuid")
        self.assertEqual(result["header"]["parentMessageIds"], [])
        
        # Check payload fields
        self.assertEqual(result["payload"]["stateVectorId"], "sv-test-uuid")
        self.assertEqual(result["payload"]["objectId"], "SATCAT-12345")
        self.assertEqual(result["payload"]["noradId"], 12345)
        self.assertEqual(result["payload"]["objectName"], "TEST-SAT")
        self.assertEqual(result["payload"]["epoch"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["payload"]["referenceFrame"], "GCRF")
        self.assertEqual(result["payload"]["position"], {"x": 1.0, "y": 2.0, "z": 3.0})
        self.assertEqual(result["payload"]["velocity"], {"x": 4.0, "y": 5.0, "z": 6.0})
        self.assertIsNotNone(result["payload"]["covariance"])
        self.assertEqual(result["payload"]["metadata"]["source"], "TEST")

    @patch("asttroshield.udl_integration.transformers.uuid.uuid4")
    @patch("asttroshield.udl_integration.transformers.datetime")
    def test_transform_conjunction(self, mock_datetime, mock_uuid4):
        """Test transforming a UDL conjunction to AstroShield format."""
        # Mock uuid4 and datetime
        mock_uuid4.return_value = "test-uuid"
        mock_now = datetime(2023, 1, 1, 0, 0, 0)
        mock_datetime.utcnow.return_value = mock_now
        mock_datetime.fromisoformat.return_value = mock_now + timedelta(hours=24)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        udl_conjunction = {
            "object1": {
                "satno": 12345,
                "objectName": "PRIMARY-SAT",
            },
            "object2": {
                "satno": 67890,
                "objectName": "SECONDARY-SAT",
            },
            "tca": "2023-01-02T00:00:00Z",
            "missDistance": 1000.0,
            "relVelMag": 10000.0,
            "collisionProb": 1e-6,
        }
        
        result = transform_conjunction(udl_conjunction)
        
        # Check header fields
        self.assertEqual(result["header"]["messageId"], "conj-test-uuid")
        self.assertEqual(result["header"]["timestamp"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["header"]["source"], "udl_integration")
        self.assertEqual(result["header"]["messageType"], "ss5.conjunction.event")
        self.assertEqual(result["header"]["traceId"], "trace-test-uuid")
        self.assertEqual(result["header"]["parentMessageIds"], [])
        
        # Check payload fields
        self.assertEqual(result["payload"]["conjunctionId"], "conj-test-uuid")
        self.assertEqual(result["payload"]["detectionTime"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["payload"]["primaryObject"]["objectId"], "SATCAT-12345")
        self.assertEqual(result["payload"]["primaryObject"]["noradId"], 12345)
        self.assertEqual(result["payload"]["primaryObject"]["objectName"], "PRIMARY-SAT")
        self.assertEqual(result["payload"]["secondaryObject"]["objectId"], "SATCAT-67890")
        self.assertEqual(result["payload"]["secondaryObject"]["noradId"], 67890)
        self.assertEqual(result["payload"]["secondaryObject"]["objectName"], "SECONDARY-SAT")
        self.assertEqual(result["payload"]["timeOfClosestApproach"], "2023-01-02T00:00:00Z")
        self.assertEqual(result["payload"]["missDistance"]["value"], 1.0)
        self.assertEqual(result["payload"]["missDistance"]["units"], "km")
        self.assertEqual(result["payload"]["relativeVelocity"]["value"], 10.0)
        self.assertEqual(result["payload"]["relativeVelocity"]["units"], "km/s")
        self.assertEqual(result["payload"]["probabilityOfCollision"], 1e-6)
        self.assertEqual(result["payload"]["riskLevel"], "LOW")
        self.assertEqual(result["payload"]["timeToClosestApproach"]["value"], 24.0)
        self.assertEqual(result["payload"]["timeToClosestApproach"]["units"], "hours")
        self.assertGreater(len(result["payload"]["mitigationOptions"]), 0)

    @patch("asttroshield.udl_integration.transformers.uuid.uuid4")
    @patch("asttroshield.udl_integration.transformers.datetime")
    def test_transform_launch_event(self, mock_datetime, mock_uuid4):
        """Test transforming a UDL launch event to AstroShield format."""
        # Mock uuid4 and datetime
        mock_uuid4.return_value = "test-uuid"
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 0, 0, 0)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        udl_launch_event = {
            "launchSite": {
                "name": "Cape Canaveral",
                "country": "United States",
                "latitude": 28.5,
                "longitude": -80.5,
                "altitude": 100.0,
            },
            "launchVehicle": {
                "type": "Falcon 9",
                "configuration": "Block 5",
            },
            "launchTime": "2023-01-01T00:00:00Z",
            "initialAzimuth": 45.0,
            "initialElevation": 85.0,
            "estimatedStages": 2,
            "estimatedPayloadCount": 60,
            "detectionMethod": "RADAR",
            "supportingDetectionMethods": ["OPTICAL", "INFRARED"],
            "orbitType": "LEO",
            "semiMajorAxis": 6800.0,
            "eccentricity": 0.001,
            "inclination": 53.0,
            "raan": 180.0,
            "argumentOfPerigee": 0.0,
            "purpose": "COMMERCIAL",
            "description": "Starlink launch",
        }
        
        result = transform_launch_event(udl_launch_event)
        
        # Check header fields
        self.assertEqual(result["header"]["messageId"], "lnch-test-uuid")
        self.assertEqual(result["header"]["timestamp"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["header"]["source"], "udl_integration")
        self.assertEqual(result["header"]["messageType"], "ss0.launch.detection")
        self.assertEqual(result["header"]["traceId"], "trace-test-uuid")
        
        # Check payload fields
        self.assertEqual(result["payload"]["detectionId"], "lnch-test-uuid")
        self.assertEqual(result["payload"]["detectionTime"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["payload"]["launchSite"]["name"], "Cape Canaveral")
        self.assertEqual(result["payload"]["launchSite"]["country"], "United States")
        self.assertEqual(result["payload"]["launchSite"]["coordinates"]["latitude"], 28.5)
        self.assertEqual(result["payload"]["launchSite"]["coordinates"]["longitude"], -80.5)
        self.assertEqual(result["payload"]["launchSite"]["coordinates"]["altitude"], 100.0)
        self.assertEqual(result["payload"]["launchVehicle"]["type"], "Falcon 9")
        self.assertEqual(result["payload"]["launchVehicle"]["configuration"], "Block 5")
        self.assertEqual(result["payload"]["launchTime"]["estimated"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["payload"]["trajectory"]["initialAzimuth"], 45.0)
        self.assertEqual(result["payload"]["trajectory"]["initialElevation"], 85.0)
        self.assertEqual(result["payload"]["trajectory"]["estimatedStages"], 2)
        self.assertEqual(result["payload"]["trajectory"]["estimatedPayloadCount"], 60)
        self.assertEqual(result["payload"]["detectionMethod"]["primary"], "RADAR")
        self.assertEqual(result["payload"]["detectionMethod"]["supporting"], ["OPTICAL", "INFRARED"])
        self.assertEqual(result["payload"]["predictedTargetOrbit"]["type"], "LEO")
        self.assertEqual(result["payload"]["predictedTargetOrbit"]["semiMajorAxis"], 6800.0)
        self.assertEqual(result["payload"]["predictedTargetOrbit"]["eccentricity"], 0.001)
        self.assertEqual(result["payload"]["predictedTargetOrbit"]["inclination"], 53.0)
        self.assertEqual(result["payload"]["predictedTargetOrbit"]["raan"], 180.0)
        self.assertEqual(result["payload"]["predictedTargetOrbit"]["argumentOfPerigee"], 0.0)
        self.assertEqual(result["payload"]["assessedPurpose"]["category"], "COMMERCIAL")
        self.assertEqual(result["payload"]["assessedPurpose"]["description"], "Starlink launch")

    def test_determine_orbit_type(self):
        """Test determining the orbit type based on position."""
        # LEO
        position = {"x": 6000.0, "y": 0.0, "z": 0.0}
        self.assertEqual(determine_orbit_type(position), "LEO")
        
        # MEO
        position = {"x": 15000.0, "y": 0.0, "z": 0.0}
        self.assertEqual(determine_orbit_type(position), "MEO")
        
        # GEO
        position = {"x": 42000.0, "y": 0.0, "z": 0.0}
        self.assertEqual(determine_orbit_type(position), "GEO")
        
        # HEO
        position = {"x": 60000.0, "y": 0.0, "z": 0.0}
        self.assertEqual(determine_orbit_type(position), "HEO")

    def test_determine_risk_level(self):
        """Test determining the risk level based on miss distance and probability."""
        # CRITICAL
        self.assertEqual(determine_risk_level(1000.0, 1.5e-3), "CRITICAL")
        
        # HIGH
        self.assertEqual(determine_risk_level(2000.0, 5e-4), "HIGH")
        
        # MEDIUM
        self.assertEqual(determine_risk_level(3000.0, 5e-5), "MEDIUM")
        self.assertEqual(determine_risk_level(500.0, 1e-6), "MEDIUM")
        
        # LOW
        self.assertEqual(determine_risk_level(10000.0, 1e-6), "LOW")

    @patch("asttroshield.udl_integration.transformers.uuid.uuid4")
    @patch("asttroshield.udl_integration.transformers.datetime")
    def test_transform_track(self, mock_datetime, mock_uuid4):
        """Test transforming a UDL track to AstroShield format."""
        # Mock uuid4 and datetime
        mock_uuid4.return_value = "test-uuid"
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 0, 0, 0)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        udl_track = {
            "trackId": "track-123",
            "satno": 12345,
            "objectName": "TEST-SAT",
            "sensorId": "sensor-456",
            "sensorName": "TEST-SENSOR",
            "sensorType": "RADAR",
            "sensorLatitude": 40.0,
            "sensorLongitude": -75.0,
            "sensorAltitude": 100.0,
            "observationCount": 10,
            "observationStart": "2023-01-01T00:00:00Z",
            "observationEnd": "2023-01-01T01:00:00Z",
            "trackQuality": "HIGH",
            "trackType": "RADAR",
            "trackState": "ACTIVE",
            "confidence": 0.95,
            "stateVectorId": "sv-789"
        }
        
        result = transform_track(udl_track)
        
        # Assert header structure
        self.assertEqual(result["header"]["messageId"], "track-test-uuid")
        self.assertEqual(result["header"]["timestamp"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["header"]["source"], "udl_integration")
        self.assertEqual(result["header"]["messageType"], "ss1.track.detection")
        
        # Assert payload structure
        self.assertEqual(result["payload"]["trackId"], "track-123")
        self.assertEqual(result["payload"]["objectId"], "SATCAT-12345")
        self.assertEqual(result["payload"]["noradId"], 12345)
        self.assertEqual(result["payload"]["objectName"], "TEST-SAT")
        self.assertEqual(result["payload"]["trackQuality"], "HIGH")
        self.assertEqual(result["payload"]["trackType"], "RADAR")
        
        # Assert sensor info
        self.assertEqual(result["payload"]["sensorInfo"]["sensorId"], "sensor-456")
        self.assertEqual(result["payload"]["sensorInfo"]["sensorName"], "TEST-SENSOR")
        self.assertEqual(result["payload"]["sensorInfo"]["sensorType"], "RADAR")
        self.assertEqual(result["payload"]["sensorInfo"]["sensorLocation"]["latitude"], 40.0)
        self.assertEqual(result["payload"]["sensorInfo"]["sensorLocation"]["longitude"], -75.0)
        self.assertEqual(result["payload"]["sensorInfo"]["sensorLocation"]["altitude"], 100.0)
        
        # Assert observation stats
        self.assertEqual(result["payload"]["observationStats"]["observationCount"], 10)
        self.assertEqual(result["payload"]["observationStats"]["startTime"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["payload"]["observationStats"]["endTime"], "2023-01-01T01:00:00Z")
        self.assertEqual(result["payload"]["observationStats"]["trackDuration"]["value"], 3600.0)
        self.assertEqual(result["payload"]["observationStats"]["trackDuration"]["units"], "seconds")
        
        # Assert other fields
        self.assertEqual(result["payload"]["trackState"], "ACTIVE")
        self.assertEqual(result["payload"]["confidence"], 0.95)
        self.assertEqual(result["payload"]["stateVectorId"], "sv-789")

    @patch("asttroshield.udl_integration.transformers.uuid.uuid4")
    @patch("asttroshield.udl_integration.transformers.datetime")
    def test_transform_ephemeris(self, mock_datetime, mock_uuid4):
        """Test transforming a UDL ephemeris to AstroShield format."""
        # Mock uuid4 and datetime
        mock_uuid4.return_value = "test-uuid"
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 0, 0, 0)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        udl_ephemeris = {
            "satno": 12345,
            "objectName": "TEST-SAT",
            "startTime": "2023-01-01T00:00:00Z",
            "endTime": "2023-01-01T06:00:00Z",
            "referenceFrame": "GCRF",
            "propagationMethod": "SGP4",
            "stepSize": 60,
            "ephemerisPoints": [
                {
                    "epoch": "2023-01-01T00:00:00Z",
                    "x": 1000.0,
                    "y": 2000.0,
                    "z": 3000.0,
                    "xDot": 1.0,
                    "yDot": 2.0,
                    "zDot": 3.0
                },
                {
                    "epoch": "2023-01-01T01:00:00Z",
                    "x": 1100.0,
                    "y": 2100.0,
                    "z": 3100.0,
                    "xDot": 1.1,
                    "yDot": 2.1,
                    "zDot": 3.1
                }
            ],
            "source": "TEST-SOURCE",
            "propagationParameters": {
                "drag": 0.1,
                "solarRadiationPressure": 0.2
            }
        }
        
        result = transform_ephemeris(udl_ephemeris)
        
        # Assert header structure
        self.assertEqual(result["header"]["messageId"], "ephem-test-uuid")
        self.assertEqual(result["header"]["timestamp"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["header"]["source"], "udl_integration")
        self.assertEqual(result["header"]["messageType"], "ss2.ephemeris")
        
        # Assert payload structure
        self.assertEqual(result["payload"]["ephemerisId"], "ephem-test-uuid")
        self.assertEqual(result["payload"]["objectId"], "SATCAT-12345")
        self.assertEqual(result["payload"]["noradId"], 12345)
        self.assertEqual(result["payload"]["objectName"], "TEST-SAT")
        self.assertEqual(result["payload"]["startTime"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["payload"]["endTime"], "2023-01-01T06:00:00Z")
        self.assertEqual(result["payload"]["referenceFrame"], "GCRF")
        self.assertEqual(result["payload"]["propagationMethod"], "SGP4")
        self.assertEqual(result["payload"]["stepSize"]["value"], 60)
        self.assertEqual(result["payload"]["stepSize"]["units"], "seconds")
        
        # Assert ephemeris points
        self.assertEqual(len(result["payload"]["ephemerisPoints"]), 2)
        self.assertEqual(result["payload"]["ephemerisPoints"][0]["epoch"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["payload"]["ephemerisPoints"][0]["position"]["x"], 1000.0)
        self.assertEqual(result["payload"]["ephemerisPoints"][0]["position"]["y"], 2000.0)
        self.assertEqual(result["payload"]["ephemerisPoints"][0]["position"]["z"], 3000.0)
        self.assertEqual(result["payload"]["ephemerisPoints"][0]["velocity"]["x"], 1.0)
        self.assertEqual(result["payload"]["ephemerisPoints"][0]["velocity"]["y"], 2.0)
        self.assertEqual(result["payload"]["ephemerisPoints"][0]["velocity"]["z"], 3.0)
        
        # Assert metadata
        self.assertEqual(result["payload"]["metadata"]["source"], "TEST-SOURCE")
        self.assertEqual(result["payload"]["metadata"]["generationTime"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["payload"]["metadata"]["propagationParameters"]["drag"], 0.1)
        self.assertEqual(result["payload"]["metadata"]["propagationParameters"]["solarRadiationPressure"], 0.2)

    @patch("asttroshield.udl_integration.transformers.uuid.uuid4")
    @patch("asttroshield.udl_integration.transformers.datetime")
    def test_transform_maneuver(self, mock_datetime, mock_uuid4):
        """Test transforming a UDL maneuver to AstroShield format."""
        # Mock uuid4 and datetime
        mock_uuid4.return_value = "test-uuid"
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 0, 0, 0)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        udl_maneuver = {
            "satno": 12345,
            "objectName": "TEST-SAT",
            "startTime": "2023-01-01T00:00:00Z",
            "endTime": "2023-01-01T01:00:00Z",
            "maneuverType": "STATION_KEEPING",
            "deltaV": 10.0,
            "deltaVx": 5.0,
            "deltaVy": 8.0,
            "deltaVz": 3.0,
            "preManeuverStateVectorId": "sv-pre-123",
            "postManeuverStateVectorId": "sv-post-456",
            "preManeuverOrbitType": "LEO",
            "postManeuverOrbitType": "LEO",
            "detectionMethod": "STATISTICAL",
            "confidence": 0.9,
            "purpose": "COLLISION_AVOIDANCE",
            "source": "TEST-SOURCE",
            "detector": "TEST-DETECTOR",
            "anomalyScore": 0.1
        }
        
        result = transform_maneuver(udl_maneuver)
        
        # Assert header structure
        self.assertEqual(result["header"]["messageId"], "mnvr-test-uuid")
        self.assertEqual(result["header"]["timestamp"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["header"]["source"], "udl_integration")
        self.assertEqual(result["header"]["messageType"], "ss2.maneuver.detection")
        
        # Assert payload structure
        self.assertEqual(result["payload"]["maneuverId"], "mnvr-test-uuid")
        self.assertEqual(result["payload"]["objectId"], "SATCAT-12345")
        self.assertEqual(result["payload"]["noradId"], 12345)
        self.assertEqual(result["payload"]["objectName"], "TEST-SAT")
        self.assertEqual(result["payload"]["detectionTime"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["payload"]["maneuverStart"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["payload"]["maneuverEnd"], "2023-01-01T01:00:00Z")
        self.assertEqual(result["payload"]["duration"]["value"], 3600.0)
        self.assertEqual(result["payload"]["duration"]["units"], "seconds")
        self.assertEqual(result["payload"]["maneuverType"], "STATION_KEEPING")
        
        # Assert delta-V
        self.assertEqual(result["payload"]["deltaV"]["value"], 10.0)
        self.assertEqual(result["payload"]["deltaV"]["units"], "m/s")
        self.assertEqual(result["payload"]["deltaVVector"]["x"], 5.0)
        self.assertEqual(result["payload"]["deltaVVector"]["y"], 8.0)
        self.assertEqual(result["payload"]["deltaVVector"]["z"], 3.0)
        
        # Assert pre/post maneuver states
        self.assertEqual(result["payload"]["preManeuverState"]["stateVectorId"], "sv-pre-123")
        self.assertEqual(result["payload"]["preManeuverState"]["orbitType"], "LEO")
        self.assertEqual(result["payload"]["postManeuverState"]["stateVectorId"], "sv-post-456")
        self.assertEqual(result["payload"]["postManeuverState"]["orbitType"], "LEO")
        
        # Assert other fields
        self.assertEqual(result["payload"]["detectionMethod"], "STATISTICAL")
        self.assertEqual(result["payload"]["confidence"], 0.9)
        self.assertEqual(result["payload"]["purpose"], "COLLISION_AVOIDANCE")
        
        # Assert metadata
        self.assertEqual(result["payload"]["metadata"]["source"], "TEST-SOURCE")
        self.assertEqual(result["payload"]["metadata"]["detector"], "TEST-DETECTOR")
        self.assertEqual(result["payload"]["metadata"]["anomalyScore"], 0.1)

    @patch("asttroshield.udl_integration.transformers.uuid.uuid4")
    @patch("asttroshield.udl_integration.transformers.datetime")
    def test_transform_observation(self, mock_datetime, mock_uuid4):
        """Test transforming a UDL observation to AstroShield format."""
        # Mock uuid4 and datetime
        mock_uuid4.return_value = "test-uuid"
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 0, 0, 0)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        udl_observation = {
            "sensorId": "sensor-123",
            "sensorName": "TEST-SENSOR",
            "sensorType": "RADAR",
            "sensorMode": "TRACKING",
            "sensorLatitude": 40.0,
            "sensorLongitude": -75.0,
            "sensorAltitude": 100.0,
            "observationTime": "2023-01-01T00:00:00Z",
            "measurementType": "RANGE_ANGLE",
            "measurementData": {
                "range": 1000.0,
                "azimuth": 45.0,
                "elevation": 30.0
            },
            "measurementUncertainties": {
                "range": 10.0,
                "azimuth": 0.5,
                "elevation": 0.5
            },
            "targetId": "target-456",
            "targetType": "SPACE_OBJECT",
            "trackId": "track-789",
            "processingLevel": "CALIBRATED",
            "calibrationApplied": True,
            "noiseReductionApplied": True,
            "source": "TEST-SOURCE",
            "quality": "HIGH",
            "observationCampaign": "TEST-CAMPAIGN"
        }
        
        result = transform_observation(udl_observation)
        
        # Assert header structure
        self.assertEqual(result["header"]["messageId"], "obs-test-uuid")
        self.assertEqual(result["header"]["timestamp"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["header"]["source"], "udl_integration")
        self.assertEqual(result["header"]["messageType"], "ss0.observation")
        
        # Assert payload structure
        self.assertEqual(result["payload"]["observationId"], "obs-test-uuid")
        self.assertEqual(result["payload"]["observationTime"], "2023-01-01T00:00:00Z")
        
        # Assert sensor info
        self.assertEqual(result["payload"]["sensorInfo"]["sensorId"], "sensor-123")
        self.assertEqual(result["payload"]["sensorInfo"]["sensorName"], "TEST-SENSOR")
        self.assertEqual(result["payload"]["sensorInfo"]["sensorType"], "RADAR")
        self.assertEqual(result["payload"]["sensorInfo"]["sensorMode"], "TRACKING")
        self.assertEqual(result["payload"]["sensorInfo"]["sensorLocation"]["latitude"], 40.0)
        self.assertEqual(result["payload"]["sensorInfo"]["sensorLocation"]["longitude"], -75.0)
        self.assertEqual(result["payload"]["sensorInfo"]["sensorLocation"]["altitude"], 100.0)
        
        # Assert measurements
        self.assertEqual(result["payload"]["measurements"]["type"], "RANGE_ANGLE")
        self.assertEqual(result["payload"]["measurements"]["data"]["range"], 1000.0)
        self.assertEqual(result["payload"]["measurements"]["data"]["azimuth"], 45.0)
        self.assertEqual(result["payload"]["measurements"]["data"]["elevation"], 30.0)
        self.assertEqual(result["payload"]["measurements"]["uncertainties"]["range"], 10.0)
        self.assertEqual(result["payload"]["measurements"]["uncertainties"]["azimuth"], 0.5)
        self.assertEqual(result["payload"]["measurements"]["uncertainties"]["elevation"], 0.5)
        
        # Assert target info
        self.assertEqual(result["payload"]["targetInfo"]["targetId"], "target-456")
        self.assertEqual(result["payload"]["targetInfo"]["targetType"], "SPACE_OBJECT")
        self.assertEqual(result["payload"]["targetInfo"]["trackId"], "track-789")
        
        # Assert processing info
        self.assertEqual(result["payload"]["processingInfo"]["processingLevel"], "CALIBRATED")
        self.assertEqual(result["payload"]["processingInfo"]["calibrationApplied"], True)
        self.assertEqual(result["payload"]["processingInfo"]["noiseReductionApplied"], True)
        
        # Assert metadata
        self.assertEqual(result["payload"]["metadata"]["source"], "TEST-SOURCE")
        self.assertEqual(result["payload"]["metadata"]["quality"], "HIGH")
        self.assertEqual(result["payload"]["metadata"]["observationCampaign"], "TEST-CAMPAIGN")

    @patch("asttroshield.udl_integration.transformers.uuid.uuid4")
    @patch("asttroshield.udl_integration.transformers.datetime")
    def test_transform_elset(self, mock_datetime, mock_uuid4):
        """Test transforming a UDL ELSET to AstroShield format."""
        # Mock uuid4 and datetime
        mock_uuid4.return_value = "test-uuid"
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 0, 0, 0)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        udl_elset = {
            "satno": 12345,
            "objectName": "TEST-SAT",
            "epoch": "2023-01-01T00:00:00Z",
            "line1": "1 12345U 98067A   23001.00000000  .00000000  00000-0  00000-0 0  9995",
            "line2": "2 12345  51.6416 236.2857 0006317  47.4769  89.9851 15.49135672    06",
            "meanMotion": 15.49135672,
            "eccentricity": 0.0006317,
            "inclination": 51.6416,
            "raan": 236.2857,
            "argOfPerigee": 47.4769,
            "meanAnomaly": 89.9851,
            "bstar": 0.0,
            "revolutionNumber": 6,
            "source": "TEST-SOURCE",
            "elsetNumber": 999,
            "classification": "UNCLASSIFIED",
            "meanElementTheory": "SGP4"
        }
        
        result = transform_elset(udl_elset)
        
        # Assert header structure
        self.assertEqual(result["header"]["messageId"], "elset-test-uuid")
        self.assertEqual(result["header"]["timestamp"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["header"]["source"], "udl_integration")
        self.assertEqual(result["header"]["messageType"], "ss2.elset")
        
        # Assert payload structure
        self.assertEqual(result["payload"]["elsetId"], "elset-test-uuid")
        self.assertEqual(result["payload"]["objectId"], "SATCAT-12345")
        self.assertEqual(result["payload"]["noradId"], 12345)
        self.assertEqual(result["payload"]["objectName"], "TEST-SAT")
        self.assertEqual(result["payload"]["epoch"], "2023-01-01T00:00:00Z")
        
        # Assert TLE
        self.assertEqual(result["payload"]["tle"]["line1"], "1 12345U 98067A   23001.00000000  .00000000  00000-0  00000-0 0  9995")
        self.assertEqual(result["payload"]["tle"]["line2"], "2 12345  51.6416 236.2857 0006317  47.4769  89.9851 15.49135672    06")
        
        # Assert mean elements
        self.assertEqual(result["payload"]["meanElements"]["epoch"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["payload"]["meanElements"]["meanMotion"]["value"], 15.49135672)
        self.assertEqual(result["payload"]["meanElements"]["meanMotion"]["units"], "revs/day")
        self.assertEqual(result["payload"]["meanElements"]["eccentricity"], 0.0006317)
        self.assertEqual(result["payload"]["meanElements"]["inclination"]["value"], 51.6416)
        self.assertEqual(result["payload"]["meanElements"]["inclination"]["units"], "degrees")
        self.assertEqual(result["payload"]["meanElements"]["raan"]["value"], 236.2857)
        self.assertEqual(result["payload"]["meanElements"]["raan"]["units"], "degrees")
        self.assertEqual(result["payload"]["meanElements"]["argOfPerigee"]["value"], 47.4769)
        self.assertEqual(result["payload"]["meanElements"]["argOfPerigee"]["units"], "degrees")
        self.assertEqual(result["payload"]["meanElements"]["meanAnomaly"]["value"], 89.9851)
        self.assertEqual(result["payload"]["meanElements"]["meanAnomaly"]["units"], "degrees")
        self.assertEqual(result["payload"]["meanElements"]["bstar"], 0.0)
        self.assertEqual(result["payload"]["meanElements"]["revolutionNumber"], 6)
        
        # Assert other fields
        self.assertEqual(result["payload"]["source"], "TEST-SOURCE")
        self.assertEqual(result["payload"]["elsetNumber"], 999)
        self.assertEqual(result["payload"]["classification"], "UNCLASSIFIED")
        self.assertEqual(result["payload"]["meanElementTheory"], "SGP4")

    @patch("asttroshield.udl_integration.transformers.uuid.uuid4")
    @patch("asttroshield.udl_integration.transformers.datetime")
    def test_transform_orbit_determination(self, mock_datetime, mock_uuid4):
        """Test transforming a UDL orbit determination to AstroShield format."""
        # Mock uuid4 and datetime
        mock_uuid4.return_value = "test-uuid"
        mock_datetime.utcnow.return_value = datetime(2023, 1, 1, 0, 0, 0)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        udl_orbit_determination = {
            "satno": 12345,
            "objectName": "TEST-SAT",
            "epoch": "2023-01-01T00:00:00Z",
            "referenceFrame": "GCRF",
            "semiMajorAxis": 7000.0,
            "eccentricity": 0.001,
            "inclination": 51.6,
            "raan": 236.3,
            "argOfPerigee": 47.5,
            "meanAnomaly": 90.0,
            "observationCount": 100,
            "observationArcs": 3,
            "observationSpan": 7.0,
            "residualRms": 0.05,
            "covarianceAvailable": True,
            "covarianceMatrix": [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0]
            ],
            "source": "TEST-SOURCE",
            "orbitalModel": "SGP4",
            "quality": "HIGH",
            "determiniationMethod": "BATCH_LEAST_SQUARES"
        }
        
        result = transform_orbit_determination(udl_orbit_determination)
        
        # Assert header structure
        self.assertEqual(result["header"]["messageId"], "orb-test-uuid")
        self.assertEqual(result["header"]["timestamp"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["header"]["source"], "udl_integration")
        self.assertEqual(result["header"]["messageType"], "ss2.orbit.determination")
        
        # Assert payload structure
        self.assertEqual(result["payload"]["orbitDeterminationId"], "orb-test-uuid")
        self.assertEqual(result["payload"]["objectId"], "SATCAT-12345")
        self.assertEqual(result["payload"]["noradId"], 12345)
        self.assertEqual(result["payload"]["objectName"], "TEST-SAT")
        self.assertEqual(result["payload"]["epoch"], "2023-01-01T00:00:00Z")
        self.assertEqual(result["payload"]["referenceFrame"], "GCRF")
        
        # Assert orbital elements
        self.assertEqual(result["payload"]["orbitalElements"]["semiMajorAxis"]["value"], 7000.0)
        self.assertEqual(result["payload"]["orbitalElements"]["semiMajorAxis"]["units"], "km")
        self.assertEqual(result["payload"]["orbitalElements"]["eccentricity"], 0.001)
        self.assertEqual(result["payload"]["orbitalElements"]["inclination"]["value"], 51.6)
        self.assertEqual(result["payload"]["orbitalElements"]["inclination"]["units"], "degrees")
        self.assertEqual(result["payload"]["orbitalElements"]["raan"]["value"], 236.3)
        self.assertEqual(result["payload"]["orbitalElements"]["raan"]["units"], "degrees")
        self.assertEqual(result["payload"]["orbitalElements"]["argOfPerigee"]["value"], 47.5)
        self.assertEqual(result["payload"]["orbitalElements"]["argOfPerigee"]["units"], "degrees")
        self.assertEqual(result["payload"]["orbitalElements"]["meanAnomaly"]["value"], 90.0)
        self.assertEqual(result["payload"]["orbitalElements"]["meanAnomaly"]["units"], "degrees")
        
        # Assert derived parameters
        self.assertIsNotNone(result["payload"]["derivedParameters"]["period"]["value"])
        self.assertEqual(result["payload"]["derivedParameters"]["period"]["units"], "minutes")
        self.assertIsNotNone(result["payload"]["derivedParameters"]["apogee"]["value"])
        self.assertEqual(result["payload"]["derivedParameters"]["apogee"]["units"], "km")
        self.assertIsNotNone(result["payload"]["derivedParameters"]["perigee"]["value"])
        self.assertEqual(result["payload"]["derivedParameters"]["perigee"]["units"], "km")
        self.assertIsNotNone(result["payload"]["derivedParameters"]["orbitType"])
        self.assertIsNotNone(result["payload"]["derivedParameters"]["meanMotion"]["value"])
        self.assertEqual(result["payload"]["derivedParameters"]["meanMotion"]["units"], "revs/day")
        
        # Assert correlation info
        self.assertEqual(result["payload"]["correlationInfo"]["observations"], 100)
        self.assertEqual(result["payload"]["correlationInfo"]["observationArcs"], 3)
        self.assertEqual(result["payload"]["correlationInfo"]["observationSpan"]["value"], 7.0)
        self.assertEqual(result["payload"]["correlationInfo"]["observationSpan"]["units"], "days")
        self.assertEqual(result["payload"]["correlationInfo"]["residualRms"], 0.05)
        self.assertEqual(result["payload"]["correlationInfo"]["covarianceAvailable"], True)
        
        # Assert covariance
        self.assertEqual(result["payload"]["covariance"], [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ])
        
        # Assert metadata
        self.assertEqual(result["payload"]["metadata"]["source"], "TEST-SOURCE")
        self.assertEqual(result["payload"]["metadata"]["orbitalModel"], "SGP4")
        self.assertEqual(result["payload"]["metadata"]["quality"], "HIGH")
        self.assertEqual(result["payload"]["metadata"]["determiniationMethod"], "BATCH_LEAST_SQUARES")

    def test_calculate_track_duration(self):
        """Test calculating track duration."""
        start_time = "2023-01-01T00:00:00Z"
        end_time = "2023-01-01T01:30:00Z"
        
        result = calculate_track_duration(start_time, end_time)
        
        self.assertEqual(result, 5400.0)  # 1.5 hours = 5400 seconds
    
    def test_calculate_maneuver_duration(self):
        """Test calculating maneuver duration."""
        start_time = "2023-01-01T00:00:00Z"
        end_time = "2023-01-01T00:30:00Z"
        
        result = calculate_maneuver_duration(start_time, end_time)
        
        self.assertEqual(result, 1800.0)  # 30 minutes = 1800 seconds
    
    def test_calculate_orbital_period(self):
        """Test calculating orbital period."""
        semi_major_axis = 7000.0  # km
        
        result = calculate_orbital_period(semi_major_axis)
        
        # This is an approximate value
        self.assertAlmostEqual(result, 97.65, delta=1.0)  # ~97.65 minutes
    
    def test_calculate_apogee_perigee(self):
        """Test calculating apogee and perigee."""
        semi_major_axis = 7000.0  # km
        eccentricity = 0.1
        
        apogee = calculate_apogee(semi_major_axis, eccentricity)
        perigee = calculate_perigee(semi_major_axis, eccentricity)
        
        self.assertEqual(apogee, 7700.0)  # 7000 * (1 + 0.1) = 7700
        self.assertEqual(perigee, 6300.0)  # 7000 * (1 - 0.1) = 6300
    
    def test_calculate_mean_motion(self):
        """Test calculating mean motion."""
        semi_major_axis = 7000.0  # km
        
        result = calculate_mean_motion(semi_major_axis)
        
        # This is an approximate value
        self.assertAlmostEqual(result, 14.74, delta=0.1)  # ~14.74 revs/day
    
    def test_determine_orbit_type_from_elements(self):
        """Test determining orbit type from orbital elements."""
        # Test LEO
        result = determine_orbit_type_from_elements(7000.0, 0.001)
        self.assertEqual(result, "LEO")
        
        # Test MEO
        result = determine_orbit_type_from_elements(20000.0, 0.001)
        self.assertEqual(result, "MEO")
        
        # Test GEO
        result = determine_orbit_type_from_elements(42164.0, 0.001)
        self.assertEqual(result, "GEO")
        
        # Test HEO
        result = determine_orbit_type_from_elements(42164.0, 0.5)
        self.assertEqual(result, "HEO")
        
        # Test SUPER_GEO
        result = determine_orbit_type_from_elements(45000.0, 0.001)
        self.assertEqual(result, "SUPER_GEO")
        
        # Test DECAYING
        result = determine_orbit_type_from_elements(6400.0, 0.1)
        self.assertEqual(result, "DECAYING")


if __name__ == "__main__":
    unittest.main() 