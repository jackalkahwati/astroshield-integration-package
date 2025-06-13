"""
UDL Integration Example

This script demonstrates how to use the UDL integration to retrieve data from UDL,
transform it to AstroShield format, and publish it to Kafka topics.
"""

import json
import logging
import os
import sys
from datetime import datetime

# Import and load dotenv to ensure environment variables are loaded from .env file
from dotenv import load_dotenv
load_dotenv()  # This will load variables from .env file into the environment

from asttroshield.udl_integration.client import UDLClient
from asttroshield.udl_integration.transformers import (
    transform_state_vector,
    transform_conjunction,
    transform_launch_event,
)
from asttroshield.udl_integration.integration import UDLIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def example_retrieve_and_transform():
    """Example of retrieving data from UDL and transforming it to AstroShield format."""
    # Initialize UDL client
    udl_client = UDLClient(
        base_url=os.environ.get("UDL_BASE_URL", "https://unifieddatalibrary.com"),
        api_key=os.environ.get("UDL_API_KEY"),
        username=os.environ.get("UDL_USERNAME"),
        password=os.environ.get("UDL_PASSWORD"),
    )

    # Get current time in ISO format
    current_time = datetime.utcnow().isoformat() + "Z"

    try:
        # Retrieve state vectors from UDL
        logger.info("Retrieving state vectors from UDL")
        udl_state_vectors = udl_client.get_state_vectors(epoch=current_time)
        logger.info(f"Retrieved {len(udl_state_vectors)} state vectors")

        # Transform the first state vector to AstroShield format
        if udl_state_vectors:
            astroshield_state_vector = transform_state_vector(udl_state_vectors[0])
            logger.info("Transformed state vector to AstroShield format")
            logger.info(f"State vector ID: {astroshield_state_vector['payload']['stateVectorId']}")
            logger.info(f"Object ID: {astroshield_state_vector['payload']['objectId']}")
            logger.info(f"Position: {astroshield_state_vector['payload']['position']}")
            logger.info(f"Velocity: {astroshield_state_vector['payload']['velocity']}")

            # Save the transformed state vector to a file
            with open("example_state_vector.json", "w") as f:
                json.dump(astroshield_state_vector, f, indent=2)
                logger.info("Saved transformed state vector to example_state_vector.json")
        else:
            logger.warning("No state vectors retrieved from UDL")

        # Retrieve conjunctions from UDL
        logger.info("Retrieving conjunctions from UDL")
        udl_conjunctions = udl_client.get_conjunctions()
        logger.info(f"Retrieved {len(udl_conjunctions)} conjunctions")

        # Transform the first conjunction to AstroShield format
        if udl_conjunctions:
            astroshield_conjunction = transform_conjunction(udl_conjunctions[0])
            logger.info("Transformed conjunction to AstroShield format")
            logger.info(f"Conjunction ID: {astroshield_conjunction['payload']['conjunctionId']}")
            logger.info(f"Primary object: {astroshield_conjunction['payload']['primaryObject']['objectName']}")
            logger.info(f"Secondary object: {astroshield_conjunction['payload']['secondaryObject']['objectName']}")
            logger.info(f"Miss distance: {astroshield_conjunction['payload']['missDistance']['value']} {astroshield_conjunction['payload']['missDistance']['units']}")
            logger.info(f"Risk level: {astroshield_conjunction['payload']['riskLevel']}")

            # Save the transformed conjunction to a file
            with open("example_conjunction.json", "w") as f:
                json.dump(astroshield_conjunction, f, indent=2)
                logger.info("Saved transformed conjunction to example_conjunction.json")
        else:
            logger.warning("No conjunctions retrieved from UDL")

        # Retrieve launch events from UDL
        logger.info("Retrieving launch events from UDL")
        udl_launch_events = udl_client.get_launch_events(msg_create_date=current_time)
        logger.info(f"Retrieved {len(udl_launch_events)} launch events")

        # Transform the first launch event to AstroShield format
        if udl_launch_events:
            astroshield_launch_event = transform_launch_event(udl_launch_events[0])
            logger.info("Transformed launch event to AstroShield format")
            logger.info(f"Launch event ID: {astroshield_launch_event['payload']['detectionId']}")
            logger.info(f"Launch site: {astroshield_launch_event['payload']['launchSite']['name']}, {astroshield_launch_event['payload']['launchSite']['country']}")
            logger.info(f"Launch vehicle: {astroshield_launch_event['payload']['launchVehicle']['type']}")
            logger.info(f"Launch time: {astroshield_launch_event['payload']['launchTime']['estimated']}")

            # Save the transformed launch event to a file
            with open("example_launch_event.json", "w") as f:
                json.dump(astroshield_launch_event, f, indent=2)
                logger.info("Saved transformed launch event to example_launch_event.json")
        else:
            logger.warning("No launch events retrieved from UDL")

    except Exception as e:
        logger.error(f"Error in example: {e}")
        return False

    return True


def example_integration():
    """Example of using the UDL integration to process data and publish to Kafka."""
    # Initialize UDL integration
    integration = UDLIntegration(
        udl_base_url=os.environ.get("UDL_BASE_URL", "https://unifieddatalibrary.com"),
        udl_api_key=os.environ.get("UDL_API_KEY"),
        udl_username=os.environ.get("UDL_USERNAME"),
        udl_password=os.environ.get("UDL_PASSWORD"),
        kafka_bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        kafka_sasl_username=os.environ.get("KAFKA_SASL_USERNAME"),
        kafka_sasl_password=os.environ.get("KAFKA_SASL_PASSWORD"),
    )

    try:
        # Process state vectors
        logger.info("Processing state vectors")
        integration.process_state_vectors()

        # Process conjunctions
        logger.info("Processing conjunctions")
        integration.process_conjunctions()

        # Process launch events
        logger.info("Processing launch events")
        integration.process_launch_events()

        logger.info("Integration example completed successfully")
    except Exception as e:
        logger.error(f"Error in integration example: {e}")
        return False

    return True


if __name__ == "__main__":
    # Check if required environment variables are set
    if not os.environ.get("UDL_API_KEY") and not (os.environ.get("UDL_USERNAME") and os.environ.get("UDL_PASSWORD")):
        logger.error("UDL_API_KEY or UDL_USERNAME and UDL_PASSWORD must be set")
        sys.exit(1)

    # Run the retrieve and transform example
    logger.info("Running retrieve and transform example")
    if example_retrieve_and_transform():
        logger.info("Retrieve and transform example completed successfully")
    else:
        logger.error("Retrieve and transform example failed")

    # Check if Kafka environment variables are set
    if not os.environ.get("KAFKA_BOOTSTRAP_SERVERS"):
        logger.warning("KAFKA_BOOTSTRAP_SERVERS not set, skipping integration example")
        sys.exit(0)

    # Run the integration example
    logger.info("Running integration example")
    if example_integration():
        logger.info("Integration example completed successfully")
    else:
        logger.error("Integration example failed")
        sys.exit(1) 