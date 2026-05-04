"""
Vibration Sensor Mock Device

This module simulates a vibration sensor that provides realistic vibration readings
for industrial equipment monitoring with fault detection capabilities.
"""

import asyncio
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from ..base_device import BaseDevice, TelemetryData, DeviceConfig, DeviceStatus, DeviceType
from ..utils.data_generator import DataGenerator


class VibrationSensor(BaseDevice):
    """Mock vibration sensor device"""
    
    def __init__(self, device_id: int, equipment_name: str = "Unknown Equipment"):
        config = DeviceConfig(
            device_id=device_id,
            device_name=f"Vibration Sensor {device_id:04d}",
            device_type=DeviceType.MONITOR,
            manufacturer="VibraTech Corp",
            model="VT-V5000",
            firmware_version="2.3.1",
            location=f"Equipment: {equipment_name}",
            mqtt_topic=f"valtronics/devices/{device_id}/telemetry",
            api_endpoint="/api/v1/telemetry/",
            telemetry_interval=10,  # Vibration measured frequently
            health_check_interval=300
        )
        
        super().__init__(config)
        
        # Vibration sensor specific parameters
        self.base_vibration = 0.1         # Base vibration in mm/s
        self.frequency_range = [10, 1000]  # Frequency range in Hz
        self.sensor_accuracy = 0.01       # Sensor accuracy in mm/s
        self.mounting_type = "bearing"     # bearing, motor, pump, gearbox
        
        # Data generator
        self.data_generator = DataGenerator()
        
        # Current readings
        self.current_vibration = self.base_vibration
        self.current_frequency = 50.0      # Dominant frequency in Hz
        self.current_rms = self.base_vibration
        self.current_peak = self.base_vibration * 1.5
        self.current_crest_factor = 1.5    # Peak/RMS ratio
        
        # Equipment parameters
        self.equipment_name = equipment_name
        self.equipment_speed = 1800        # RPM
        self.equipment_load = 0.7          # 0-1 scale
        self.equipment_age = 5.0           # Years
        self.maintenance_status = "good"    # good, fair, poor, critical
        
        # Fault simulation
        self.fault_conditions = {
            "bearing_fault": False,
            "misalignment": False,
            "unbalance": False,
            "looseness": False,
            "gear_fault": False
        }
        
        self.fault_severity = {
            "bearing_fault": 0.0,      # 0-1 scale
            "misalignment": 0.0,
            "unbalance": 0.0,
            "looseness": 0.0,
            "gear_fault": 0.0
        }
        
        # Sensor health metrics
        self.calibration_factor = 1.0
        self.last_calibration = datetime.utcnow() - timedelta(days=90)
        self.sensor_temperature = 25.0    # Sensor temperature in °C
        
        # Alert thresholds
        self.vibration_warning_threshold = 0.5
        self.vibration_critical_threshold = 1.0
        self.crest_factor_threshold = 3.0
        self.frequency_anomaly_threshold = 50.0
        
        # Historical data
        self.vibration_history = []
        self.frequency_spectrum = []
        self.max_history_size = 1440  # 24 hours of data
        
        # FFT simulation parameters
        self.fft_bins = 64
        self.harmonics = [1, 2, 3, 4, 5]  # Harmonics of running frequency
    
    async def generate_telemetry(self) -> List[TelemetryData]:
        """Generate vibration telemetry data"""
        telemetry = []
        
        try:
            # Calculate realistic vibration values
            await self._calculate_vibration()
            
            # Generate main vibration telemetry
            telemetry.extend(await self._generate_vibration_metrics())
            
            # Generate frequency spectrum
            telemetry.extend(await self._generate_frequency_spectrum())
            
            # Generate fault indicators
            telemetry.extend(await self._generate_fault_indicators())
            
            # Update history
            self._update_vibration_history()
            
            # Check for alerts
            await self._check_vibration_alerts()
            
            # Simulate sensor aging
            self._simulate_sensor_aging()
            
        except Exception as e:
            self.logger.error(f"Error generating vibration telemetry: {e}")
            self.error_count += 1
        
        return telemetry
    
    async def _calculate_vibration(self):
        """Calculate realistic vibration values"""
        # Base vibration from equipment operation
        running_frequency = self.equipment_speed / 60.0  # Convert RPM to Hz
        
        # Load effect on vibration
        load_factor = 1.0 + (self.equipment_load - 0.5) * 0.5
        
        # Age effect on vibration
        age_factor = 1.0 + (self.equipment_age / 10.0) * 0.3
        
        # Calculate base vibration
        base_vib = self.base_vibration * load_factor * age_factor
        
        # Add fault contributions
        fault_vibration = 0.0
        
        if self.fault_conditions["bearing_fault"]:
            bearing_freq = running_frequency * 3  # Bearing frequency
            bearing_contribution = self.fault_severity["bearing_fault"] * 0.5
            fault_vibration += bearing_contribution * math.sin(2 * math.pi * bearing_freq * 0.1)
        
        if self.fault_conditions["misalignment"]:
            alignment_contribution = self.fault_severity["misalignment"] * 0.3
            fault_vibration += alignment_contribution * math.sin(2 * math.pi * running_frequency * 2 * 0.1)
        
        if self.fault_conditions["unbalance"]:
            unbalance_contribution = self.fault_severity["unbalance"] * 0.4
            fault_vibration += unbalance_contribution * math.sin(2 * math.pi * running_frequency * 0.1)
        
        if self.fault_conditions["looseness"]:
            looseness_contribution = self.fault_severity["looseness"] * 0.6
            # Looseness creates multiple frequency components
            for harmonic in self.harmonics:
                fault_vibration += looseness_contribution * 0.1 * math.sin(2 * math.pi * running_frequency * harmonic * 0.1)
        
        if self.fault_conditions["gear_fault"]:
            gear_freq = running_frequency * 4  # Gear mesh frequency
            gear_contribution = self.fault_severity["gear_fault"] * 0.3
            fault_vibration += gear_contribution * math.sin(2 * math.pi * gear_freq * 0.1)
        
        # Random environmental noise
        noise = self.data_generator.add_noise(0, base_vib * 0.1)
        
        # Calculate total vibration
        total_vibration = base_vib + fault_vibration + noise
        self.current_vibration = max(0, total_vibration)
        
        # Calculate RMS and Peak values
        self.current_rms = self.current_vibration
        self.current_peak = self.current_vibration * (1.5 + random.gauss(0, 0.2))
        self.current_crest_factor = self.current_peak / self.current_rms if self.current_rms > 0 else 1.0
        
        # Update dominant frequency
        if self.fault_conditions["bearing_fault"]:
            self.current_frequency = running_frequency * 3
        elif self.fault_conditions["misalignment"]:
            self.current_frequency = running_frequency * 2
        elif self.fault_conditions["unbalance"]:
            self.current_frequency = running_frequency
        else:
            self.current_frequency = running_frequency + random.gauss(0, 5)
    
    async def _generate_vibration_metrics(self) -> List[TelemetryData]:
        """Generate main vibration metrics telemetry"""
        telemetry = []
        
        # RMS vibration
        rms_measured = self.current_rms * self.calibration_factor
        rms_measured += random.gauss(0, self.sensor_accuracy)
        
        rms_data = TelemetryData(
            metric_name="vibration_rms",
            metric_value=round(rms_measured, 3),
            unit="mm/s",
            timestamp=datetime.utcnow(),
            device_id=self.device_id,
            metadata={
                "sensor_type": "vibration",
                "parameter": "root_mean_square",
                "sensor_model": self.config.model,
                "calibration_factor": self.calibration_factor,
                "equipment_name": self.equipment_name,
                "equipment_speed": self.equipment_speed,
                "mounting_type": self.mounting_type
            }
        )
        telemetry.append(rms_data)
        
        # Peak vibration
        peak_measured = self.current_peak * self.calibration_factor
        peak_measured += random.gauss(0, self.sensor_accuracy * 1.5)
        
        peak_data = TelemetryData(
            metric_name="vibration_peak",
            metric_value=round(peak_measured, 3),
            unit="mm/s",
            timestamp=datetime.utcnow(),
            device_id=self.device_id,
            metadata={
                "sensor_type": "vibration",
                "parameter": "peak",
                "sensor_model": self.config.model,
                "calibration_factor": self.calibration_factor,
                "crest_factor": self.current_crest_factor
            }
        )
        telemetry.append(peak_data)
        
        # Crest factor
        crest_data = TelemetryData(
            metric_name="vibration_crest_factor",
            metric_value=round(self.current_crest_factor, 2),
            unit="ratio",
            timestamp=datetime.utcnow(),
            device_id=self.device_id,
            metadata={
                "sensor_type": "vibration",
                "parameter": "crest_factor",
                "calculation": "peak/rms",
                "normal_range": "1.5-3.0"
            }
        )
        telemetry.append(crest_data)
        
        # Sensor temperature
        temp_data = TelemetryData(
            metric_name="sensor_temperature",
            metric_value=round(self.sensor_temperature, 1),
            unit="°C",
            timestamp=datetime.utcnow(),
            device_id=self.device_id,
            metadata={
                "sensor_type": "vibration",
                "parameter": "temperature",
                "sensor_model": self.config.model
            }
        )
        telemetry.append(temp_data)
        
        return telemetry
    
    async def _generate_frequency_spectrum(self) -> List[TelemetryData]:
        """Generate frequency spectrum telemetry"""
        telemetry = []
        
        # Simulate FFT spectrum
        running_frequency = self.equipment_speed / 60.0
        spectrum = []
        
        for i in range(self.fft_bins):
            freq = i * (self.frequency_range[1] / self.fft_bins)
            amplitude = 0.0
            
            # Add fundamental and harmonics
            for harmonic in self.harmonics:
                harmonic_freq = running_frequency * harmonic
                if abs(freq - harmonic_freq) < 5:  # Within 5 Hz of harmonic
                    if harmonic == 1:
                        amplitude = self.current_vibration * 0.8
                    elif harmonic == 2 and self.fault_conditions["misalignment"]:
                        amplitude = self.current_vibration * 0.4 * self.fault_severity["misalignment"]
                    elif harmonic == 3 and self.fault_conditions["bearing_fault"]:
                        amplitude = self.current_vibration * 0.6 * self.fault_severity["bearing_fault"]
                    else:
                        amplitude = self.current_vibration * 0.1 * random.random()
                    break
            
            # Add noise floor
            amplitude += random.gauss(0, 0.01)
            amplitude = max(0, amplitude)
            
            spectrum.append((freq, amplitude))
        
        self.frequency_spectrum = spectrum
        
        # Send dominant frequency
        dominant_freq_data = TelemetryData(
            metric_name="dominant_frequency",
            metric_value=round(self.current_frequency, 1),
            unit="Hz",
            timestamp=datetime.utcnow(),
            device_id=self.device_id,
            metadata={
                "sensor_type": "vibration",
                "parameter": "frequency",
                "calculation": "fft_peak_detection",
                "equipment_speed": self.equipment_speed
            }
        )
        telemetry.append(dominant_freq_data)
        
        # Send frequency spectrum summary (top 5 peaks)
        top_peaks = sorted(spectrum, key=lambda x: x[1], reverse=True)[:5]
        
        for i, (freq, amp) in enumerate(top_peaks):
            if amp > 0.01:  # Only send significant peaks
                peak_data = TelemetryData(
                    metric_name=f"frequency_peak_{i+1}",
                    metric_value=round(amp, 3),
                    unit="mm/s",
                    timestamp=datetime.utcnow(),
                    device_id=self.device_id,
                    metadata={
                        "sensor_type": "vibration",
                        "parameter": "frequency_spectrum",
                        "frequency": round(freq, 1),
                        "peak_rank": i+1,
                        "harmonic": self._identify_harmonic(freq, running_frequency)
                    }
                )
                telemetry.append(peak_data)
        
        return telemetry
    
    async def _generate_fault_indicators(self) -> List[TelemetryData]:
        """Generate fault indicator telemetry"""
        telemetry = []
        
        # Overall health score
        health_score = self._calculate_health_score()
        
        health_data = TelemetryData(
            metric_name="equipment_health_score",
            metric_value=round(health_score, 1),
            unit="%",
            timestamp=datetime.utcnow(),
            device_id=self.device_id,
            metadata={
                "sensor_type": "vibration",
                "parameter": "health_score",
                "calculation": "vibration_based",
                "maintenance_status": self.maintenance_status
            }
        )
        telemetry.append(health_data)
        
        # Individual fault indicators
        for fault_type, severity in self.fault_severity.items():
            if severity > 0.1:  # Only send if significant
                fault_data = TelemetryData(
                    metric_name=f"fault_{fault_type}",
                    metric_value=round(severity, 3),
                    unit="severity",
                    timestamp=datetime.utcnow(),
                    device_id=self.device_id,
                    metadata={
                        "sensor_type": "vibration",
                        "parameter": "fault_indicator",
                        "fault_type": fault_type,
                        "severity_level": self._get_severity_level(severity),
                        "active": self.fault_conditions[fault_type]
                    }
                )
                telemetry.append(fault_data)
        
        return telemetry
    
    def _identify_harmonic(self, freq: float, running_freq: float) -> Optional[str]:
        """Identify if frequency corresponds to a harmonic"""
        for harmonic in self.harmonics:
            harmonic_freq = running_freq * harmonic
            if abs(freq - harmonic_freq) < 5:
                return f"{harmonic}x"
        return None
    
    def _calculate_health_score(self) -> float:
        """Calculate equipment health score based on vibration"""
        # Base score starts at 100
        health_score = 100.0
        
        # Deduct points based on vibration level
        if self.current_vibration > self.vibration_critical_threshold:
            health_score -= 40
        elif self.current_vibration > self.vibration_warning_threshold:
            health_score -= 20
        
        # Deduct points based on crest factor
        if self.current_crest_factor > self.crest_factor_threshold:
            health_score -= 15
        elif self.current_crest_factor > 2.5:
            health_score -= 5
        
        # Deduct points based on fault severity
        for fault_severity in self.fault_severity.values():
            health_score -= fault_severity * 20
        
        # Deduct points based on equipment age
        health_score -= self.equipment_age * 2
        
        # Ensure score stays within bounds
        return max(0, min(100, health_score))
    
    def _get_severity_level(self, severity: float) -> str:
        """Get severity level description"""
        if severity < 0.2:
            return "low"
        elif severity < 0.5:
            return "moderate"
        elif severity < 0.8:
            return "high"
        else:
            return "critical"
    
    def _update_vibration_history(self):
        """Update vibration history"""
        self.vibration_history.append((datetime.utcnow(), self.current_vibration))
        
        if len(self.vibration_history) > self.max_history_size:
            self.vibration_history = self.vibration_history[-self.max_history_size:]
    
    def _simulate_sensor_aging(self):
        """Simulate sensor aging effects"""
        # Calibration factor drift
        drift = random.gauss(0, 0.0001)
        self.calibration_factor *= (1 + drift)
        self.calibration_factor = max(0.9, min(1.1, self.calibration_factor))
        
        # Sensor temperature variation
        self.sensor_temperature += random.gauss(0, 0.5)
        self.sensor_temperature = max(20, min(40, self.sensor_temperature))
        
        # Gradual fault development
        for fault_type in self.fault_severity:
            if self.fault_conditions[fault_type]:
                # Existing faults can worsen over time
                self.fault_severity[fault_type] += random.gauss(0, 0.001)
                self.fault_severity[fault_type] = min(1.0, self.fault_severity[fault_type])
            else:
                # Random fault development (very low probability)
                if random.random() < 0.0001:  # 0.01% chance per reading
                    self.fault_conditions[fault_type] = True
                    self.fault_severity[fault_type] = random.uniform(0.1, 0.3)
                    self.logger.warning(f"Fault developed: {fault_type}")
    
    async def _check_vibration_alerts(self):
        """Check for vibration-related alerts"""
        alerts = []
        
        # High vibration alert
        if self.current_vibration > self.vibration_critical_threshold:
            alert_data = {
                "device_id": self.device_id,
                "title": "Critical Vibration Alert",
                "description": f"Vibration level {self.current_vibration:.3f} mm/s exceeds critical threshold",
                "severity": "critical",
                "metric_name": "vibration_rms",
                "metric_value": self.current_vibration,
                "threshold_value": self.vibration_critical_threshold,
                "equipment_name": self.equipment_name
            }
            alerts.append(alert_data)
        elif self.current_vibration > self.vibration_warning_threshold:
            alert_data = {
                "device_id": self.device_id,
                "title": "High Vibration Warning",
                "description": f"Vibration level {self.current_vibration:.3f} mm/s exceeds warning threshold",
                "severity": "warning",
                "metric_name": "vibration_rms",
                "metric_value": self.current_vibration,
                "threshold_value": self.vibration_warning_threshold,
                "equipment_name": self.equipment_name
            }
            alerts.append(alert_data)
        
        # Crest factor alert
        if self.current_crest_factor > self.crest_factor_threshold:
            alert_data = {
                "device_id": self.device_id,
                "title": "High Crest Factor Alert",
                "description": f"Crest factor {self.current_crest_factor:.2f} indicates possible impact events",
                "severity": "warning",
                "metric_name": "vibration_crest_factor",
                "metric_value": self.current_crest_factor,
                "threshold_value": self.crest_factor_threshold,
                "equipment_name": self.equipment_name
            }
            alerts.append(alert_data)
        
        # Fault alerts
        for fault_type, severity in self.fault_severity.items():
            if self.fault_conditions[fault_type] and severity > 0.5:
                alert_data = {
                    "device_id": self.device_id,
                    "title": f"{fault_type.replace('_', ' ').title()} Alert",
                    "description": f"Fault detected with severity {severity:.3f}",
                    "severity": "critical" if severity > 0.8 else "warning",
                    "metric_name": f"fault_{fault_type}",
                    "metric_value": severity,
                    "threshold_value": 0.5,
                    "equipment_name": self.equipment_name
                }
                alerts.append(alert_data)
        
        # Health score alert
        health_score = self._calculate_health_score()
        if health_score < 50:
            alert_data = {
                "device_id": self.device_id,
                "title": "Equipment Health Alert",
                "description": f"Equipment health score is {health_score:.1f}%",
                "severity": "critical" if health_score < 30 else "warning",
                "metric_name": "equipment_health_score",
                "metric_value": health_score,
                "threshold_value": 50,
                "equipment_name": self.equipment_name
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
    
    def set_equipment_parameters(self, speed: float, load: float, age: float):
        """Set equipment operating parameters"""
        self.equipment_speed = speed
        self.equipment_load = max(0.0, min(1.0, load))
        self.equipment_age = max(0.0, age)
        self.logger.info(f"Updated equipment: speed={speed} RPM, load={load:.1f}, age={age:.1f} years")
    
    def induce_fault(self, fault_type: str, severity: float = 0.5):
        """Induce a fault condition for testing"""
        if fault_type in self.fault_conditions:
            self.fault_conditions[fault_type] = True
            self.fault_severity[fault_type] = max(0.0, min(1.0, severity))
            self.logger.info(f"Induced fault: {fault_type} with severity {severity}")
        else:
            self.logger.warning(f"Unknown fault type: {fault_type}")
    
    def clear_fault(self, fault_type: str):
        """Clear a fault condition"""
        if fault_type in self.fault_conditions:
            self.fault_conditions[fault_type] = False
            self.fault_severity[fault_type] = 0.0
            self.logger.info(f"Cleared fault: {fault_type}")
        else:
            self.logger.warning(f"Unknown fault type: {fault_type}")
    
    def clear_all_faults(self):
        """Clear all fault conditions"""
        for fault_type in self.fault_conditions:
            self.fault_conditions[fault_type] = False
            self.fault_severity[fault_type] = 0.0
        self.logger.info("Cleared all fault conditions")
    
    def calibrate_sensor(self, reference_vibration: float):
        """Calibrate the sensor"""
        current_reading = self.current_vibration
        self.calibration_factor = reference_vibration / current_reading
        self.last_calibration = datetime.utcnow()
        
        self.logger.info(f"Sensor calibrated: factor={self.calibration_factor:.3f}, reference={reference_vibration} mm/s")
    
    def get_vibration_statistics(self) -> Dict[str, Any]:
        """Get vibration statistics"""
        if not self.vibration_history:
            return {}
        
        vibrations = [v for _, v in self.vibration_history]
        
        return {
            "current_vibration": self.current_vibration,
            "current_rms": self.current_rms,
            "current_peak": self.current_peak,
            "current_crest_factor": self.current_crest_factor,
            "current_frequency": self.current_frequency,
            "average_vibration": sum(vibrations) / len(vibrations),
            "min_vibration": min(vibrations),
            "max_vibration": max(vibrations),
            "vibration_range": max(vibrations) - min(vibrations),
            "data_points": len(vibrations),
            "health_score": self._calculate_health_score(),
            "calibration_factor": self.calibration_factor,
            "sensor_temperature": self.sensor_temperature,
            "equipment_parameters": {
                "name": self.equipment_name,
                "speed": self.equipment_speed,
                "load": self.equipment_load,
                "age": self.equipment_age
            },
            "fault_conditions": {
                condition: active for condition, active in self.fault_conditions.items()
            },
            "fault_severity": self.fault_severity
        }
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get extended device information"""
        base_info = super().get_device_info()
        
        # Add vibration sensor specific info
        base_info.update({
            "sensor_type": "vibration",
            "current_vibration": self.current_vibration,
            "current_rms": self.current_rms,
            "current_peak": self.current_peak,
            "current_crest_factor": self.current_crest_factor,
            "current_frequency": self.current_frequency,
            "sensor_temperature": self.sensor_temperature,
            "calibration_factor": self.calibration_factor,
            "equipment_name": self.equipment_name,
            "equipment_speed": self.equipment_speed,
            "equipment_load": self.equipment_load,
            "equipment_age": self.equipment_age,
            "mounting_type": self.mounting_type,
            "vibration_history_size": len(self.vibration_history),
            "fault_conditions": self.fault_conditions,
            "fault_severity": self.fault_severity,
            "health_score": self._calculate_health_score(),
            "vibration_statistics": self.get_vibration_statistics()
        })
        
        return base_info


def create_vibration_sensor(device_id: int, equipment_name: str = "Unknown Equipment") -> VibrationSensor:
    """Factory function to create a vibration sensor"""
    return VibrationSensor(device_id, equipment_name)


if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Create vibration sensor
        sensor = create_vibration_sensor(5001, "Motor A")
        
        # Set equipment parameters
        sensor.set_equipment_parameters(speed=1800, load=0.8, age=3.5)
        
        # Induce a bearing fault for testing
        sensor.induce_fault("bearing_fault", severity=0.6)
        
        try:
            await sensor.start()
            await asyncio.sleep(300)
        except KeyboardInterrupt:
            print("Stopping sensor...")
        finally:
            await sensor.stop()
    
    asyncio.run(main())
