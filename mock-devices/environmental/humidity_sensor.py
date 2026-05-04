"""
Humidity Sensor Mock Device

This module simulates a humidity sensor that provides realistic humidity readings
with inverse correlation to temperature and environmental factors.
"""

import asyncio
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from ..base_device import BaseDevice, TelemetryData, DeviceConfig, DeviceStatus, DeviceType
from ..utils.data_generator import DataGenerator


class HumiditySensor(BaseDevice):
    """Mock humidity sensor device"""
    
    def __init__(self, device_id: int, location: str = "Unknown"):
        config = DeviceConfig(
            device_id=device_id,
            device_name=f"Humidity Sensor {device_id:04d}",
            device_type=DeviceType.SENSOR,
            manufacturer="HumidiSense Corp",
            model="HS-H2000",
            firmware_version="1.8.2",
            location=location,
            mqtt_topic=f"valtronics/devices/{device_id}/telemetry",
            api_endpoint="/api/v1/telemetry/",
            telemetry_interval=30,
            health_check_interval=300
        )
        
        super().__init__(config)
        
        # Humidity sensor specific parameters
        self.base_humidity = 50.0         # Base humidity percentage
        self.humidity_range = 30.0        # Daily humidity variation range
        self.sensor_accuracy = 2.0        # Sensor accuracy in percentage
        self.response_time = 3.0          # Response time in seconds
        
        # Data generator
        self.data_generator = DataGenerator()
        
        # Current humidity state
        self.current_humidity = self.base_humidity
        self.target_humidity = self.base_humidity
        
        # Sensor health metrics
        self.calibration_offset = 0.0
        self.aging_factor = 1.0
        self.last_calibration = datetime.utcnow() - timedelta(days=45)
        
        # Environmental factors
        self.temperature_coupling = 0.7   # How strongly humidity correlates with temperature
        self.current_temperature = 22.0    # Current temperature for correlation
        self.humidity_sources = []         # Sources of humidity (e.g., water leaks)
        self.air_circulation = 0.5        # Air circulation rate (0-1)
        
        # Alert thresholds
        self.humidity_min_threshold = 30.0
        self.humidity_max_threshold = 70.0
        self.humidity_critical_min = 20.0
        self.humidity_critical_max = 80.0
        
        # Historical data
        self.humidity_history = []
        self.max_history_size = 1440  # 24 hours of data
        
        # Dew point calculation
        self.enable_dew_point = True
        self.dew_point_threshold = 15.0
    
    async def generate_telemetry(self) -> List[TelemetryData]:
        """Generate humidity telemetry data"""
        telemetry = []
        
        try:
            # Calculate realistic humidity
            current_humidity = await self._calculate_humidity()
            self.current_humidity = current_humidity
            
            # Apply sensor effects
            measured_humidity = self._apply_sensor_effects(current_humidity)
            
            # Create main humidity telemetry
            humidity_data = TelemetryData(
                metric_name="humidity",
                metric_value=round(measured_humidity, 1),
                unit="%",
                timestamp=datetime.utcnow(),
                device_id=self.device_id,
                metadata={
                    "sensor_type": "humidity",
                    "sensor_model": self.config.model,
                    "calibration_offset": self.calibration_offset,
                    "sensor_accuracy": self.sensor_accuracy,
                    "temperature_coupling": self.temperature_coupling,
                    "air_circulation": self.air_circulation,
                    "location": self.config.location
                }
            )
            
            telemetry.append(humidity_data)
            
            # Calculate dew point if enabled
            if self.enable_dew_point:
                dew_point = self._calculate_dew_point(measured_humidity, self.current_temperature)
                dew_point_data = TelemetryData(
                    metric_name="dew_point",
                    metric_value=round(dew_point, 1),
                    unit="°C",
                    timestamp=datetime.utcnow(),
                    device_id=self.device_id,
                    metadata={
                        "sensor_type": "humidity",
                        "calculation_method": "magnus",
                        "input_humidity": measured_humidity,
                        "input_temperature": self.current_temperature
                    }
                )
                telemetry.append(dew_point_data)
            
            # Update history
            self._update_humidity_history(current_humidity)
            
            # Check for alerts
            await self._check_humidity_alerts(measured_humidity)
            
            # Simulate sensor drift
            self._simulate_calibration_drift()
            
        except Exception as e:
            self.logger.error(f"Error generating humidity telemetry: {e}")
            self.error_count += 1
        
        return telemetry
    
    async def _calculate_humidity(self) -> float:
        """Calculate realistic humidity based on environmental factors"""
        now = datetime.utcnow()
        
        # Daily humidity cycle (opposite to temperature)
        hour_of_day = now.hour + now.minute / 60.0
        daily_cycle = self.humidity_range * math.sin(2 * math.pi * (hour_of_day + 6) / 24)
        
        # Base humidity with daily variation
        humidity = self.base_humidity + daily_cycle
        
        # Temperature correlation (inverse relationship)
        temp_effect = (self.current_temperature - 20.0) * self.temperature_coupling * -0.5
        humidity += temp_effect
        
        # Apply humidity sources
        for source in self.humidity_sources:
            humidity += source['intensity'] * source['proximity_factor']
        
        # Apply air circulation effect (drying)
        ambient_humidity = 40.0  # Assumed ambient humidity
        circulation_effect = (humidity - ambient_humidity) * self.air_circulation * 0.2
        humidity -= circulation_effect
        
        # Add environmental noise
        noise = self.data_generator.add_noise(humidity, 1.0)
        
        # Ensure humidity stays within physical bounds
        humidity = max(0, min(100, noise))
        
        return humidity
    
    def _apply_sensor_effects(self, humidity: float) -> float:
        """Apply sensor-specific effects to measured humidity"""
        # Apply calibration offset
        measured_humidity = humidity + self.calibration_offset
        
        # Apply aging factor
        days_since_calibration = (datetime.utcnow() - self.last_calibration).days
        aging_degradation = 1 + (days_since_calibration / 365) * 0.015  # 1.5% degradation per year
        measured_humidity *= aging_degradation
        
        # Add sensor noise
        sensor_noise = self.data_generator.add_noise(0, self.sensor_accuracy)
        measured_humidity += sensor_noise
        
        # Apply response time delay
        response_delay_factor = 0.92 if self.response_time > 2 else 0.96
        measured_humidity = self.target_humidity * response_delay_factor + measured_humidity * (1 - response_delay_factor)
        
        # Update target for next reading
        self.target_humidity = humidity
        
        # Ensure within bounds
        measured_humidity = max(0, min(100, measured_humidity))
        
        return round(measured_humidity, 1)
    
    def _calculate_dew_point(self, humidity: float, temperature: float) -> float:
        """Calculate dew point using Magnus formula"""
        # Magnus formula constants
        a = 17.27
        b = 237.7
        
        # Calculate dew point
        alpha = ((a * temperature) / (b + temperature)) + math.log(humidity / 100.0)
        dew_point = (b * alpha) / (a - alpha)
        
        return dew_point
    
    def _update_humidity_history(self, humidity: float):
        """Update humidity history"""
        self.humidity_history.append((datetime.utcnow(), humidity))
        
        if len(self.humidity_history) > self.max_history_size:
            self.humidity_history = self.humidity_history[-self.max_history_size:]
    
    def _simulate_calibration_drift(self):
        """Simulate gradual calibration drift"""
        drift = random.gauss(0, 0.002)
        self.calibration_offset += drift
        
        if abs(self.calibration_offset) > 1.0:
            self.logger.info(f"Sensor {self.device_id} requires recalibration (offset: {self.calibration_offset:.3f})")
    
    async def _check_humidity_alerts(self, humidity: float):
        """Check for humidity-related alerts"""
        alerts = []
        
        # Critical high humidity alert
        if humidity > self.humidity_critical_max:
            alert_data = {
                "device_id": self.device_id,
                "title": "Critical High Humidity Alert",
                "description": f"Humidity {humidity}% exceeds critical threshold of {self.humidity_critical_max}%",
                "severity": "critical",
                "metric_name": "humidity",
                "metric_value": humidity,
                "threshold_value": self.humidity_critical_max,
                "location": self.config.location
            }
            alerts.append(alert_data)
        
        # Critical low humidity alert
        elif humidity < self.humidity_critical_min:
            alert_data = {
                "device_id": self.device_id,
                "title": "Critical Low Humidity Alert",
                "description": f"Humidity {humidity}% below critical threshold of {self.humidity_critical_min}%",
                "severity": "critical",
                "metric_name": "humidity",
                "metric_value": humidity,
                "threshold_value": self.humidity_critical_min,
                "location": self.config.location
            }
            alerts.append(alert_data)
        
        # High humidity warning
        elif humidity > self.humidity_max_threshold:
            alert_data = {
                "device_id": self.device_id,
                "title": "High Humidity Warning",
                "description": f"Humidity {humidity}% exceeds warning threshold of {self.humidity_max_threshold}%",
                "severity": "warning",
                "metric_name": "humidity",
                "metric_value": humidity,
                "threshold_value": self.humidity_max_threshold,
                "location": self.config.location
            }
            alerts.append(alert_data)
        
        # Low humidity warning
        elif humidity < self.humidity_min_threshold:
            alert_data = {
                "device_id": self.device_id,
                "title": "Low Humidity Warning",
                "description": f"Humidity {humidity}% below warning threshold of {self.humidity_min_threshold}%",
                "severity": "warning",
                "metric_name": "humidity",
                "metric_value": humidity,
                "threshold_value": self.humidity_min_threshold,
                "location": self.config.location
            }
            alerts.append(alert_data)
        
        # Dew point alert
        if self.enable_dew_point:
            dew_point = self._calculate_dew_point(humidity, self.current_temperature)
            if dew_point > self.dew_point_threshold:
                alert_data = {
                    "device_id": self.device_id,
                    "title": "High Dew Point Alert",
                    "description": f"Dew point {dew_point:.1f}°C exceeds threshold of {self.dew_point_threshold}°C",
                    "severity": "warning",
                    "metric_name": "dew_point",
                    "metric_value": dew_point,
                    "threshold_value": self.dew_point_threshold,
                    "location": self.config.location
                }
                alerts.append(alert_data)
        
        # Rapid humidity change alert
        if len(self.humidity_history) >= 2:
            recent_humidities = [h for _, h in self.humidity_history[-10:]]
            if len(recent_humidities) >= 2:
                humidity_change = abs(recent_humidities[-1] - recent_humidities[0])
                if humidity_change > 10.0:  # Rapid change > 10% in recent readings
                    alert_data = {
                        "device_id": self.device_id,
                        "title": "Rapid Humidity Change Alert",
                        "description": f"Humidity changed by {humidity_change:.1f}% in recent readings",
                        "severity": "warning",
                        "metric_name": "humidity_change_rate",
                        "metric_value": humidity_change,
                        "threshold_value": 10.0,
                        "location": self.config.location
                    }
                    alerts.append(alert_data)
        
        # Send alerts
        for alert_data in alerts:
            await self._send_alert(alert_data)
    
    async def _send_alert(self, alert_data: Dict[str, Any]):
        """Send alert to Valtronics system"""
        try:
            from ..utils.api_client import AsyncAPIClient
            
            api_client = AsyncAPIClient()
            result = await api_client.create_alert(alert_data)
            
            if result:
                self.alert_count += 1
                self.logger.info(f"Alert created: {alert_data['title']}")
            else:
                self.logger.warning(f"Failed to create alert: {alert_data['title']}")
                
        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")
    
    def set_temperature_coupling(self, coupling: float):
        """Set temperature coupling factor (0.0 to 1.0)"""
        self.temperature_coupling = max(0.0, min(1.0, coupling))
        self.logger.info(f"Set temperature coupling to {self.temperature_coupling}")
    
    def update_temperature(self, temperature: float):
        """Update current temperature for correlation calculations"""
        self.current_temperature = temperature
        self.logger.debug(f"Updated temperature to {temperature}°C")
    
    def add_humidity_source(self, name: str, intensity: float, proximity_factor: float = 1.0):
        """Add a humidity source"""
        humidity_source = {
            "name": name,
            "intensity": intensity,
            "proximity_factor": proximity_factor,
            "added_at": datetime.utcnow()
        }
        self.humidity_sources.append(humidity_source)
        self.logger.info(f"Added humidity source: {name} (intensity: {intensity}, proximity: {proximity_factor})")
    
    def remove_humidity_source(self, name: str):
        """Remove a humidity source"""
        self.humidity_sources = [hs for hs in self.humidity_sources if hs["name"] != name]
        self.logger.info(f"Removed humidity source: {name}")
    
    def set_air_circulation(self, circulation: float):
        """Set air circulation rate (0.0 to 1.0)"""
        self.air_circulation = max(0.0, min(1.0, circulation))
        self.logger.info(f"Set air circulation to {self.air_circulation}")
    
    def calibrate_sensor(self, reference_humidity: float):
        """Calibrate the sensor against a known reference"""
        current_reading = self.current_humidity
        self.calibration_offset = reference_humidity - current_reading
        self.last_calibration = datetime.utcnow()
        self.aging_factor = 1.0
        
        self.logger.info(f"Sensor calibrated: offset={self.calibration_offset:.3f}, reference={reference_humidity}%")
    
    def get_humidity_statistics(self) -> Dict[str, Any]:
        """Get humidity statistics"""
        if not self.humidity_history:
            return {}
        
        humidities = [h for _, h in self.humidity_history]
        
        stats = {
            "current_humidity": self.current_humidity,
            "average_humidity": sum(humidities) / len(humidities),
            "min_humidity": min(humidities),
            "max_humidity": max(humidities),
            "humidity_range": max(humidities) - min(humidities),
            "data_points": len(humidities),
            "calibration_offset": self.calibration_offset,
            "days_since_calibration": (datetime.utcnow() - self.last_calibration).days,
            "sensor_accuracy": self.sensor_accuracy,
            "temperature_coupling": self.temperature_coupling,
            "air_circulation": self.air_circulation,
            "humidity_sources_count": len(self.humidity_sources)
        }
        
        # Add dew point statistics if enabled
        if self.enable_dew_point:
            dew_points = []
            for _, humidity in self.humidity_history:
                dew_point = self._calculate_dew_point(humidity, self.current_temperature)
                dew_points.append(dew_point)
            
            stats.update({
                "current_dew_point": self._calculate_dew_point(self.current_humidity, self.current_temperature),
                "average_dew_point": sum(dew_points) / len(dew_points),
                "min_dew_point": min(dew_points),
                "max_dew_point": max(dew_points)
            })
        
        return stats
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get extended device information"""
        base_info = super().get_device_info()
        
        # Add humidity sensor specific info
        base_info.update({
            "sensor_type": "humidity",
            "current_humidity": self.current_humidity,
            "target_humidity": self.target_humidity,
            "base_humidity": self.base_humidity,
            "calibration_offset": self.calibration_offset,
            "sensor_accuracy": self.sensor_accuracy,
            "temperature_coupling": self.temperature_coupling,
            "current_temperature": self.current_temperature,
            "humidity_history_size": len(self.humidity_history),
            "humidity_sources": self.humidity_sources,
            "air_circulation": self.air_circulation,
            "enable_dew_point": self.enable_dew_point,
            "humidity_statistics": self.get_humidity_statistics()
        })
        
        return base_info


def create_humidity_sensor(device_id: int, location: str = "Unknown") -> HumiditySensor:
    """Factory function to create a humidity sensor"""
    return HumiditySensor(device_id, location)


if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Create humidity sensor
        sensor = create_humidity_sensor(2001, "Data Center Room B")
        
        # Add humidity source (e.g., water leak)
        sensor.add_humidity_source("Water Source 1", intensity=8.0, proximity_factor=0.6)
        
        # Set air circulation
        sensor.set_air_circulation(0.3)
        
        # Set temperature coupling
        sensor.set_temperature_coupling(0.8)
        
        # Update temperature for correlation
        sensor.update_temperature(22.5)
        
        try:
            await sensor.start()
            await asyncio.sleep(300)
        except KeyboardInterrupt:
            print("Stopping sensor...")
        finally:
            await sensor.stop()
    
    asyncio.run(main())
