"""
UDL Integration

This module provides the main integration between UDL APIs and AstroShield Kafka topics.
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Set

# Import and load dotenv at the top level to ensure environment variables are loaded
from dotenv import load_dotenv
load_dotenv()  # This will load variables from .env file into the environment

from .client import UDLClient
from .messaging_client import UDLMessagingClient
from .transformers import (
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
    transform_cyber_threat,
    transform_link_status,
    transform_comm_data,
    transform_mission_ops,
    transform_vessel,
    transform_aircraft,
    transform_ground_imagery,
    transform_sky_imagery,
    transform_video_streaming,
)
from .kafka_producer import AstroShieldKafkaProducer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class UDLIntegration:
    """Main integration class for UDL and AstroShield."""

    def __init__(
        self,
        udl_base_url: str = "https://unifieddatalibrary.com",
        udl_api_key: Optional[str] = None,
        udl_username: Optional[str] = None,
        udl_password: Optional[str] = None,
        udl_timeout: int = 30,
        udl_max_retries: int = 3,
        kafka_bootstrap_servers: Optional[str] = None,
        kafka_security_protocol: str = "PLAINTEXT",
        kafka_sasl_mechanism: Optional[str] = None,
        kafka_sasl_username: Optional[str] = None,
        kafka_sasl_password: Optional[str] = None,
        use_secure_messaging: bool = False,
        sample_period: float = 0.34,
    ):
        """
        Initialize the UDL Integration.

        Args:
            udl_base_url: Base URL for the UDL API.
            udl_api_key: API key for UDL authentication.
            udl_username: Username for UDL authentication.
            udl_password: Password for UDL authentication.
            udl_timeout: Timeout for UDL API requests.
            udl_max_retries: Maximum number of retries for UDL API requests.
            kafka_bootstrap_servers: Comma-separated list of Kafka bootstrap servers.
            kafka_security_protocol: Security protocol for Kafka (PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL).
            kafka_sasl_mechanism: SASL mechanism for Kafka (PLAIN, SCRAM-SHA-256, SCRAM-SHA-512).
            kafka_sasl_username: SASL username for Kafka.
            kafka_sasl_password: SASL password for Kafka.
            use_secure_messaging: Whether to use the UDL Secure Messaging API.
            sample_period: Minimum time between requests (seconds) to respect rate limits.
        """
        # Initialize UDL client
        self.udl_client = UDLClient(
            base_url=udl_base_url,
            api_key=udl_api_key,
            username=udl_username,
            password=udl_password,
            timeout=udl_timeout,
            max_retries=udl_max_retries,
        )
        
        # Initialize UDL Secure Messaging client if enabled
        self.messaging_client = None
        self.use_secure_messaging = use_secure_messaging
        self.active_streaming_topics = set()
        
        if use_secure_messaging:
            try:
                self.messaging_client = UDLMessagingClient(
                    base_url=udl_base_url,
                    username=udl_username,
                    password=udl_password,
                    timeout=udl_timeout,
                    max_retries=udl_max_retries,
                    sample_period=sample_period,
                )
                logger.info("UDL Secure Messaging client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize UDL Secure Messaging client: {str(e)}")
                logger.warning("Secure Messaging will be disabled. Make sure you have proper authorization.")
                self.use_secure_messaging = False
        
        # Initialize topic to transformer and publisher mappings
        self.topic_transformers = {}
        self.topic_publishers = {}
        
        # Initialize Kafka producer if bootstrap servers are provided
        self.producer = None
        if kafka_bootstrap_servers:
            kafka_config = {
                "bootstrap_servers": kafka_bootstrap_servers,
                "client_id": "udl_integration",
            }
            
            # Add security configuration if provided
            if kafka_security_protocol != "PLAINTEXT":
                kafka_config["security_protocol"] = kafka_security_protocol
                
                if "SASL" in kafka_security_protocol:
                    if not kafka_sasl_mechanism or not kafka_sasl_username or not kafka_sasl_password:
                        raise ValueError("SASL mechanism, username, and password are required for SASL authentication")
                    
                    kafka_config["sasl_mechanism"] = kafka_sasl_mechanism
                    kafka_config["sasl_plain_username"] = kafka_sasl_username
                    kafka_config["sasl_plain_password"] = kafka_sasl_password
            
            # Initialize Kafka producer
            from kafka import KafkaProducer
            self.producer = KafkaProducer(**kafka_config)
        
        logger.info("UDL Integration initialized successfully")
        if self.use_secure_messaging:
            logger.info("Secure Messaging is enabled")
        else:
            logger.info("Secure Messaging is disabled")

    def process_state_vectors(self, epoch: Optional[str] = None) -> None:
        """
        Process state vectors from UDL and publish to AstroShield.

        Args:
            epoch: Time of validity for state vector in ISO 8601 UTC format
        """
        # Use current time if epoch not provided
        if epoch is None:
            epoch = datetime.utcnow().isoformat() + "Z"

        logger.info(f"Processing state vectors for epoch {epoch}")

        try:
            # Get state vectors from UDL
            udl_state_vectors = self.udl_client.get_state_vectors(epoch=epoch)
            logger.info(f"Retrieved {len(udl_state_vectors)} state vectors from UDL")

            # Transform state vectors to AstroShield format
            astroshield_state_vectors = [
                transform_state_vector(sv) for sv in udl_state_vectors
            ]

            # Publish state vectors to Kafka
            self.producer.send(
                "statevector",
                key=None,
                value=json.dumps(astroshield_state_vectors).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_state_vectors)} state vectors to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing state vectors: {e}")
            raise

    def process_conjunctions(self, **query_params) -> None:
        """
        Process conjunctions from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL conjunction API
        """
        logger.info("Processing conjunctions")

        try:
            # Get conjunctions from UDL
            udl_conjunctions = self.udl_client.get_conjunctions(**query_params)
            logger.info(f"Retrieved {len(udl_conjunctions)} conjunctions from UDL")

            # Transform conjunctions to AstroShield format
            astroshield_conjunctions = [
                transform_conjunction(conj) for conj in udl_conjunctions
            ]

            # Publish conjunctions to Kafka
            self.producer.send(
                "conjunction",
                key=None,
                value=json.dumps(astroshield_conjunctions).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_conjunctions)} conjunctions to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing conjunctions: {e}")
            raise

    def process_launch_events(self, msg_create_date: Optional[str] = None, **query_params) -> None:
        """
        Process launch events from UDL and publish to AstroShield.

        Args:
            msg_create_date: Timestamp of the originating message in ISO8601 UTC format
            **query_params: Additional query parameters for UDL launch event API
        """
        # Use current time if msg_create_date not provided
        if msg_create_date is None:
            msg_create_date = datetime.utcnow().isoformat() + "Z"

        logger.info(f"Processing launch events for msg_create_date {msg_create_date}")

        try:
            # Get launch events from UDL
            udl_launch_events = self.udl_client.get_launch_events(
                msg_create_date=msg_create_date, **query_params
            )
            logger.info(f"Retrieved {len(udl_launch_events)} launch events from UDL")

            # Transform launch events to AstroShield format
            astroshield_launch_events = [
                transform_launch_event(event) for event in udl_launch_events
            ]

            # Publish launch events to Kafka
            self.producer.send(
                "launchevent",
                key=None,
                value=json.dumps(astroshield_launch_events).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_launch_events)} launch events to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing launch events: {e}")
            raise

    def process_tracks(self, **query_params) -> None:
        """
        Process tracks from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL track API
        """
        logger.info("Processing tracks")

        try:
            # Get tracks from UDL
            udl_tracks = self.udl_client.get_tracks(**query_params)
            logger.info(f"Retrieved {len(udl_tracks)} tracks from UDL")

            # Transform tracks to AstroShield format
            astroshield_tracks = [
                transform_track(track) for track in udl_tracks
            ]

            # Publish tracks to Kafka
            self.producer.send(
                "track",
                key=None,
                value=json.dumps(astroshield_tracks).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_tracks)} tracks to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing tracks: {e}")
            raise

    def process_ephemeris(self, **query_params) -> None:
        """
        Process ephemeris data from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL ephemeris API
        """
        logger.info("Processing ephemeris data")

        try:
            # Get ephemeris data from UDL
            udl_ephemeris_list = self.udl_client.get_ephemeris(**query_params)
            logger.info(f"Retrieved {len(udl_ephemeris_list)} ephemeris entries from UDL")

            # Transform ephemeris data to AstroShield format
            astroshield_ephemeris_list = [
                transform_ephemeris(ephem) for ephem in udl_ephemeris_list
            ]

            # Publish ephemeris data to Kafka
            self.producer.send(
                "ephemeris",
                key=None,
                value=json.dumps(astroshield_ephemeris_list).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_ephemeris_list)} ephemeris entries to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing ephemeris data: {e}")
            raise

    def process_maneuvers(self, **query_params) -> None:
        """
        Process maneuvers from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL maneuver API
        """
        logger.info("Processing maneuvers")

        try:
            # Get maneuvers from UDL
            udl_maneuvers = self.udl_client.get_maneuvers(**query_params)
            logger.info(f"Retrieved {len(udl_maneuvers)} maneuvers from UDL")

            # Transform maneuvers to AstroShield format
            astroshield_maneuvers = [
                transform_maneuver(maneuver) for maneuver in udl_maneuvers
            ]

            # Publish maneuvers to Kafka
            self.producer.send(
                "maneuver",
                key=None,
                value=json.dumps(astroshield_maneuvers).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_maneuvers)} maneuvers to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing maneuvers: {e}")
            raise

    def process_observations(self, **query_params) -> None:
        """
        Process observations from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL observation API
        """
        logger.info("Processing observations")

        try:
            # Get observations from UDL
            udl_observations = self.udl_client.get_observations(**query_params)
            logger.info(f"Retrieved {len(udl_observations)} observations from UDL")

            # Transform observations to AstroShield format
            astroshield_observations = [
                transform_observation(obs) for obs in udl_observations
            ]

            # Publish observations to Kafka
            self.producer.send(
                "eoobservation",
                key=None,
                value=json.dumps(astroshield_observations).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_observations)} observations to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing observations: {e}")
            raise

    def process_sensor_data(self, **query_params) -> None:
        """
        Process sensor data from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL sensor API
        """
        logger.info("Processing sensor data")

        try:
            # Get sensor data from UDL
            udl_sensor_data = self.udl_client.get_sensor_data(**query_params)
            logger.info(f"Retrieved {len(udl_sensor_data)} sensor records from UDL")

            # Transform sensor data to AstroShield format
            astroshield_sensor_data = [
                transform_sensor(sensor) for sensor in udl_sensor_data
            ]

            # Publish sensor data to Kafka
            self.producer.send(
                "sensor",
                key=None,
                value=json.dumps(astroshield_sensor_data).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_sensor_data)} sensor records to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing sensor data: {e}")
            raise

    def process_orbit_determinations(self, **query_params) -> None:
        """
        Process orbit determinations from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL orbit determination API
        """
        logger.info("Processing orbit determinations")

        try:
            # Get orbit determinations from UDL
            udl_orbit_determinations = self.udl_client.get_orbit_determination(**query_params)
            logger.info(f"Retrieved {len(udl_orbit_determinations)} orbit determinations from UDL")

            # Transform orbit determinations to AstroShield format
            astroshield_orbit_determinations = [
                transform_orbit_determination(od) for od in udl_orbit_determinations
            ]

            # Publish orbit determinations to Kafka
            self.producer.send(
                "orbitdetermination",
                key=None,
                value=json.dumps(astroshield_orbit_determinations).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_orbit_determinations)} orbit determinations to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing orbit determinations: {e}")
            raise

    def process_elsets(self, **query_params) -> None:
        """
        Process ELSETs from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL ELSET API
        """
        logger.info("Processing ELSETs")

        try:
            # Get ELSETs from UDL
            udl_elsets = self.udl_client.get_elset_data(**query_params)
            logger.info(f"Retrieved {len(udl_elsets)} ELSETs from UDL")

            # Transform ELSETs to AstroShield format
            astroshield_elsets = [
                transform_elset(elset) for elset in udl_elsets
            ]

            # Publish ELSETs to Kafka
            self.producer.send(
                "elset",
                key=None,
                value=json.dumps(astroshield_elsets).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_elsets)} ELSETs to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing ELSETs: {e}")
            raise

    def process_weather_data(self, **query_params) -> None:
        """
        Process weather data from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL weather API
        """
        logger.info("Processing weather data")

        try:
            # Get weather data from UDL
            udl_weather_data = self.udl_client.get_weather_data(**query_params)
            logger.info(f"Retrieved {len(udl_weather_data)} weather records from UDL")

            # Transform weather data to AstroShield format
            astroshield_weather_data = [
                transform_weather(weather) for weather in udl_weather_data
            ]

            # Publish weather data to Kafka
            self.producer.send(
                "weatherdata",
                key=None,
                value=json.dumps(astroshield_weather_data).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_weather_data)} weather records to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing weather data: {e}")
            raise

    def process_sensor_tasking(self, **query_params) -> None:
        """
        Process sensor tasking from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL sensor tasking API
        """
        logger.info("Processing sensor tasking")

        try:
            # Get sensor tasking from UDL
            udl_sensor_tasking = self.udl_client.get_sensor_tasking(**query_params)
            logger.info(f"Retrieved {len(udl_sensor_tasking)} sensor tasking records from UDL")

            # For sensor tasking, we might need a custom transformer
            # For now, we'll use a simplified approach with the sensor format
            astroshield_sensor_tasking = []
            for tasking in udl_sensor_tasking:
                # Add custom fields for tasking
                sensor_data = {
                    "taskingId": tasking.get("taskingId", f"tasking-{tasking.get('sensorId', 'unknown')}"),
                    "status": tasking.get("status", "SCHEDULED"),
                    "priority": tasking.get("priority", "MEDIUM"),
                    "requestTime": tasking.get("requestTime", datetime.utcnow().isoformat() + "Z"),
                    "executionTime": tasking.get("executionTime", datetime.utcnow().isoformat() + "Z"),
                    "targetId": tasking.get("targetId", "UNKNOWN"),
                    "targetType": tasking.get("targetType", "SPACE_OBJECT"),
                    "taskingParameters": tasking.get("taskingParameters", {})
                }
                
                # Merge with basic sensor data
                tasking.update(sensor_data)
                
                # Transform using the sensor transformer as a base
                transformed = transform_sensor(tasking)
                
                # Update message type
                transformed["header"]["messageType"] = "ss0.sensor.tasking"
                
                astroshield_sensor_tasking.append(transformed)

            # Publish sensor tasking to Kafka
            self.producer.send(
                "missionops",
                key=None,
                value=json.dumps(astroshield_sensor_tasking).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_sensor_tasking)} sensor tasking records to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing sensor tasking: {e}")
            raise

    def process_cyber_threats(self, **query_params) -> None:
        """
        Process cyber threat data from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL cyber threats API
        """
        logger.info("Processing cyber threats")

        try:
            # Get cyber threat data from UDL
            udl_cyber_threats = self.udl_client.get_cyber_threats(**query_params)
            logger.info(f"Retrieved {len(udl_cyber_threats)} cyber threats from UDL")

            # Transform cyber threat data to AstroShield format
            astroshield_cyber_threats = [
                transform_cyber_threat(threat) for threat in udl_cyber_threats
            ]

            # Publish cyber threat data to Kafka
            self.producer.send(
                "cyberthreat",
                key=None,
                value=json.dumps(astroshield_cyber_threats).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_cyber_threats)} cyber threats to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing cyber threats: {e}")
            raise

    def process_link_status(self, **query_params) -> None:
        """
        Process link status data from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL link status API
        """
        logger.info("Processing link status")

        try:
            # Get link status data from UDL
            udl_link_status = self.udl_client.get_link_status(**query_params)
            logger.info(f"Retrieved {len(udl_link_status)} link status records from UDL")

            # Transform link status data to AstroShield format
            astroshield_link_status = [
                transform_link_status(status) for status in udl_link_status
            ]

            # Publish link status data to Kafka
            self.producer.send(
                "linkstatus",
                key=None,
                value=json.dumps(astroshield_link_status).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_link_status)} link status records to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing link status: {e}")
            raise

    def process_comm_data(self, **query_params) -> None:
        """
        Process communications data from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL communications API
        """
        logger.info("Processing communications data")

        try:
            # Get communications data from UDL
            udl_comm_data = self.udl_client.get_comm_data(**query_params)
            logger.info(f"Retrieved {len(udl_comm_data)} communications records from UDL")

            # Transform communications data to AstroShield format
            astroshield_comm_data = [
                transform_comm_data(comm) for comm in udl_comm_data
            ]

            # Publish communications data to Kafka
            self.producer.send(
                "commdata",
                key=None,
                value=json.dumps(astroshield_comm_data).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_comm_data)} communications records to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing communications data: {e}")
            raise

    def process_mission_ops_data(self, **query_params) -> None:
        """
        Process mission operations data from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL mission operations API
        """
        logger.info("Processing mission operations data")

        try:
            # Get mission operations data from UDL
            udl_mission_ops = self.udl_client.get_mission_ops_data(**query_params)
            logger.info(f"Retrieved {len(udl_mission_ops)} mission operations records from UDL")

            # Transform mission operations data to AstroShield format
            astroshield_mission_ops = [
                transform_mission_ops(ops) for ops in udl_mission_ops
            ]

            # Publish mission operations data to Kafka
            self.producer.send(
                "missionops",
                key=None,
                value=json.dumps(astroshield_mission_ops).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_mission_ops)} mission operations records to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing mission operations data: {e}")
            raise

    def process_vessel_data(self, **query_params) -> None:
        """
        Process vessel tracking data from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL vessel API
        """
        logger.info("Processing vessel tracking data")

        try:
            # Get vessel tracking data from UDL
            udl_vessel_data = self.udl_client.get_vessel_data(**query_params)
            logger.info(f"Retrieved {len(udl_vessel_data)} vessel records from UDL")

            # Transform vessel tracking data to AstroShield format
            astroshield_vessel_data = [
                transform_vessel(vessel) for vessel in udl_vessel_data
            ]

            # Publish vessel tracking data to Kafka
            self.producer.send(
                "vesseltracking",
                key=None,
                value=json.dumps(astroshield_vessel_data).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_vessel_data)} vessel records to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing vessel tracking data: {e}")
            raise

    def process_aircraft_data(self, **query_params) -> None:
        """
        Process aircraft tracking data from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL aircraft API
        """
        logger.info("Processing aircraft tracking data")

        try:
            # Get aircraft tracking data from UDL
            udl_aircraft_data = self.udl_client.get_aircraft_data(**query_params)
            logger.info(f"Retrieved {len(udl_aircraft_data)} aircraft records from UDL")

            # Transform aircraft tracking data to AstroShield format
            astroshield_aircraft_data = [
                transform_aircraft(aircraft) for aircraft in udl_aircraft_data
            ]

            # Publish aircraft tracking data to Kafka
            self.producer.send(
                "aircrafttracking",
                key=None,
                value=json.dumps(astroshield_aircraft_data).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_aircraft_data)} aircraft records to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing aircraft tracking data: {e}")
            raise

    def process_ground_imagery(self, **query_params) -> None:
        """
        Process ground imagery data from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL ground imagery API
        """
        logger.info("Processing ground imagery data")

        try:
            # Get ground imagery data from UDL
            udl_ground_imagery = self.udl_client.get_ground_imagery(**query_params)
            logger.info(f"Retrieved {len(udl_ground_imagery)} ground imagery records from UDL")

            # Transform ground imagery data to AstroShield format
            astroshield_ground_imagery = [
                transform_ground_imagery(img) for img in udl_ground_imagery
            ]

            # Publish ground imagery data to Kafka
            self.producer.send(
                "groundimagery",
                key=None,
                value=json.dumps(astroshield_ground_imagery).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_ground_imagery)} ground imagery records to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing ground imagery data: {e}")
            raise

    def process_sky_imagery(self, **query_params) -> None:
        """
        Process sky imagery data from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL sky imagery API
        """
        logger.info("Processing sky imagery data")

        try:
            # Get sky imagery data from UDL
            udl_sky_imagery = self.udl_client.get_sky_imagery(**query_params)
            logger.info(f"Retrieved {len(udl_sky_imagery)} sky imagery records from UDL")

            # Transform sky imagery data to AstroShield format
            astroshield_sky_imagery = [
                transform_sky_imagery(img) for img in udl_sky_imagery
            ]

            # Publish sky imagery data to Kafka
            self.producer.send(
                "skyimagery",
                key=None,
                value=json.dumps(astroshield_sky_imagery).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_sky_imagery)} sky imagery records to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing sky imagery data: {e}")
            raise

    def process_video_streaming(self, **query_params) -> None:
        """
        Process video streaming data from UDL and publish to AstroShield.

        Args:
            **query_params: Query parameters for UDL video streaming API
        """
        logger.info("Processing video streaming data")

        try:
            # Get video streaming data from UDL
            udl_video_streaming = self.udl_client.get_video_streaming(**query_params)
            logger.info(f"Retrieved video streaming information from UDL")

            # Transform video streaming data to AstroShield format (might be a single object)
            if isinstance(udl_video_streaming, list):
                astroshield_video_streaming = [
                    transform_video_streaming(vs) for vs in udl_video_streaming
                ]
            else:
                astroshield_video_streaming = [transform_video_streaming(udl_video_streaming)]

            # Publish video streaming data to Kafka
            self.producer.send(
                "videostreaming",
                key=None,
                value=json.dumps(astroshield_video_streaming).encode("utf-8"),
            )
            logger.info(f"Published {len(astroshield_video_streaming)} video streaming records to Kafka")

            # Flush the producer
            self.producer.flush()

        except Exception as e:
            logger.error(f"Error processing video streaming data: {e}")
            raise

    def run_continuous_integration(
        self, interval_seconds: int = 60, max_iterations: Optional[int] = None,
        data_types: Optional[List[str]] = None
    ) -> None:
        """
        Run continuous integration between UDL and AstroShield.

        Args:
            interval_seconds: Interval between integration runs in seconds
            max_iterations: Maximum number of iterations (None for infinite)
            data_types: List of data types to process (None for all)
        """
        logger.info(
            f"Starting continuous integration with interval {interval_seconds} seconds"
        )

        # Define all available data types and their processing methods
        available_types = {
            "state_vectors": self.process_state_vectors,
            "conjunctions": self.process_conjunctions,
            "launch_events": self.process_launch_events,
            "tracks": self.process_tracks,
            "ephemeris": self.process_ephemeris,
            "maneuvers": self.process_maneuvers,
            "observations": self.process_observations,
            "sensor_data": self.process_sensor_data,
            "orbit_determinations": self.process_orbit_determinations,
            "elsets": self.process_elsets,
            "weather_data": self.process_weather_data,
            "sensor_tasking": self.process_sensor_tasking,
            "cyber_threats": self.process_cyber_threats,
            "link_status": self.process_link_status,
            "comm_data": self.process_comm_data,
            "mission_ops_data": self.process_mission_ops_data,
            "vessel_data": self.process_vessel_data,
            "aircraft_data": self.process_aircraft_data,
            "ground_imagery": self.process_ground_imagery,
            "sky_imagery": self.process_sky_imagery,
            "video_streaming": self.process_video_streaming,
        }

        # If no data types specified, use all available types
        if data_types is None:
            data_types = list(available_types.keys())
        
        # Validate data types
        for data_type in data_types.copy():
            if data_type not in available_types:
                logger.warning(f"Unknown data type: {data_type}, skipping")
                data_types.remove(data_type)
        
        if not data_types:
            logger.error("No valid data types specified")
            return

        logger.info(f"Processing data types: {', '.join(data_types)}")

        iteration = 0
        while max_iterations is None or iteration < max_iterations:
            iteration += 1
            logger.info(f"Starting integration iteration {iteration}")

            try:
                # Process each selected data type
                for data_type in data_types:
                    try:
                        logger.info(f"Processing {data_type}")
                        available_types[data_type]()
                    except Exception as e:
                        logger.error(f"Error processing {data_type}: {e}")

                logger.info(f"Completed integration iteration {iteration}")

            except Exception as e:
                logger.error(f"Error in integration iteration {iteration}: {e}")

            # Sleep until next iteration
            logger.info(f"Sleeping for {interval_seconds} seconds")
            time.sleep(interval_seconds)

    def stream_topic(self, topic_name: str, transformer_func: Callable, kafka_topic: str, start_from_latest: bool = True) -> bool:
        """
        Stream data from a UDL Secure Messaging topic to a Kafka topic.
        
        Args:
            topic_name: Name of the UDL topic to stream.
            transformer_func: Function to transform UDL messages to Kafka format.
            kafka_topic: Name of the Kafka topic to publish to.
            start_from_latest: Whether to start from the latest offset.
            
        Returns:
            True if streaming was started successfully, False otherwise.
        """
        if not self.use_secure_messaging or not self.messaging_client:
            logger.error("Secure Messaging is not enabled or client is not initialized")
            return False
            
        if not self.producer:
            logger.error("Kafka producer is not initialized")
            return False
            
        # Register transformer and publisher
        self.topic_transformers[topic_name] = transformer_func
        self.topic_publishers[topic_name] = kafka_topic
        
        # Define callback function for messages
        def message_callback(messages):
            if not messages:
                return
                
            for message in messages:
                try:
                    # Transform message
                    transformed = transformer_func(message)
                    if transformed:
                        # Publish to Kafka
                        self.producer.send(
                            kafka_topic,
                            key=transformed.get("id", "").encode("utf-8") if isinstance(transformed, dict) else None,
                            value=json.dumps(transformed).encode("utf-8"),
                        )
                except Exception as e:
                    logger.error(f"Error processing message from {topic_name}: {str(e)}")
        
        try:
            # Start consumer
            self.messaging_client.start_consumer(
                topic_name,
                message_callback,
                start_from_latest=start_from_latest,
            )
            self.active_streaming_topics.add(topic_name)
            logger.info(f"Started streaming from UDL topic {topic_name} to Kafka topic {kafka_topic}")
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logger.error(f"Access forbidden to UDL topic {topic_name}. Make sure you have proper authorization for Secure Messaging API.")
            else:
                logger.error(f"HTTP error when starting consumer for {topic_name}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error starting consumer for {topic_name}: {str(e)}")
            return False


def main():
    """Main entry point for UDL integration."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="UDL Integration")
    parser.add_argument(
        "--udl-base-url",
        type=str,
        default=os.environ.get("UDL_BASE_URL", "https://unifieddatalibrary.com"),
        help="Base URL for the UDL API",
    )
    parser.add_argument(
        "--udl-api-key",
        type=str,
        default=os.environ.get("UDL_API_KEY"),
        help="API key for UDL authentication",
    )
    parser.add_argument(
        "--udl-username",
        type=str,
        default=os.environ.get("UDL_USERNAME"),
        help="Username for UDL authentication",
    )
    parser.add_argument(
        "--udl-password",
        type=str,
        default=os.environ.get("UDL_PASSWORD"),
        help="Password for UDL authentication",
    )
    parser.add_argument(
        "--udl-timeout",
        type=int,
        default=int(os.environ.get("UDL_TIMEOUT", "30")),
        help="Timeout for UDL API requests",
    )
    parser.add_argument(
        "--udl-max-retries",
        type=int,
        default=int(os.environ.get("UDL_MAX_RETRIES", "3")),
        help="Maximum number of retries for UDL API requests",
    )
    parser.add_argument(
        "--kafka-bootstrap-servers",
        type=str,
        default=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        help="Comma-separated list of Kafka broker addresses",
    )
    parser.add_argument(
        "--kafka-security-protocol",
        type=str,
        default=os.environ.get("KAFKA_SECURITY_PROTOCOL", "SASL_SSL"),
        help="Security protocol for Kafka",
    )
    parser.add_argument(
        "--kafka-sasl-mechanism",
        type=str,
        default=os.environ.get("KAFKA_SASL_MECHANISM", "PLAIN"),
        help="SASL mechanism for Kafka",
    )
    parser.add_argument(
        "--kafka-sasl-username",
        type=str,
        default=os.environ.get("KAFKA_SASL_USERNAME"),
        help="SASL username for Kafka",
    )
    parser.add_argument(
        "--kafka-sasl-password",
        type=str,
        default=os.environ.get("KAFKA_SASL_PASSWORD"),
        help="SASL password for Kafka",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=int(os.environ.get("UDL_INTEGRATION_INTERVAL", "60")),
        help="Interval between integration runs in seconds",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=os.environ.get("UDL_INTEGRATION_MAX_ITERATIONS"),
        help="Maximum number of iterations (None for infinite)",
    )
    parser.add_argument(
        "--data-types",
        type=str,
        nargs="*",
        default=os.environ.get("UDL_INTEGRATION_DATA_TYPES", "").split(",") if os.environ.get("UDL_INTEGRATION_DATA_TYPES") else None,
        help="List of data types to process (None for all). Available types: state_vectors, conjunctions, launch_events, tracks, ephemeris, maneuvers, observations, sensor_data, orbit_determinations, elsets, weather_data, sensor_tasking, cyber_threats, link_status, comm_data, mission_ops_data, vessel_data, aircraft_data, ground_imagery, sky_imagery, video_streaming",
    )
    parser.add_argument(
        "--one-shot",
        action="store_true",
        help="Run a single integration and exit",
    )
    # Add new arguments for Secure Messaging functionality
    parser.add_argument(
        "--use-secure-messaging",
        action="store_true",
        default=os.environ.get("UDL_USE_SECURE_MESSAGING", "").lower() == "true",
        help="Use UDL Secure Messaging API for real-time data streaming",
    )
    parser.add_argument(
        "--sample-period",
        type=float,
        default=float(os.environ.get("UDL_SAMPLE_PERIOD", "0.34")),
        help="Sample period for UDL Secure Messaging in seconds (default: 0.34)",
    )
    parser.add_argument(
        "--streaming-topics",
        type=str,
        default=os.environ.get("UDL_STREAMING_TOPICS", ""),
        help="Comma-separated list of topics to stream from (requires --use-secure-messaging)",
    )

    args = parser.parse_args()

    # Initialize UDL integration
    integration = UDLIntegration(
        udl_base_url=args.udl_base_url,
        udl_api_key=args.udl_api_key,
        udl_username=args.udl_username,
        udl_password=args.udl_password,
        udl_timeout=args.udl_timeout,
        udl_max_retries=args.udl_max_retries,
        kafka_bootstrap_servers=args.kafka_bootstrap_servers,
        kafka_security_protocol=args.kafka_security_protocol,
        kafka_sasl_mechanism=args.kafka_sasl_mechanism,
        kafka_sasl_username=args.kafka_sasl_username,
        kafka_sasl_password=args.kafka_sasl_password,
        use_secure_messaging=args.use_secure_messaging,
        sample_period=args.sample_period,
    )

    try:
        # Handle Secure Messaging mode if enabled
        if args.use_secure_messaging and args.streaming_topics:
            streaming_topics = [topic.strip() for topic in args.streaming_topics.split(",") if topic.strip()]
            
            if not streaming_topics:
                logger.error("Secure Messaging enabled but no valid streaming topics specified.")
                return 1
                
            # Validate topics
            valid_topics = []
            for topic in streaming_topics:
                if topic in integration.topic_transformers:
                    valid_topics.append(topic)
                else:
                    logger.warning(f"Ignoring unsupported topic: {topic}")
            
            if not valid_topics:
                logger.error("No valid streaming topics specified.")
                return 1
                
            # Start streaming from valid topics
            logger.info(f"Starting secure messaging streams for topics: {', '.join(valid_topics)}")
            
            # Use the stream_topic method to start all streams at once
            results = {}
            for topic in valid_topics:
                results[topic] = integration.stream_topic(topic, integration.topic_transformers[topic], integration.topic_publishers[topic])
            
            # Log the results
            for topic, success in results.items():
                if success:
                    logger.info(f"Successfully started streaming from topic: {topic}")
                else:
                    logger.error(f"Failed to start streaming from topic: {topic}")
            
            # Keep running until interrupted
            try:
                logger.info("Streams started. Press Ctrl+C to stop.")
                # Use a loop to keep the main thread alive
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Stopping all streams...")
                for topic in valid_topics:
                    integration.messaging_client.stop_consumer(topic)
                logger.info("All streams stopped.")
            
            return 0
            
        # Regular polling mode (one-shot or continuous)
        if args.one_shot:
            # Process each selected data type once
            available_types = {
                "state_vectors": integration.process_state_vectors,
                "conjunctions": integration.process_conjunctions,
                "launch_events": integration.process_launch_events,
                "tracks": integration.process_tracks,
                "ephemeris": integration.process_ephemeris,
                "maneuvers": integration.process_maneuvers,
                "observations": integration.process_observations,
                "sensor_data": integration.process_sensor_data,
                "orbit_determinations": integration.process_orbit_determinations,
                "elsets": integration.process_elsets,
                "weather_data": integration.process_weather_data,
                "sensor_tasking": integration.process_sensor_tasking,
                "cyber_threats": integration.process_cyber_threats,
                "link_status": integration.process_link_status,
                "comm_data": integration.process_comm_data,
                "mission_ops_data": integration.process_mission_ops_data,
                "vessel_data": integration.process_vessel_data,
                "aircraft_data": integration.process_aircraft_data,
                "ground_imagery": integration.process_ground_imagery,
                "sky_imagery": integration.process_sky_imagery,
                "video_streaming": integration.process_video_streaming,
            }
            
            data_types = args.data_types if args.data_types else list(available_types.keys())
            
            # Validate data types
            for data_type in data_types.copy():
                if data_type not in available_types:
                    logger.warning(f"Unknown data type: {data_type}, skipping")
                    data_types.remove(data_type)
            
            if not data_types:
                logger.error("No valid data types specified")
                return 1
                
            logger.info(f"Processing data types: {', '.join(data_types)}")
            
            for data_type in data_types:
                try:
                    logger.info(f"Processing {data_type}")
                    available_types[data_type]()
                except Exception as e:
                    logger.error(f"Error processing {data_type}: {e}")
        else:
            # Run continuous integration
            integration.run_continuous_integration(
                interval_seconds=args.interval,
                max_iterations=args.max_iterations,
                data_types=args.data_types,
            )
    except KeyboardInterrupt:
        logger.info("Integration stopped by user")
    except Exception as e:
        logger.error(f"Error in UDL integration: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main()) 