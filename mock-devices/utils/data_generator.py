"""
Data Generation Utilities for Mock Devices

This module provides realistic data generation functions for mock devices.
"""

import random
import math
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from scipy import signal
import logging


class DataGenerator:
    """Realistic data generator for IoT devices"""
    
    def __init__(self, seed: int = None):
        """Initialize data generator with optional seed"""
        if seed:
            random.seed(seed)
            np.random.seed(seed)
        
        self.logger = logging.getLogger("data_generator")
    
    def generate_temperature_series(self, hours: int = 24, base_temp: float = 22.0, 
                                  seasonal_variation: float = 5.0,
                                  noise_level: float = 0.5) -> List[Tuple[datetime, float]]:
        """Generate realistic temperature time series"""
        timestamps = []
        temperatures = []
        
        base_time = datetime.utcnow() - timedelta(hours=hours)
        
        for i in range(hours * 60):  # One data point per minute
            timestamp = base_time + timedelta(minutes=i)
            
            # Daily temperature cycle (sinusoidal)
            hour_of_day = timestamp.hour + timestamp.minute / 60.0
            daily_cycle = seasonal_variation * math.sin(2 * math.pi * (hour_of_day - 6) / 24)
            
            # Add some random noise
            noise = random.gauss(0, noise_level)
            
            # Add occasional spikes (e.g., HVAC turning on)
            if random.random() < 0.02:  # 2% chance of spike
                spike = random.uniform(2, 5) * (1 if random.random() > 0.5 else -1)
                daily_cycle += spike
            
            temperature = base_temp + daily_cycle + noise
            temperatures.append(temperature)
            timestamps.append(timestamp)
        
        return list(zip(timestamps, temperatures))
    
    def generate_humidity_series(self, hours: int = 24, base_humidity: float = 50.0,
                               temp_series: List[Tuple[datetime, float]] = None) -> List[Tuple[datetime, float]]:
        """Generate realistic humidity time series with inverse correlation to temperature"""
        timestamps = []
        humidities = []
        
        if temp_series:
            # Use temperature series for inverse correlation
            for timestamp, temp in temp_series:
                # Inverse correlation with temperature
                temp_normalized = (temp - 20) / 20  # Normalize around 20°C
                humidity = base_humidity - temp_normalized * 15  # Inverse relationship
                
                # Add noise and constraints
                humidity += random.gauss(0, 2)
                humidity = max(20, min(90, humidity))  # Keep within realistic bounds
                
                humidities.append(humidity)
                timestamps.append(timestamp)
        else:
            # Generate independent humidity series
            base_time = datetime.utcnow() - timedelta(hours=hours)
            
            for i in range(hours * 60):
                timestamp = base_time + timedelta(minutes=i)
                
                # Daily humidity cycle (opposite to temperature)
                hour_of_day = timestamp.hour + timestamp.minute / 60.0
                daily_cycle = 10 * math.sin(2 * math.pi * (hour_of_day + 6) / 24)
                
                noise = random.gauss(0, 3)
                humidity = base_humidity + daily_cycle + noise
                humidity = max(20, min(90, humidity))
                
                humidities.append(humidity)
                timestamps.append(timestamp)
        
        return list(zip(timestamps, humidities))
    
    def generate_pressure_series(self, hours: int = 24, base_pressure: float = 1013.25,
                                altitude: float = 0.0) -> List[Tuple[datetime, float]]:
        """Generate realistic barometric pressure time series"""
        timestamps = []
        pressures = []
        
        # Adjust base pressure for altitude (rough approximation)
        altitude_adjustment = altitude * 0.12  # ~0.12 hPa per meter
        adjusted_base = base_pressure - altitude_adjustment
        
        base_time = datetime.utcnow() - timedelta(hours=hours)
        
        for i in range(hours * 60):
            timestamp = base_time + timedelta(minutes=i)
            
            # Weather patterns (slow changes)
            weather_trend = 2 * math.sin(2 * math.pi * i / (hours * 60 * 4))  # 4-hour cycle
            
            # Daily pressure variation
            hour_of_day = timestamp.hour + timestamp.minute / 60.0
            daily_variation = 1 * math.sin(2 * math.pi * (hour_of_day - 12) / 24)
            
            noise = random.gauss(0, 0.5)
            
            pressure = adjusted_base + weather_trend + daily_variation + noise
            pressure = max(980, min(1050, pressure))  # Keep within realistic bounds
            
            pressures.append(pressure)
            timestamps.append(timestamp)
        
        return list(zip(timestamps, pressures))
    
    def generate_vibration_series(self, hours: int = 24, base_vibration: float = 0.1,
                                fault_probability: float = 0.05) -> List[Tuple[datetime, float]]:
        """Generate vibration sensor data with occasional fault patterns"""
        timestamps = []
        vibrations = []
        
        base_time = datetime.utcnow() - timedelta(hours=hours)
        
        for i in range(hours * 60):
            timestamp = base_time + timedelta(minutes=i)
            
            # Normal vibration with small variations
            normal_vibration = base_vibration * (1 + 0.1 * math.sin(2 * math.pi * i / 60))
            
            # Add noise
            noise = random.gauss(0, 0.02)
            vibration = normal_vibration + noise
            
            # Simulate fault conditions
            if random.random() < fault_probability:
                # Bearing fault - higher frequency vibration
                fault_vibration = base_vibration * 3 + 0.5 * math.sin(2 * math.pi * i / 5)
                vibration = max(vibration, fault_vibration)
            elif random.random() < 0.02:  # 2% chance of temporary spike
                spike = random.uniform(0.5, 2.0)
                vibration += spike
            
            vibration = max(0, vibration)  # Ensure non-negative
            vibrations.append(vibration)
            timestamps.append(timestamp)
        
        return list(zip(timestamps, vibrations))
    
    def generate_flow_rate_series(self, hours: int = 24, base_flow: float = 100.0,
                                pipe_diameter: float = 0.1) -> List[Tuple[datetime, float]]:
        """Generate flow rate time series with realistic patterns"""
        timestamps = []
        flow_rates = []
        
        base_time = datetime.utcnow() - timedelta(hours=hours)
        
        for i in range(hours * 60):
            timestamp = base_time + timedelta(minutes=i)
            
            # Demand patterns (e.g., industrial usage)
            hour_of_day = timestamp.hour + timestamp.minute / 60.0
            
            # Peak usage during business hours
            if 8 <= hour_of_day <= 18:
                demand_multiplier = 1.2 + 0.3 * math.sin(2 * math.pi * (hour_of_day - 8) / 10)
            else:
                demand_multiplier = 0.8 + 0.1 * math.sin(2 * math.pi * (hour_of_day - 18) / 10)
            
            # Add turbulence
            turbulence = random.gauss(0, base_flow * 0.05)
            
            flow_rate = base_flow * demand_multiplier + turbulence
            flow_rate = max(0, flow_rate)  # Ensure non-negative
            
            flow_rates.append(flow_rate)
            timestamps.append(timestamp)
        
        return list(zip(timestamps, flow_rates))
    
    def generate_power_consumption(self, hours: int = 24, base_power: float = 100.0,
                                 load_pattern: str = "office") -> List[Tuple[datetime, float]]:
        """Generate power consumption time series"""
        timestamps = []
        power_values = []
        
        base_time = datetime.utcnow() - timedelta(hours=hours)
        
        for i in range(hours * 60):
            timestamp = base_time + timedelta(minutes=i)
            hour_of_day = timestamp.hour + timestamp.minute / 60.0
            
            if load_pattern == "office":
                # Office building pattern
                if 8 <= hour_of_day <= 18:
                    # Business hours
                    load_multiplier = 1.0 + 0.3 * math.sin(2 * math.pi * (hour_of_day - 8) / 10)
                elif 18 <= hour_of_day <= 22:
                    # Evening reduced load
                    load_multiplier = 0.6
                else:
                    # Night minimal load
                    load_multiplier = 0.2
            elif load_pattern == "industrial":
                # Industrial facility pattern
                if 6 <= hour_of_day <= 22:
                    # Operating hours
                    load_multiplier = 0.9 + 0.2 * math.sin(2 * math.pi * (hour_of_day - 6) / 16)
                else:
                    # Maintenance/low load
                    load_multiplier = 0.3
            else:
                # Residential pattern
                if 6 <= hour_of_day <= 9:
                    # Morning peak
                    load_multiplier = 0.8 + 0.2 * math.sin(2 * math.pi * (hour_of_day - 6) / 3)
                elif 18 <= hour_of_day <= 23:
                    # Evening peak
                    load_multiplier = 0.9 + 0.3 * math.sin(2 * math.pi * (hour_of_day - 18) / 5)
                else:
                    # Off-peak
                    load_multiplier = 0.4
            
            # Add random variations and spikes
            variation = random.gauss(0, base_power * 0.05)
            
            # Occasional equipment startup
            if random.random() < 0.01:  # 1% chance
                startup_spike = random.uniform(20, 50)
                variation += startup_spike
            
            power = base_power * load_multiplier + variation
            power = max(0, power)
            
            power_values.append(power)
            timestamps.append(timestamp)
        
        return list(zip(timestamps, power_values))
    
    def generate_network_traffic(self, hours: int = 24, base_traffic: float = 1000.0,
                                peak_hours: List[int] = None) -> List[Tuple[datetime, float]]:
        """Generate network traffic time series"""
        if peak_hours is None:
            peak_hours = [9, 14, 16, 20]  # Default peak hours
        
        timestamps = []
        traffic_values = []
        
        base_time = datetime.utcnow() - timedelta(hours=hours)
        
        for i in range(hours * 60):
            timestamp = base_time + timedelta(minutes=i)
            hour_of_day = int(timestamp.hour)
            
            # Base traffic with hourly variation
            if hour_of_day in peak_hours:
                traffic_multiplier = 1.5 + 0.5 * random.random()
            else:
                traffic_multiplier = 0.7 + 0.3 * random.random()
            
            # Add bursty traffic patterns
            burst = 0
            if random.random() < 0.1:  # 10% chance of burst
                burst = random.uniform(100, 500)
            
            noise = random.gauss(0, base_traffic * 0.1)
            
            traffic = base_traffic * traffic_multiplier + burst + noise
            traffic = max(0, traffic)
            
            traffic_values.append(traffic)
            timestamps.append(timestamp)
        
        return list(zip(timestamps, traffic_values))
    
    def generate_cpu_usage(self, hours: int = 24, base_cpu: float = 30.0,
                         workload_pattern: str = "variable") -> List[Tuple[datetime, float]]:
        """Generate CPU usage time series"""
        timestamps = []
        cpu_values = []
        
        base_time = datetime.utcnow() - timedelta(hours=hours)
        
        for i in range(hours * 60):
            timestamp = base_time + timedelta(minutes=i)
            hour_of_day = timestamp.hour + timestamp.minute / 60.0
            
            if workload_pattern == "variable":
                # Variable workload with peaks
                if 9 <= hour_of_day <= 17:
                    # Business hours - higher CPU
                    cpu_multiplier = 1.5 + 0.5 * math.sin(2 * math.pi * (hour_of_day - 9) / 8)
                else:
                    # Off-peak - lower CPU
                    cpu_multiplier = 0.5 + 0.2 * math.sin(2 * math.pi * (hour_of_day - 17) / 7)
            elif workload_pattern == "constant":
                # Relatively constant workload
                cpu_multiplier = 1.0 + 0.1 * math.sin(2 * math.pi * i / 60)
            else:
                # High-performance workload
                cpu_multiplier = 0.8 + 0.2 * math.sin(2 * math.pi * i / 30)
            
            # Add random spikes (processes starting/stopping)
            spike = 0
            if random.random() < 0.05:  # 5% chance of spike
                spike = random.uniform(10, 30)
            
            noise = random.gauss(0, 2)
            
            cpu = base_cpu * cpu_multiplier + spike + noise
            cpu = max(0, min(100, cpu))  # Keep within 0-100%
            
            cpu_values.append(cpu)
            timestamps.append(timestamp)
        
        return list(zip(timestamps, cpu_values))
    
    def generate_memory_usage(self, hours: int = 24, base_memory: float = 60.0,
                           total_memory: float = 16.0) -> List[Tuple[datetime, float]]:
        """Generate memory usage time series"""
        timestamps = []
        memory_values = []
        
        base_time = datetime.utcnow() - timedelta(hours=hours)
        
        for i in range(hours * 60):
            timestamp = base_time + timedelta(minutes=i)
            
            # Memory usage tends to be more stable than CPU
            # Slow daily variation
            hour_of_day = timestamp.hour + timestamp.minute / 60.0
            daily_variation = 10 * math.sin(2 * math.pi * (hour_of_day - 12) / 24)
            
            # Gradual memory leaks (simulated)
            leak_factor = (i / (hours * 60)) * 5  # 5% increase over the period
            
            # Random allocations/deallocations
            random_alloc = random.gauss(0, 2)
            
            memory = base_memory + daily_variation + leak_factor + random_alloc
            memory = max(10, min(total_memory * 100, memory))  # Keep within bounds
            
            memory_values.append(memory)
            timestamps.append(timestamp)
        
        return list(zip(timestamps, memory_values))
    
    def add_anomalies(self, data_series: List[Tuple[datetime, float]], 
                     anomaly_types: List[str] = None,
                     anomaly_probability: float = 0.01) -> List[Tuple[datetime, float]]:
        """Add anomalies to time series data"""
        if anomaly_types is None:
            anomaly_types = ['spike', 'drop', 'drift', 'noise']
        
        anomalous_data = []
        
        for timestamp, value in data_series:
            if random.random() < anomaly_probability:
                anomaly_type = random.choice(anomaly_types)
                
                if anomaly_type == 'spike':
                    # Sudden spike
                    anomaly_factor = random.uniform(2, 5)
                    value = value * anomaly_factor
                elif anomaly_type == 'drop':
                    # Sudden drop
                    anomaly_factor = random.uniform(0.1, 0.5)
                    value = value * anomaly_factor
                elif anomaly_type == 'drift':
                    # Gradual drift
                    drift_rate = random.uniform(0.01, 0.05)
                    value = value * (1 + drift_rate)
                elif anomaly_type == 'noise':
                    # High noise
                    noise = random.gauss(0, abs(value) * 0.5)
                    value = value + noise
            
                self.logger.debug(f"Added {anomaly_type} anomaly at {timestamp}: {value}")
            
            anomalous_data.append((timestamp, value))
        
        return anomalous_data


class SyntheticDataGenerator:
    """Advanced synthetic data generator for complex IoT scenarios"""
    
    def __init__(self, seed: int = None):
        self.data_gen = DataGenerator(seed)
        self.logger = logging.getLogger("synthetic_data_generator")
    
    def generate_multi_sensor_correlation(self, hours: int = 24) -> Dict[str, List[Tuple[datetime, float]]]:
        """Generate correlated multi-sensor data"""
        # Generate base temperature series
        temp_series = self.data_gen.generate_temperature_series(hours)
        
        # Generate correlated humidity (inverse correlation with temperature)
        humidity_series = self.data_gen.generate_humidity_series(hours, temp_series=temp_series)
        
        # Generate pressure (slight correlation with temperature)
        pressure_series = []
        for timestamp, temp in temp_series:
            # Pressure typically rises with temperature
            pressure_temp_factor = (temp - 20) * 0.5
            base_pressure = 1013.25 + pressure_temp_factor
            pressure_series.append((timestamp, base_pressure + random.gauss(0, 1)))
        
        return {
            'temperature': temp_series,
            'humidity': humidity_series,
            'pressure': pressure_series
        }
    
    def generate_equipment_health_indicators(self, hours: int = 24, 
                                           degradation_rate: float = 0.001) -> Dict[str, List[Tuple[datetime, float]]]:
        """Generate equipment health indicator data with degradation"""
        timestamps = []
        vibration = []
        temperature = []
        noise = []
        
        base_time = datetime.utcnow() - timedelta(hours=hours)
        
        for i in range(hours * 60):
            timestamp = base_time + timedelta(minutes=i)
            
            # Gradual degradation
            degradation = 1 + (degradation_rate * i)
            
            # Vibration increases with degradation
            vib_base = 0.1 * degradation
            vib_noise = random.gauss(0, 0.02)
            vibration.append(vib_base + vib_noise)
            
            # Temperature increases with degradation
            temp_base = 25.0 * degradation
            temp_noise = random.gauss(0, 0.5)
            temperature.append(temp_base + temp_noise)
            
            # Noise increases with degradation
            noise_base = 30.0 * degradation
            noise_variation = 5 * math.sin(2 * math.pi * i / 10)
            noise.append(noise_base + noise_variation)
            
            timestamps.append(timestamp)
        
        return {
            'vibration': list(zip(timestamps, vibration)),
            'temperature': list(zip(timestamps, temperature)),
            'noise': list(zip(timestamps, noise))
        }
    
    def generate_batch_process_data(self, batch_count: int = 100, 
                                  process_duration: int = 60) -> Dict[str, Any]:
        """Generate data for batch process simulation"""
        process_data = []
        
        for i in range(batch_count):
            process_id = f"BATCH-{i:04d}"
            
            # Process duration with variation
            duration = process_duration + random.gauss(0, 10)
            duration = max(30, min(120, duration))  # Keep within reasonable bounds
            
            # Resource usage
            cpu_usage = 20 + random.uniform(10, 60)
            memory_usage = 30 + random.uniform(20, 50)
            
            # Success/failure probability
            success_probability = 0.95  # 95% success rate
            success = random.random() < success_probability
            
            # Processing time
            processing_time = duration * (1 + random.gauss(0, 0.1))
            
            process_data.append({
                'process_id': process_id,
                'duration': duration,
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'success': success,
                'processing_time': processing_time,
                'start_time': datetime.utcnow() + timedelta(minutes=i),
                'end_time': datetime.utcnow() + timedelta(minutes=i + duration)
            })
        
        return {
            'processes': process_data,
            'success_rate': sum(1 for p in process_data if p['success']) / len(process_data),
            'avg_duration': sum(p['duration'] for p in process_data) / len(process_data),
            'avg_cpu_usage': sum(p['cpu_usage'] for p in process_data) / len(process_data),
            'avg_memory_usage': sum(p['memory_usage'] for p in process_data) / len(process_data)
        }
