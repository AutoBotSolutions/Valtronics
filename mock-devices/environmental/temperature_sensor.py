"""
Temperature Sensor Mock Device

This module simulates a temperature sensor that provides realistic temperature readings
with daily cycles, seasonal variations, and occasional anomalies.
"""

import asyncio
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any
from ..base_device import BaseDevice, TelemetryData, DeviceConfig, DeviceStatus, DeviceType
from ..utils.data_generator import DataGenerator


class TemperatureSensor(BaseDevice):
    """Mock temperature sensor device"""
    
    def __init__(self, device_id: int, location: str = "Unknown"):
        config = DeviceConfig(
            device_id=device_id,
            device_name=f"Temperature Sensor {device_id:04d}",
            device_type=DeviceType.SENSOR,
            manufacturer="SensorTech Corp",
            model="ST-T1000",
            firmware_version="2.1.3",
            location=location,
            mqtt_topic=f"valtronics/devices/{device_id}/telemetry",
            api_endpoint="/api/v1/telemetry/",
            telemetry_interval=30,
            health_check_interval=300
        )
        
        super().__init__(config)
        
        # Temperature sensor specific parameters
        self.base_temperature = 22.0  # Base temperature in Celsius
        self.seasonal_variation = 5.0    # Seasonal variation amplitude
        self.daily_amplitude = 8.0        # Daily temperature variation
        self.sensor_accuracy = 0.1        # Sensor accuracy in Celsius
        self.response_time = 2.0          # Response time in seconds
        
        # Data generator for realistic temperature patterns
        self.data_generator = DataGenerator()
        
        # Current temperature state
        self.current_temperature = self.base_temperature
        self.target_temperature = self.base_temperature
        
        # Sensor health metrics
        self.calibration_offset = 0.0
        self.aging_factor = 1.0
        self.last_calibration = datetime.utcnow() - timedelta(days=30)
        
        # Environmental factors
        self.heat_sources = []  # List of heat sources affecting this sensor
        self.ventilation_rate = 0.5  # 0 = no ventilation, 1 = full ventilation
        
        # Alert thresholds
        self.temp_min_threshold = 10.0
        self.temp_max_threshold = 35.0
        self.temp_critical_min = 5.0
        self.temp_critical_max = 40.0
        
        # Historical data for trend simulation
        self.temperature_history = []
        self.max_history_size = 1440  # 24 hours of data at 1-minute intervals
    
    async def generate_telemetry(self) -> List[TelemetryData]:
        """Generate temperature telemetry data"""
        telemetry = []
        
        try:
            # Calculate realistic temperature
            current_temp = await self._calculate_temperature()
            self.current_temperature = current_temp
            
            # Add sensor noise and aging effects
            measured_temp = self._apply_sensor_effects(current_temp)
            
            # Create telemetry data
            telemetry_data = TelemetryData(
                metric_name="temperature",
                metric_value=round(measured_temp, 2),
                unit="°C",
                timestamp=datetime.utcnow(),
                device_id=self.device_id,
                metadata={
                    "sensor_type": "temperature",
                    "sensor_model": self.config.model,
                    "calibration_offset": self.calibration_offset,
                    "sensor_accuracy": self.sensor_accuracy,
                    "response_time": self.response_time,
                    "heat_sources": len(self.heat_sources),
                    "ventilation_rate": self.ventilation_rate,
                    "location": self.config.location
                }
            )
            
            telemetry.append(telemetry_data)
            
            # Update history
            self._update_temperature_history(current_temp)
            
            # Check for alerts
            await self._check_temperature_alerts(measured_temp)
            
            # Simulate sensor calibration drift
            self._simulate_calibration_drift()
            
        except Exception as e:
            self.logger.error(f"Error generating temperature telemetry: {e}")
            self.error_count += 1
        
        return telemetry
    
    async def _calculate_temperature(self) -> float:
        """Calculate realistic temperature based on time and environmental factors"""
        now = datetime.utcnow()
        
        # Daily temperature cycle (peak around 2 PM, minimum around 6 AM)
        hour_of_day = now.hour + now.minute / 60.0
        daily_cycle = self.daily_amplitude * math.sin(2 * math.pi * (hour_of_day - 6) / 24)
        
        # Seasonal variation (simplified - assumes summer)
        day_of_year = now.timetuple().tm_yday
        seasonal_cycle = self.seasonal_variation * math.sin(2 * math.pi * (day_of_year - 80) / 365)
        
        # Combine cycles with base temperature
        temperature = self.base_temperature + daily_cycle + seasonal_cycle
        
        # Apply heat sources
        for heat_source in self.heat_sources:
            heat_contribution = heat_source['intensity'] * heat_source['proximity_factor']
            temperature += heat_contribution
        
        # Apply ventilation effect (cooling)
        ambient_temp = 20.0  # Assumed ambient temperature
        ventilation_cooling = (temperature - ambient_temp) * self.ventilation_rate * 0.3
        temperature -= ventilation_cooling
        
        # Add random environmental noise
        noise = self.data_generator.add_noise(temperature, 0.2)
        
        return noise
    
    def _apply_sensor_effects(self, temperature: float) -> float:
        """Apply sensor-specific effects to measured temperature"""
        # Apply calibration offset
        measured_temp = temperature + self.calibration_offset
        
        # Apply aging factor (sensor becomes less accurate over time)
        days_since_calibration = (datetime.utcnow() - self.last_calibration).days
        aging_degradation = 1 + (days_since_calibration / 365) * 0.01  # 1% degradation per year
        measured_temp *= aging_degradation
        
        # Add sensor noise
        sensor_noise = self.data_generator.add_noise(0, self.sensor_accuracy)
        measured_temp += sensor_noise
        
        # Apply sensor response time delay (simulated)
        # In real sensors, this would be a temporal effect
        response_delay_factor = 0.95 if self.response_time > 1 else 0.98
        measured_temp = self.target_temperature * response_delay_factor + measured_temp * (1 - response_delay_factor)
        
        # Update target temperature for next reading
        self.target_temperature = temperature
        
        return round(measured_temp, 2)
    
    def _update_temperature_history(self, temperature: float):
        """Update temperature history for trend analysis"""
        self.temperature_history.append((datetime.utcnow(), temperature))
        
        # Keep only recent history
        if len(self.temperature_history) > self.max_history_size:
            self.temperature_history = self.temperature_history[-self.max_history_size:]
    
    def _simulate_calibration_drift(self):
        """Simulate gradual calibration drift over time"""
        # Small random drift
        drift = random.gauss(0, 0.001)  # Very small drift per reading
        self.calibration_offset += drift
        
        # Occasionally require recalibration
        if abs(self.calibration_offset) > 0.5:
            self.logger.info(f"Sensor {self.device_id} requires recalibration (offset: {self.calibration_offset:.3f})")
            # In a real system, this would trigger a maintenance alert
    
    async def _check_temperature_alerts(self, temperature: float):
        """Check for temperature-related alerts"""
        alerts = []
        
        # Critical high temperature alert
        if temperature > self.temp_critical_max:
            alert_data = {
                "device_id": self.device_id,
                "title": "Critical High Temperature Alert",
                "description": f"Temperature {temperature}°C exceeds critical threshold of {self.temp_critical_max}°C",
                "severity": "critical",
                "metric_name": "temperature",
                "metric_value": temperature,
                "threshold_value": self.temp_critical_max,
                "location": self.config.location
            }
            alerts.append(alert_data)
        
        # Critical low temperature alert
        elif temperature < self.temp_critical_min:
            alert_data = {
                "device_id": self.device_id,
                "title": "Critical Low Temperature Alert",
                "description": f"Temperature {temperature}°C below critical threshold of {self.temp_critical_min}°C",
                "severity": "critical",
                "metric_name": "temperature",
                "metric_value": temperature,
                "threshold_value": self.temp_critical_min,
                "location": self.config.location
            }
            alerts.append(alert_data)
        
        # High temperature warning
        elif temperature > self.temp_max_threshold:
            alert_data = {
                "device_id": self.device_id,
                "title": "High Temperature Warning",
                "description": f"Temperature {temperature}°C exceeds warning threshold of {self.temp_max_threshold}°C",
                "severity": "warning",
                "metric_name": "temperature",
                "metric_value": temperature,
                "threshold_value": self.temp_max_threshold,
                "location": self.config.location
            }
            alerts.append(alert_data)
        
        # Low temperature warning
        elif temperature < self.temp_min_threshold:
            alert_data = {
                "device_id": self.device_id,
                "title": "Low Temperature Warning",
                "description": f"Temperature {temperature}°C below warning threshold of {self.temp_min_threshold}°C",
                "severity": "warning",
                "metric_name": "temperature",
                "metric_value": temperature,
                "threshold_value": self.temp_min_threshold,
                "location": self.config.location
            }
            alerts.append(alert_data)
        
        # Rapid temperature change alert
        if len(self.temperature_history) >= 2:
            recent_temps = [temp for _, temp in self.temperature_history[-10:]]
            if len(recent_temps) >= 2:
                temp_change = abs(recent_temps[-1] - recent_temps[0])
                if temp_change > 5.0:  # Rapid change > 5°C in recent readings
                    alert_data = {
                        "device_id": self.device_id,
                        "title": "Rapid Temperature Change Alert",
                        "description": f"Temperature changed by {temp_change:.2f}°C in recent readings",
                        "severity": "warning",
                        "metric_name": "temperature_change_rate",
                        "metric_value": temp_change,
                        "threshold_value": 5.0,
                        "location": self.config.location
                    }
                    alerts.append(alert_data)
        
        # Send alerts via API
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
    
    def add_heat_source(self, name: str, intensity: float, proximity_factor: float = 1.0):
        """Add a heat source that affects this sensor"""
        heat_source = {
            "name": name,
            "intensity": intensity,
            "proximity_factor": proximity_factor,
            "added_at": datetime.utcnow()
        }
        self.heat_sources.append(heat_source)
        self.logger.info(f"Added heat source: {name} (intensity: {intensity}, proximity: {proximity_factor})")
    
    def remove_heat_source(self, name: str):
        """Remove a heat source"""
        self.heat_sources = [hs for hs in self.heat_sources if hs["name"] != name]
        self.logger.info(f"Removed heat source: {name}")
    
    def set_ventilation_rate(self, rate: float):
        """Set ventilation rate (0.0 to 1.0)"""
        self.ventilation_rate = max(0.0, min(1.0, rate))
        self.logger.info(f"Set ventilation rate to {self.ventilation_rate}")
    
    def calibrate_sensor(self, reference_temperature: float):
        """Calibrate the sensor against a known reference temperature"""
        current_reading = self.current_temperature
        self.calibration_offset = reference_temperature - current_reading
        self.last_calibration = datetime.utcnow()
        
        # Reset aging factor after calibration
        self.aging_factor = 1.0
        
        self.logger.info(f"Sensor calibrated: offset={self.calibration_offset:.3f}, reference={reference_temperature}°C")
    
    def get_temperature_statistics(self) -> Dict[str, Any]:
        """Get temperature statistics"""
        if not self.temperature_history:
            return {}
        
        temperatures = [temp for _, temp in self.temperature_history]
        
        return {
            "current_temperature": self.current_temperature,
            "average_temperature": sum(temperatures) / len(temperatures),
            "min_temperature": min(temperatures),
            "max_temperature": max(temperatures),
            "temperature_range": max(temperatures) - min(temperatures),
            "data_points": len(temperatures),
            "calibration_offset": self.calibration_offset,
            "days_since_calibration": (datetime.utcnow() - self.last_calibration).days,
            "sensor_accuracy": self.sensor_accuracy,
            "heat_sources_count": len(self.heat_sources),
            "ventilation_rate": self.ventilation_rate
        }
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get extended device information"""
        base_info = super().get_device_info()
        
        # Add temperature sensor specific info
        base_info.update({
            "sensor_type": "temperature",
            "current_temperature": self.current_temperature,
            "target_temperature": self.target_temperature,
            "base_temperature": self.base_temperature,
            "calibration_offset": self.calibration_offset,
            "sensor_accuracy": self.sensor_accuracy,
            "response_time": self.response_time,
            "temperature_history_size": len(self.temperature_history),
            "heat_sources": self.heat_sources,
            "ventilation_rate": self.ventilation_rate,
            "temperature_statistics": self.get_temperature_statistics()
        })
        
        return base_info


# Factory function for creating temperature sensors
def create_temperature_sensor(device_id: int, location: str = "Unknown") -> TemperatureSensor:
    """Factory function to create a temperature sensor"""
    return TemperatureSensor(device_id, location)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Create temperature sensor
        sensor = create_temperature_sensor(1001, "Server Room A")
        
        # Add heat source (e.g., server rack)
        sensor.add_heat_source("Server Rack 1", intensity=5.0, proximity_factor=0.8)
        
        # Set ventilation rate
        sensor.set_ventilation_rate(0.7)
        
        # Start the sensor
        try:
            await sensor.start()
            
            # Run for demonstration
            await asyncio.sleep(300)  # Run for 5 minutes
            
        except KeyboardInterrupt:
            print("Stopping sensor...")
        finally:
            await sensor.stop()
    
    asyncio.run(main())
