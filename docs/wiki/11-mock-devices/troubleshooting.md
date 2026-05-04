# Mock Devices Troubleshooting Guide

**Comprehensive troubleshooting guide for Valtronics Mock Devices**

---

## Overview

This guide provides solutions to common issues, debugging techniques, and performance optimization tips for the Valtronics Mock Devices system.

---

## Common Issues

### Installation and Setup Issues

#### Python Dependencies
```bash
# Issue: ModuleNotFoundError
# Solution: Install dependencies properly
pip install -r requirements.txt

# Issue: Version conflicts
# Solution: Use virtual environment
python -m venv mock_devices_env
source mock_devices_env/bin/activate
pip install -r requirements.txt
```

#### MQTT Connection Problems
```bash
# Issue: Connection refused
# Check if MQTT broker is running
sudo systemctl status mosquitto

# Start MQTT broker
sudo systemctl start mosquitto
sudo systemctl enable mosquitto

# Test MQTT connection
mosquitto_pub -h localhost -t test/topic -m "Hello MQTT"
mosquitto_sub -h localhost -t test/topic

# Check MQTT configuration
sudo nano /etc/mosquitto/mosquitto.conf
```

#### API Server Connection
```bash
# Issue: API server unavailable
# Check if Valtronics API is running
curl -X GET http://localhost:8000/health

# Start API server
cd /path/to/valtronics/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Check API endpoints
curl -X GET http://localhost:8000/api/v1/devices/
```

### Device Operation Issues

#### Device Registration Failures
```python
# Issue: Device not registering
# Debug code
import asyncio
from mock_devices.environmental.temperature_sensor import TemperatureSensor

async def debug_registration():
    sensor = TemperatureSensor(9999, "Test")
    
    try:
        # Check API connection
        from mock_devices.utils.api_client import APIClient
        api_client = APIClient()
        
        # Test API connection
        response = api_client._make_request('GET', '/health')
        if response:
            print("API connection successful")
        else:
            print("API connection failed")
        
        # Try manual registration
        device_data = {
            "name": sensor.device_name,
            "device_id": f"MOCK-{sensor.device_id:04d}",
            "device_type": sensor.device_type.value,
            "manufacturer": sensor.config.manufacturer,
            "model": sensor.config.model,
            "firmware_version": sensor.config.firmware_version,
            "location": sensor.config.location
        }
        
        result = api_client.register_device(device_data)
        if result:
            print("Device registration successful")
            print(f"Device ID: {result.get('id')}")
        else:
            print("Device registration failed")
            print("Check API server logs for details")
    
    except Exception as e:
        print(f"Registration error: {e}")

asyncio.run(debug_registration())
```

#### MQTT Publishing Failures
```python
# Issue: MQTT messages not being published
# Debug code
import asyncio
from mock_devices.environmental.temperature_sensor import TemperatureSensor

async def debug_mqtt():
    sensor = TemperatureSensor(9998, "Test")
    
    # Test MQTT connection
    try:
        await sensor._connect_mqtt()
        print(f"MQTT connected: {sensor.mqtt_connected}")
        
        # Test message publishing
        test_topic = f"valtronics/devices/{sensor.device_id}/test"
        test_payload = {"test": "message", "timestamp": datetime.utcnow().isoformat()}
        
        result = sensor.mqtt_client.publish(test_topic, test_payload)
        if result:
            print("Test message published successfully")
        else:
            print("Test message publish failed")
        
        # Check broker logs
        print("Check MQTT broker logs:")
        print("  sudo journalctl -u mosquitto -f")
        
    except Exception as e:
        print(f"MQTT error: {e}")
        print("Check MQTT configuration in config.json")
        print("Verify broker host and port")

asyncio.run(debug_mqtt())
```

#### Telemetry Generation Issues
```python
# Issue: No telemetry data being generated
# Debug code
import asyncio
from mock_devices.environmental.temperature_sensor import TemperatureSensor

async def debug_telemetry():
    sensor = TemperatureSensor(9997, "Test")
    
    try:
        # Generate telemetry without starting device
        telemetry = await sensor.generate_telemetry()
        print(f"Generated {len(telemetry)} telemetry points")
        
        for data in telemetry:
            print(f"  {data.metric_name}: {data.metric_value} {data.unit}")
        
        # Check device configuration
        print(f"Telemetry interval: {sensor.config.telemetry_interval}")
        print(f"Simulation enabled: {sensor.simulation_enabled}")
        
        # Check data generator
        from mock_devices.utils.data_generator import DataGenerator
        generator = DataGenerator()
        
        # Test data generation
        test_temp = generator.add_noise(22.0, 0.1)
        print(f"Test temperature with noise: {test_temp}")
        
    except Exception as e:
        print(f"Telemetry error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(debug_telemetry())
```

### Fleet Management Issues

#### Fleet Startup Failures
```python
# Issue: Fleet not starting properly
# Debug code
import asyncio
from mock_devices.device_fleet import FleetConfig, DeviceFleetManager

async def debug_fleet_startup():
    config = FleetConfig(total_devices=5)
    fleet_manager = DeviceFleetManager(config)
    
    try:
        # Create fleet
        devices = await fleet_manager.create_fleet()
        print(f"Created {len(devices)} devices")
        
        # Check device instances
        for device_id, device_instance in devices.items():
            print(f"Device {device_id}: {device_instance.device_type}")
            print(f"  Location: {device_instance.location}")
            print(f"  Status: {device_instance.status}")
        
        # Test individual device creation
        print("Testing individual device creation...")
        test_device = await fleet_manager._create_device(devices[1000])
        print(f"Test device created: {test_device is not None}")
        
        # Check configuration
        print(f"Start stagger: {fleet_manager.config.start_stagger}")
        print(f"Enable failures: {fleet_manager.config.enable_failures}")
        
    except Exception as e:
        print(f"Fleet startup error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(debug_fleet_startup())
```

#### High Error Rates
```python
# Issue: High error rates in fleet
# Debug code
import asyncio
from mock_devices.device_fleet import FleetConfig, DeviceFleetManager

async def debug_high_errors():
    config = FleetConfig(total_devices=10, enable_failures=False)  # Disable failures
    fleet_manager = DeviceFleetManager(config)
    
    try:
        await fleet_manager.create_fleet()
        await fleet_manager.start_fleet()
        
        # Monitor for 2 minutes
        for i in range(12):  # 12 * 10 seconds = 2 minutes
            await asyncio.sleep(10)
            
            stats = fleet_manager.get_fleet_statistics()
            error_rate = stats['performance_metrics']['error_rate']
            
            print(f"Minute {i+1}: Error rate = {error_rate:.4f}")
            
            if error_rate > 0.05:  # 5% error rate threshold
                print("High error rate detected!")
                
                # Check individual devices
                for device_id, device_instance in fleet_manager.devices.items():
                    if device_instance.device_class:
                        device_info = device_instance.device_class.get_device_info()
                        device_errors = device_info.get('error_count', 0)
                        if device_errors > 0:
                            print(f"  Device {device_id}: {device_errors} errors")
                            print(f"    Status: {device_instance.status}")
                            print(f"    MQTT connected: {device_info.get('mqtt_connected', False)}")
    
    finally:
        await fleet_manager.stop_fleet()

asyncio.run(debug_high_errors())
```

---

## Performance Issues

### Memory Usage

#### High Memory Consumption
```python
# Issue: High memory usage with large fleets
# Solution: Optimize history size and data retention

# Reduce history size in device configuration
sensor.max_history_size = 500  # Instead of 1440

# Clean up old data periodically
async def cleanup_old_data(device):
    """Clean up old telemetry data"""
    if len(device.temperature_history) > device.max_history_size:
        device.temperature_history = device.temperature_history[-device.max_history_size:]
    
    # Clean up other history data as needed
    if hasattr(device, 'vibration_history'):
        if len(device.vibration_history) > device.max_history_size:
            device.vibration_history = device.vibration_history[-device.max_history_size:]

# Monitor memory usage
import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    memory_mb = memory_info.rss / 1024 / 1024
    
    print(f"Memory usage: {memory_mb:.2f} MB")
    
    if memory_mb > 500:  # 500 MB threshold
        print("High memory usage detected!")
        print("Consider reducing fleet size or history size")
    
    return memory_mb
```

#### CPU Usage Optimization
```python
# Issue: High CPU usage
# Solution: Optimize telemetry intervals and reduce processing

# Increase telemetry intervals
device.config.telemetry_interval = 60  # Instead of 30

# Use async operations efficiently
async def optimized_telemetry_generation(device):
    """Optimized telemetry generation"""
    # Generate all telemetry in one call
    telemetry = await device.generate_telemetry()
    
    # Batch send telemetry
    if telemetry:
        await device._send_telemetry_batch(telemetry)

# Implement rate limiting
import asyncio
from asyncio import Semaphore

class RateLimiter:
    def __init__(self, rate_limit: int):
        self.semaphore = Semaphore(rate_limit)
        self.rate_limit = rate_limit
    
    async def acquire(self):
        await self.semaphore.acquire()
    
    def release(self):
        self.semaphore.release()

# Use rate limiter for fleet operations
rate_limiter = RateLimiter(10)  # Limit to 10 concurrent operations
```

### Network Performance

#### MQTT Connection Issues
```python
# Issue: MQTT connection drops
# Solution: Implement robust reconnection logic

class RobustMQTTClient:
    def __init__(self, broker_host, broker_port):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 5
    
    async def connect_with_retry(self):
        """Connect with automatic retry"""
        while self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                self.client = mqtt.Client()
                self.client.connect(self.broker_host, self.broker_port, 60)
                self.client.loop_start()
                self.reconnect_attempts = 0
                return True
            except Exception as e:
                self.reconnect_attempts += 1
                print(f"MQTT connection failed (attempt {self.reconnect_attempts}): {e}")
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay *= 2  # Exponential backoff
        
        return False
```

#### API Rate Limiting
```python
# Issue: API rate limiting
# Solution: Implement rate limiting and batching

class RateLimitedAPIClient:
    def __init__(self, base_url, rate_limit=10):
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.request_times = []
    
    async def make_request(self, method, endpoint, data=None):
        """Make rate-limited API request"""
        # Check rate limit
        now = time.time()
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        if len(self.request_times) >= self.rate_limit:
            sleep_time = 60 - (now - self.request_times[0])
            await asyncio.sleep(sleep_time)
        
        # Make request
        self.request_times.append(now)
        return await self._make_request(method, endpoint, data)
    
    async def batch_requests(self, requests):
        """Batch multiple requests"""
        results = []
        for request in requests:
            result = await self.make_request(**request)
            results.append(result)
        return results
```

---

## Debugging Techniques

### Logging and Monitoring

#### Enable Debug Logging
```python
import logging
import sys

# Configure debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mock_devices_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Enable specific logger debugging
logger = logging.getLogger('mock_device')
logger.setLevel(logging.DEBUG)

# Add debug logging to device
class DebuggableDevice(BaseDevice):
    def __init__(self, config):
        super().__init__(config)
        self.debug_mode = True
    
    def debug_log(self, message):
        if self.debug_mode:
            self.logger.debug(f"[{self.device_id}] {message}")
    
    async def generate_telemetry(self):
        self.debug_log("Starting telemetry generation")
        
        try:
            telemetry = await super().generate_telemetry()
            self.debug_log(f"Generated {len(telemetry)} telemetry points")
            
            for data in telemetry:
                self.debug_log(f"  {data.metric_name}: {data.metric_value}")
            
            return telemetry
        except Exception as e:
            self.debug_log(f"Telemetry generation failed: {e}")
            raise
```

#### Performance Monitoring
```python
import time
import psutil
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        try:
            result = await func(*args, **kwargs)
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            
            execution_time = end_time - start_time
            memory_delta = (end_memory - start_memory) / 1024 / 1024  # MB
            
            print(f"Function {func.__name__}:")
            print(f"  Execution time: {execution_time:.3f}s")
            print(f"  Memory delta: {memory_delta:.2f} MB")
            
            return result
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Function {func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper

# Apply to device methods
class MonitoredDevice(BaseDevice):
    @monitor_performance
    async def generate_telemetry(self):
        return await super().generate_telemetry()
    
    @monitor_performance
    async def start(self):
        return await super().start()
```

### Data Validation

#### Validate Telemetry Data
```python
def validate_telemetry(telemetry_data):
    """Validate telemetry data"""
    errors = []
    
    for data in telemetry_data:
        # Check required fields
        if not data.metric_name:
            errors.append(f"Missing metric name in telemetry data")
        
        if data.unit is None:
            errors.append(f"Missing unit for {data.metric_name}")
        
        if data.timestamp is None:
            errors.append(f"Missing timestamp for {data.metric_name}")
        
        # Check data types
        if not isinstance(data.metric_value, (int, float)):
            errors.append(f"Invalid metric value type for {data.metric_name}")
        
        # Check value ranges (example for temperature)
        if data.metric_name == "temperature":
            if not (-50 <= data.metric_value <= 100):
                errors.append(f"Temperature {data.metric_value} out of range")
        
        # Check timestamp
        if data.timestamp and data.timestamp > datetime.utcnow():
            errors.append(f"Future timestamp for {data.metric_name}")
    
    return errors

# Use validation
async def generate_validated_telemetry(device):
    """Generate and validate telemetry"""
    telemetry = await device.generate_telemetry()
    
    errors = validate_telemetry(telemetry)
    if errors:
        print(f"Telemetry validation errors:")
        for error in errors:
            print(f"  - {error}")
    
    return telemetry
```

#### Device Health Checks
```python
async def comprehensive_health_check(device):
    """Comprehensive device health check"""
    health_report = {
        'device_id': device.device_id,
        'timestamp': datetime.utcnow(),
        'checks': {}
    }
    
    # Check MQTT connection
    health_report['checks']['mqtt'] = {
        'status': 'healthy' if device.mqtt_connected else 'unhealthy',
        'details': f"Connected: {device.mqtt_connected}"
    }
    
    # Check error rate
    error_rate = device.error_count / max(1, device.total_telemetry_points)
    health_report['checks']['error_rate'] = {
        'status': 'healthy' if error_rate < 0.05 else 'unhealthy',
        'details': f"Error rate: {error_rate:.4f}"
    }
    
    # Check telemetry generation
    try:
        telemetry = await device.generate_telemetry()
        health_report['checks']['telemetry'] = {
            'status': 'healthy',
            'details': f"Generated {len(telemetry)} points"
        }
    except Exception as e:
        health_report['checks']['telemetry'] = {
            'status': 'unhealthy',
            'details': f"Error: {e}"
        }
    
    # Check memory usage
    memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
    health_report['checks']['memory'] = {
        'status': 'healthy' if memory_mb < 100 else 'warning',
        'details': f"Memory usage: {memory_mb:.2f} MB"
    }
    
    return health_report
```

---

## Configuration Issues

### MQTT Configuration

#### Common MQTT Problems
```json
// Issue: Incorrect MQTT configuration
// Solution: Verify configuration in config.json
{
  "mqtt": {
    "broker_host": "localhost",  // Check if correct
    "broker_port": 1883,        // Check if port is correct
    "username": "valtronics_user",
    "password": "valtronics_password",
    "keepalive": 60,
    "qos": 1
  }
}

// Test MQTT configuration
// mosquitto_pub -h localhost -p 1883 -u valtronics_user -P valtronics_password -t test/topic -m "test"
```

#### MQTT Broker Configuration
```bash
# /etc/mosquitto/mosquitto.conf
# Basic MQTT broker configuration

# Allow anonymous connections (for testing)
allow_anonymous true

# Enable authentication
# password_file /etc/mosquitto/passwd

# Set up persistence
persistence true
persistence_location /var/lib/mosquitto/

# Log settings
log_dest file /var/log/mosquitto/mosquitto.log
log_type error
log_type warning
log_type notice
log_type information

# Connection logging
connection_messages true
log_timestamp true
```

### API Configuration

#### API Server Configuration
```python
# Issue: API server not accessible
# Solution: Check API configuration and server status

# Test API connection
import requests

def test_api_connection(base_url="http://localhost:8000"):
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("API server is accessible")
            return True
        else:
            print(f"API server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("Cannot connect to API server")
        return False
    except requests.exceptions.Timeout:
        print("API server timeout")
        return False

# Check API endpoints
def check_api_endpoints(base_url="http://localhost:8000"):
    endpoints = [
        "/health",
        "/api/v1/devices/",
        "/api/v1/telemetry/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✓" if response.status_code in [200, 404] else "✗"
            print(f"{status} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"✗ {endpoint}: {e}")
```

---

## Environment-Specific Issues

### Docker Environment

#### Docker Network Issues
```bash
# Issue: MQTT connection fails in Docker
# Solution: Use Docker networking properly

# Create Docker network
docker network create valtronics-network

# Run MQTT broker in network
docker run -d --name mosquitto \
  --network valtronics-network \
  -p 1883:1883 \
  eclipse-mosquitto

# Run mock devices in network
docker run -d --name mock-devices \
  --network valtronics-network \
  -v $(pwd)/config.json:/app/config.json \
  valtronics/mock-devices

# Use service names instead of localhost
# In config.json:
{
  "mqtt": {
    "broker_host": "mosquitto",  // Use service name
    "broker_port": 1883
  }
}
```

#### Docker Volume Issues
```bash
# Issue: Configuration not loading in Docker
# Solution: Mount volumes correctly

# Mount configuration file
docker run -d --name mock-devices \
  -v $(pwd)/config.json:/app/config.json \
  -v $(pwd)/requirements.txt:/app/requirements.txt \
  valtronics/mock-devices

# Check file permissions
ls -la config.json
chmod 644 config.json

# Verify file content in container
docker exec mock-devices cat /app/config.json
```

### Development Environment

#### Virtual Environment Issues
```bash
# Issue: Package not found in virtual environment
# Solution: Ensure virtual environment is activated

# Create and activate virtual environment
python -m venv mock-devices-env
source mock-devices-env/bin/activate  # Linux/Mac
# or
mock-devices-env\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep mock

# Check Python path
which python
python --version
```

#### Path Issues
```python
# Issue: Import errors
# Solution: Fix Python path

import sys
import os

# Add mock devices to path
mock_devices_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, mock_devices_path)

# Test imports
try:
    from mock_devices.environmental.temperature_sensor import TemperatureSensor
    print("Import successful")
except ImportError as e:
    print(f"Import failed: {e}")
    print(f"Python path: {sys.path}")
```

---

## Recovery Procedures

### Device Recovery

#### Automatic Recovery
```python
class ResilientDevice(BaseDevice):
    def __init__(self, config):
        super().__init__(config)
        self.recovery_attempts = 0
        self.max_recovery_attempts = 5
        self.recovery_backoff = 10
    
    async def start_with_recovery(self):
        """Start device with automatic recovery"""
        while self.recovery_attempts < self.max_recovery_attempts:
            try:
                await self.start()
                self.recovery_attempts = 0
                return True
            except Exception as e:
                self.recovery_attempts += 1
                self.logger.error(f"Device start failed (attempt {self.recovery_attempts}): {e}")
                
                if self.recovery_attempts < self.max_recovery_attempts:
                    await asyncio.sleep(self.recovery_backoff)
                    self.recovery_backoff *= 2  # Exponential backoff
                else:
                    raise Exception(f"Device start failed after {self.max_recovery_attempts} attempts")
        
        return False
    
    async def monitor_and_recover(self):
        """Monitor device and recover from failures"""
        while self.running:
            try:
                health = await self.perform_health_check()
                
                if health != DeviceStatus.ONLINE:
                    self.logger.warning(f"Device health degraded: {health.value}")
                    
                    # Attempt recovery
                    if await self.attempt_recovery():
                        self.logger.info("Device recovery successful")
                    else:
                        self.logger.error("Device recovery failed")
                        break
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Health monitoring failed: {e}")
                await asyncio.sleep(30)
    
    async def attempt_recovery(self):
        """Attempt to recover device"""
        try:
            # Stop device
            await self.stop()
            
            # Wait before restart
            await asyncio.sleep(5)
            
            # Restart device
            await self.start()
            
            return True
        except Exception as e:
            self.logger.error(f"Recovery attempt failed: {e}")
            return False
```

#### Fleet Recovery
```python
class ResilientFleetManager(DeviceFleetManager):
    def __init__(self, config):
        super().__init__(config)
        self.recovery_enabled = True
        self.recovery_interval = 300  # 5 minutes
    
    async def monitor_and_recover_fleet(self):
        """Monitor fleet and recover failed devices"""
        while self.running:
            try:
                # Check for failed devices
                failed_devices = [
                    device_id for device_id, device_instance in self.devices.items()
                    if device_instance.status == "error"
                ]
                
                if failed_devices:
                    self.logger.info(f"Attempting recovery for {len(failed_devices)} devices")
                    
                    for device_id in failed_devices:
                        device_instance = self.devices[device_id]
                        
                        if await self.recover_device(device_instance):
                            self.logger.info(f"Device {device_id} recovered successfully")
                        else:
                            self.logger.error(f"Device {device_id} recovery failed")
                
                await asyncio.sleep(self.recovery_interval)
                
            except Exception as e:
                self.logger.error(f"Fleet recovery monitoring failed: {e}")
                await asyncio.sleep(60)
    
    async def recover_device(self, device_instance):
        """Recover a single device"""
        try:
            # Reset device state
            device_instance.status = "recovering"
            device_instance.error_count = 0
            
            # Restart device
            if device_instance.device_class:
                await device_instance.device_class.start()
                device_instance.status = "running"
                return True
            
        except Exception as e:
            self.logger.error(f"Device recovery failed: {e}")
            device_instance.status = "error"
            device_instance.error_count += 1
        
        return False
```

---

## Performance Optimization

### Memory Optimization

#### Reduce Memory Footprint
```python
# Use generators instead of lists
def generate_telemetry_stream(device, duration_minutes):
    """Generate telemetry as a stream"""
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    while datetime.utcnow() < end_time:
        telemetry = await device.generate_telemetry()
        yield telemetry
        await asyncio.sleep(device.config.telemetry_interval)

# Use circular buffers for history
from collections import deque

class CircularBuffer:
    def __init__(self, max_size):
        self.buffer = deque(maxlen=max_size)
    
    def append(self, item):
        self.buffer.append(item)
    
    def get_recent(self, count):
        return list(self.buffer)[-count:]

# Use in device
class MemoryOptimizedDevice(BaseDevice):
    def __init__(self, config):
        super().__init__(config)
        self.temperature_buffer = CircularBuffer(500)  # Reduced size
```

### CPU Optimization

#### Batch Processing
```python
class BatchProcessor:
    def __init__(self, batch_size=10, flush_interval=30):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batch = []
        self.last_flush = time.time()
    
    async def add_telemetry(self, telemetry):
        """Add telemetry to batch"""
        self.batch.extend(telemetry)
        
        # Flush if batch is full or time interval passed
        if (len(self.batch) >= self.batch_size or 
            time.time() - self.last_flush > self.flush_interval):
            await self.flush_batch()
    
    async def flush_batch(self):
        """Flush telemetry batch"""
        if self.batch:
            await self._send_telemetry_batch(self.batch)
            self.batch.clear()
            self.last_flush = time.time()
```

---

## Support

For troubleshooting support:
- **Overview**: [Mock Devices Overview](mock-devices-overview.md)
- **Reference**: [Device Reference](device-reference.md)
- **Usage Examples**: [Usage Examples](usage-examples.md)
- **Development**: [Development Setup](../08-development/development-setup.md)
- **API Integration**: [API Overview](../03-api/api-overview.md)
- **Email**: autobotsolution@gmail.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Mock Devices Troubleshooting Guide v1.0**
