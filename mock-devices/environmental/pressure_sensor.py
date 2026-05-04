"""
Pressure Sensor Mock Device

This module simulates a barometric pressure sensor that provides realistic pressure readings
with weather patterns and altitude effects.
"""

import asyncio
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any
from ..base_device import BaseDevice, TelemetryData, DeviceConfig, DeviceStatus, DeviceType
from ..utils.data_generator import DataGenerator


class PressureSensor(BaseDevice):
    """Mock pressure sensor device"""
    
    def __init__(self, device_id: int, location: str = "Unknown", altitude: float = 0.0):
        config = DeviceConfig(
            device_id=device_id,
            device_name=f"Pressure Sensor {device_id:04d}",
            device_type=DeviceType.SENSOR,
            manufacturer="BaroMetrics Corp",
            model="BM-P3000",
            firmware_version="3.2.1",
            location=location,
            mqtt_topic=f"valtronics/devices/{device_id}/telemetry",
            api_endpoint="/api/v1/telemetry/",
            telemetry_interval=30,
            health_check_interval=300
        )
        
        super().__init__(config)
        
        # Pressure sensor specific parameters
        self.base_pressure = 1013.25       # Base pressure in hPa (sea level)
        self.altitude = altitude            # Altitude in meters
        self.sensor_accuracy = 0.5         # Sensor accuracy in hPa
        self.response_time = 2.5            # Response time in seconds
        
        # Data generator
        self.data_generator = DataGenerator()
        
        # Current pressure state
        self.current_pressure = self.base_pressure
        self.target_pressure = self.base_pressure
        
        # Sensor health metrics
        self.calibration_offset = 0.0
        self.aging_factor = 1.0
        self.last_calibration = datetime.utcnow() - timedelta(days=60)
        
        # Weather simulation parameters
        self.weather_trend = 0.0           # Current weather trend (-1 to 1)
        self.weather_cycle_length = 720     # Weather cycle in minutes (12 hours)
        self.pressure_trend_rate = 0.01     # Rate of pressure change per minute
        
        # Altitude compensation
        self.altitude_coefficient = 0.12    # hPa per meter
        self.temperature_compensation = True
        self.current_temperature = 15.0     # Current temperature for compensation
        
        # Alert thresholds
        self.pressure_min_threshold = 980.0
        self.pressure_max_threshold = 1050.0
        self.pressure_critical_min = 950.0
        self.pressure_critical_max = 1080.0
        self.rapid_change_threshold = 5.0    # hPa change in 30 minutes
        
        # Historical data
        self.pressure_history = []
        self.max_history_size = 1440  # 24 hours of data
        
        # Calculate altitude-adjusted base pressure
        self.altitude_adjusted_base = self.base_pressure - (self.altitude * self.altitude_coefficient)
    
    async def generate_telemetry(self) -> List[TelemetryData]:
        """Generate pressure telemetry data"""
        telemetry = []
        
        try:
            # Calculate realistic pressure
            current_pressure = await self._calculate_pressure()
            self.current_pressure = current_pressure
            
            # Apply sensor effects
            measured_pressure = self._apply_sensor_effects(current_pressure)
            
            # Create main pressure telemetry
            pressure_data = TelemetryData(
                metric_name="pressure",
                metric_value=round(measured_pressure, 1),
                unit="hPa",
                timestamp=datetime.utcnow(),
                device_id=self.device_id,
                metadata={
                    "sensor_type": "pressure",
                    "sensor_model": self.config.model,
                    "calibration_offset": self.calibration_offset,
                    "sensor_accuracy": self.sensor_accuracy,
                    "altitude": self.altitude,
                    "altitude_coefficient": self.altitude_coefficient,
                    "weather_trend": self.weather_trend,
                    "location": self.config.location
                }
            )
            
            telemetry.append(pressure_data)
            
            # Calculate sea level pressure if altitude compensation is enabled
            if self.altitude > 0:
                sea_level_pressure = self._calculate_sea_level_pressure(measured_pressure)
                sea_level_data = TelemetryData(
                    metric_name="sea_level_pressure",
                    metric_value=round(sea_level_pressure, 1),
                    unit="hPa",
                    timestamp=datetime.utcnow(),
                    device_id=self.device_id,
                    metadata={
                        "sensor_type": "pressure",
                        "calculation_method": "altitude_compensation",
                        "input_pressure": measured_pressure,
                        "altitude": self.altitude,
                        "temperature": self.current_temperature
                    }
                )
                telemetry.append(sea_level_data)
            
            # Calculate pressure trend
            if len(self.pressure_history) >= 2:
                trend = self._calculate_pressure_trend()
                trend_data = TelemetryData(
                    metric_name="pressure_trend",
                    metric_value=round(trend, 3),
                    unit="hPa/min",
                    timestamp=datetime.utcnow(),
                    device_id=self.device_id,
                    metadata={
                        "sensor_type": "pressure",
                        "calculation_method": "linear_regression",
                        "data_points": min(30, len(self.pressure_history))
                    }
                )
                telemetry.append(trend_data)
            
            # Update history
            self._update_pressure_history(current_pressure)
            
            # Check for alerts
            await self._check_pressure_alerts(measured_pressure)
            
            # Simulate sensor drift
            self._simulate_calibration_drift()
            
        except Exception as e:
            self.logger.error(f"Error generating pressure telemetry: {e}")
            self.error_count += 1
        
        return telemetry
    
    async def _calculate_pressure(self) -> float:
        """Calculate realistic pressure based on weather patterns"""
        now = datetime.utcnow()
        minutes_since_start = (now.hour * 60) + now.minute
        
        # Weather cycle (slow changes over 12-hour periods)
        weather_phase = (minutes_since_start % self.weather_cycle_length) / self.weather_cycle_length
        weather_cycle = 10 * math.sin(2 * math.pi * weather_phase)
        
        # Update weather trend gradually
        self.weather_trend += random.gauss(0, 0.01)
        self.weather_trend = max(-1, min(1, self.weather_trend))
        
        # Apply weather trend
        trend_effect = self.weather_trend * 5.0
        
        # Seasonal variation (simplified)
        day_of_year = now.timetuple().tm_yday
        seasonal_cycle = 3 * math.sin(2 * math.pi * (day_of_year - 80) / 365)
        
        # Combine all effects with altitude-adjusted base
        pressure = self.altitude_adjusted_base + weather_cycle + trend_effect + seasonal_cycle
        
        # Add random environmental noise
        noise = self.data_generator.add_noise(pressure, 0.3)
        
        # Simulate weather fronts (occasional rapid changes)
        if random.random() < 0.005:  # 0.5% chance of weather front
            front_change = random.uniform(-10, 10)
            pressure += front_change
            self.weather_trend += front_change / 20.0  # Update trend based on front
        
        return noise
    
    def _apply_sensor_effects(self, pressure: float) -> float:
        """Apply sensor-specific effects to measured pressure"""
        # Apply calibration offset
        measured_pressure = pressure + self.calibration_offset
        
        # Apply aging factor
        days_since_calibration = (datetime.utcnow() - self.last_calibration).days
        aging_degradation = 1 + (days_since_calibration / 365) * 0.01  # 1% degradation per year
        measured_pressure *= aging_degradation
        
        # Add sensor noise
        sensor_noise = self.data_generator.add_noise(0, self.sensor_accuracy)
        measured_pressure += sensor_noise
        
        # Apply response time delay
        response_delay_factor = 0.94 if self.response_time > 2 else 0.97
        measured_pressure = self.target_pressure * response_delay_factor + measured_pressure * (1 - response_delay_factor)
        
        # Update target for next reading
        self.target_pressure = pressure
        
        return round(measured_pressure, 1)
    
    def _calculate_sea_level_pressure(self, measured_pressure: float) -> float:
        """Calculate sea level pressure from measured pressure"""
        if not self.temperature_compensation:
            return measured_pressure + (self.altitude * self.altitude_coefficient)
        
        # More accurate calculation using temperature compensation
        # Barometric formula: P0 = P * exp((g * h) / (R * T))
        # Simplified version for practical use
        temp_kelvin = self.current_temperature + 273.15
        altitude_factor = math.exp((self.altitude * 0.034163) / temp_kelvin)
        sea_level_pressure = measured_pressure * altitude_factor
        
        return sea_level_pressure
    
    def _calculate_pressure_trend(self) -> float:
        """Calculate pressure trend over recent history"""
        if len(self.pressure_history) < 2:
            return 0.0
        
        # Use last 30 data points (15 minutes at 30-second intervals)
        recent_data = self.pressure_history[-30:]
        
        if len(recent_data) < 2:
            return 0.0
        
        # Simple linear regression to calculate trend
        n = len(recent_data)
        sum_x = sum(range(n))
        sum_y = sum(pressure for _, pressure in recent_data)
        sum_xy = sum(i * pressure for i, (_, pressure) in enumerate(recent_data))
        sum_x2 = sum(i * i for i in range(n))
        
        # Calculate slope (trend)
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Convert to hPa per minute
        trend_per_minute = slope * 2.0  # 2 readings per minute
        
        return trend_per_minute
    
    def _update_pressure_history(self, pressure: float):
        """Update pressure history"""
        self.pressure_history.append((datetime.utcnow(), pressure))
        
        if len(self.pressure_history) > self.max_history_size:
            self.pressure_history = self.pressure_history[-self.max_history_size:]
    
    def _simulate_calibration_drift(self):
        """Simulate gradual calibration drift"""
        drift = random.gauss(0, 0.001)
        self.calibration_offset += drift
        
        if abs(self.calibration_offset) > 0.5:
            self.logger.info(f"Sensor {self.device_id} requires recalibration (offset: {self.calibration_offset:.3f})")
    
    async def _check_pressure_alerts(self, pressure: float):
        """Check for pressure-related alerts"""
        alerts = []
        
        # Critical high pressure alert
        if pressure > self.pressure_critical_max:
            alert_data = {
                "device_id": self.device_id,
                "title": "Critical High Pressure Alert",
                "description": f"Pressure {pressure} hPa exceeds critical threshold of {self.pressure_critical_max} hPa",
                "severity": "critical",
                "metric_name": "pressure",
                "metric_value": pressure,
                "threshold_value": self.pressure_critical_max,
                "location": self.config.location
            }
            alerts.append(alert_data)
        
        # Critical low pressure alert
        elif pressure < self.pressure_critical_min:
            alert_data = {
                "device_id": self.device_id,
                "title": "Critical Low Pressure Alert",
                "description": f"Pressure {pressure} hPa below critical threshold of {self.pressure_critical_min} hPa",
                "severity": "critical",
                "metric_name": "pressure",
                "metric_value": pressure,
                "threshold_value": self.pressure_critical_min,
                "location": self.config.location
            }
            alerts.append(alert_data)
        
        # High pressure warning
        elif pressure > self.pressure_max_threshold:
            alert_data = {
                "device_id": self.device_id,
                "title": "High Pressure Warning",
                "description": f"Pressure {pressure} hPa exceeds warning threshold of {self.pressure_max_threshold} hPa",
                "severity": "warning",
                "metric_name": "pressure",
                "metric_value": pressure,
                "threshold_value": self.pressure_max_threshold,
                "location": self.config.location
            }
            alerts.append(alert_data)
        
        # Low pressure warning
        elif pressure < self.pressure_min_threshold:
            alert_data = {
                "device_id": self.device_id,
                "title": "Low Pressure Warning",
                "description": f"Pressure {pressure} hPa below warning threshold of {self.pressure_min_threshold} hPa",
                "severity": "warning",
                "metric_name": "pressure",
                "metric_value": pressure,
                "threshold_value": self.pressure_min_threshold,
                "location": self.config.location
            }
            alerts.append(alert_data)
        
        # Rapid pressure change alert
        if len(self.pressure_history) >= 60:  # Check last 30 minutes
            recent_data = self.pressure_history[-60:]
            recent_pressures = [p for _, p in recent_data]
            pressure_change = abs(recent_pressures[-1] - recent_pressures[0])
            
            if pressure_change > self.rapid_change_threshold:
                alert_data = {
                    "device_id": self.device_id,
                    "title": "Rapid Pressure Change Alert",
                    "description": f"Pressure changed by {pressure_change:.1f} hPa in the last 30 minutes",
                    "severity": "warning",
                    "metric_name": "pressure_change_rate",
                    "metric_value": pressure_change,
                    "threshold_value": self.rapid_change_threshold,
                    "location": self.config.location
                }
                alerts.append(alert_data)
        
        # Weather trend alert (significant pressure drop indicating storm)
        trend = self._calculate_pressure_trend()
        if trend < -0.1:  # Dropping faster than 0.1 hPa per minute
            alert_data = {
                "device_id": self.device_id,
                "title": "Storm Warning",
                "description": f"Rapid pressure drop detected (trend: {trend:.3f} hPa/min) - possible approaching storm",
                "severity": "warning",
                "metric_name": "pressure_trend",
                "metric_value": trend,
                "threshold_value": -0.1,
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
    
    def set_altitude(self, altitude: float):
        """Set sensor altitude"""
        self.altitude = altitude
        self.altitude_adjusted_base = self.base_pressure - (self.altitude * self.altitude_coefficient)
        self.logger.info(f"Set altitude to {altitude}m (base pressure adjusted to {self.altitude_adjusted_base:.1f} hPa)")
    
    def set_temperature_compensation(self, enabled: bool):
        """Enable or disable temperature compensation"""
        self.temperature_compensation = enabled
        self.logger.info(f"Temperature compensation {'enabled' if enabled else 'disabled'}")
    
    def update_temperature(self, temperature: float):
        """Update current temperature for compensation calculations"""
        self.current_temperature = temperature
        self.logger.debug(f"Updated temperature to {temperature}°C")
    
    def simulate_weather_front(self, pressure_change: float):
        """Simulate a weather front passing through"""
        self.weather_trend += pressure_change / 20.0
        self.logger.info(f"Simulated weather front: pressure change {pressure_change} hPa")
    
    def calibrate_sensor(self, reference_pressure: float):
        """Calibrate the sensor against a known reference"""
        current_reading = self.current_pressure
        self.calibration_offset = reference_pressure - current_reading
        self.last_calibration = datetime.utcnow()
        self.aging_factor = 1.0
        
        self.logger.info(f"Sensor calibrated: offset={self.calibration_offset:.3f}, reference={reference_pressure} hPa")
    
    def get_pressure_statistics(self) -> Dict[str, Any]:
        """Get pressure statistics"""
        if not self.pressure_history:
            return {}
        
        pressures = [p for _, p in self.pressure_history]
        
        stats = {
            "current_pressure": self.current_pressure,
            "average_pressure": sum(pressures) / len(pressures),
            "min_pressure": min(pressures),
            "max_pressure": max(pressures),
            "pressure_range": max(pressures) - min(pressures),
            "data_points": len(pressures),
            "calibration_offset": self.calibration_offset,
            "days_since_calibration": (datetime.utcnow() - self.last_calibration).days,
            "sensor_accuracy": self.sensor_accuracy,
            "altitude": self.altitude,
            "altitude_adjusted_base": self.altitude_adjusted_base,
            "weather_trend": self.weather_trend,
            "pressure_trend": self._calculate_pressure_trend()
        }
        
        # Add sea level pressure statistics if altitude > 0
        if self.altitude > 0:
            sea_level_pressures = []
            for _, pressure in self.pressure_history:
                sea_level_pressure = self._calculate_sea_level_pressure(pressure)
                sea_level_pressures.append(sea_level_pressure)
            
            stats.update({
                "current_sea_level_pressure": self._calculate_sea_level_pressure(self.current_pressure),
                "average_sea_level_pressure": sum(sea_level_pressures) / len(sea_level_pressures),
                "min_sea_level_pressure": min(sea_level_pressures),
                "max_sea_level_pressure": max(sea_level_pressures)
            })
        
        return stats
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get extended device information"""
        base_info = super().get_device_info()
        
        # Add pressure sensor specific info
        base_info.update({
            "sensor_type": "pressure",
            "current_pressure": self.current_pressure,
            "target_pressure": self.target_pressure,
            "base_pressure": self.base_pressure,
            "altitude_adjusted_base": self.altitude_adjusted_base,
            "calibration_offset": self.calibration_offset,
            "sensor_accuracy": self.sensor_accuracy,
            "altitude": self.altitude,
            "temperature_compensation": self.temperature_compensation,
            "current_temperature": self.current_temperature,
            "pressure_history_size": len(self.pressure_history),
            "weather_trend": self.weather_trend,
            "pressure_statistics": self.get_pressure_statistics()
        })
        
        return base_info


def create_pressure_sensor(device_id: int, location: str = "Unknown", altitude: float = 0.0) -> PressureSensor:
    """Factory function to create a pressure sensor"""
    return PressureSensor(device_id, location, altitude)


if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Create pressure sensor at 500m altitude
        sensor = create_pressure_sensor(3001, "Mountain Station A", altitude=500.0)
        
        # Enable temperature compensation
        sensor.set_temperature_compensation(True)
        
        # Update temperature
        sensor.update_temperature(12.5)
        
        # Simulate weather front
        sensor.simulate_weather_front(-8.0)
        
        try:
            await sensor.start()
            await asyncio.sleep(300)
        except KeyboardInterrupt:
            print("Stopping sensor...")
        finally:
            await sensor.stop()
    
    asyncio.run(main())
