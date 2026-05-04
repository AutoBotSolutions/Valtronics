"""
Air Quality Monitor Mock Device

This module simulates an air quality monitor that provides realistic readings for
various air quality parameters including PM2.5, PM10, CO2, VOC, and AQI calculations.
"""

import asyncio
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from ..base_device import BaseDevice, TelemetryData, DeviceConfig, DeviceStatus, DeviceType
from ..utils.data_generator import DataGenerator


class AirQualityMonitor(BaseDevice):
    """Mock air quality monitor device"""
    
    def __init__(self, device_id: int, location: str = "Unknown"):
        config = DeviceConfig(
            device_id=device_id,
            device_name=f"Air Quality Monitor {device_id:04d}",
            device_type=DeviceType.MONITOR,
            manufacturer="AirSense Corp",
            model="AS-AQ5000",
            firmware_version="4.1.2",
            location=location,
            mqtt_topic=f"valtronics/devices/{device_id}/telemetry",
            api_endpoint="/api/v1/telemetry/",
            telemetry_interval=60,  # Air quality typically measured less frequently
            health_check_interval=300
        )
        
        super().__init__(config)
        
        # Air quality sensor parameters
        self.pm25_base = 15.0           # Base PM2.5 in μg/m³
        self.pm10_base = 25.0           # Base PM10 in μg/m³
        self.co2_base = 400.0           # Base CO2 in ppm
        self.voc_base = 0.2              # Base VOC in ppm
        self.o3_base = 0.05              # Base Ozone in ppm
        self.no2_base = 0.02             # Base NO2 in ppm
        self.so2_base = 0.01             # Base SO2 in ppm
        
        # Sensor accuracies
        self.pm25_accuracy = 2.0        # PM2.5 accuracy in μg/m³
        self.pm10_accuracy = 3.0        # PM10 accuracy in μg/m³
        self.co2_accuracy = 20.0         # CO2 accuracy in ppm
        self.voc_accuracy = 0.05         # VOC accuracy in ppm
        
        # Data generator
        self.data_generator = DataGenerator()
        
        # Current readings
        self.current_pm25 = self.pm25_base
        self.current_pm10 = self.pm10_base
        self.current_co2 = self.co2_base
        self.current_voc = self.voc_base
        self.current_o3 = self.o3_base
        self.current_no2 = self.no2_base
        self.current_so2 = self.so2_base
        self.current_aqi = 50  # AQI value
        
        # Environmental factors
        self.ventilation_rate = 0.5      # 0-1 scale
        self.occupancy_level = 1.0       # Relative occupancy
        self.pollution_sources = []       # List of pollution sources
        self.weather_conditions = "clear" # Weather affects air quality
        
        # Sensor health metrics
        self.sensor_calibration_factors = {
            'pm25': 1.0,
            'pm10': 1.0,
            'co2': 1.0,
            'voc': 1.0,
            'o3': 1.0,
            'no2': 1.0,
            'so2': 1.0
        }
        
        self.last_calibration = datetime.utcnow() - timedelta(days=30)
        
        # Alert thresholds
        self.aqi_thresholds = {
            'moderate': 100,
            'unhealthy_sensitive': 150,
            'unhealthy': 200,
            'very_unhealthy': 300,
            'hazardous': 500
        }
        
        self.pm25_alert_threshold = 35.0
        self.pm10_alert_threshold = 50.0
        self.co2_alert_threshold = 1000.0
        
        # Historical data
        self.aqi_history = []
        self.max_history_size = 1440  # 24 hours of data
    
    async def generate_telemetry(self) -> List[TelemetryData]:
        """Generate air quality telemetry data"""
        telemetry = []
        
        try:
            # Calculate realistic air quality values
            await self._calculate_air_quality()
            
            # Generate telemetry for each parameter
            telemetry.extend(await self._generate_particulate_telemetry())
            telemetry.extend(await self._generate_gas_telemetry())
            telemetry.extend(await self._generate_aqi_telemetry())
            
            # Update history
            self._update_aqi_history()
            
            # Check for alerts
            await self._check_air_quality_alerts()
            
            # Simulate sensor drift
            self._simulate_sensor_drift()
            
        except Exception as e:
            self.logger.error(f"Error generating air quality telemetry: {e}")
            self.error_count += 1
        
        return telemetry
    
    async def _calculate_air_quality(self):
        """Calculate realistic air quality values"""
        now = datetime.utcnow()
        hour_of_day = now.hour + now.minute / 60.0
        
        # Time-based variations
        # PM levels typically higher during rush hours
        if 7 <= hour_of_day <= 9 or 17 <= hour_of_day <= 19:
            rush_hour_factor = 1.5
        else:
            rush_hour_factor = 1.0
        
        # Calculate PM2.5
        pm25_variation = random.gauss(0, 5.0)
        pm25 = self.pm25_base * rush_hour_factor * self.occupancy_level
        pm25 += pm25_variation
        
        # Apply pollution sources
        for source in self.pollution_sources:
            if source['type'] in ['pm25', 'pm10', 'all']:
                pm25 += source['intensity'] * source['proximity_factor']
        
        # Apply ventilation effect
        pm25 *= (1 - self.ventilation_rate * 0.6)
        self.current_pm25 = max(0, pm25)
        
        # Calculate PM10 (typically correlated with PM2.5)
        pm10 = self.current_pm25 * 1.7 + random.gauss(0, 8.0)
        for source in self.pollution_sources:
            if source['type'] in ['pm10', 'all']:
                pm10 += source['intensity'] * source['proximity_factor']
        pm10 *= (1 - self.ventilation_rate * 0.6)
        self.current_pm10 = max(0, pm10)
        
        # Calculate CO2 (heavily affected by occupancy and ventilation)
        co2 = self.co2_base + (self.occupancy_level * 400) + random.gauss(0, 50)
        co2 *= (2 - self.ventilation_rate)  # Poor ventilation increases CO2
        self.current_co2 = max(350, co2)  # Minimum outdoor CO2 level
        
        # Calculate VOC (from various sources)
        voc = self.voc_base + random.gauss(0, 0.1)
        for source in self.pollution_sources:
            if source['type'] in ['voc', 'all']:
                voc += source['intensity'] * source['proximity_factor'] * 0.1
        voc *= (2 - self.ventilation_rate * 0.8)
        self.current_voc = max(0, voc)
        
        # Calculate O3 (higher during sunny days, affected by NOx)
        if self.weather_conditions == "sunny":
            o3_factor = 1.5
        elif self.weather_conditions == "cloudy":
            o3_factor = 0.8
        else:
            o3_factor = 1.0
        
        o3 = self.o3_base * o3_factor + random.gauss(0, 0.02)
        self.current_o3 = max(0, o3)
        
        # Calculate NO2 (from combustion sources)
        no2 = self.no2_base + (self.occupancy_level * 0.01) + random.gauss(0, 0.005)
        for source in self.pollution_sources:
            if source['type'] in ['combustion', 'all']:
                no2 += source['intensity'] * source['proximity_factor'] * 0.02
        self.current_no2 = max(0, no2)
        
        # Calculate SO2 (mainly from industrial sources)
        so2 = self.so2_base + random.gauss(0, 0.002)
        for source in self.pollution_sources:
            if source['type'] in ['industrial', 'all']:
                so2 += source['intensity'] * source['proximity_factor'] * 0.005
        self.current_so2 = max(0, so2)
        
        # Calculate AQI
        self.current_aqi = self._calculate_aqi()
    
    async def _generate_particulate_telemetry(self) -> List[TelemetryData]:
        """Generate particulate matter telemetry"""
        telemetry = []
        
        # PM2.5
        pm25_measured = self.current_pm25 * self.sensor_calibration_factors['pm25']
        pm25_measured += random.gauss(0, self.pm25_accuracy)
        
        pm25_data = TelemetryData(
            metric_name="pm25",
            metric_value=round(pm25_measured, 1),
            unit="μg/m³",
            timestamp=datetime.utcnow(),
            device_id=self.device_id,
            metadata={
                "sensor_type": "air_quality",
                "parameter": "particulate_matter",
                "size": "2.5",
                "accuracy": self.pm25_accuracy,
                "calibration_factor": self.sensor_calibration_factors['pm25']
            }
        )
        telemetry.append(pm25_data)
        
        # PM10
        pm10_measured = self.current_pm10 * self.sensor_calibration_factors['pm10']
        pm10_measured += random.gauss(0, self.pm10_accuracy)
        
        pm10_data = TelemetryData(
            metric_name="pm10",
            metric_value=round(pm10_measured, 1),
            unit="μg/m³",
            timestamp=datetime.utcnow(),
            device_id=self.device_id,
            metadata={
                "sensor_type": "air_quality",
                "parameter": "particulate_matter",
                "size": "10",
                "accuracy": self.pm10_accuracy,
                "calibration_factor": self.sensor_calibration_factors['pm10']
            }
        )
        telemetry.append(pm10_data)
        
        return telemetry
    
    async def _generate_gas_telemetry(self) -> List[TelemetryData]:
        """Generate gas concentration telemetry"""
        telemetry = []
        
        # CO2
        co2_measured = self.current_co2 * self.sensor_calibration_factors['co2']
        co2_measured += random.gauss(0, self.co2_accuracy)
        
        co2_data = TelemetryData(
            metric_name="co2",
            metric_value=round(co2_measured, 0),
            unit="ppm",
            timestamp=datetime.utcnow(),
            device_id=self.device_id,
            metadata={
                "sensor_type": "air_quality",
                "parameter": "gas",
                "gas_type": "carbon_dioxide",
                "accuracy": self.co2_accuracy,
                "calibration_factor": self.sensor_calibration_factors['co2']
            }
        )
        telemetry.append(co2_data)
        
        # VOC
        voc_measured = self.current_voc * self.sensor_calibration_factors['voc']
        voc_measured += random.gauss(0, self.voc_accuracy)
        
        voc_data = TelemetryData(
            metric_name="voc",
            metric_value=round(voc_measured, 3),
            unit="ppm",
            timestamp=datetime.utcnow(),
            device_id=self.device_id,
            metadata={
                "sensor_type": "air_quality",
                "parameter": "gas",
                "gas_type": "volatile_organic_compounds",
                "accuracy": self.voc_accuracy,
                "calibration_factor": self.sensor_calibration_factors['voc']
            }
        )
        telemetry.append(voc_data)
        
        # O3
        o3_measured = self.current_o3 * self.sensor_calibration_factors['o3']
        
        o3_data = TelemetryData(
            metric_name="o3",
            metric_value=round(o3_measured, 3),
            unit="ppm",
            timestamp=datetime.utcnow(),
            device_id=self.device_id,
            metadata={
                "sensor_type": "air_quality",
                "parameter": "gas",
                "gas_type": "ozone",
                "calibration_factor": self.sensor_calibration_factors['o3']
            }
        )
        telemetry.append(o3_data)
        
        # NO2
        no2_measured = self.current_no2 * self.sensor_calibration_factors['no2']
        
        no2_data = TelemetryData(
            metric_name="no2",
            metric_value=round(no2_measured, 3),
            unit="ppm",
            timestamp=datetime.utcnow(),
            device_id=self.device_id,
            metadata={
                "sensor_type": "air_quality",
                "parameter": "gas",
                "gas_type": "nitrogen_dioxide",
                "calibration_factor": self.sensor_calibration_factors['no2']
            }
        )
        telemetry.append(no2_data)
        
        # SO2
        so2_measured = self.current_so2 * self.sensor_calibration_factors['so2']
        
        so2_data = TelemetryData(
            metric_name="so2",
            metric_value=round(so2_measured, 3),
            unit="ppm",
            timestamp=datetime.utcnow(),
            device_id=self.device_id,
            metadata={
                "sensor_type": "air_quality",
                "parameter": "gas",
                "gas_type": "sulfur_dioxide",
                "calibration_factor": self.sensor_calibration_factors['so2']
            }
        )
        telemetry.append(so2_data)
        
        return telemetry
    
    async def _generate_aqi_telemetry(self) -> List[TelemetryData]:
        """Generate Air Quality Index telemetry"""
        telemetry = []
        
        # Main AQI
        aqi_data = TelemetryData(
            metric_name="aqi",
            metric_value=round(self.current_aqi, 0),
            unit="AQI",
            timestamp=datetime.utcnow(),
            device_id=self.device_id,
            metadata={
                "sensor_type": "air_quality",
                "parameter": "index",
                "index_type": "air_quality_index",
                "calculation_method": "epa_aqi",
                "dominant_pollutant": self._get_dominant_pollutant(),
                "aqi_level": self._get_aqi_level()
            }
        )
        telemetry.append(aqi_data)
        
        # Individual pollutant AQI contributions
        pm25_aqi = self._calculate_pollutant_aqi(self.current_pm25, 'pm25')
        pm10_aqi = self._calculate_pollutant_aqi(self.current_pm10, 'pm10')
        co2_aqi = self._calculate_pollutant_aqi(self.current_co2, 'co2')
        
        for pollutant, aqi in [('pm25', pm25_aqi), ('pm10', pm10_aqi), ('co2', co2_aqi)]:
            aqi_contrib_data = TelemetryData(
                metric_name=f"{pollutant}_aqi",
                metric_value=round(aqi, 0),
                unit="AQI",
                timestamp=datetime.utcnow(),
                device_id=self.device_id,
                metadata={
                    "sensor_type": "air_quality",
                    "parameter": "index",
                    "index_type": "pollutant_aqi",
                    "pollutant": pollutant,
                    "raw_value": getattr(self, f"current_{pollutant}")
                }
            )
            telemetry.append(aqi_contrib_data)
        
        return telemetry
    
    def _calculate_aqi(self) -> int:
        """Calculate overall Air Quality Index"""
        # Calculate AQI for each pollutant
        pm25_aqi = self._calculate_pollutant_aqi(self.current_pm25, 'pm25')
        pm10_aqi = self._calculate_pollutant_aqi(self.current_pm10, 'pm10')
        co2_aqi = self._calculate_pollutant_aqi(self.current_co2, 'co2')
        
        # AQI is the maximum of individual pollutant AQIs
        return max(pm25_aqi, pm10_aqi, co2_aqi)
    
    def _calculate_pollutant_aqi(self, concentration: float, pollutant: str) -> int:
        """Calculate AQI for a specific pollutant"""
        # EPA AQI breakpoints (simplified)
        if pollutant == 'pm25':
            # PM2.5 breakpoints (24-hour average)
            if concentration <= 12.0:
                return int((50 / 12.0) * concentration)
            elif concentration <= 35.4:
                return int(100 + ((100 - 50) / (35.4 - 12.0)) * (concentration - 12.0))
            elif concentration <= 55.4:
                return int(150 + ((150 - 100) / (55.4 - 35.4)) * (concentration - 35.4))
            elif concentration <= 150.4:
                return int(200 + ((200 - 150) / (150.4 - 55.4)) * (concentration - 55.4))
            elif concentration <= 250.4:
                return int(300 + ((300 - 200) / (250.4 - 150.4)) * (concentration - 150.4))
            else:
                return int(400 + ((500 - 400) / (500.4 - 250.4)) * min(concentration - 250.4, 250.0))
        
        elif pollutant == 'pm10':
            # PM10 breakpoints (24-hour average)
            if concentration <= 54:
                return int((50 / 54) * concentration)
            elif concentration <= 154:
                return int(100 + ((100 - 50) / (154 - 54)) * (concentration - 54))
            elif concentration <= 254:
                return int(150 + ((150 - 100) / (254 - 154)) * (concentration - 154))
            elif concentration <= 354:
                return int(200 + ((200 - 150) / (354 - 254)) * (concentration - 254))
            elif concentration <= 424:
                return int(300 + ((300 - 200) / (424 - 354)) * (concentration - 354))
            else:
                return int(400 + ((500 - 400) / (604 - 424)) * min(concentration - 424, 180.0))
        
        elif pollutant == 'co2':
            # CO2 (not standard in EPA AQI, but we'll approximate)
            if concentration <= 600:
                return int((50 / 600) * concentration)
            elif concentration <= 1000:
                return int(100 + ((100 - 50) / (1000 - 600)) * (concentration - 600))
            elif concentration <= 1500:
                return int(150 + ((150 - 100) / (1500 - 1000)) * (concentration - 1000))
            elif concentration <= 2000:
                return int(200 + ((200 - 150) / (2000 - 1500)) * (concentration - 1500))
            else:
                return int(300 + ((400 - 300) / (5000 - 2000)) * min(concentration - 2000, 3000.0))
        
        return 50  # Default to moderate
    
    def _get_dominant_pollutant(self) -> str:
        """Get the dominant pollutant contributing to AQI"""
        pm25_aqi = self._calculate_pollutant_aqi(self.current_pm25, 'pm25')
        pm10_aqi = self._calculate_pollutant_aqi(self.current_pm10, 'pm10')
        co2_aqi = self._calculate_pollutant_aqi(self.current_co2, 'co2')
        
        aqi_values = {'pm25': pm25_aqi, 'pm10': pm10_aqi, 'co2': co2_aqi}
        return max(aqi_values, key=aqi_values.get)
    
    def _get_aqi_level(self) -> str:
        """Get AQI level description"""
        aqi = self.current_aqi
        
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"
    
    def _update_aqi_history(self):
        """Update AQI history"""
        self.aqi_history.append((datetime.utcnow(), self.current_aqi))
        
        if len(self.aqi_history) > self.max_history_size:
            self.aqi_history = self.aqi_history[-self.max_history_size:]
    
    def _simulate_sensor_drift(self):
        """Simulate sensor calibration drift"""
        for sensor in self.sensor_calibration_factors:
            drift = random.gauss(0, 0.001)
            self.sensor_calibration_factors[sensor] *= (1 + drift)
            self.sensor_calibration_factors[sensor] = max(0.8, min(1.2, self.sensor_calibration_factors[sensor]))
    
    async def _check_air_quality_alerts(self):
        """Check for air quality alerts"""
        alerts = []
        
        # AQI alerts
        aqi_level = self._get_aqi_level()
        if self.current_aqi >= self.aqi_thresholds['unhealthy_sensitive']:
            severity = "warning" if self.current_aqi < self.aqi_thresholds['unhealthy'] else "critical"
            
            alert_data = {
                "device_id": self.device_id,
                "title": f"Air Quality Alert - {aqi_level}",
                "description": f"AQI is {self.current_aqi} ({aqi_level})",
                "severity": severity,
                "metric_name": "aqi",
                "metric_value": self.current_aqi,
                "threshold_value": self.aqi_thresholds['unhealthy_sensitive'],
                "dominant_pollutant": self._get_dominant_pollutant(),
                "location": self.config.location
            }
            alerts.append(alert_data)
        
        # PM2.5 alert
        if self.current_pm25 > self.pm25_alert_threshold:
            alert_data = {
                "device_id": self.device_id,
                "title": "High PM2.5 Alert",
                "description": f"PM2.5 level is {self.current_pm25:.1f} μg/m³",
                "severity": "warning",
                "metric_name": "pm25",
                "metric_value": self.current_pm25,
                "threshold_value": self.pm25_alert_threshold,
                "location": self.config.location
            }
            alerts.append(alert_data)
        
        # PM10 alert
        if self.current_pm10 > self.pm10_alert_threshold:
            alert_data = {
                "device_id": self.device_id,
                "title": "High PM10 Alert",
                "description": f"PM10 level is {self.current_pm10:.1f} μg/m³",
                "severity": "warning",
                "metric_name": "pm10",
                "metric_value": self.current_pm10,
                "threshold_value": self.pm10_alert_threshold,
                "location": self.config.location
            }
            alerts.append(alert_data)
        
        # CO2 alert
        if self.current_co2 > self.co2_alert_threshold:
            alert_data = {
                "device_id": self.device_id,
                "title": "High CO2 Alert",
                "description": f"CO2 level is {self.current_co2:.0f} ppm",
                "severity": "warning",
                "metric_name": "co2",
                "metric_value": self.current_co2,
                "threshold_value": self.co2_alert_threshold,
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
    
    def set_ventilation_rate(self, rate: float):
        """Set ventilation rate (0.0 to 1.0)"""
        self.ventilation_rate = max(0.0, min(1.0, rate))
        self.logger.info(f"Set ventilation rate to {self.ventilation_rate}")
    
    def set_occupancy_level(self, level: float):
        """Set occupancy level (0.0 to 2.0, where 1.0 is normal)"""
        self.occupancy_level = max(0.0, min(2.0, level))
        self.logger.info(f"Set occupancy level to {self.occupancy_level}")
    
    def set_weather_conditions(self, conditions: str):
        """Set weather conditions"""
        valid_conditions = ["clear", "cloudy", "rainy", "foggy", "sunny"]
        if conditions in valid_conditions:
            self.weather_conditions = conditions
            self.logger.info(f"Set weather conditions to {conditions}")
    
    def add_pollution_source(self, name: str, source_type: str, intensity: float, proximity_factor: float = 1.0):
        """Add a pollution source"""
        pollution_source = {
            "name": name,
            "type": source_type,
            "intensity": intensity,
            "proximity_factor": proximity_factor,
            "added_at": datetime.utcnow()
        }
        self.pollution_sources.append(pollution_source)
        self.logger.info(f"Added pollution source: {name} (type: {source_type}, intensity: {intensity})")
    
    def remove_pollution_source(self, name: str):
        """Remove a pollution source"""
        self.pollution_sources = [ps for ps in self.pollution_sources if ps["name"] != name]
        self.logger.info(f"Removed pollution source: {name}")
    
    def calibrate_sensor(self, sensor: str, reference_value: float):
        """Calibrate a specific sensor"""
        if sensor in self.sensor_calibration_factors:
            current_value = getattr(self, f"current_{sensor}")
            calibration_factor = reference_value / current_value
            self.sensor_calibration_factors[sensor] = calibration_factor
            self.last_calibration = datetime.utcnow()
            
            self.logger.info(f"Calibrated {sensor} sensor: factor={calibration_factor:.3f}, reference={reference_value}")
    
    def get_air_quality_statistics(self) -> Dict[str, Any]:
        """Get air quality statistics"""
        if not self.aqi_history:
            return {}
        
        aqi_values = [aqi for _, aqi in self.aqi_history]
        
        return {
            "current_aqi": self.current_aqi,
            "aqi_level": self._get_aqi_level(),
            "dominant_pollutant": self._get_dominant_pollutant(),
            "average_aqi": sum(aqi_values) / len(aqi_values),
            "min_aqi": min(aqi_values),
            "max_aqi": max(aqi_values),
            "data_points": len(aqi_values),
            "current_readings": {
                "pm25": self.current_pm25,
                "pm10": self.current_pm10,
                "co2": self.current_co2,
                "voc": self.current_voc,
                "o3": self.current_o3,
                "no2": self.current_no2,
                "so2": self.current_so2
            },
            "environmental_factors": {
                "ventilation_rate": self.ventilation_rate,
                "occupancy_level": self.occupancy_level,
                "weather_conditions": self.weather_conditions,
                "pollution_sources": len(self.pollution_sources)
            }
        }
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get extended device information"""
        base_info = super().get_device_info()
        
        # Add air quality monitor specific info
        base_info.update({
            "sensor_type": "air_quality_monitor",
            "current_aqi": self.current_aqi,
            "aqi_level": self._get_aqi_level(),
            "dominant_pollutant": self._get_dominant_pollutant(),
            "current_readings": {
                "pm25": self.current_pm25,
                "pm10": self.current_pm10,
                "co2": self.current_co2,
                "voc": self.current_voc,
                "o3": self.current_o3,
                "no2": self.current_no2,
                "so2": self.current_so2
            },
            "sensor_calibration_factors": self.sensor_calibration_factors,
            "environmental_factors": {
                "ventilation_rate": self.ventilation_rate,
                "occupancy_level": self.occupancy_level,
                "weather_conditions": self.weather_conditions,
                "pollution_sources": self.pollution_sources
            },
            "aqi_history_size": len(self.aqi_history),
            "air_quality_statistics": self.get_air_quality_statistics()
        })
        
        return base_info


def create_air_quality_monitor(device_id: int, location: str = "Unknown") -> AirQualityMonitor:
    """Factory function to create an air quality monitor"""
    return AirQualityMonitor(device_id, location)


if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Create air quality monitor
        monitor = create_air_quality_monitor(4001, "Office Building A")
        
        # Set environmental factors
        monitor.set_ventilation_rate(0.3)
        monitor.set_occupancy_level(1.5)
        monitor.set_weather_conditions("sunny")
        
        # Add pollution sources
        monitor.add_pollution_source("Traffic", "all", intensity=15.0, proximity_factor=0.8)
        monitor.add_pollution_source("HVAC System", "voc", intensity=5.0, proximity_factor=0.5)
        
        try:
            await monitor.start()
            await asyncio.sleep(300)
        except KeyboardInterrupt:
            print("Stopping monitor...")
        finally:
            await monitor.stop()
    
    asyncio.run(main())
