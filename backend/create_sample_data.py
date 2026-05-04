#!/usr/bin/env python3
"""
Create sample data for testing the Valtronics system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.session_sqlite import SessionLocal
from app.models.device import Device, TelemetryData, DeviceCommand
from app.models.alert import Alert, AlertRule
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create sample devices, telemetry data, and alerts"""
    print("Creating sample data for Valtronics system...")
    
    db = SessionLocal()
    
    try:
        # Sample devices
        sample_devices = [
            {
                "name": "Temperature Sensor Alpha",
                "device_id": "TEMP-001",
                "device_type": "sensor",
                "manufacturer": "SensorTech",
                "model": "ST-T1000",
                "firmware_version": "2.1.4",
                "location": "Zone A - Server Room",
                "status": "online"
            },
            {
                "name": "Pressure Monitor Beta",
                "device_id": "PRESS-002", 
                "device_type": "sensor",
                "manufacturer": "PressurePro",
                "model": "PP-M200",
                "firmware_version": "3.0.1",
                "location": "Zone B - Production Line",
                "status": "online"
            },
            {
                "name": "Flow Controller Gamma",
                "device_id": "FLOW-003",
                "device_type": "actuator", 
                "manufacturer": "FlowControl",
                "model": "FC-X500",
                "firmware_version": "1.8.2",
                "location": "Zone C - Cooling System",
                "status": "warning"
            },
            {
                "name": "Voltage Sensor Delta",
                "device_id": "VOLT-004",
                "device_type": "sensor",
                "manufacturer": "VoltMeter",
                "model": "VM-V300",
                "firmware_version": "2.5.0",
                "location": "Zone D - Power Distribution",
                "status": "offline"
            },
            {
                "name": "Humidity Monitor Epsilon",
                "device_id": "HUMID-005",
                "device_type": "sensor",
                "manufacturer": "HumidiTech",
                "model": "HT-H400",
                "firmware_version": "1.9.3",
                "location": "Zone E - Storage Area",
                "status": "online"
            }
        ]
        
        # Create devices
        created_devices = []
        for device_data in sample_devices:
            device = Device(**device_data)
            device.last_seen = datetime.now() - timedelta(minutes=random.randint(1, 30))
            db.add(device)
            created_devices.append(device)
        
        db.commit()
        print(f"✅ Created {len(created_devices)} devices")
        
        # Create telemetry data for each device
        telemetry_metrics = {
            "sensor": ["temperature", "humidity", "pressure", "voltage"],
            "actuator": ["flow_rate", "position", "power_consumption", "efficiency"]
        }
        
        for device in created_devices:
            metrics = telemetry_metrics.get(device.device_type, ["status"])
            
            # Create last 24 hours of telemetry data
            for hours_ago in range(24, 0, -1):
                timestamp = datetime.now() - timedelta(hours=hours_ago)
                
                for metric in metrics:
                    # Generate realistic values
                    if metric == "temperature":
                        value = round(random.uniform(18.0, 28.0), 2)
                    elif metric == "humidity":
                        value = round(random.uniform(35.0, 65.0), 2)
                    elif metric == "pressure":
                        value = round(random.uniform(1010.0, 1025.0), 2)
                    elif metric == "voltage":
                        value = round(random.uniform(110.0, 125.0), 2)
                    elif metric == "flow_rate":
                        value = round(random.uniform(50.0, 150.0), 2)
                    elif metric == "position":
                        value = round(random.uniform(0.0, 100.0), 2)
                    elif metric == "power_consumption":
                        value = round(random.uniform(100.0, 500.0), 2)
                    elif metric == "efficiency":
                        value = round(random.uniform(70.0, 95.0), 2)
                    else:
                        value = round(random.uniform(0.0, 100.0), 2)
                    
                    telemetry = TelemetryData(
                        device_id=device.id,
                        metric_name=metric,
                        metric_value=value,
                        unit=get_unit(metric),
                        timestamp=timestamp
                    )
                    db.add(telemetry)
        
        db.commit()
        print("✅ Created telemetry data")
        
        # Create some alerts
        sample_alerts = [
            {
                "device_id": created_devices[2].id,  # Flow Controller Gamma (warning status)
                "title": "Low Flow Rate Detected",
                "description": "Flow rate below threshold for extended period",
                "severity": "warning",
                "alert_type": "threshold",
                "threshold_value": 50.0,
                "actual_value": 42.5,
                "metric_name": "flow_rate"
            },
            {
                "device_id": created_devices[3].id,  # Voltage Sensor Delta (offline status)
                "title": "Device Offline",
                "description": "Device has not reported data for over 15 minutes",
                "severity": "critical",
                "alert_type": "device",
                "metric_name": "connectivity"
            },
            {
                "device_id": created_devices[0].id,  # Temperature Sensor Alpha
                "title": "Temperature Spike",
                "description": "Brief temperature spike detected",
                "severity": "info",
                "alert_type": "anomaly",
                "threshold_value": 28.0,
                "actual_value": 28.5,
                "metric_name": "temperature"
            }
        ]
        
        for alert_data in sample_alerts:
            alert = Alert(**alert_data)
            alert.created_at = datetime.now() - timedelta(minutes=random.randint(5, 120))
            db.add(alert)
        
        db.commit()
        print(f"✅ Created {len(sample_alerts)} alerts")
        
        # Create alert rules
        sample_rules = [
            {
                "name": "High Temperature Alert",
                "description": "Alert when temperature exceeds 30°C",
                "device_type": "sensor",
                "metric_name": "temperature",
                "condition": "gt",
                "threshold_value": 30.0,
                "severity": "warning"
            },
            {
                "name": "Low Battery Alert",
                "description": "Alert when device battery is below 20%",
                "device_type": "sensor",
                "metric_name": "battery_level",
                "condition": "lt",
                "threshold_value": 20.0,
                "severity": "critical"
            },
            {
                "name": "Device Offline Alert",
                "description": "Alert when device is offline for more than 10 minutes",
                "device_type": None,  # Global rule
                "metric_name": "connectivity",
                "condition": "eq",
                "threshold_value": 0.0,
                "severity": "critical"
            }
        ]
        
        for rule_data in sample_rules:
            rule = AlertRule(**rule_data)
            db.add(rule)
        
        db.commit()
        print(f"✅ Created {len(sample_rules)} alert rules")
        
        # Create some device commands
        sample_commands = [
            {
                "device_id": created_devices[2].id,  # Flow Controller
                "command": "adjust_flow_rate",
                "parameters": '{"target_rate": 75.0, "duration": 3600}',
                "status": "executed"
            },
            {
                "device_id": created_devices[4].id,  # Humidity Monitor
                "command": "calibrate",
                "parameters": '{"reference_value": 50.0}',
                "status": "pending"
            }
        ]
        
        for cmd_data in sample_commands:
            command = DeviceCommand(**cmd_data)
            command.created_at = datetime.now() - timedelta(minutes=random.randint(1, 60))
            if cmd_data["status"] == "executed":
                command.executed_at = command.created_at + timedelta(minutes=5)
            db.add(command)
        
        db.commit()
        print(f"✅ Created {len(sample_commands)} device commands")
        
        print("\n🎉 Sample data creation completed!")
        print(f"📊 Summary:")
        print(f"   - Devices: {len(created_devices)}")
        print(f"   - Telemetry points: {len(created_devices) * 24 * len(telemetry_metrics['sensor'])}")
        print(f"   - Alerts: {len(sample_alerts)}")
        print(f"   - Alert rules: {len(sample_rules)}")
        print(f"   - Commands: {len(sample_commands)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def get_unit(metric_name):
    """Get appropriate unit for a metric"""
    units = {
        "temperature": "°C",
        "humidity": "%",
        "pressure": "hPa", 
        "voltage": "V",
        "flow_rate": "L/min",
        "position": "%",
        "power_consumption": "W",
        "efficiency": "%",
        "battery_level": "%",
        "connectivity": "bool"
    }
    return units.get(metric_name, "")

if __name__ == "__main__":
    success = create_sample_data()
    sys.exit(0 if success else 1)
