"""
Kafka Producer for UDL Integration

This module provides a Kafka producer for publishing transformed UDL data to AstroShield Kafka topics.
"""

import json
import logging
from typing import Dict, Any, Optional, List

from confluent_kafka import Producer

logger = logging.getLogger(__name__)


class AstroShieldKafkaProducer:
    """Kafka producer for publishing transformed UDL data to AstroShield Kafka topics."""

    def __init__(
        self,
        bootstrap_servers: str,
        client_id: str = "udl-integration",
        security_protocol: str = "SASL_SSL",
        sasl_mechanism: str = "PLAIN",
        sasl_username: Optional[str] = None,
        sasl_password: Optional[str] = None,
        ssl_ca_location: Optional[str] = None,
        **additional_config
    ):
        """
        Initialize the Kafka producer.

        Args:
            bootstrap_servers: Comma-separated list of Kafka broker addresses
            client_id: Client ID for the producer
            security_protocol: Security protocol (PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL)
            sasl_mechanism: SASL mechanism (PLAIN, SCRAM-SHA-256, SCRAM-SHA-512)
            sasl_username: SASL username
            sasl_password: SASL password
            ssl_ca_location: Path to CA certificate file
            **additional_config: Additional configuration parameters for the producer
        """
        config = {
            "bootstrap.servers": bootstrap_servers,
            "client.id": client_id,
        }

        # Add security configuration if provided
        if security_protocol:
            config["security.protocol"] = security_protocol

        if sasl_mechanism and sasl_username and sasl_password:
            config["sasl.mechanism"] = sasl_mechanism
            config["sasl.username"] = sasl_username
            config["sasl.password"] = sasl_password

        if ssl_ca_location:
            config["ssl.ca.location"] = ssl_ca_location

        # Add additional configuration
        config.update(additional_config)

        self.producer = Producer(config)
        logger.info(f"Initialized Kafka producer with client ID {client_id}")

    def _delivery_callback(self, err, msg):
        """
        Callback function for message delivery reports.

        Args:
            err: Error (if any)
            msg: Message that was delivered
        """
        if err:
            logger.error(f"Message delivery failed: {err}")
        else:
            topic = msg.topic()
            partition = msg.partition()
            offset = msg.offset()
            key = msg.key().decode("utf-8") if msg.key() else None
            logger.debug(
                f"Message delivered to {topic} [{partition}] at offset {offset} with key {key}"
            )

    def publish_message(
        self, topic: str, message: Dict[str, Any], key: Optional[str] = None
    ) -> None:
        """
        Publish a message to a Kafka topic.

        Args:
            topic: Kafka topic
            message: Message to publish
            key: Message key (optional)
        """
        try:
            # Convert message to JSON
            value = json.dumps(message).encode("utf-8")
            
            # Use message ID as key if not provided
            if key is None and "header" in message and "messageId" in message["header"]:
                key = message["header"]["messageId"]
            
            # Encode key if provided
            key_bytes = key.encode("utf-8") if key else None
            
            # Produce message
            self.producer.produce(
                topic=topic, key=key_bytes, value=value, callback=self._delivery_callback
            )
            
            # Poll to handle delivery reports
            self.producer.poll(0)
            
            logger.info(f"Published message to topic {topic} with key {key}")
        except Exception as e:
            logger.error(f"Error publishing message to topic {topic}: {e}")
            raise

    def publish_state_vectors(self, state_vectors: List[Dict[str, Any]]) -> None:
        """
        Publish state vectors to the AstroShield state vector topic.

        Args:
            state_vectors: List of state vectors in AstroShield format
        """
        for state_vector in state_vectors:
            self.publish_message(
                topic="ss2.data.state-vector",
                message=state_vector,
                key=state_vector.get("header", {}).get("messageId")
            )

    def publish_conjunctions(self, conjunctions: List[Dict[str, Any]]) -> None:
        """
        Publish conjunctions to the AstroShield conjunction events topic.

        Args:
            conjunctions: List of conjunctions in AstroShield format
        """
        for conjunction in conjunctions:
            self.publish_message(
                topic="ss5.conjunction.events",
                message=conjunction,
                key=conjunction.get("header", {}).get("messageId")
            )

    def publish_launch_events(self, launch_events: List[Dict[str, Any]]) -> None:
        """
        Publish launch events to the AstroShield launch detection topic.

        Args:
            launch_events: List of launch events in AstroShield format
        """
        for launch_event in launch_events:
            self.publish_message(
                topic="ss0.launch.detection",
                message=launch_event,
                key=launch_event.get("header", {}).get("messageId")
            )

    def publish_tracks(self, tracks: List[Dict[str, Any]]) -> None:
        """
        Publish tracks to the AstroShield track detection topic.

        Args:
            tracks: List of tracks in AstroShield format
        """
        for track in tracks:
            self.publish_message(
                topic="ss1.track.detection",
                message=track,
                key=track.get("header", {}).get("messageId")
            )

    def publish_ephemeris(self, ephemeris_list: List[Dict[str, Any]]) -> None:
        """
        Publish ephemeris data to the AstroShield ephemeris topic.

        Args:
            ephemeris_list: List of ephemeris data in AstroShield format
        """
        for ephemeris in ephemeris_list:
            self.publish_message(
                topic="ss2.ephemeris",
                message=ephemeris,
                key=ephemeris.get("header", {}).get("messageId")
            )

    def publish_maneuvers(self, maneuvers: List[Dict[str, Any]]) -> None:
        """
        Publish maneuvers to the AstroShield maneuver detection topic.

        Args:
            maneuvers: List of maneuvers in AstroShield format
        """
        for maneuver in maneuvers:
            self.publish_message(
                topic="ss2.maneuver.detection",
                message=maneuver,
                key=maneuver.get("header", {}).get("messageId")
            )

    def publish_observations(self, observations: List[Dict[str, Any]]) -> None:
        """
        Publish observations to the AstroShield observation topic.

        Args:
            observations: List of observations in AstroShield format
        """
        for observation in observations:
            self.publish_message(
                topic="ss0.observation",
                message=observation,
                key=observation.get("header", {}).get("messageId")
            )

    def publish_sensor_data(self, sensor_data_list: List[Dict[str, Any]]) -> None:
        """
        Publish sensor data to the AstroShield sensor info topic.

        Args:
            sensor_data_list: List of sensor data in AstroShield format
        """
        for sensor_data in sensor_data_list:
            self.publish_message(
                topic="ss0.sensor.info",
                message=sensor_data,
                key=sensor_data.get("header", {}).get("messageId")
            )

    def publish_orbit_determinations(self, orbit_determinations: List[Dict[str, Any]]) -> None:
        """
        Publish orbit determinations to the AstroShield orbit determination topic.

        Args:
            orbit_determinations: List of orbit determinations in AstroShield format
        """
        for orbit_determination in orbit_determinations:
            self.publish_message(
                topic="ss2.orbit.determination",
                message=orbit_determination,
                key=orbit_determination.get("header", {}).get("messageId")
            )

    def publish_elsets(self, elsets: List[Dict[str, Any]]) -> None:
        """
        Publish ELSETs to the AstroShield ELSET topic.

        Args:
            elsets: List of ELSETs in AstroShield format
        """
        for elset in elsets:
            self.publish_message(
                topic="ss2.elset",
                message=elset,
                key=elset.get("header", {}).get("messageId")
            )

    def publish_weather_data(self, weather_data_list: List[Dict[str, Any]]) -> None:
        """
        Publish weather data to the AstroShield weather topic.

        Args:
            weather_data_list: List of weather data in AstroShield format
        """
        for weather_data in weather_data_list:
            self.publish_message(
                topic="ss0.weather",
                message=weather_data,
                key=weather_data.get("header", {}).get("messageId")
            )

    def publish_sensor_tasking(self, sensor_tasking_list: List[Dict[str, Any]]) -> None:
        """
        Publish sensor tasking to the AstroShield sensor tasking topic.

        Args:
            sensor_tasking_list: List of sensor tasking in AstroShield format
        """
        for sensor_tasking in sensor_tasking_list:
            self.publish_message(
                topic="ss0.sensor.tasking",
                message=sensor_tasking,
                key=sensor_tasking.get("header", {}).get("messageId")
            )

    def publish_site_data(self, site_data_list: List[Dict[str, Any]]) -> None:
        """
        Publish site data to the AstroShield site info topic.

        Args:
            site_data_list: List of site data in AstroShield format
        """
        for site_data in site_data_list:
            self.publish_message(
                topic="ss0.site.info",
                message=site_data,
                key=site_data.get("header", {}).get("messageId")
            )

    def publish_rf_data(self, rf_data_list: List[Dict[str, Any]]) -> None:
        """
        Publish RF data to the AstroShield RF detection topic.

        Args:
            rf_data_list: List of RF data in AstroShield format
        """
        for rf_data in rf_data_list:
            self.publish_message(
                topic="ss0.rf.detection",
                message=rf_data,
                key=rf_data.get("header", {}).get("messageId")
            )

    def publish_earth_orientation_parameters(self, eop_list: List[Dict[str, Any]]) -> None:
        """
        Publish Earth orientation parameters to the AstroShield EOP topic.

        Args:
            eop_list: List of Earth orientation parameters in AstroShield format
        """
        for eop in eop_list:
            self.publish_message(
                topic="ss0.earth.orientation",
                message=eop,
                key=eop.get("header", {}).get("messageId")
            )

    def publish_solar_geomagnetic_data(self, sol_geo_list: List[Dict[str, Any]]) -> None:
        """
        Publish solar and geomagnetic data to the AstroShield solar activity topic.

        Args:
            sol_geo_list: List of solar and geomagnetic data in AstroShield format
        """
        for sol_geo in sol_geo_list:
            self.publish_message(
                topic="ss0.solar.activity",
                message=sol_geo,
                key=sol_geo.get("header", {}).get("messageId")
            )

    def publish_star_catalog(self, star_catalog_list: List[Dict[str, Any]]) -> None:
        """
        Publish star catalog to the AstroShield star catalog topic.

        Args:
            star_catalog_list: List of star catalog entries in AstroShield format
        """
        for star_catalog in star_catalog_list:
            self.publish_message(
                topic="ss0.star.catalog",
                message=star_catalog,
                key=star_catalog.get("header", {}).get("messageId")
            )

    def publish_cyber_threats(self, cyber_threats: List[Dict[str, Any]]) -> None:
        """
        Publish cyber threats to the AstroShield cyber threat topic.

        Args:
            cyber_threats: List of cyber threats in AstroShield format
        """
        for cyber_threat in cyber_threats:
            self.publish_message(
                topic="ss0.cyber.threat",
                message=cyber_threat,
                key=cyber_threat.get("header", {}).get("messageId")
            )

    def publish_link_status(self, link_status_list: List[Dict[str, Any]]) -> None:
        """
        Publish link status to the AstroShield link status topic.

        Args:
            link_status_list: List of link status records in AstroShield format
        """
        for link_status in link_status_list:
            self.publish_message(
                topic="ss0.link.status",
                message=link_status,
                key=link_status.get("header", {}).get("messageId")
            )

    def publish_comm_data(self, comm_data_list: List[Dict[str, Any]]) -> None:
        """
        Publish communications data to the AstroShield communications topic.

        Args:
            comm_data_list: List of communications data in AstroShield format
        """
        for comm_data in comm_data_list:
            self.publish_message(
                topic="ss0.comm.data",
                message=comm_data,
                key=comm_data.get("header", {}).get("messageId")
            )

    def publish_mission_ops_data(self, mission_ops_list: List[Dict[str, Any]]) -> None:
        """
        Publish mission operations data to the AstroShield mission ops topic.

        Args:
            mission_ops_list: List of mission operations data in AstroShield format
        """
        for mission_ops in mission_ops_list:
            self.publish_message(
                topic="ss0.mission.ops",
                message=mission_ops,
                key=mission_ops.get("header", {}).get("messageId")
            )

    def publish_vessel_data(self, vessel_data_list: List[Dict[str, Any]]) -> None:
        """
        Publish vessel tracking data to the AstroShield vessel topic.

        Args:
            vessel_data_list: List of vessel tracking data in AstroShield format
        """
        for vessel_data in vessel_data_list:
            self.publish_message(
                topic="ss0.vessel",
                message=vessel_data,
                key=vessel_data.get("header", {}).get("messageId")
            )

    def publish_aircraft_data(self, aircraft_data_list: List[Dict[str, Any]]) -> None:
        """
        Publish aircraft tracking data to the AstroShield aircraft topic.

        Args:
            aircraft_data_list: List of aircraft tracking data in AstroShield format
        """
        for aircraft_data in aircraft_data_list:
            self.publish_message(
                topic="ss0.aircraft",
                message=aircraft_data,
                key=aircraft_data.get("header", {}).get("messageId")
            )

    def publish_ground_imagery(self, ground_imagery_list: List[Dict[str, Any]]) -> None:
        """
        Publish ground imagery data to the AstroShield ground imagery topic.

        Args:
            ground_imagery_list: List of ground imagery data in AstroShield format
        """
        for ground_imagery in ground_imagery_list:
            self.publish_message(
                topic="ss0.ground.imagery",
                message=ground_imagery,
                key=ground_imagery.get("header", {}).get("messageId")
            )

    def publish_sky_imagery(self, sky_imagery_list: List[Dict[str, Any]]) -> None:
        """
        Publish sky imagery data to the AstroShield sky imagery topic.

        Args:
            sky_imagery_list: List of sky imagery data in AstroShield format
        """
        for sky_imagery in sky_imagery_list:
            self.publish_message(
                topic="ss0.sky.imagery",
                message=sky_imagery,
                key=sky_imagery.get("header", {}).get("messageId")
            )

    def publish_video_streaming(self, video_streaming_list: List[Dict[str, Any]]) -> None:
        """
        Publish video streaming data to the AstroShield video streaming topic.

        Args:
            video_streaming_list: List of video streaming data in AstroShield format
        """
        for video_streaming in video_streaming_list:
            self.publish_message(
                topic="ss0.video.streaming",
                message=video_streaming,
                key=video_streaming.get("header", {}).get("messageId")
            )

    def flush(self, timeout: float = 10.0) -> None:
        """
        Flush the producer to ensure all messages are delivered.

        Args:
            timeout: Maximum time to block in seconds
        """
        remaining = self.producer.flush(timeout)
        if remaining > 0:
            logger.warning(f"{remaining} messages remain in the queue after flush")
        else:
            logger.info("All messages flushed successfully") 