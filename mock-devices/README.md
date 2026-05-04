# Mock Devices for Valtronics Testing

This directory contains mock devices for testing the Valtronics IoT monitoring system. These devices simulate real IoT hardware and provide realistic telemetry data for development and testing purposes.

## Device Categories

### 1. Environmental Sensors
- Temperature sensors
- Humidity sensors
- Pressure sensors
- Air quality monitors
- Light sensors

### 2. Industrial Sensors
- Vibration sensors
- Flow meters
- Pressure transducers
- Level sensors
- Temperature probes

### 3. Smart Home Devices
- Smart thermostats
- Smart lights
- Security sensors
- Energy monitors
- Door/window sensors

### 4. Network Devices
- Routers
- Switches
- Access points
- Firewalls
- Load balancers

### 5. Server Infrastructure
- CPU monitors
- Memory monitors
- Disk monitors
- Network monitors
- Power supplies

## Usage

Each mock device can be run independently or as part of a device fleet. They connect to the Valtronics system via MQTT or REST APIs and send realistic telemetry data.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run individual device
python temperature_sensor.py

# Run device fleet
python device_fleet.py
```

## Configuration

Edit the `config.json` file to configure:
- MQTT broker settings
- API endpoints
- Device parameters
- Telemetry intervals

## Architecture

```
mock-devices/
├── README.md
├── requirements.txt
├── config.json
├── base_device.py
├── environmental/
│   ├── temperature_sensor.py
│   ├── humidity_sensor.py
│   ├── pressure_sensor.py
│   └── air_quality_monitor.py
├── industrial/
│   ├── vibration_sensor.py
│   ├── flow_meter.py
│   └── pressure_transducer.py
├── smart_home/
│   ├── smart_thermostat.py
│   ├── smart_light.py
│   └── security_sensor.py
├── network/
│   ├── router_monitor.py
│   └── switch_monitor.py
├── infrastructure/
│   ├── server_monitor.py
│   └── power_monitor.py
├── utils/
│   ├── mqtt_client.py
│   ├── api_client.py
│   └── data_generator.py
└── device_fleet.py
```

## Features

- Realistic telemetry data generation
- Configurable device parameters
- Multiple communication protocols (MQTT, REST)
- Device health monitoring
- Alert generation
- Simulated failures and recovery
- Batch device management

## License

© 2024 Software Customs Auto Bot Solution. All Rights Reserved.
