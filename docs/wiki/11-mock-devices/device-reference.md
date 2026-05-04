# Mock Devices Reference Guide

**Complete reference for all mock device types and their configurations**

---

## Overview

This reference guide provides detailed information about all available mock device types, their parameters, configuration options, and usage examples.

---

## Device Types Reference

### Environmental Sensors

#### Temperature Sensor

**Class**: `TemperatureSensor`

**Location**: `/mock-devices/environmental/temperature_sensor.py`

**Purpose**: Simulates temperature monitoring with realistic daily cycles, seasonal variations, and environmental factors.

**Constructor**:
```python
TemperatureSensor(device_id: int, location: str = "Unknown")
```

**Key Parameters**:
- `base_temperature`: Base temperature in °C (default: 22.0)
- `seasonal_variation`: Seasonal variation amplitude (default: 5.0)
- `daily_amplitude`: Daily temperature variation (default: 8.0)
- `sensor_accuracy`: Sensor accuracy in °C (default: 0.1)
- `response_time`: Response time in seconds (default: 2.0)

**Configuration Methods**:
```python
# Set ventilation rate (0.0 to 1.0)
sensor.set_ventilation_rate(0.7)

# Add heat source
sensor.add_heat_source(name="Server Rack", intensity=5.0, proximity_factor=0.8)

# Remove heat source
sensor.remove_heat_source("Server Rack")

# Calibrate sensor
sensor.calibrate_sensor(reference_temperature=22.5)
```

**Alert Thresholds**:
- `temp_min_threshold`: 10.0°C
- `temp_max_threshold`: 35.0°C
- `temp_critical_min`: 5.0°C
- `temp_critical_max`: 40.0°C

**Telemetry Metrics**:
- `temperature`: Current temperature (°C)
- Sensor metadata: accuracy, calibration offset, heat sources

**Example Usage**:
```python
from mock_devices.environmental.temperature_sensor import create_temperature_sensor

# Create and configure sensor
sensor = create_temperature_sensor(1001, "Server Room A")
sensor.add_heat_source("Server Rack 1", intensity=5.0, proximity_factor=0.8)
sensor.set_ventilation_rate(0.7)

# Start sensor
await sensor.start()
```

#### Humidity Sensor

**Class**: `HumiditySensor`

**Location**: `/mock-devices/environmental/humidity_sensor.py`

**Purpose**: Simulates humidity monitoring with inverse correlation to temperature and dew point calculations.

**Constructor**:
```python
HumiditySensor(device_id: int, location: str = "Unknown")
```

**Key Parameters**:
- `base_humidity`: Base humidity percentage (default: 50.0)
- `humidity_range`: Daily humidity variation range (default: 30.0)
- `sensor_accuracy`: Sensor accuracy in percentage (default: 2.0)
- `temperature_coupling`: Temperature correlation strength (0.0-1.0, default: 0.7)

**Configuration Methods**:
```python
# Set temperature coupling
sensor.set_temperature_coupling(0.8)

# Update temperature for correlation
sensor.update_temperature(22.5)

# Add humidity source
sensor.add_humidity_source("Water Leak", intensity=8.0, proximity_factor=0.6)

# Set air circulation
sensor.set_air_circulation(0.5)

# Calibrate sensor
sensor.calibrate_sensor(reference_humidity=55.0)
```

**Alert Thresholds**:
- `humidity_min_threshold`: 30%
- `humidity_max_threshold`: 70%
- `humidity_critical_min`: 20%
- `humidity_critical_max`: 80%

**Telemetry Metrics**:
- `humidity`: Current humidity (%)
- `dew_point`: Calculated dew point (°C)
- Sensor metadata: temperature coupling, air circulation

**Example Usage**:
```python
from mock_devices.environmental.humidity_sensor import create_humidity_sensor

# Create and configure sensor
sensor = create_humidity_sensor(2001, "Data Center B")
sensor.set_temperature_coupling(0.8)
sensor.add_humidity_source("Water Source", intensity=8.0, proximity_factor=0.6)

# Start sensor
await sensor.start()
```

#### Pressure Sensor

**Class**: `PressureSensor`

**Location**: `/mock-devices/environmental/pressure_sensor.py`

**Purpose**: Simulates barometric pressure monitoring with weather patterns and altitude compensation.

**Constructor**:
```python
PressureSensor(device_id: int, location: str = "Unknown", altitude: float = 0.0)
```

**Key Parameters**:
- `base_pressure`: Base pressure in hPa (default: 1013.25)
- `altitude`: Altitude in meters (default: 0.0)
- `altitude_coefficient`: hPa per meter (default: 0.12)
- `sensor_accuracy`: Sensor accuracy in hPa (default: 0.5)

**Configuration Methods**:
```python
# Set altitude
sensor.set_altitude(500.0)

# Enable temperature compensation
sensor.set_temperature_compensation(True)

# Update temperature
sensor.update_temperature(15.0)

# Simulate weather front
sensor.simulate_weather_front(pressure_change=-8.0)

# Calibrate sensor
sensor.calibrate_sensor(reference_pressure=1013.25)
```

**Alert Thresholds**:
- `pressure_min_threshold`: 980.0 hPa
- `pressure_max_threshold`: 1050.0 hPa
- `pressure_critical_min`: 950.0 hPa
- `pressure_critical_max`: 1080.0 hPa

**Telemetry Metrics**:
- `pressure`: Current pressure (hPa)
- `sea_level_pressure`: Sea level pressure (hPa)
- `pressure_trend`: Pressure trend (hPa/min)
- Sensor metadata: altitude, weather trend

**Example Usage**:
```python
from mock_devices.environmental.pressure_sensor import create_pressure_sensor

# Create and configure sensor
sensor = create_pressure_sensor(3001, "Mountain Station", altitude=500.0)
sensor.set_temperature_compensation(True)
sensor.simulate_weather_front(-8.0)

# Start sensor
await sensor.start()
```

#### Air Quality Monitor

**Class**: `AirQualityMonitor`

**Location**: `/mock-devices/environmental/air_quality_monitor.py`

**Purpose**: Simulates comprehensive air quality monitoring with multiple pollutants and AQI calculations.

**Constructor**:
```python
AirQualityMonitor(device_id: int, location: str = "Unknown")
```

**Key Parameters**:
- `pm25_base`: Base PM2.5 in μg/m³ (default: 15.0)
- `pm10_base`: Base PM10 in μg/m³ (default: 25.0)
- `co2_base`: Base CO2 in ppm (default: 400.0)
- `voc_base`: Base VOC in ppm (default: 0.2)

**Configuration Methods**:
```python
# Set ventilation rate
sensor.set_ventilation_rate(0.5)

# Set occupancy level
sensor.set_occupancy_level(1.2)

# Set weather conditions
sensor.set_weather_conditions("sunny")

# Add pollution source
sensor.add_pollution_source("Traffic", "all", intensity=15.0, proximity_factor=0.8)

# Remove pollution source
sensor.remove_pollution_source("Traffic")

# Calibrate specific sensor
sensor.calibrate_sensor("pm25", reference_value=20.0)
```

**AQI Thresholds**:
- `moderate`: 100
- `unhealthy_sensitive`: 150
- `unhealthy`: 200
- `very_unhealthy`: 300
- `hazardous`: 500

**Telemetry Metrics**:
- `pm25`: PM2.5 concentration (μg/m³)
- `pm10`: PM10 concentration (μg/m³)
- `co2`: CO2 concentration (ppm)
- `voc`: VOC concentration (ppm)
- `o3`: Ozone concentration (ppm)
- `no2`: NO2 concentration (ppm)
- `so2`: SO2 concentration (ppm)
- `aqi`: Air Quality Index
- Individual pollutant AQI values

**Example Usage**:
```python
from mock_devices.environmental.air_quality_monitor import create_air_quality_monitor

# Create and configure monitor
monitor = create_air_quality_monitor(4001, "Office Building A")
monitor.set_ventilation_rate(0.3)
monitor.set_occupancy_level(1.5)
monitor.add_pollution_source("Traffic", "all", intensity=15.0, proximity_factor=0.8)

# Start monitor
await monitor.start()
```

### Industrial Sensors

#### Vibration Sensor

**Class**: `VibrationSensor`

**Location**: `/mock-devices/industrial/vibration_sensor.py`

**Purpose**: Simulates equipment vibration monitoring with fault detection and frequency analysis.

**Constructor**:
```python
VibrationSensor(device_id: int, equipment_name: str = "Unknown Equipment")
```

**Key Parameters**:
- `base_vibration`: Base vibration in mm/s (default: 0.1)
- `frequency_range`: Frequency range in Hz (default: [10, 1000])
- `sensor_accuracy`: Sensor accuracy in mm/s (default: 0.01)
- `mounting_type`: Mounting type (default: "bearing")

**Configuration Methods**:
```python
# Set equipment parameters
sensor.set_equipment_parameters(speed=1800, load=0.8, age=3.5)

# Induce fault for testing
sensor.induce_fault("bearing_fault", severity=0.6)

# Clear fault
sensor.clear_fault("bearing_fault")

# Clear all faults
sensor.clear_all_faults()

# Calibrate sensor
sensor.calibrate_sensor(reference_vibration=0.1)
```

**Fault Types**:
- `bearing_fault`: Bearing wear/failure
- `misalignment`: Shaft misalignment
- `unbalance`: Rotational unbalance
- `looseness`: Mechanical looseness
- `gear_fault`: Gear wear/damage

**Alert Thresholds**:
- `vibration_warning_threshold`: 0.5 mm/s
- `vibration_critical_threshold`: 1.0 mm/s
- `crest_factor_threshold`: 3.0

**Telemetry Metrics**:
- `vibration_rms`: RMS vibration (mm/s)
- `vibration_peak`: Peak vibration (mm/s)
- `vibration_crest_factor`: Crest factor (ratio)
- `dominant_frequency`: Dominant frequency (Hz)
- `equipment_health_score`: Health percentage
- Fault indicators for each fault type

**Example Usage**:
```python
from mock_devices.industrial.vibration_sensor import create_vibration_sensor

# Create and configure sensor
sensor = create_vibration_sensor(5001, "Motor A")
sensor.set_equipment_parameters(speed=1800, load=0.8, age=3.5)
sensor.induce_fault("bearing_fault", severity=0.6)

# Start sensor
await sensor.start()
```

---

## Configuration Reference

### Global Configuration

**File**: `config.json`

```json
{
  "mqtt": {
    "broker_host": "localhost",
    "broker_port": 1883,
    "username": "valtronics_user",
    "password": "valtronics_password",
    "keepalive": 60,
    "qos": 1
  },
  "api": {
    "base_url": "http://localhost:8000",
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 5
  },
  "device": {
    "telemetry_interval": 30,
    "health_check_interval": 300,
    "batch_size": 10,
    "max_retries": 3
  },
  "simulation": {
    "noise_level": 0.1,
    "drift_rate": 0.01,
    "failure_probability": 0.02,
    "alert_probability": 0.05
  },
  "logging": {
    "level": "INFO",
    "format": "rich",
    "file": "mock_devices.log"
  }
}
```

### Fleet Configuration

**Class**: `FleetConfig`

```python
from mock_devices.device_fleet import FleetConfig

config = FleetConfig(
    total_devices=50,
    device_distribution={
        "temperature_sensor": 20,
        "humidity_sensor": 15,
        "pressure_sensor": 10,
        "air_quality_monitor": 5
    },
    locations=[
        "Server Room A", "Server Room B", "Data Center 1",
        "Office Building A", "Factory Floor A", "Warehouse A"
    ],
    start_stagger=5,
    enable_failures=True,
    failure_rate=0.02,
    enable_anomalies=True,
    anomaly_rate=0.05
)
```

---

## Data Models

### TelemetryData Structure

```python
@dataclass
class TelemetryData:
    metric_name: str
    metric_value: float
    unit: str
    timestamp: datetime
    device_id: int
    metadata: Optional[Dict[str, Any]] = None
```

### DeviceConfig Structure

```python
@dataclass
class DeviceConfig:
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
```

### DeviceInstance Structure

```python
@dataclass
class DeviceInstance:
    device_id: int
    device_type: str
    device_class: Any
    location: str
    status: str
    start_time: Optional[datetime]
    stop_time: Optional[datetime]
    error_count: int
    telemetry_points: int
```

---

## API Reference

### Base Device Methods

#### Core Methods
```python
# Start device
await device.start()

# Stop device
await device.stop()

# Get device information
info = device.get_device_info()

# Add noise to value
noisy_value = device.add_noise(value, noise_level=0.1)

# Simulate drift
drifted_value = device.simulate_drift(base_value, drift_rate=0.01)
```

#### Telemetry Generation
```python
# Generate telemetry data
telemetry = await device.generate_telemetry()

# Each device must implement this method
async def generate_telemetry(self) -> List[TelemetryData]:
    # Implementation required
    pass
```

#### Health Monitoring
```python
# Perform health check
health_status = await device.perform_health_check()

# Returns DeviceStatus enum:
# - ONLINE
# - OFFLINE
# - ERROR
# - WARNING
# - MAINTENANCE
```

### Fleet Manager Methods

#### Fleet Operations
```python
# Create fleet
devices = await fleet_manager.create_fleet()

# Start fleet
await fleet_manager.start_fleet()

# Stop fleet
await fleet_manager.stop_fleet()

# Get fleet statistics
stats = fleet_manager.get_fleet_statistics()

# Get device details
details = fleet_manager.get_device_details(device_id)
```

#### Configuration Management
```python
# Export fleet configuration
fleet_manager.export_fleet_config("fleet_config.json")

# Import configuration (manual)
with open("fleet_config.json", "r") as f:
    config_data = json.load(f)
```

---

## Error Handling

### Common Exceptions

#### Device Errors
```python
# Connection errors
try:
    await device.start()
except Exception as e:
    print(f"Device start failed: {e}")

# MQTT errors
if not device.mqtt_connected:
    print("MQTT connection lost")

# API errors
try:
    await device._register_device()
except requests.exceptions.ConnectionError:
    print("API server unavailable")
```

#### Fleet Errors
```python
# Fleet startup errors
try:
    await fleet_manager.start_fleet()
except Exception as e:
    print(f"Fleet startup failed: {e}")

# Device restart errors
await fleet_manager._restart_failed_devices()
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Monitor device logs
device.logger.setLevel(logging.DEBUG)

# Enable detailed device info
device_info = device.get_device_info()
print(json.dumps(device_info, indent=2, default=str))
```

---

## Performance Considerations

### Resource Usage

#### Memory Management
```python
# Limit history size
device.max_history_size = 1440  # 24 hours at 1-minute intervals

# Clean up old data
if len(device.temperature_history) > device.max_history_size:
    device.temperature_history = device.temperature_history[-device.max_history_size:]
```

#### CPU Optimization
```python
# Use appropriate telemetry intervals
device.config.telemetry_interval = 60  # Increase for less frequent updates

# Batch operations
batch_size = 10
for i in range(0, len(telemetry_data), batch_size):
    batch = telemetry_data[i:i+batch_size]
    await device._send_telemetry_batch(batch)
```

#### Network Optimization
```python
# Use appropriate QoS levels
mqtt_qos = 1  # Balance reliability and performance

# Implement connection pooling
mqtt_client = EnhancedMQTTClient(
    broker_host="localhost",
    broker_port=1883,
    max_reconnect_attempts=5
)
```

### Scaling Guidelines

#### Single Device Limits
- **Memory**: ~1MB per device with 24-hour history
- **CPU**: ~1% CPU per device
- **Network**: ~1KB/s telemetry data

#### Fleet Scaling
- **Small Fleet**: 1-10 devices (development)
- **Medium Fleet**: 10-50 devices (testing)
- **Large Fleet**: 50-100+ devices (stress testing)

#### Performance Monitoring
```python
# Monitor device performance
stats = device.get_device_info()
print(f"Telemetry points: {stats['total_telemetry_points']}")
print(f"Error count: {stats['error_count']}")
print(f"Memory usage: {stats['memory_usage']}")
```

---

## Integration Examples

### With External Systems

#### Prometheus Metrics
```python
from prometheus_client import Gauge, Counter

# Create metrics
temperature_gauge = Gauge('mock_device_temperature', 'Temperature reading')
error_counter = Counter('mock_device_errors', 'Device errors')

# Update metrics
temperature_gauge.set(current_temperature)
error_counter.inc()
```

#### Database Integration
```python
import sqlite3

# Store telemetry in database
def store_telemetry(telemetry_data):
    conn = sqlite3.connect('telemetry.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO telemetry 
        (device_id, metric_name, value, unit, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (telemetry_data.device_id, telemetry_data.metric_name, 
          telemetry_data.metric_value, telemetry_data.unit, 
          telemetry_data.timestamp))
    
    conn.commit()
    conn.close()
```

#### WebSocket Integration
```python
import websockets

async def send_telemetry_websocket(telemetry_data):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        message = json.dumps({
            'type': 'telemetry',
            'data': telemetry_data.__dict__
        })
        await websocket.send(message)
```

---

## Troubleshooting

### Common Issues

#### Device Registration Failures
```bash
# Check API server
curl -X GET http://localhost:8000/health

# Check MQTT broker
sudo systemctl status mosquitto

# Test device creation
python -c "
from mock_devices.environmental.temperature_sensor import TemperatureSensor
device = TemperatureSensor(9999, 'Test')
print('Device creation successful')
"
```

#### MQTT Connection Issues
```bash
# Test MQTT connection
mosquitto_pub -h localhost -t test/topic -m "test message"

# Check broker logs
sudo journalctl -u mosquitto -f

# Verify configuration
mosquitto_sub -h localhost -t '$SYS/#'
```

#### Performance Issues
```python
# Monitor resource usage
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
print(f"CPU: {process.cpu_percent()}%")
```

### Debug Commands

#### Device Debugging
```python
# Enable debug mode
device.simulation_enabled = False
device.running = True

# Check device state
print(f"Status: {device.status}")
print(f"MQTT connected: {device.mqtt_connected}")
print(f"Error count: {device.error_count}")

# Test telemetry generation
telemetry = await device.generate_telemetry()
print(f"Generated {len(telemetry)} telemetry points")
```

#### Fleet Debugging
```python
# Check fleet status
stats = fleet_manager.get_fleet_statistics()
print(json.dumps(stats, indent=2, default=str))

# Check individual devices
for device_id, device_instance in fleet_manager.devices.items():
    print(f"Device {device_id}: {device_instance.status}")
```

---

## Support

For Mock Devices support:
- **Overview**: [Mock Devices Overview](mock-devices-overview.md)
- **Development**: [Development Setup](../08-development/development-setup.md)
- **API Reference**: [API Overview](../03-api/api-overview.md)
- **Troubleshooting**: [Troubleshooting Guide](../10-reference/troubleshooting.md)
- **Email**: autobotsolution@gmail.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Mock Devices Reference Guide v1.0**
