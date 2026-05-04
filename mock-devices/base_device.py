"""
Base Device Class for Valtronics Mock Devices

This module provides the base functionality for all mock devices in the Valtronics system.
"""

import asyncio
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import random
import paho.mqtt.client as mqtt
import requests
from pydantic import BaseModel, Field


class DeviceStatus(Enum):
    """Device status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    WARNING = "warning"
    MAINTENANCE = "maintenance"


class DeviceType(Enum):
    """Device type enumeration"""
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    MONITOR = "monitor"
    CONTROLLER = "controller"
    GATEWAY = "gateway"


@dataclass
class TelemetryData:
    """Telemetry data structure"""
    metric_name: str
    metric_value: float
    unit: str
    timestamp: datetime
    device_id: int
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DeviceConfig:
    """Device configuration structure"""
    device_id: int
    device_name: str
    device_type: DeviceType
    manufacturer: str
    model: str
    firmware_version: str
    location: str
    mqtt_topic: str
    api_endpoint: str
    telemetry_interval: int
    health_check_interval: int


class BaseDevice(ABC):
    """Base class for all mock devices"""
    
    def __init__(self, config: DeviceConfig):
        self.config = config
        self.device_id = config.device_id
        self.device_name = config.device_name
        self.device_type = config.device_type
        self.status = DeviceStatus.OFFLINE
        self.last_telemetry = None
        self.last_health_check = None
        self.error_count = 0
        self.total_telemetry_points = 0
        self.alert_count = 0
        
        # MQTT client
        self.mqtt_client = None
        self.mqtt_connected = False
        
        # Control flags
        self.running = False
        self.simulation_enabled = True
        
        # Setup logging
        self.logger = logging.getLogger(f"mock_device_{self.device_id}")
        
        # Load configuration
        self._load_config()
    
    def _load_config(self):
        """Load device configuration"""
        try:
            with open('config.json', 'r') as f:
                self.global_config = json.load(f)
        except FileNotFoundError:
            self.global_config = {
                "mqtt": {"broker_host": "localhost", "broker_port": 1883},
                "api": {"base_url": "http://localhost:8000"},
                "simulation": {"noise_level": 0.1, "failure_probability": 0.02}
            }
    
    async def start(self):
        """Start the device"""
        self.logger.info(f"Starting device {self.device_name} (ID: {self.device_id})")
        
        try:
            # Connect to MQTT
            await self._connect_mqtt()
            
            # Register device with API
            await self._register_device()
            
            # Start telemetry generation
            self.running = True
            await self._run_device_loop()
            
        except Exception as e:
            self.logger.error(f"Error starting device {self.device_id}: {e}")
            self.status = DeviceStatus.ERROR
            raise
    
    async def stop(self):
        """Stop the device"""
        self.logger.info(f"Stopping device {self.device_name} (ID: {self.device_id})")
        
        self.running = False
        
        # Disconnect MQTT
        if self.mqtt_client and self.mqtt_connected:
            self.mqtt_client.disconnect()
            self.mqtt_connected = False
        
        # Update status
        await self._update_device_status(DeviceStatus.OFFLINE)
    
    async def _connect_mqtt(self):
        """Connect to MQTT broker"""
        try:
            self.mqtt_client = mqtt.Client()
            
            # Set callbacks
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            self.mqtt_client.on_publish = self._on_mqtt_publish
            
            # Connect
            mqtt_config = self.global_config["mqtt"]
            self.mqtt_client.username_pw_set(
                mqtt_config.get("username"),
                mqtt_config.get("password")
            )
            
            self.mqtt_client.connect(
                mqtt_config["broker_host"],
                mqtt_config["broker_port"],
                mqtt_config.get("keepalive", 60)
            )
            
            self.mqtt_client.loop_start()
            
            # Wait for connection
            for _ in range(10):
                if self.mqtt_connected:
                    break
                await asyncio.sleep(0.5)
            
            if not self.mqtt_connected:
                raise Exception("Failed to connect to MQTT broker")
            
            self.status = DeviceStatus.ONLINE
            self.logger.info(f"Connected to MQTT broker")
            
        except Exception as e:
            self.logger.error(f"Error connecting to MQTT: {e}")
            raise
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.mqtt_connected = True
            self.logger.info("MQTT connected successfully")
        else:
            self.mqtt_connected = False
            self.logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.mqtt_connected = False
        self.logger.warning(f"MQTT disconnected with code {rc}")
    
    def _on_mqtt_publish(self, client, userdata, mid):
        """MQTT publish callback"""
        pass
    
    async def _register_device(self):
        """Register device with Valtronics API"""
        try:
            api_config = self.global_config["api"]
            
            device_data = {
                "name": self.device_name,
                "device_id": f"MOCK-{self.device_id:04d}",
                "device_type": self.device_type.value,
                "manufacturer": self.config.manufacturer,
                "model": self.config.model,
                "firmware_version": self.config.firmware_version,
                "location": self.config.location,
                "metadata": {
                    "mock_device": True,
                    "simulation_enabled": True,
                    "created_at": datetime.utcnow().isoformat()
                }
            }
            
            response = requests.post(
                f"{api_config['base_url']}/api/v1/devices/",
                json=device_data,
                timeout=api_config.get("timeout", 30)
            )
            
            if response.status_code in [200, 201]:
                self.logger.info(f"Device {self.device_id} registered successfully")
            else:
                self.logger.warning(f"Failed to register device: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error registering device: {e}")
    
    async def _run_device_loop(self):
        """Main device loop"""
        telemetry_task = asyncio.create_task(self._telemetry_loop())
        health_check_task = asyncio.create_task(self._health_check_loop())
        
        try:
            await asyncio.gather(telemetry_task, health_check_task)
        except asyncio.CancelledError:
            self.logger.info("Device loop cancelled")
        finally:
            telemetry_task.cancel()
            health_check_task.cancel()
    
    async def _telemetry_loop(self):
        """Generate and send telemetry data"""
        while self.running:
            try:
                # Generate telemetry data
                telemetry_data = await self.generate_telemetry()
                
                if telemetry_data:
                    # Send telemetry
                    await self._send_telemetry(telemetry_data)
                    
                    # Update counters
                    self.total_telemetry_points += 1
                    self.last_telemetry = datetime.utcnow()
                
                # Wait for next interval
                await asyncio.sleep(self.config.telemetry_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in telemetry loop: {e}")
                self.error_count += 1
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _health_check_loop(self):
        """Perform periodic health checks"""
        while self.running:
            try:
                # Perform health check
                health_status = await self.perform_health_check()
                
                # Update device status if needed
                if health_status != self.status:
                    old_status = self.status
                    self.status = health_status
                    await self._update_device_status(health_status)
                    self.logger.info(f"Device status changed: {old_status.value} -> {health_status.value}")
                
                self.last_health_check = datetime.utcnow()
                
                # Wait for next health check
                await asyncio.sleep(self.config.health_check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    @abstractmethod
    async def generate_telemetry(self) -> List[TelemetryData]:
        """Generate telemetry data - to be implemented by subclasses"""
        pass
    
    async def perform_health_check(self) -> DeviceStatus:
        """Perform device health check"""
        # Check MQTT connection
        if not self.mqtt_connected:
            return DeviceStatus.OFFLINE
        
        # Check error rate
        if self.error_count > 10:
            return DeviceStatus.ERROR
        
        # Check last telemetry
        if self.last_telemetry:
            time_since_last = datetime.utcnow() - self.last_telemetry
            if time_since_last > timedelta(minutes=5):
                return DeviceStatus.WARNING
        
        # Simulate random failures
        if self.simulation_enabled:
            failure_prob = self.global_config["simulation"]["failure_probability"]
            if random.random() < failure_prob:
                return DeviceStatus.ERROR
        
        return DeviceStatus.ONLINE
    
    async def _send_telemetry(self, telemetry_data: List[TelemetryData]):
        """Send telemetry data via MQTT"""
        if not self.mqtt_connected:
            return
        
        try:
            for data in telemetry_data:
                # Prepare MQTT message
                topic = f"valtronics/devices/{self.device_id}/telemetry/{data.metric_name}"
                
                payload = {
                    "value": data.metric_value,
                    "unit": data.unit,
                    "timestamp": data.timestamp.isoformat(),
                    "device_id": self.device_id,
                    "metadata": data.metadata or {}
                }
                
                # Publish to MQTT
                result = self.mqtt_client.publish(
                    topic,
                    json.dumps(payload),
                    qos=self.global_config["mqtt"].get("qos", 1)
                )
                
                self.logger.debug(f"Published telemetry: {data.metric_name} = {data.metric_value}")
                
        except Exception as e:
            self.logger.error(f"Error sending telemetry: {e}")
            self.error_count += 1
    
    async def _update_device_status(self, status: DeviceStatus):
        """Update device status via API"""
        try:
            api_config = self.global_config["api"]
            
            status_data = {
                "status": status.value,
                "metadata": {
                    "last_health_check": datetime.utcnow().isoformat(),
                    "error_count": self.error_count,
                    "total_telemetry_points": self.total_telemetry_points
                }
            }
            
            response = requests.patch(
                f"{api_config['base_url']}/api/v1/devices/{self.device_id}/status",
                json=status_data,
                timeout=api_config.get("timeout", 30)
            )
            
            if response.status_code != 200:
                self.logger.warning(f"Failed to update device status: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error updating device status: {e}")
    
    def add_noise(self, value: float, noise_level: float = None) -> float:
        """Add realistic noise to sensor values"""
        if noise_level is None:
            noise_level = self.global_config["simulation"]["noise_level"]
        
        noise = random.gauss(0, noise_level * abs(value))
        return max(0, value + noise)
    
    def simulate_drift(self, base_value: float, drift_rate: float = None) -> float:
        """Simulate sensor drift over time"""
        if drift_rate is None:
            drift_rate = self.global_config["simulation"]["drift_rate"]
        
        # Add small random drift
        drift = random.uniform(-drift_rate, drift_rate) * base_value
        return base_value + drift
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get device information"""
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "device_type": self.device_type.value,
            "status": self.status.value,
            "manufacturer": self.config.manufacturer,
            "model": self.config.model,
            "firmware_version": self.config.firmware_version,
            "location": self.config.location,
            "mqtt_connected": self.mqtt_connected,
            "error_count": self.error_count,
            "total_telemetry_points": self.total_telemetry_points,
            "alert_count": self.alert_count,
            "last_telemetry": self.last_telemetry.isoformat() if self.last_telemetry else None,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "running": self.running,
            "simulation_enabled": self.simulation_enabled
        }
