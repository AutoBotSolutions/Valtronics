# Mock Devices Usage Examples

**Practical examples and use cases for Valtronics Mock Devices**

---

## Overview

This guide provides comprehensive usage examples for the Valtronics Mock Devices system, covering individual device operation, fleet management, data analysis, and integration scenarios.

---

## Quick Start Examples

### Single Device Quick Start

#### Temperature Sensor Example
```python
import asyncio
from mock_devices.environmental.temperature_sensor import TemperatureSensor

async def temperature_sensor_example():
    """Complete temperature sensor example"""
    # Create sensor
    sensor = TemperatureSensor(1001, "Server Room A")
    
    print(f"Created sensor: {sensor.device_name}")
    print(f"Location: {sensor.config.location}")
    
    try:
        # Configure sensor
        sensor.add_heat_source("Server Rack 1", intensity=5.0, proximity_factor=0.8)
        sensor.add_heat_source("Server Rack 2", intensity=3.0, proximity_factor=0.6)
        sensor.set_ventilation_rate(0.7)
        
        print("Sensor configured successfully")
        
        # Start sensor
        await sensor.start()
        print("Sensor started successfully")
        
        # Run for 2 minutes
        await asyncio.sleep(120)
        
        # Get statistics
        stats = sensor.get_temperature_statistics()
        print(f"Temperature stats: {stats}")
        
        # Get device info
        info = sensor.get_device_info()
        print(f"Device info: {info['current_temperature']}°C")
        
    except KeyboardInterrupt:
        print("Stopping sensor...")
    finally:
        await sensor.stop()
        print("Sensor stopped")

if __name__ == "__main__":
    asyncio.run(temperature_sensor_example())
```

#### Air Quality Monitor Example
```python
import asyncio
from mock_devices.environmental.air_quality_monitor import AirQualityMonitor

async def air_quality_example():
    """Air quality monitoring with pollution sources"""
    # Create monitor
    monitor = AirQualityMonitor(4001, "Office Building A")
    
    # Configure environmental factors
    monitor.set_ventilation_rate(0.3)  # Poor ventilation
    monitor.set_occupancy_level(1.5)      # High occupancy
    monitor.set_weather_conditions("sunny")
    
    # Add pollution sources
    monitor.add_pollution_source("Traffic", "all", intensity=15.0, proximity_factor=0.8)
    monitor.add_pollution_source("HVAC System", "voc", intensity=5.0, proximity_factor=0.5)
    monitor.add_pollution_source("Cleaning Supplies", "voc", intensity=3.0, proximity_factor=0.3)
    
    try:
        await monitor.start()
        
        # Monitor for 5 minutes
        for i in range(5):
            await asyncio.sleep(60)
            
            stats = monitor.get_air_quality_statistics()
            print(f"Minute {i+1}: AQI={stats['current_aqi']} ({stats['aqi_level']})")
            print(f"  PM2.5: {stats['current_readings']['pm25']} μg/m³")
            print(f"  CO2: {stats['current_readings']['co2']} ppm")
            print(f"  Active pollution sources: {stats['environmental_factors']['pollution_sources']}")
            
            # Alert if AQI is high
            if stats['current_aqi'] > 100:
                print("  ⚠️  High AQI alert!")
    
    except KeyboardInterrupt:
        print("Stopping monitor...")
    finally:
        await monitor.stop()

if __name__ == "__main__":
    asyncio.run(air_quality_example())
```

---

## Fleet Management Examples

### Basic Fleet Operation
```python
import asyncio
from mock_devices.device_fleet import FleetConfig, DeviceFleetManager

async def basic_fleet_example():
    """Basic fleet management example"""
    # Configure fleet
    config = FleetConfig(
        total_devices=15,
        device_distribution={
            "temperature_sensor": 8,
            "humidity_sensor": 4,
            "air_quality_monitor": 3
        },
        locations=[
            "Server Room A", "Server Room B", "Data Center 1",
            "Office Building A", "Office Building B"
        ],
        start_stagger=3,
        enable_failures=False,
        enable_anomalies=True,
        anomaly_rate=0.02
    )
    
    # Create fleet manager
    fleet_manager = DeviceFleetManager(config)
    
    try:
        # Create fleet
        await fleet_manager.create_fleet()
        print(f"Created {len(fleet_manager.devices)} devices")
        
        # Start fleet
        await fleet_manager.start_fleet()
        
        # Monitor fleet for 10 minutes
        start_time = datetime.utcnow()
        while (datetime.utcnow() - start_time).total_seconds() < 600:
            await asyncio.sleep(60)
            
            stats = fleet_manager.get_fleet_statistics()
            print(f"Fleet Status:")
            print(f"  Running: {stats['status_distribution'].get('running', 0)}")
            print(f"  Errors: {stats['status_distribution'].get('error', 0)}")
            print(f"  Telemetry: {stats['performance_metrics']['total_telemetry_points']}")
            print(f"  Errors: {stats['performance_metrics']['total_errors']}")
            
            # Check for issues
            error_rate = stats['performance_metrics']['error_rate']
            if error_rate > 0.05:  # 5% error rate
                print(f"  ⚠️  High error rate: {error_rate:.4f}")
    
    except KeyboardInterrupt:
        print("Shutting down fleet...")
    finally:
        await fleet_manager.stop_fleet()
        
        # Export final statistics
        final_stats = fleet_manager.get_fleet_statistics()
        print(f"\nFinal Fleet Statistics:")
        print(f"  Total Telemetry Points: {final_stats['performance_metrics']['total_telemetry_points']}")
        print(f"  Total Errors: {final_stats['performance_metrics']['total_errors']}")
        print(f"  Uptime: {final_stats['fleet_info']['uptime_hours']:.2f} hours")
        
        # Export configuration
        fleet_manager.export_fleet_config("fleet_config.json")
        print("Fleet configuration exported to fleet_config.json")

if __name__ == "__main__":
    asyncio.run(basic_fleet_example())
```

### Advanced Fleet with Failures
```python
import asyncio
from mock_devices.device_fleet import FleetConfig, DeviceFleetManager

async def fleet_with_failures_example():
    """Fleet with simulated failures and recovery"""
    config = FleetConfig(
        total_devices=25,
        device_distribution={
            "temperature_sensor": 10,
            "humidity_sensor": 8,
            "pressure_sensor": 7
        },
        start_stagger=2,
        enable_failures=True,
        failure_rate=0.01,  # 1% failure rate
        enable_anomalies=True,
        anomaly_rate=0.03
    )
    
    fleet_manager = DeviceFleetManager(config)
    
    try:
        await fleet_manager.create_fleet()
        await fleet_manager.start_fleet()
        
        # Monitor with failure handling
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while consecutive_errors < max_consecutive_errors:
            await asyncio.sleep(30)
            
            try:
                stats = fleet_manager.get_fleet_statistics()
                
                # Check for high error rate
                error_rate = stats['performance_metrics']['error_rate']
                if error_rate > 0.1:  # 10% error rate
                    print(f"⚠️  High error rate detected: {error_rate:.4f}")
                    
                    # Get error details
                    error_devices = [d for d in fleet_manager.devices.values() 
                                  if d.status == "error"]
                    print(f"Error devices: {[d.device_id for d in error_devices[:5]]")
                    
                    consecutive_errors += 1
                else:
                    consecutive_errors = 0
                    print(f"✅ Fleet healthy - Error rate: {error_rate:.4f}")
                
                # Show fleet status
                status_counts = stats['status_distribution']
                print(f"Status: {status_counts}")
                
            except Exception as e:
                print(f"Error monitoring fleet: {e}")
                consecutive_errors += 1
    
    except KeyboardInterrupt:
        print("Shutting down fleet...")
    finally:
        await fleet_manager.stop_fleet()

if __name__ == "__main__":
    asyncio.run(fleet_with_failures_example())
```

---

## Data Analysis Examples

### Telemetry Data Collection
```python
import asyncio
import json
import pandas as pd
from datetime import datetime, timedelta
from mock_devices.environmental.temperature_sensor import TemperatureSensor

class TelemetryCollector:
    def __init__(self):
        self.telemetry_data = []
        self.start_time = datetime.utcnow()
    
    async def collect_data(self, device, duration_minutes=5):
        """Collect telemetry data from a device"""
        print(f"Collecting data for {duration_minutes} minutes...")
        
        # Override device's telemetry method to capture data
        original_generate = device.generate_telemetry
        collected_data = []
        
        async def capture_telemetry():
            telemetry = await original_generate()
            for data in telemetry:
                collected_data.append({
                    'timestamp': data.timestamp,
                    'metric_name': data.metric_name,
                    'value': data.metric_value,
                    'unit': data.unit,
                    'metadata': data.metadata
                })
            return telemetry
        
        device.generate_telemetry = capture_telemetry
        
        # Start device and collect data
        await device.start()
        
        try:
            await asyncio.sleep(duration_minutes * 60)
        finally:
            await device.stop()
        
        # Store collected data
        self.telemetry_data.extend(collected_data)
        print(f"Collected {len(collected_data)} data points")
        
        return collected_data

async def data_analysis_example():
    """Collect and analyze telemetry data"""
    # Create collector
    collector = TelemetryCollector()
    
    # Create and configure sensor
    sensor = TemperatureSensor(1001, "Test Lab")
    sensor.add_heat_source("Equipment A", intensity=8.0, proximity_factor=0.7)
    sensor.set_ventilation_rate(0.4)
    
    # Collect data for 3 minutes
    data = await collector.collect_data(sensor, duration_minutes=3)
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(data)
    
    # Basic analysis
    print(f"Data Analysis Results:")
    print(f"  Total data points: {len(df)}")
    print(f"  Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"  Average temperature: {df['value'].mean():.2f}°C")
    print(f"  Min temperature: {df['value'].min():.2f}°C")
    print(f"  Max temperature: {df['value'].max():.2f}°C")
    print(f"  Standard deviation: {df['value'].std():.2f}°C")
    
    # Export data
    df.to_csv('temperature_data.csv', index=False)
    print("Data exported to temperature_data.csv")
    
    # Create simple plot (if matplotlib available)
    try:
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(12, 6))
        plt.plot(df['timestamp'], df['value'], label='Temperature')
        plt.title('Temperature Over Time')
        plt.xlabel('Time')
        plt.ylabel('Temperature (°C)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('temperature_plot.png')
        plt.show()
        print("Plot saved to temperature_plot.png")
        
    except ImportError:
        print("Matplotlib not available for plotting")

if __name__ == "__main__":
    asyncio.run(data_analysis_example())
```

### Multi-Device Correlation Analysis
```python
import asyncio
import pandas as pd
import numpy as np
from mock_devices.environmental.temperature_sensor import TemperatureSensor
from mock_devices.environmental.humidity_sensor import HumiditySensor

async def correlation_analysis_example():
    """Analyze correlation between temperature and humidity"""
    # Create sensors
    temp_sensor = TemperatureSensor(1001, "Test Lab")
    humidity_sensor = HumiditySensor(2001, "Test Lab")
    
    # Configure sensors with correlation
    temp_sensor.add_heat_source("Equipment", intensity=5.0, proximity_factor=0.8)
    temp_sensor.set_ventilation_rate(0.5)
    
    humidity_sensor.set_temperature_coupling(0.8)
    humidity_sensor.add_humidity_source("Water Source", intensity=6.0, proximity_factor=0.7)
    
    # Data collection
    temp_data = []
    humidity_data = []
    
    async def collect_telemetry(device, data_list):
        original_generate = device.generate_telemetry
        async def capture():
            telemetry = await original_generate()
            for data in telemetry:
                data_list.append({
                    'timestamp': data.timestamp,
                    'value': data.metric_value
                })
            return telemetry
        device.generate_telemetry = capture
    
    # Start sensors
    await temp_sensor.start()
    await humidity_sensor.start()
    
    try:
        # Collect data for 5 minutes
        await asyncio.sleep(300)
    finally:
        await temp_sensor.stop()
        await humidity_sensor.stop()
    
    # Convert to DataFrames
    temp_df = pd.DataFrame(temp_data)
    humidity_df = pd.DataFrame(humidity_data)
    
    # Merge data on timestamp (approximate)
    merged_df = pd.merge_asof(temp_df, humidity_df, on='timestamp', direction='nearest')
    
    # Calculate correlation
    correlation = merged_df['value_x'].corr(merged_df['value_y'])
    
    print(f"Temperature-Humidity Correlation Analysis:")
    print(f"  Temperature data points: {len(temp_df)}")
    print(f"  Humidity data points: {len(humidity_df)}")
    print(f"  Merged data points: {len(merged_df)}")
    print(f"  Correlation coefficient: {correlation:.4f}")
    
    if correlation < -0.5:
        print("  ✅ Strong negative correlation (as expected)")
    elif correlation < -0.3:
        print("  ⚠️  Moderate negative correlation")
    else:
        print("  ❌ Weak or no correlation")
    
    # Export data
    merged_df.to_csv('temperature_humidity_correlation.csv', index=False)
    print("Correlation data exported to temperature_humidity_correlation.csv")
    
    # Create scatter plot
    try:
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 6))
        plt.scatter(merged_df['value_x'], merged_df['value_y'], alpha=0.6)
        plt.xlabel('Temperature (°C)')
        plt.ylabel('Humidity (%)')
        plt.title(f'Temperature vs Humidity (Correlation: {correlation:.3f})')
        plt.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(merged_df['value_x'], merged_df['value_y'], 1)
        p = np.poly1d(z)
        plt.plot(merged_df['value_x'], p(merged_df['value_x']), "r--", alpha=0.8)
        
        plt.tight_layout()
        plt.savefig('correlation_plot.png')
        plt.show()
        print("Correlation plot saved to correlation_plot.png")
        
    except ImportError:
        print("Matplotlib not available for plotting")

if __name__ == "__main__":
    asyncio.run(correlation_analysis_example())
```

---

## Integration Examples

### Database Integration
```python
import asyncio
import sqlite3
import json
from datetime import datetime
from mock_devices.device_fleet import FleetConfig, DeviceFleetManager

class DatabaseIntegration:
    def __init__(self, db_path="telemetry.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                device_id INTEGER PRIMARY KEY,
                device_name TEXT,
                device_type TEXT,
                location TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER,
                metric_name TEXT,
                value REAL,
                unit TEXT,
                timestamp TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (device_id) REFERENCES devices (device_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER,
                alert_type TEXT,
                severity TEXT,
                message TEXT,
                metric_value REAL,
                threshold_value REAL,
                created_at TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices (device_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def register_device(self, device):
        """Register device in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO devices 
            (device_id, device_name, device_type, location, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            device.device_id,
            device.device_name,
            device.device_type.value,
            device.config.location,
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        conn.commit()
        conn.close()
    
    def store_telemetry(self, device_id, telemetry_data):
        """Store telemetry data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for data in telemetry_data:
            cursor.execute("""
                INSERT INTO telemetry 
                (device_id, metric_name, value, unit, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                device_id,
                data.metric_name,
                data.metric_value,
                data.unit,
                data.timestamp,
                json.dumps(data.metadata) if data.metadata else None
            ))
        
        conn.commit()
        conn.close()
    
    def store_alert(self, device_id, alert_data):
        """Store alert data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO alerts 
            (device_id, alert_type, severity, message, metric_value, threshold_value, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            device_id,
            alert_data.get('title', ''),
            alert_data.get('severity', ''),
            alert_data.get('description', ''),
            alert_data.get('metric_value', 0),
            alert_data.get('threshold_value', 0),
            datetime.utcnow()
        ))
        
        conn.commit()
        conn.close()
    
    def get_device_telemetry(self, device_id, hours=24):
        """Get telemetry data for a device"""
        conn = sqlite3.connect(self.db_path)
        
        cursor = conn.execute("""
            SELECT * FROM telemetry 
            WHERE device_id = ? 
            AND timestamp > datetime('now', '-{} hours')
            ORDER BY timestamp
        """, (device_id, hours))
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]

async def database_integration_example():
    """Example of database integration with mock devices"""
    # Create database integration
    db_integration = DatabaseIntegration()
    
    # Create fleet
    config = FleetConfig(
        total_devices=5,
        device_distribution={
            "temperature_sensor": 3,
            "humidity_sensor": 2
        }
    )
    
    fleet_manager = DeviceFleetManager(config)
    
    # Override device methods to integrate with database
    original_start = BaseDevice.start
    async def start_with_db_integration(self):
        # Register device
        db_integration.register_device(self)
        
        # Override telemetry generation to store in database
        original_generate = self.generate_telemetry
        async def generate_and_store():
            telemetry = await original_generate()
            db_integration.store_telemetry(self.device_id, telemetry)
            return telemetry
        self.generate_telemetry = generate_and_store
        
        # Start device
        await original_start(self)
    
    # Apply override to all devices
    for device_instance in fleet_manager.devices.values():
        device_instance.device_class.start = start_with_db_integration.__get__(device_instance.device_class)
    
    try:
        await fleet_manager.create_fleet()
        await fleet_manager.start_fleet()
        
        # Run for 2 minutes
        await asyncio.sleep(120)
        
        # Query database
        print("Database Query Results:")
        for device_id in fleet_manager.devices.keys():
            telemetry = db_integration.get_device_telemetry(device_id, hours=0.1)
            if telemetry:
                latest = telemetry[-1]
                print(f"  Device {device_id}: {latest['metric_name']} = {latest['value']} {latest['unit']}")
        
    finally:
        await fleet_manager.stop_fleet()

if __name__ == "__main__":
    asyncio.run(database_integration_example())
```

### Prometheus Metrics Integration
```python
import asyncio
import time
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram
from mock_devices.device_fleet import FleetConfig, DeviceFleetManager

class PrometheusMetrics:
    def __init__(self):
        self.registry = CollectorRegistry()
        
        # Create metrics
        self.telemetry_counter = Counter(
            'mock_devices_telemetry_total',
            'Total telemetry points generated',
            registry=self.registry
        )
        
        self.error_counter = Counter(
            'mock_devices_errors_total',
            'Total errors encountered',
            registry=self.registry
        )
        
        self.device_gauge = Gauge(
            'mock_devices_active',
            'Number of active devices',
            registry=self.registry
        )
        
        self.alert_counter = Counter(
            'mock_devices_alerts_total',
            'Total alerts generated',
            registry=self.registry
        )
        
        self.telemetry_histogram = Histogram(
            'mock_devices_telemetry_duration',
            'Time taken to generate telemetry',
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
    
    def update_metrics(self, fleet_manager):
        """Update Prometheus metrics"""
        # Update device count
        active_devices = len([d for d in fleet_manager.devices.values() if d.status == 'running'])
        self.device_gauge.set(active_devices)
        
        # Update counters
        self.telemetry_counter._value._value = fleet_manager.total_telemetry_points
        self.error_counter._value._value = fleet_manager.total_errors
        self.alert_counter._value._value = fleet_manager.total_alerts

async def prometheus_integration_example():
    """Example of Prometheus metrics integration"""
    # Create metrics
    metrics = PrometheusMetrics()
    
    # Create fleet
    config = FleetConfig(
        total_devices=10,
        enable_failures=True,
        failure_rate=0.01
    )
    
    fleet_manager = DeviceFleetManager(config)
    
    # Start metrics server
    from prometheus_client import start_http_server
    start_http_server(metrics.registry, port=8001)
    
    try:
        await fleet_manager.create_fleet()
        await fleet_manager.start_fleet()
        
        # Update metrics every 10 seconds
        while True:
            metrics.update_metrics(fleet_manager)
            await asyncio.sleep(10)
            
            # Print current metrics
            print(f"Metrics - Devices: {metrics.device_gauge._value.get()}, "
                  f"Telemetry: {metrics.telemetry_counter._value.get()}, "
                  f"Errors: {metrics.error_counter._value.get()}, "
                  f"Alerts: {metrics.alert_counter._value.get()}")
    
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        await fleet_manager.stop_fleet()

if __name__ == "__main__":
    asyncio.run(prometheus_integration_example())
```

---

## Testing Examples

### Load Testing
```python
import asyncio
import time
import statistics
from mock_devices.device_fleet import FleetConfig, DeviceFleetManager

class LoadTester:
    def __init__(self):
        self.results = {
            'telemetry_rates': [],
            'error_rates': [],
            'response_times': [],
            'memory_usage': [],
            'cpu_usage': []
        }
    
    async def run_load_test(self, fleet_config, duration_minutes=10):
        """Run load test on fleet"""
        print(f"Starting load test with {fleet_config.total_devices} devices for {duration_minutes} minutes")
        
        fleet_manager = DeviceFleetManager(fleet_config)
        
        start_time = time.time()
        
        try:
            await fleet_manager.create_fleet()
            fleet_start_time = time.time()
            
            await fleet_manager.start_fleet()
            
            # Monitor performance during test
            test_duration = duration_minutes * 60
            check_interval = 10  # Check every 10 seconds
            
            for _ in range(0, test_duration // check_interval):
                await asyncio.sleep(check_interval)
                
                current_time = time.time()
                elapsed = current_time - start_time
                fleet_elapsed = current_time - fleet_start_time
                
                # Get fleet statistics
                stats = fleet_manager.get_fleet_statistics()
                
                # Calculate metrics
                telemetry_rate = stats['performance_metrics']['total_telemetry_points'] / max(1, elapsed)
                error_rate = stats['performance_metrics']['error_rate']
                
                self.results['telemetry_rates'].append(telemetry_rate)
                self.results['error_rates'].append(error_rate)
                
                print(f"Time: {elapsed:.1f}s, "
                      f"Telemetry Rate: {telemetry_rate:.2f}/s, "
                      f"Error Rate: {error_rate:.4f}, "
                      f"Active: {stats['status_distribution'].get('running', 0)}")
        
        except Exception as e:
            print(f"Load test error: {e}")
        finally:
            await fleet_manager.stop_fleet()
        
        # Calculate final results
        if self.results['telemetry_rates']:
            avg_telemetry_rate = statistics.mean(self.results['telemetry_rates'])
            max_telemetry_rate = max(self.results['telemetry_rates'])
            min_telemetry_rate = min(self.results['telemetry_rates'])
        else:
            avg_telemetry_rate = max_telemetry_rate = min_telemetry_rate = 0
        
        if self.results['error_rates']:
            avg_error_rate = statistics.mean(self.results['error_rates'])
            max_error_rate = max(self.results['error_rates'])
            min_error_rate = min(self.results['error_rates'])
        else:
            avg_error_rate = max_error_rate = min_error_rate = 0
        
        print(f"\nLoad Test Results:")
        print(f"  Test Duration: {duration_minutes} minutes")
        print(f"  Average Telemetry Rate: {avg_telemetry_rate:.2f}/s")
        print(f"  Max Telemetry Rate: {max_telemetry_rate:.2f}/s")
        print(f"  Min Telemetry Rate: {min_telemetry_rate:.2f}/s")
        print(f"  Average Error Rate: {avg_error_rate:.4f}")
        print(f"  Max Error Rate: {max_error_rate:.4f}")
        print(f"  Min Error Rate: {min_error_rate:.4f}")

async def load_test_example():
    """Run load test with different fleet sizes"""
    load_tester = LoadTester()
    
    # Test with small fleet
    small_config = FleetConfig(total_devices=5, enable_failures=False)
    print("=== Small Fleet Test (5 devices) ===")
    await load_tester.run_load_test(small_config, duration_minutes=5)
    
    # Test with medium fleet
    medium_config = FleetConfig(total_devices=25, enable_failures=False)
    print("\n=== Medium Fleet Test (25 devices) ===")
    await load_tester.run_load_test(medium_config, duration_minutes=5)
    
    # Test with large fleet
    large_config = FleetConfig(total_devices=50, enable_failures=False)
    print("\n=== Large Fleet Test (50 devices) ===")
    await load_tester.run_load_test(large_config, duration_minutes=5)

if __name__ == "__main__":
    asyncio.run(load_test_example())
```

### Fault Injection Testing
```python
import asyncio
from mock_devices.industrial.vibration_sensor import create_vibration_sensor

async def fault_injection_test():
    """Test fault detection and recovery"""
    # Create vibration sensor
    sensor = create_vibration_sensor(5001, "Test Motor")
    sensor.set_equipment_parameters(speed=1800, load=0.8, age=5.0)
    
    print("Fault Injection Test")
    print("=" * 50)
    
    try:
        await sensor.start()
        
        # Baseline measurements
        await asyncio.sleep(30)
        baseline_health = sensor._calculate_health_score()
        baseline_vibration = sensor.current_vibration
        print(f"Baseline - Health: {baseline_health:.1f}%, Vibration: {baseline_vibration:.3f} mm/s")
        
        # Test 1: Bearing fault
        print("\n1. Inducing bearing fault...")
        sensor.induce_fault("bearing_fault", severity=0.3)
        await asyncio.sleep(60)
        
        bearing_health = sensor._calculate_health_score()
        bearing_vibration = sensor.current_vibration
        print(f"Bearing fault - Health: {bearing_health:.1f}%, Vibration: {bearing_vibration:.3f} mm/s")
        
        # Test 2: Increase fault severity
        print("\n2. Increasing bearing fault severity...")
        sensor.induce_fault("bearing_fault", severity=0.7)
        await asyncio.sleep(60)
        
        high_severity_health = sensor._calculate_health_score()
        high_severity_vibration = sensor.current_vibration
        print(f"High severity - Health: {high_severity_health:.1f}%, Vibration: {high_severity_vibration:.3f} mm/s")
        
        # Test 3: Clear fault
        print("\n3. Clearing fault...")
        sensor.clear_fault("bearing_fault")
        await asyncio.sleep(60)
        
        recovery_health = sensor._calculate_health_score()
        recovery_vibration = sensor.current_vibration
        print(f"Recovery - Health: {recovery_health:.1f}%, Vibration: {recovery_vibration:.3f} mm/s")
        
        # Test 4: Multiple faults
        print("\n4. Inducing multiple faults...")
        sensor.induce_fault("misalignment", severity=0.4)
        sensor.induce_fault("unbalance", severity=0.3)
        await asyncio.sleep(60)
        
        multi_fault_health = sensor._calculate_health_score()
        multi_fault_vibration = sensor.current_vibration
        print(f"Multiple faults - Health: {multi_fault_health:.1f}%, Vibration: {multi_fault_vibration:.3f} mm/s")
        
        # Clear all faults
        print("\n5. Clearing all faults...")
        sensor.clear_all_faults()
        await asyncio.sleep(60)
        
        final_health = sensor._calculate_health_score()
        final_vibration = sensor.current_vibration
        print(f"Final - Health: {final_health:.1f}%, Vibration: {final_vibration:.3f} mm/s")
        
    finally:
        await sensor.stop()
    
    print("\nFault Injection Test Results:")
    print(f"  Baseline Health: {baseline_health:.1f}%")
    print(f"  Bearing Fault (Low): {bearing_health:.1f}%")
    print(f"  Bearing Fault (High): {high_severity_health:.1f}%")
    print(f"  Recovery: {recovery_health:.1f}%")
    print(f"  Multiple Faults: {multi_fault_health:.1f}%")
    print(f"  Final Health: {final_health:.1f}%")

if __name__ == "__main__":
    asyncio.run(fault_injection_test())
```

---

## Support

For usage examples support:
- **Overview**: [Mock Devices Overview](mock-devices-overview.md)
- **Reference**: [Device Reference](device-reference.md)
- **Development**: [Development Setup](../08-development/development-setup.md)
- **API Integration**: [API Overview](../03-api/api-overview.md)
- **Troubleshooting**: [Troubleshooting Guide](../10-reference/troubleshooting.md)
- **Email**: autobotsolution@gmail.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Mock Devices Usage Examples v1.0**
