"""
UDL Secure Messaging Client

This module provides a client for interacting with the Unified Data Library (UDL) Secure Messaging API.
"""

import json
import logging
import os
import time
import datetime
import dateutil.parser
from typing import Dict, List, Optional, Union, Any, Tuple
from threading import Thread, Event

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class UDLMessagingClient:
    """Client for interacting with the Unified Data Library (UDL) Secure Messaging API."""

    def __init__(
        self,
        base_url: str = "https://unifieddatalibrary.com",
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        sample_period: float = 0.34,  # Based on UDL rate limiting (3 requests per second)
    ):
        """
        Initialize the UDL Secure Messaging client.

        Args:
            base_url: The base URL for the UDL API.
            username: Username for authentication.
            password: Password for authentication.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
            sample_period: Minimum time between requests (seconds) to respect rate limits.
        """
        self.base_url = base_url
        self.username = username or os.environ.get("UDL_USERNAME")
        self.password = password or os.environ.get("UDL_PASSWORD")
        self.timeout = timeout
        self.sample_period = max(0.34, sample_period)  # Ensure not below minimum allowed
        self.topic_offsets = {}  # Track latest offset for each topic
        self._stop_event = Event()
        self._consumers = {}  # Track active consumer threads

        # Set up session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set authentication
        if not self.username or not self.password:
            raise ValueError("Username and password are required for Secure Messaging API")
        self.session.auth = (self.username, self.password)

    def list_topics(self) -> List[Dict[str, Any]]:
        """
        List available UDL Secure Messaging topics.
        
        Returns:
            List of topic information dictionaries.
        """
        url = f"{self.base_url}/sm/listTopics"
        response = self.session.get(url, timeout=self.timeout, verify=True)
        response.raise_for_status()
        return response.json()

    def describe_topic(self, topic: str, partition: int = 0) -> Dict[str, Any]:
        """
        Get detailed information about a specific topic.
        
        Args:
            topic: Name of the topic to describe.
            partition: Topic partition (default: 0).
            
        Returns:
            Dictionary with topic details.
        """
        url = f"{self.base_url}/sm/describeTopic/{topic}/{partition}"
        response = self.session.get(url, timeout=self.timeout, verify=True)
        response.raise_for_status()
        return response.json()

    def get_latest_offset(self, topic: str, partition: int = 0) -> int:
        """
        Get the latest offset for a topic.
        
        Args:
            topic: Name of the topic.
            partition: Topic partition (default: 0).
            
        Returns:
            Latest offset as an integer.
        """
        url = f"{self.base_url}/sm/getLatestOffset/{topic}/{partition}"
        response = self.session.get(url, timeout=self.timeout, verify=True)
        response.raise_for_status()
        return int(response.text)

    def get_messages(
        self, 
        topic: str, 
        offset: int = -1, 
        partition: int = 0,
        query_params: Optional[Dict[str, str]] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get messages from a topic starting at a specific offset.
        
        Args:
            topic: Name of the topic.
            offset: Starting offset (-1 for latest).
            partition: Topic partition (default: 0).
            query_params: Optional query parameters to filter results.
            
        Returns:
            Tuple of (list of messages, next offset)
        """
        url = f"{self.base_url}/sm/getMessages/{topic}/{partition}/{offset}"
        
        if query_params:
            params = query_params
        else:
            params = {}
            
        response = self.session.get(url, params=params, timeout=self.timeout, verify=True)
        
        if response.status_code != 200:
            if "KAFKA_ERROR" in response.headers and response.headers["KAFKA_ERROR"] == "true":
                logger.error(f"Kafka error when fetching messages: {response.text}")
            response.raise_for_status()
            
        # Get the next offset from response headers
        next_offset = response.headers.get("KAFKA_NEXT_OFFSET", offset)
        if next_offset is not None:
            next_offset = int(next_offset)
        
        # Parse response body as JSON
        messages = response.json()
        
        return messages, next_offset

    def start_consumer(
        self, 
        topic: str, 
        callback_fn, 
        partition: int = 0, 
        start_from_latest: bool = True,
        query_params: Optional[Dict[str, str]] = None,
        process_historical: bool = False
    ) -> None:
        """
        Start a continuous consumer for a topic.
        
        Args:
            topic: Name of the topic to consume.
            callback_fn: Function to call with received messages.
            partition: Topic partition (default: 0).
            start_from_latest: Whether to start from latest offset or beginning.
            query_params: Optional query parameters to filter results.
            process_historical: If True, process all historical data before streaming.
        """
        if f"{topic}:{partition}" in self._consumers:
            logger.warning(f"Consumer for topic {topic}:{partition} already running")
            return
            
        thread = Thread(
            target=self._consumer_thread,
            args=(topic, callback_fn, partition, start_from_latest, query_params, process_historical),
            daemon=True
        )
        self._consumers[f"{topic}:{partition}"] = thread
        thread.start()
        logger.info(f"Started consumer for {topic}:{partition}")

    def stop_consumer(self, topic: str, partition: int = 0) -> None:
        """
        Stop a specific consumer thread.
        
        Args:
            topic: Name of the topic.
            partition: Topic partition.
        """
        key = f"{topic}:{partition}"
        if key in self._consumers:
            # Consumer will check _stop_event and terminate
            logger.info(f"Stopping consumer for {topic}:{partition}")
            # Remove from active consumers
            del self._consumers[key]
        else:
            logger.warning(f"No active consumer found for {topic}:{partition}")

    def stop_all_consumers(self) -> None:
        """Stop all active consumer threads."""
        self._stop_event.set()
        # Wait a bit for threads to terminate
        time.sleep(0.5)
        # Clear consumer registry
        self._consumers.clear()
        # Reset stop event for future use
        self._stop_event.clear()
        logger.info("All consumers stopped")

    def _consumer_thread(
        self, 
        topic: str, 
        callback_fn, 
        partition: int,
        start_from_latest: bool,
        query_params: Optional[Dict[str, str]],
        process_historical: bool
    ) -> None:
        """
        Background thread for continuous topic consumption.
        
        Args:
            topic: Name of the topic to consume.
            callback_fn: Function to call with received messages.
            partition: Topic partition.
            start_from_latest: Whether to start from latest offset.
            query_params: Optional query parameters.
            process_historical: If True, process all historical data.
        """
        # Determine starting offset
        if start_from_latest and not process_historical:
            # Start from latest offset
            offset = -1
        else:
            # Get topic info to find earliest offset
            topic_info = self.describe_topic(topic, partition)
            offset = topic_info.get("minPos", 0) if process_historical else topic_info.get("maxPos", -1)
            
        logger.info(f"Starting consumer for {topic}:{partition} from offset {offset}")
        
        # Track the current offset
        current_offset = offset
        
        while not self._stop_event.is_set():
            try:
                # Get messages from the topic at the current offset
                start_time = time.time()
                messages, next_offset = self.get_messages(topic, current_offset, partition, query_params)
                
                # Process messages if any were received
                if messages:
                    receive_time_utc = datetime.datetime.utcnow()
                    message_count = len(messages)
                    logger.debug(f"Received {message_count} messages from {topic}:{partition}")
                    
                    # Process messages with timing information
                    for msg in messages:
                        # Add metadata about receive time for latency calculations
                        msg["_receive_time_utc"] = receive_time_utc.isoformat()
                        
                        # Calculate latency if possible (depends on topic schema)
                        if "epoch" in msg and "createdAt" in msg:
                            try:
                                v_time_collect = dateutil.parser.parse(msg["epoch"]).replace(tzinfo=None)
                                v_time_create = dateutil.parser.parse(msg["createdAt"]).replace(tzinfo=None)
                                
                                # Time between collection and creation in UDL
                                time_to_push = (v_time_create - v_time_collect).total_seconds()
                                
                                # Time from UDL creation to client receipt
                                time_to_pull = (receive_time_utc - v_time_create).total_seconds() - self.sample_period
                                
                                # Total latency
                                total_latency = (receive_time_utc - v_time_collect).total_seconds()
                                
                                # Add latency info to message
                                msg["_latency"] = {
                                    "time_to_push": time_to_push,
                                    "time_to_pull": time_to_pull,
                                    "total_latency": total_latency
                                }
                            except (ValueError, TypeError) as e:
                                logger.debug(f"Couldn't calculate latency for message: {e}")
                        
                        # Call the callback function with the enriched message
                        try:
                            callback_fn(msg)
                        except Exception as e:
                            logger.error(f"Error in callback function: {e}")
                    
                # Update offset for next iteration
                current_offset = next_offset
                
                # Check if we've reached the current end of the topic
                if str(next_offset) == str(current_offset):
                    # We've caught up, sleep for a bit before checking again
                    time.sleep(self.sample_period)
                else:
                    # Calculate time elapsed and sleep if needed to respect rate limits
                    elapsed = time.time() - start_time
                    if elapsed < self.sample_period:
                        time.sleep(self.sample_period - elapsed)
                        
            except requests.exceptions.RequestException as e:
                logger.error(f"Error getting messages from {topic}:{partition}: {e}")
                # Back off on errors
                time.sleep(min(30, self.sample_period * 5))
            except Exception as e:
                logger.error(f"Unexpected error in consumer thread for {topic}:{partition}: {e}")
                time.sleep(min(30, self.sample_period * 5))
                
        logger.info(f"Consumer thread for {topic}:{partition} terminated")

    def calculate_latency(self, message: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate latency metrics for a message if it has timestamp fields.
        
        Args:
            message: Message from UDL Secure Messaging.
            
        Returns:
            Dictionary with latency metrics (or empty if not calculable).
        """
        latency = {}
        receive_time_utc = datetime.datetime.utcnow()
        
        if "epoch" in message and "createdAt" in message:
            try:
                v_time_collect = dateutil.parser.parse(message["epoch"]).replace(tzinfo=None)
                v_time_create = dateutil.parser.parse(message["createdAt"]).replace(tzinfo=None)
                
                # Time between collection and creation in UDL
                latency["time_to_push"] = (v_time_create - v_time_collect).total_seconds()
                
                # Time from UDL creation to client receipt
                latency["time_to_pull"] = (receive_time_utc - v_time_create).total_seconds() - self.sample_period
                
                # Total latency
                latency["total_latency"] = (receive_time_utc - v_time_collect).total_seconds()
            except (ValueError, TypeError) as e:
                logger.debug(f"Couldn't calculate latency for message: {e}")
                
        return latency 