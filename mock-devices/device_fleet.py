"""
Device Fleet Manager

This module manages a fleet of mock devices for comprehensive testing of the Valtronics system.
It can create, start, stop, and monitor multiple devices simultaneously.
"""

import asyncio
import json
import logging
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import time

# Import device classes
from .base_device import DeviceStatus
from .environmental.temperature_sensor import TemperatureSensor
from .environmental.humidity_sensor import HumiditySensor
from .environmental.pressure_sensor import PressureSensor
from .environmental.air_quality_monitor import AirQualityMonitor
from .industrial.vibration_sensor import VibrationSensor


@dataclass
class FleetConfig:
    """Configuration for device fleet"""
    total_devices: int = 50
    device_distribution: Dict[str, int] = None
    locations: List[str] = None
    start_stagger: int = 5  # Seconds between device starts
    enable_failures: bool = True
    failure_rate: float = 0.02
    enable_anomalies: bool = True
    anomaly_rate: float = 0.05


@dataclass
class DeviceInstance:
    """Instance of a device in the fleet"""
    device_id: int
    device_type: str
    device_class: Any
    location: str
    status: str
    start_time: Optional[datetime] = None
    stop_time: Optional[datetime] = None
    error_count: int = 0
    telemetry_points: int = 0


class DeviceFleetManager:
    """Manages a fleet of mock devices"""
    
    def __init__(self, config: FleetConfig):
        self.config = config
        self.logger = logging.getLogger("device_fleet")
        
        # Device registry
        self.devices: Dict[int, DeviceInstance] = {}
        self.device_tasks: Dict[int, asyncio.Task] = {}
        
        # Fleet statistics
        self.start_time = datetime.utcnow()
        self.total_telemetry_points = 0
        self.total_errors = 0
        self.total_alerts = 0
        
        # Control flags
        self.running = False
        self.shutdown_requested = False
        
        # Default device distribution
        self.default_distribution = {
            "temperature_sensor": 15,
            "humidity_sensor": 10,
            "pressure_sensor": 8,
            "air_quality_monitor": 7,
            "vibration_sensor": 10
        }
        
        # Default locations
        self.default_locations = [
            "Server Room A", "Server Room B", "Data Center 1", "Data Center 2",
            "Office Building A", "Office Building B", "Factory Floor A", "Factory Floor B",
            "Warehouse A", "Warehouse B", "Lab A", "Lab B",
            "Outdoor Station 1", "Outdoor Station 2", "Rooftop A", "Rooftop B"
        ]
        
        # Override defaults if provided
        if config.device_distribution:
            self.default_distribution = config.device_distribution
        if config.locations:
            self.default_locations = config.locations
        
        # Device factory
        self.device_factory = {
            "temperature_sensor": self._create_temperature_sensor,
            "humidity_sensor": self._create_humidity_sensor,
            "pressure_sensor": self._create_pressure_sensor,
            "air_quality_monitor": self._create_air_quality_monitor,
            "vibration_sensor": self._create_vibration_sensor
        }
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down fleet...")
        self.shutdown_requested = True
        asyncio.create_task(self.stop_fleet())
    
    async def create_fleet(self) -> Dict[int, DeviceInstance]:
        """Create the device fleet"""
        self.logger.info(f"Creating fleet with {self.config.total_devices} devices")
        
        device_id = 1000  # Start from device ID 1000
        
        # Create devices according to distribution
        for device_type, count in self.default_distribution.items():
            for i in range(min(count, self.config.total_devices - len(self.devices))):
                if device_id >= 1000 + self.config.total_devices:
                    break
                
                # Select location
                location = self.default_locations[len(self.devices) % len(self.default_locations)]
                
                # Create device instance
                device_instance = DeviceInstance(
                    device_id=device_id,
                    device_type=device_type,
                    device_class=None,  # Will be set when device is created
                    location=location,
                    status="created"
                )
                
                self.devices[device_id] = device_instance
                device_id += 1
        
        self.logger.info(f"Created {len(self.devices)} devices")
        return self.devices
    
    async def start_fleet(self):
        """Start all devices in the fleet"""
        self.logger.info("Starting device fleet...")
        self.running = True
        self.start_time = datetime.utcnow()
        
        # Start devices with stagger
        start_tasks = []
        
        for device_id, device_instance in self.devices.items():
            # Create device
            device = await self._create_device(device_instance)
            device_instance.device_class = device
            device_instance.status = "starting"
            
            # Start device with stagger
            start_task = asyncio.create_task(
                self._start_device_with_stagger(device_instance)
            )
            start_tasks.append(start_task)
            self.device_tasks[device_id] = start_task
            
            # Wait for stagger period
            if device_id != max(self.devices.keys()):
                await asyncio.sleep(self.config.start_stagger)
        
        # Wait for all devices to start
        await asyncio.gather(*start_tasks, return_exceptions=True)
        
        # Start fleet monitoring
        monitor_task = asyncio.create_task(self._monitor_fleet())
        
        self.logger.info(f"Fleet started with {len(self.devices)} devices")
        
        try:
            await monitor_task
        except asyncio.CancelledError:
            self.logger.info("Fleet monitoring cancelled")
    
    async def _create_device(self, device_instance: DeviceInstance):
        """Create a device instance"""
        device_type = device_instance.device_type
        device_id = device_instance.device_id
        location = device_instance.location
        
        if device_type in self.device_factory:
            device = self.device_factory[device_type](device_id, location)
            
            # Configure device for fleet operation
            await self._configure_device_for_fleet(device)
            
            return device
        else:
            raise ValueError(f"Unknown device type: {device_type}")
    
    async def _configure_device_for_fleet(self, device):
        """Configure device for fleet operation"""
        # Enable simulations
        device.simulation_enabled = True
        
        # Configure failure and anomaly rates
        if hasattr(device, 'global_config'):
            device.global_config["simulation"]["failure_probability"] = self.config.failure_rate
            device.global_config["simulation"]["anomaly_probability"] = self.config.anomaly_rate
        
        # Set random variations in telemetry intervals
        base_interval = device.config.telemetry_interval
        variation = random.uniform(0.8, 1.2)
        device.config.telemetry_interval = int(base_interval * variation)
    
    async def _start_device_with_stagger(self, device_instance: DeviceInstance):
        """Start a single device with error handling"""
        device_id = device_instance.device_id
        device = device_instance.device_class
        
        try:
            device_instance.start_time = datetime.utcnow()
            device_instance.status = "running"
            
            await device.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start device {device_id}: {e}")
            device_instance.status = "error"
            device_instance.error_count += 1
            self.total_errors += 1
    
    async def _monitor_fleet(self):
        """Monitor the fleet and collect statistics"""
        while self.running and not self.shutdown_requested:
            try:
                # Update fleet statistics
                await self._update_fleet_statistics()
                
                # Check for devices that need restart
                await self._restart_failed_devices()
                
                # Simulate random failures if enabled
                if self.config.enable_failures:
                    await self._simulate_random_failures()
                
                # Log fleet status
                await self._log_fleet_status()
                
                # Wait for next monitoring cycle
                await asyncio.sleep(60)  # Monitor every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in fleet monitoring: {e}")
                await asyncio.sleep(10)
    
    async def _update_fleet_statistics(self):
        """Update fleet statistics"""
        total_telemetry = 0
        total_errors = 0
        total_alerts = 0
        
        for device_instance in self.devices.values():
            if device_instance.device_class:
                device_info = device_instance.device_class.get_device_info()
                device_instance.telemetry_points = device_info.get("total_telemetry_points", 0)
                device_instance.error_count = device_info.get("error_count", 0)
                device_instance.alerts = device_info.get("alert_count", 0)
                
                total_telemetry += device_instance.telemetry_points
                total_errors += device_instance.error_count
                total_alerts += device_instance.alerts
        
        self.total_telemetry_points = total_telemetry
        self.total_errors = total_errors
        self.total_alerts = total_alerts
    
    async def _restart_failed_devices(self):
        """Restart devices that have failed"""
        for device_id, device_instance in self.devices.items():
            if device_instance.status == "error" and device_instance.device_class:
                self.logger.info(f"Restarting failed device {device_id}")
                
                try:
                    # Reset device
                    device_instance.status = "restarting"
                    device_instance.error_count = 0
                    
                    # Restart device
                    await device_instance.device_class.start()
                    device_instance.status = "running"
                    
                except Exception as e:
                    self.logger.error(f"Failed to restart device {device_id}: {e}")
                    device_instance.status = "error"
                    device_instance.error_count += 1
    
    async def _simulate_random_failures(self):
        """Simulate random device failures for testing"""
        if random.random() < self.config.failure_rate:
            # Select random device
            device_id = random.choice(list(self.devices.keys()))
            device_instance = self.devices[device_id]
            
            if device_instance.status == "running" and device_instance.device_class:
                self.logger.info(f"Simulating failure for device {device_id}")
                
                # Simulate different types of failures
                failure_types = ["mqtt_disconnect", "sensor_error", "calibration_drift"]
                failure_type = random.choice(failure_types)
                
                if failure_type == "mqtt_disconnect":
                    device_instance.device_class.mqtt_connected = False
                elif failure_type == "sensor_error":
                    device_instance.device_class.error_count += 5
                elif failure_type == "calibration_drift":
                    if hasattr(device_instance.device_class, 'calibration_offset'):
                        device_instance.device_class.calibration_offset += random.uniform(-1, 1)
                
                device_instance.status = "error"
    
    async def _log_fleet_status(self):
        """Log fleet status"""
        status_counts = {}
        for device_instance in self.devices.values():
            status = device_instance.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        uptime = (datetime.utcnow() - self.start_time).total_seconds() / 3600
        
        self.logger.info(
            f"Fleet Status (Uptime: {uptime:.1f}h) - "
            f"Total: {len(self.devices)}, "
            f"Running: {status_counts.get('running', 0)}, "
            f"Error: {status_counts.get('error', 0)}, "
            f"Telemetry: {self.total_telemetry_points}, "
            f"Errors: {self.total_errors}, "
            f"Alerts: {self.total_alerts}"
        )
    
    async def stop_fleet(self):
        """Stop all devices in the fleet"""
        self.logger.info("Stopping device fleet...")
        self.running = False
        self.shutdown_requested = True
        
        # Cancel all device tasks
        for task in self.device_tasks.values():
            task.cancel()
        
        # Stop all devices
        stop_tasks = []
        for device_instance in self.devices.values():
            if device_instance.device_class and device_instance.status == "running":
                stop_task = asyncio.create_task(self._stop_device(device_instance))
                stop_tasks.append(stop_task)
        
        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=True)
        
        self.logger.info("Fleet stopped")
    
    async def _stop_device(self, device_instance: DeviceInstance):
        """Stop a single device"""
        try:
            device_instance.status = "stopping"
            device_instance.stop_time = datetime.utcnow()
            
            await device_instance.device_class.stop()
            device_instance.status = "stopped"
            
        except Exception as e:
            self.logger.error(f"Error stopping device {device_instance.device_id}: {e}")
            device_instance.status = "error"
    
    # Device factory methods
    def _create_temperature_sensor(self, device_id: int, location: str):
        return TemperatureSensor(device_id, location)
    
    def _create_humidity_sensor(self, device_id: int, location: str):
        return HumiditySensor(device_id, location)
    
    def _create_pressure_sensor(self, device_id: int, location: str):
        altitude = random.uniform(0, 500)  # Random altitude
        return PressureSensor(device_id, location, altitude)
    
    def _create_air_quality_monitor(self, device_id: int, location: str):
        return AirQualityMonitor(device_id, location)
    
    def _create_vibration_sensor(self, device_id: int, location: str):
        equipment_name = f"Equipment-{device_id}"
        return VibrationSensor(device_id, equipment_name)
    
    def get_fleet_statistics(self) -> Dict[str, Any]:
        """Get comprehensive fleet statistics"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0
        
        status_counts = {}
        device_type_counts = {}
        location_counts = {}
        
        for device_instance in self.devices.values():
            # Status counts
            status = device_instance.status
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Device type counts
            device_type = device_instance.device_type
            device_type_counts[device_type] = device_type_counts.get(device_type, 0) + 1
            
            # Location counts
            location = device_instance.location
            location_counts[location] = location_counts.get(location, 0) + 1
        
        return {
            "fleet_info": {
                "total_devices": len(self.devices),
                "uptime_hours": uptime / 3600,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "running": self.running
            },
            "status_distribution": status_counts,
            "device_type_distribution": device_type_counts,
            "location_distribution": location_counts,
            "performance_metrics": {
                "total_telemetry_points": self.total_telemetry_points,
                "total_errors": self.total_errors,
                "total_alerts": self.total_alerts,
                "telemetry_rate": self.total_telemetry_points / max(1, uptime),
                "error_rate": self.total_errors / max(1, self.total_telemetry_points),
                "alert_rate": self.total_alerts / max(1, self.total_telemetry_points)
            },
            "configuration": {
                "total_devices": self.config.total_devices,
                "device_distribution": self.default_distribution,
                "locations": self.default_locations,
                "start_stagger": self.config.start_stagger,
                "enable_failures": self.config.enable_failures,
                "failure_rate": self.config.failure_rate,
                "enable_anomalies": self.config.enable_anomalies,
                "anomaly_rate": self.config.anomaly_rate
            }
        }
    
    def get_device_details(self, device_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific device"""
        if device_id not in self.devices:
            return None
        
        device_instance = self.devices[device_id]
        device_info = device_instance.device_class.get_device_info() if device_instance.device_class else {}
        
        return {
            "instance_info": {
                "device_id": device_instance.device_id,
                "device_type": device_instance.device_type,
                "location": device_instance.location,
                "status": device_instance.status,
                "start_time": device_instance.start_time.isoformat() if device_instance.start_time else None,
                "stop_time": device_instance.stop_time.isoformat() if device_instance.stop_time else None,
                "error_count": device_instance.error_count,
                "telemetry_points": device_instance.telemetry_points
            },
            "device_info": device_info
        }
    
    def export_fleet_config(self, filename: str = "fleet_config.json"):
        """Export fleet configuration to JSON file"""
        config_data = {
            "fleet_config": asdict(self.config),
            "device_distribution": self.default_distribution,
            "locations": self.default_locations,
            "devices": [
                {
                    "device_id": device_id,
                    "device_type": device_instance.device_type,
                    "location": device_instance.location
                }
                for device_id, device_instance in self.devices.items()
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(config_data, f, indent=2, default=str)
        
        self.logger.info(f"Fleet configuration exported to {filename}")


# Main execution function
async def run_fleet(config: FleetConfig = None):
    """Run the device fleet"""
    if config is None:
        config = FleetConfig()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create fleet manager
    fleet_manager = DeviceFleetManager(config)
    
    try:
        # Create fleet
        await fleet_manager.create_fleet()
        
        # Start fleet
        await fleet_manager.start_fleet()
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Stop fleet
        await fleet_manager.stop_fleet()
        
        # Export final statistics
        stats = fleet_manager.get_fleet_statistics()
        print("\nFinal Fleet Statistics:")
        print(f"Total Devices: {stats['fleet_info']['total_devices']}")
        print(f"Uptime: {stats['fleet_info']['uptime_hours']:.2f} hours")
        print(f"Total Telemetry Points: {stats['performance_metrics']['total_telemetry_points']}")
        print(f"Total Errors: {stats['performance_metrics']['total_errors']}")
        print(f"Total Alerts: {stats['performance_metrics']['total_alerts']}")
        
        # Export configuration
        fleet_manager.export_fleet_config()


if __name__ == "__main__":
    import asyncio
    
    # Example usage
    config = FleetConfig(
        total_devices=20,
        enable_failures=True,
        failure_rate=0.01,
        enable_anomalies=True,
        anomaly_rate=0.02
    )
    
    asyncio.run(run_fleet(config))
