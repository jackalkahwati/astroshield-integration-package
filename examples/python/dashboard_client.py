#!/usr/bin/env python3
"""
AstroShield Enhanced Dashboard API Client Example

This example demonstrates how to integrate with AstroShield's comprehensive
dashboard API endpoints to retrieve system metrics, feature rollups, and
real-time status information.

New Endpoints:
- /api/v1/dashboard/stats - Comprehensive dashboard statistics
- /health - System health check
- /api/v1/satellites - Satellite tracking data
- /api/v1/events - Recent system events
- /api/v1/kafka/topics - Kafka topic information
- /api/v1/kafka/publish - Publish messages to Kafka

Requirements:
    pip install requests python-dateutil

Usage:
    python dashboard_client.py

Environment Variables:
    ASTROSHIELD_API_URL - Base URL for AstroShield API (default: http://localhost:8000)
    ASTROSHIELD_API_KEY - API key for authentication (optional)
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class DashboardMetrics:
    """Data class for dashboard metrics"""
    system_health: str
    active_tracks: int
    critical_alerts: int
    response_time: str
    feature_rollup: Dict[str, Any]
    recent_activities: List[Dict[str, Any]]
    system_status: Dict[str, Any]
    timestamp: str


class AstroShieldDashboardClient:
    """
    Enhanced client for AstroShield Dashboard API
    
    Provides methods to interact with the comprehensive dashboard
    endpoints and retrieve real-time system metrics.
    """
    
    def __init__(self, base_url: str = None, api_key: str = None, timeout: int = 30):
        """
        Initialize the dashboard client
        
        Args:
            base_url: Base URL for AstroShield API
            api_key: API key for authentication (optional)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or os.getenv('ASTROSHIELD_API_URL', 'http://localhost:8000')
        self.api_key = api_key or os.getenv('ASTROSHIELD_API_KEY')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set up authentication if API key is provided
        if self.api_key:
            self.session.headers.update({'X-API-Key': self.api_key})
        
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AstroShield-Dashboard-Client/1.0'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check system health status
        
        Returns:
            Health status information
        """
        response = self._make_request('GET', '/health')
        return response.json()
    
    def get_dashboard_stats(self) -> DashboardMetrics:
        """
        Get comprehensive dashboard statistics
        
        Returns:
            Complete dashboard metrics including all feature rollups
        """
        response = self._make_request('GET', '/api/v1/dashboard/stats')
        data = response.json()
        
        return DashboardMetrics(
            system_health=data['system_metrics']['system_health'],
            active_tracks=data['system_metrics']['active_tracks'],
            critical_alerts=data['system_metrics']['critical_alerts'],
            response_time=data['system_metrics']['response_time'],
            feature_rollup=data['feature_rollup'],
            recent_activities=data['recent_activities'],
            system_status=data['system_status'],
            timestamp=data['timestamp']
        )
    
    def get_satellites(self) -> Dict[str, Any]:
        """
        Get satellite tracking data
        
        Returns:
            Satellite tracking information
        """
        response = self._make_request('GET', '/api/v1/satellites')
        return response.json()
    
    def get_events(self) -> Dict[str, Any]:
        """
        Get recent system events
        
        Returns:
            Recent events and activities
        """
        response = self._make_request('GET', '/api/v1/events')
        return response.json()
    
    def get_kafka_topics(self) -> Dict[str, Any]:
        """
        Get Kafka topic information
        
        Returns:
            Kafka topics, message counts, and partitions
        """
        response = self._make_request('GET', '/api/v1/kafka/topics')
        return response.json()
    
    def publish_kafka_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish a message to Kafka
        
        Args:
            message: Message payload to publish
            
        Returns:
            Publishing confirmation with message ID and offset
        """
        response = self._make_request('POST', '/api/v1/kafka/publish', json=message)
        return response.json()
    
    def get_feature_status(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """
        Get status for a specific feature
        
        Args:
            feature_name: Name of the feature (e.g., 'satellite_tracking', 'ccdm_analysis')
            
        Returns:
            Feature-specific metrics or None if not found
        """
        dashboard_stats = self.get_dashboard_stats()
        return dashboard_stats.feature_rollup.get(feature_name)
    
    def monitor_system(self, interval: int = 30, duration: int = 300):
        """
        Monitor system metrics continuously
        
        Args:
            interval: Monitoring interval in seconds
            duration: Total monitoring duration in seconds
        """
        print(f"🚀 Starting AstroShield system monitoring...")
        print(f"📊 Interval: {interval}s, Duration: {duration}s")
        print("-" * 80)
        
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                # Get current metrics
                metrics = self.get_dashboard_stats()
                
                # Display key metrics
                print(f"⏰ {datetime.now().strftime('%H:%M:%S')} | "
                      f"Health: {metrics.system_health} | "
                      f"Tracks: {metrics.active_tracks} | "
                      f"Alerts: {metrics.critical_alerts} | "
                      f"Response: {metrics.response_time}")
                
                # Check for critical alerts
                if metrics.critical_alerts > 0:
                    print(f"🚨 CRITICAL: {metrics.critical_alerts} alerts detected!")
                
                # Wait for next interval
                time.sleep(interval)
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(interval)
        
        print("✅ Monitoring completed")


def print_dashboard_summary(metrics: DashboardMetrics):
    """Print a formatted dashboard summary"""
    print("\n" + "="*80)
    print("🚀 ASTROSHIELD DASHBOARD SUMMARY")
    print("="*80)
    
    # System Overview
    print(f"\n📊 SYSTEM METRICS")
    print(f"   Health: {metrics.system_health}")
    print(f"   Active Tracks: {metrics.active_tracks}")
    print(f"   Critical Alerts: {metrics.critical_alerts}")
    print(f"   Response Time: {metrics.response_time}")
    print(f"   Overall Status: {metrics.system_status['overall']}")
    
    # Feature Rollup
    print(f"\n🛰️ FEATURE STATUS")
    features = [
        ('Satellite Tracking', 'satellite_tracking'),
        ('CCDM Analysis', 'ccdm_analysis'),
        ('Maneuvers', 'maneuvers'),
        ('Analytics', 'analytics'),
        ('Proximity Ops', 'proximity_operations'),
        ('Event Correlation', 'event_correlation'),
        ('Kafka Monitor', 'kafka_monitor'),
        ('Protection', 'protection')
    ]
    
    for display_name, key in features:
        if key in metrics.feature_rollup:
            feature_data = metrics.feature_rollup[key]
            # Extract a key metric for each feature
            if key == 'satellite_tracking':
                value = f"{feature_data['operational']}/{feature_data['total_satellites']} operational"
            elif key == 'ccdm_analysis':
                value = f"{feature_data['health_percentage']}% health"
            elif key == 'maneuvers':
                value = f"{feature_data['scheduled']} scheduled"
            elif key == 'analytics':
                value = f"{feature_data['accuracy_score']}% accuracy"
            elif key == 'proximity_operations':
                value = f"{feature_data['active_conjunctions']} conjunctions"
            elif key == 'event_correlation':
                value = f"{feature_data['correlations_found']} correlations"
            elif key == 'kafka_monitor':
                value = f"{feature_data['topics_active']} topics active"
            elif key == 'protection':
                value = f"{feature_data['threats_blocked']} threats blocked"
            else:
                value = "Active"
            
            print(f"   {display_name:20}: {value}")
    
    # Recent Activities
    print(f"\n📋 RECENT ACTIVITIES")
    for activity in metrics.recent_activities[:3]:  # Show last 3 activities
        timestamp = datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00'))
        print(f"   {timestamp.strftime('%H:%M:%S')} | {activity['type']:20} | {activity['message']}")
    
    print(f"\n⏰ Last Updated: {metrics.timestamp}")
    print("="*80)


def main():
    """Example usage of the dashboard client"""
    print("🚀 AstroShield Enhanced Dashboard Client")
    print("========================================\n")
    
    # Initialize client
    client = AstroShieldDashboardClient()
    
    try:
        # 1. Health Check
        print("1. 🔍 Checking system health...")
        health = client.health_check()
        print(f"   Status: {health.get('status', 'unknown')}")
        print(f"   Service: {health.get('service', 'unknown')}")
        
        # 2. Dashboard Statistics
        print("\n2. 📊 Retrieving dashboard statistics...")
        metrics = client.get_dashboard_stats()
        print_dashboard_summary(metrics)
        
        # 3. Satellite Data
        print("\n3. 🛰️ Getting satellite data...")
        satellites = client.get_satellites()
        print(f"   Total satellites: {satellites.get('count', 0)}")
        
        # 4. Recent Events
        print("\n4. 📅 Getting recent events...")
        events = client.get_events()
        print(f"   Recent events: {events.get('count', 0)}")
        
        # 5. Kafka Topics
        print("\n5. 📨 Getting Kafka topics...")
        kafka_info = client.get_kafka_topics()
        print(f"   Active topics: {kafka_info.get('total_topics', 0)}")
        
        # 6. Feature-specific status
        print("\n6. 🎯 Checking specific features...")
        ccdm_status = client.get_feature_status('ccdm_analysis')
        if ccdm_status:
            print(f"   CCDM Health: {ccdm_status.get('health_percentage', 0)}%")
        
        # 7. Test Kafka publishing
        print("\n7. 📤 Testing Kafka message publishing...")
        test_message = {
            "type": "test_message",
            "satellite_id": "TEST-001",
            "details": "Dashboard client integration test"
        }
        publish_result = client.publish_kafka_message(test_message)
        print(f"   Message published: {publish_result.get('message_id', 'unknown')}")
        
        print(f"\n✅ Dashboard integration test completed successfully!")
        
        # Optional: Start monitoring
        monitor = input("\n🔄 Start continuous monitoring? (y/N): ").lower().strip()
        if monitor == 'y':
            try:
                client.monitor_system(interval=10, duration=60)  # Monitor for 1 minute
            except KeyboardInterrupt:
                print("\n⏹️ Monitoring stopped by user")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()