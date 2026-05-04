#!/usr/bin/env python3

"""
Valtronics Device Simulator
This script simulates IoT devices sending telemetry data via MQTT
"""

import paho.mqtt.client as mqtt
import json
import time
import random
import logging
from datetime import datetime
from typing import Dict, List, Any
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeviceSimulator:
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client()
        self.devices: List[Dict[str, Any]] = []
        self.running = False
        
        # Setup MQTT callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        logger.warning(f"Disconnected from MQTT broker: {rc}")
    
    def on_publish(self, client, userdata, mid):
        logger.debug(f"Message published with mid: {mid}")
    
    def add_device(self, device_config: Dict[str, Any]):
        """Add a device to simulate"""
        device = {
            "id": device_config["id"],
            "name": device_config["name"],
            "type": device_config["type"],
            "location": device_config.get("location", "Unknown"),
            "status": "online",
            "metrics": device_config.get("metrics", {}),
            "interval": device_config.get("interval", 30),
            "last_heartbeat": time.time(),
            "last_telemetry": time.time()
        }
        self.devices.append(device)
        logger.info(f"Added device: {device['name']} ({device['id']})")
    
    def generate_telemetry(self, device: Dict[str, Any]) -> Dict[str, Any]:
        """Generate realistic telemetry data for a device"""
        telemetry = {
            "device_id": device["id"],
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": []
        }
        
        # Generate metrics based on device type
        if device["type"] == "sensor":
            telemetry["metrics"].extend(self._generate_sensor_metrics(device))
        elif device["type"] == "actuator":
            telemetry["metrics"].extend(self._generate_actuator_metrics(device))
        elif device["type"] == "gateway":
            telemetry["metrics"].extend(self._generate_gateway_metrics(device))
        else:
            telemetry["metrics"].extend(self._generate_generic_metrics(device))
        
        return telemetry
    
    def _generate_sensor_metrics(self, device: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate sensor-specific metrics"""
        metrics = []
        
        # Temperature sensor
        if "temperature" in device.get("metrics", {}):
            base_temp = device["metrics"]["temperature"].get("base", 22.0)
            variation = device["metrics"]["temperature"].get("variation", 5.0)
            temp = base_temp + random.uniform(-variation, variation)
            metrics.append({
                "name": "temperature",
                "value": round(temp, 2),
                "unit": "celsius"
            })
        
        # Humidity sensor
        if "humidity" in device.get("metrics", {}):
            base_humidity = device["metrics"]["humidity"].get("base", 45.0)
            variation = device["metrics"]["humidity"].get("variation", 10.0)
            humidity = max(0, min(100, base_humidity + random.uniform(-variation, variation)))
            metrics.append({
                "name": "humidity",
                "value": round(humidity, 2),
                "unit": "percent"
            })
        
        # Pressure sensor
        if "pressure" in device.get("metrics", {}):
            base_pressure = device["metrics"]["pressure"].get("base", 1013.25)
            variation = device["metrics"]["pressure"].get("variation", 5.0)
            pressure = base_pressure + random.uniform(-variation, variation)
            metrics.append({
                "name": "pressure",
                "value": round(pressure, 2),
                "unit": "hPa"
            })
        
        # Light sensor
        if "light" in device.get("metrics", {}):
            base_light = device["metrics"]["light"].get("base", 500.0)
            variation = device["metrics"]["light"].get("variation", 200.0)
            light = max(0, base_light + random.uniform(-variation, variation))
            metrics.append({
                "name": "light_intensity",
                "value": round(light, 2),
                "unit": "lux"
            })
        
        # Vibration sensor
        if "vibration" in device.get("metrics", {}):
            base_vibration = device["metrics"]["vibration"].get("base", 0.1)
            variation = device["metrics"]["vibration"].get("variation", 0.05)
            vibration = max(0, base_vibration + random.uniform(-variation, variation))
            metrics.append({
                "name": "vibration",
                "value": round(vibration, 3),
                "unit": "g"
            })
        
        return metrics
    
    def _generate_actuator_metrics(self, device: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actuator-specific metrics"""
        metrics = []
        
        # Power consumption
        if "power" in device.get("metrics", {}):
            base_power = device["metrics"]["power"].get("base", 50.0)
            variation = device["metrics"]["power"].get("variation", 10.0)
            power = max(0, base_power + random.uniform(-variation, variation))
            metrics.append({
                "name": "power_consumption",
                "value": round(power, 2),
                "unit": "watts"
            })
        
        # Operating status
        metrics.append({
            "name": "operational_status",
            "value": random.choice(["running", "idle", "standby"]),
            "unit": "state"
        })
        
        # Duty cycle
        metrics.append({
            "name": "duty_cycle",
            "value": round(random.uniform(0, 100), 2),
            "unit": "percent"
        })
        
        return metrics
    
    def _generate_gateway_metrics(self, device: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate gateway-specific metrics"""
        metrics = []
        
        # Connected devices count
        base_devices = device["metrics"].get("connected_devices", {}).get("base", 10)
        variation = device["metrics"].get("connected_devices", {}).get("variation", 2)
        connected_devices = max(0, base_devices + random.randint(-variation, variation))
        metrics.append({
            "name": "connected_devices",
            "value": connected_devices,
            "unit": "count"
        })
        
        # Network traffic
        metrics.append({
            "name": "network_traffic",
            "value": round(random.uniform(100, 1000), 2),
            "unit": "kbps"
        })
        
        # CPU usage
        metrics.append({
            "name": "cpu_usage",
            "value": round(random.uniform(10, 80), 2),
            "unit": "percent"
        })
        
        # Memory usage
        metrics.append({
            "name": "memory_usage",
            "value": round(random.uniform(30, 90), 2),
            "unit": "percent"
        })
        
        return metrics
    
    def _generate_generic_metrics(self, device: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate generic device metrics"""
        metrics = []
        
        # Generic status metric
        metrics.append({
            "name": "status",
            "value": random.choice(["ok", "warning", "error"]),
            "unit": "state"
        })
        
        # Generic value metric
        base_value = device.get("metrics", {}).get("value", {}).get("base", 100.0)
        variation = device.get("metrics", {}).get("value", {}).get("variation", 20.0)
        value = base_value + random.uniform(-variation, variation)
        metrics.append({
            "name": "value",
            "value": round(value, 2),
            "unit": "unit"
        })
        
        return metrics
    
    def send_telemetry(self, device: Dict[str, Any]):
        """Send telemetry data for a device"""
        telemetry = self.generate_telemetry(device)
        topic = f"valtronics/{device['id']}/telemetry"
        
        try:
            result = self.client.publish(topic, json.dumps(telemetry), qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Telemetry sent for device {device['id']}")
                device["last_telemetry"] = time.time()
            else:
                logger.error(f"Failed to send telemetry for device {device['id']}: {result.rc}")
        except Exception as e:
            logger.error(f"Error sending telemetry for device {device['id']}: {e}")
    
    def send_heartbeat(self, device: Dict[str, Any]):
        """Send heartbeat for a device"""
        heartbeat = {
            "device_id": device["id"],
            "status": device["status"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        topic = f"valtronics/{device['id']}/heartbeat"
        
        try:
            result = self.client.publish(topic, json.dumps(heartbeat), qos=0)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Heartbeat sent for device {device['id']}")
                device["last_heartbeat"] = time.time()
        except Exception as e:
            logger.error(f"Error sending heartbeat for device {device['id']}: {e}")
    
    def send_status_update(self, device: Dict[str, Any], new_status: str):
        """Send status update for a device"""
        device["status"] = new_status
        
        status_update = {
            "device_id": device["id"],
            "status": new_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        topic = f"valtronics/{device['id']}/status"
        
        try:
            result = self.client.publish(topic, json.dumps(status_update), qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Status update sent for device {device['id']}: {new_status}")
        except Exception as e:
            logger.error(f"Error sending status update for device {device['id']}: {e}")
    
    def simulate_device_failure(self, device: Dict[str, Any]):
        """Simulate a device failure"""
        logger.warning(f"Simulating device failure for {device['id']}")
        self.send_status_update(device, "error")
        
        # Send alert
        alert = {
            "device_id": device["id"],
            "type": "system",
            "severity": "critical",
            "message": f"Device {device['name']} has failed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        topic = f"valtronics/{device['id']}/alert"
        try:
            self.client.publish(topic, json.dumps(alert), qos=1)
        except Exception as e:
            logger.error(f"Error sending alert for device {device['id']}: {e}")
    
    def simulate_device_recovery(self, device: Dict[str, Any]):
        """Simulate device recovery"""
        logger.info(f"Simulating device recovery for {device['id']}")
        self.send_status_update(device, "online")
    
    def run_simulation(self):
        """Run the device simulation"""
        logger.info("Starting device simulation...")
        
        # Connect to MQTT broker
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            time.sleep(2)  # Wait for connection
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return
        
        self.running = True
        failure_simulation_time = time.time() + random.randint(300, 600)  # Random failure after 5-10 minutes
        
        try:
            while self.running:
                current_time = time.time()
                
                for device in self.devices:
                    # Send telemetry
                    if current_time - device["last_telemetry"] >= device["interval"]:
                        self.send_telemetry(device)
                    
                    # Send heartbeat
                    if current_time - device["last_heartbeat"] >= 60:  # Every minute
                        self.send_heartbeat(device)
                
                # Simulate random device failure
                if current_time >= failure_simulation_time and self.running:
                    failed_device = random.choice(self.devices)
                    self.simulate_device_failure(failed_device)
                    
                    # Recover after 30-60 seconds
                    recovery_time = current_time + random.randint(30, 60)
                    while time.time() < recovery_time and self.running:
                        time.sleep(1)
                    
                    if self.running:
                        self.simulate_device_recovery(failed_device)
                    
                    # Schedule next failure
                    failure_simulation_time = time.time() + random.randint(300, 600)
                
                time.sleep(5)  # Main loop interval
                
        except KeyboardInterrupt:
            logger.info("Simulation stopped by user")
        finally:
            self.running = False
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Device simulation stopped")
    
    def stop_simulation(self):
        """Stop the device simulation"""
        self.running = False

def create_default_devices() -> List[Dict[str, Any]]:
    """Create default device configurations"""
    return [
        {
            "id": "TEMP_SENSOR_001",
            "name": "Temperature Sensor 01",
            "type": "sensor",
            "location": "Server Room A",
            "interval": 30,
            "metrics": {
                "temperature": {"base": 22.0, "variation": 3.0},
                "humidity": {"base": 45.0, "variation": 8.0}
            }
        },
        {
            "id": "HUM_SENSOR_001",
            "name": "Humidity Sensor 01",
            "type": "sensor",
            "location": "Server Room A",
            "interval": 45,
            "metrics": {
                "humidity": {"base": 45.0, "variation": 10.0},
                "temperature": {"base": 22.0, "variation": 2.0}
            }
        },
        {
            "id": "PRESS_SENSOR_001",
            "name": "Pressure Sensor 01",
            "type": "sensor",
            "location": "Server Room B",
            "interval": 60,
            "metrics": {
                "pressure": {"base": 1013.25, "variation": 5.0},
                "temperature": {"base": 21.0, "variation": 2.0}
            }
        },
        {
            "id": "ACTUATOR_001",
            "name": "HVAC Actuator 01",
            "type": "actuator",
            "location": "Server Room A",
            "interval": 30,
            "metrics": {
                "power": {"base": 75.0, "variation": 15.0}
            }
        },
        {
            "id": "GATEWAY_001",
            "name": "IoT Gateway 01",
            "type": "gateway",
            "location": "Network Closet",
            "interval": 30,
            "metrics": {
                "connected_devices": {"base": 12, "variation": 3}
            }
        }
    ]

def main():
    parser = argparse.ArgumentParser(description="Valtronics Device Simulator")
    parser.add_argument("--broker-host", default="localhost", help="MQTT broker host")
    parser.add_argument("--broker-port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--devices", type=int, default=5, help="Number of devices to simulate")
    parser.add_argument("--interval", type=int, default=30, help="Default telemetry interval (seconds)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create simulator
    simulator = DeviceSimulator(args.broker_host, args.broker_port)
    
    # Add devices
    default_devices = create_default_devices()
    for device_config in default_devices[:args.devices]:
        if args.interval != 30:
            device_config["interval"] = args.interval
        simulator.add_device(device_config)
    
    logger.info(f"Starting simulation with {len(simulator.devices)} devices")
    
    # Run simulation
    try:
        simulator.run_simulation()
    except KeyboardInterrupt:
        logger.info("Simulation interrupted")
    finally:
        simulator.stop_simulation()

if __name__ == "__main__":
    main()
