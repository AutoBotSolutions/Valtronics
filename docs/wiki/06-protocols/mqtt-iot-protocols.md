# MQTT and IoT Protocols Documentation

**Complete guide to MQTT and IoT communication protocols in Valtronics**

---

## Overview

The Valtronics system implements comprehensive IoT communication protocols, with MQTT as the primary protocol for device communication. This documentation covers MQTT implementation, device communication patterns, and integration with various IoT protocols.

---

## MQTT Architecture

### MQTT Broker Configuration

#### Mosquitto Setup
```bash
# Install Mosquitto MQTT broker
sudo apt-get update
sudo apt-get install mosquitto mosquitto-clients

# Start Mosquitto service
sudo systemctl start mosquitto
sudo systemctl enable mosquitto

# Test MQTT broker
mosquitto_pub -h localhost -t test/topic -m "Hello MQTT"
mosquitto_sub -h localhost -t test/topic
```

#### Mosquitto Configuration
```conf
# /etc/mosquitto/mosquitto.conf

# Basic configuration
port 1883
listener 1883 localhost

# WebSocket support
listener 9001
protocol websockets

# Security
allow_anonymous false
password_file /etc/mosquitto/passwd
acl_file /etc/mosquitto/acl

# Persistence
persistence true
persistence_location /var/lib/mosquitto/

# Logging
log_dest file /var/log/mosquitto/mosquitto.log
log_type error
log_type warning
log_type notice
log_type information
log_timestamp true
```

#### MQTT Authentication
```bash
# Create MQTT user
sudo mosquitto_passwd -c /etc/mosquitto/passwd valtronics_user

# Create ACL file
sudo nano /etc/mosquitto/acl
```

ACL Configuration:
```conf
# /etc/mosquitto/acl

# User valtronics_user
user valtronics_user
topic readwrite valtronics/#

# Anonymous users (if allowed)
user anonymous
topic read $SYS/broker/load/+
```

---

## MQTT Topic Structure

### Topic Hierarchy
```
valtronics/
├── devices/
│   ├── {device_id}/
│   │   ├── telemetry/
│   │   │   ├── temperature
│   │   │   ├── humidity
│   │   │   ├── pressure
│   │   │   └── voltage
│   │   ├── status/
│   │   │   ├── online
│   │   │   ├── offline
│   │   │   └── error
│   │   ├── commands/
│   │   │   ├── reboot
│   │   │   ├── calibrate
│   │   │   └── update
│   │   └── config/
│   │       ├── sampling_rate
│   │       ├── thresholds
│   │       └── settings
├── system/
│   ├── health/
│   │   ├── broker
│   │   ├── database
│   │   └── api
│   ├── alerts/
│   │   ├── critical
│   │   ├── warning
│   │   └── info
│   └── updates/
│       ├── firmware
│       ├── config
│       └── security
└── monitoring/
    ├── metrics/
    │   ├── cpu
    │   ├── memory
    │   └── network
    └── logs/
        ├── error
        ├── warning
        └── info
```

### Topic Naming Conventions
- **Device Topics**: `valtronics/devices/{device_id}/{category}/{metric}`
- **System Topics**: `valtronics/system/{category}/{subsystem}`
- **Monitoring Topics**: `valtronics/monitoring/{category}/{metric}`
- **Command Topics**: `valtronics/devices/{device_id}/commands/{command}`
- **Alert Topics**: `valtronics/system/alerts/{severity}`

---

## MQTT Client Implementation

### Python MQTT Client
```python
# app/mqtt/mqtt_client.py
import paho.mqtt.client as mqtt
import json
import logging
from typing import Callable, Dict, Any
from app.core.config import settings
from app.services.device_service import DeviceService
from app.services.telemetry_service import TelemetryService

class ValtronicsMQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        self.client.on_subscribe = self._on_subscribe
        
        self.device_service = DeviceService()
        self.telemetry_service = TelemetryService()
        self.message_handlers: Dict[str, Callable] = {}
        
        # Setup message handlers
        self._setup_message_handlers()
        
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> None:
        """Connect to MQTT broker"""
        try:
            self.client.connect(
                settings.MQTT_BROKER_HOST,
                settings.MQTT_BROKER_PORT,
                settings.MQTT_KEEPALIVE
            )
            self.client.loop_start()
            self.logger.info(f"Connected to MQTT broker at {settings.MQTT_BROKER_HOST}")
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")
            raise
    
    def disconnect(self) -> None:
        """Disconnect from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
        self.logger.info("Disconnected from MQTT broker")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection"""
        if rc == 0:
            self.logger.info("Successfully connected to MQTT broker")
            # Subscribe to device topics
            self._subscribe_to_topics()
        else:
            self.logger.error(f"Failed to connect to MQTT broker, return code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback for received MQTT messages"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            self.logger.debug(f"Received message on topic {topic}: {payload}")
            
            # Parse topic to determine handler
            topic_parts = topic.split('/')
            
            if len(topic_parts) >= 3:
                category = topic_parts[1]  # devices, system, monitoring
                subcategory = topic_parts[2]  # device_id, health, metrics
                
                if category == 'devices':
                    self._handle_device_message(topic_parts, payload)
                elif category == 'system':
                    self._handle_system_message(topic_parts, payload)
                elif category == 'monitoring':
                    self._handle_monitoring_message(topic_parts, payload)
            
        except Exception as e:
            self.logger.error(f"Error processing MQTT message: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for MQTT disconnection"""
        self.logger.warning(f"Disconnected from MQTT broker, return code: {rc}")
    
    def _on_publish(self, client, userdata, mid):
        """Callback for published messages"""
        self.logger.debug(f"Message published with ID: {mid}")
    
    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """Callback for subscription"""
        self.logger.debug(f"Subscribed with ID: {mid}, QoS: {granted_qos}")
    
    def _setup_message_handlers(self):
        """Setup message handlers for different topics"""
        self.message_handlers = {
            'telemetry': self._handle_telemetry_message,
            'status': self._handle_status_message,
            'commands': self._handle_command_message,
            'config': self._handle_config_message,
        }
    
    def _subscribe_to_topics(self):
        """Subscribe to relevant MQTT topics"""
        topics = [
            ("valtronics/devices/+/telemetry/+", 1),
            ("valtronics/devices/+/status/+", 1),
            ("valtronics/devices/+/commands/+", 1),
            ("valtronics/system/health/+", 1),
            ("valtronics/system/alerts/+", 1),
            ("valtronics/monitoring/metrics/+", 1),
        ]
        
        for topic, qos in topics:
            self.client.subscribe(topic, qos)
            self.logger.info(f"Subscribed to topic: {topic}")
    
    def _handle_device_message(self, topic_parts: list, payload: str):
        """Handle device-related messages"""
        device_id = topic_parts[2]
        message_type = topic_parts[3] if len(topic_parts) > 3 else None
        
        if message_type in self.message_handlers:
            handler = self.message_handlers[message_type]
            handler(device_id, topic_parts, payload)
    
    def _handle_telemetry_message(self, device_id: str, topic_parts: list, payload: str):
        """Handle telemetry messages"""
        try:
            data = json.loads(payload)
            metric_name = topic_parts[4] if len(topic_parts) > 4 else 'unknown'
            
            # Store telemetry data
            telemetry_data = {
                'device_id': int(device_id),
                'metric_name': metric_name,
                'metric_value': data.get('value'),
                'unit': data.get('unit'),
                'timestamp': data.get('timestamp'),
                'metadata': data.get('metadata', {})
            }
            
            self.telemetry_service.create_telemetry(telemetry_data)
            self.logger.info(f"Stored telemetry for device {device_id}: {metric_name}")
            
        except Exception as e:
            self.logger.error(f"Error handling telemetry message: {e}")
    
    def _handle_status_message(self, device_id: str, topic_parts: list, payload: str):
        """Handle status messages"""
        try:
            data = json.loads(payload)
            status = data.get('status')
            
            # Update device status
            self.device_service.update_device_status(int(device_id), status)
            self.logger.info(f"Updated device {device_id} status to: {status}")
            
        except Exception as e:
            self.logger.error(f"Error handling status message: {e}")
    
    def _handle_command_message(self, device_id: str, topic_parts: list, payload: str):
        """Handle command messages"""
        try:
            data = json.loads(payload)
            command = data.get('command')
            
            # Process device command
            self._process_device_command(int(device_id), command, data)
            self.logger.info(f"Processed command for device {device_id}: {command}")
            
        except Exception as e:
            self.logger.error(f"Error handling command message: {e}")
    
    def _handle_config_message(self, device_id: str, topic_parts: list, payload: str):
        """Handle configuration messages"""
        try:
            data = json.loads(payload)
            
            # Update device configuration
            self.device_service.update_device_config(int(device_id), data)
            self.logger.info(f"Updated configuration for device {device_id}")
            
        except Exception as e:
            self.logger.error(f"Error handling config message: {e}")
    
    def _handle_system_message(self, topic_parts: list, payload: str):
        """Handle system messages"""
        # Handle system health, alerts, etc.
        pass
    
    def _handle_monitoring_message(self, topic_parts: list, payload: str):
        """Handle monitoring messages"""
        # Handle system metrics, logs, etc.
        pass
    
    def _process_device_command(self, device_id: int, command: str, data: Dict[str, Any]):
        """Process device command"""
        # Command processing logic
        pass
    
    def publish_message(self, topic: str, payload: Dict[str, Any], qos: int = 1):
        """Publish message to MQTT topic"""
        try:
            message = json.dumps(payload)
            result = self.client.publish(topic, message, qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"Published message to topic {topic}")
            else:
                self.logger.error(f"Failed to publish message to topic {topic}")
                
        except Exception as e:
            self.logger.error(f"Error publishing message: {e}")
    
    def publish_device_command(self, device_id: int, command: str, params: Dict[str, Any] = None):
        """Publish command to device"""
        topic = f"valtronics/devices/{device_id}/commands/{command}"
        payload = {
            'command': command,
            'timestamp': datetime.utcnow().isoformat(),
            'params': params or {}
        }
        
        self.publish_message(topic, payload)
    
    def publish_system_alert(self, severity: str, message: str, metadata: Dict[str, Any] = None):
        """Publish system alert"""
        topic = f"valtronics/system/alerts/{severity}"
        payload = {
            'severity': severity,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': metadata or {}
        }
        
        self.publish_message(topic, payload)
```

### Device-Side MQTT Client (Arduino/ESP32)
```cpp
// device_mqtt_client.cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <NTPClient.h>
#include <WiFiUdp.h>

class DeviceMQTTClient {
private:
    WiFiClient wifiClient;
    PubSubClient mqttClient;
    const char* mqttServer;
    int mqttPort;
    const char* mqttUser;
    const char* mqttPassword;
    const char* deviceId;
    
    // NTP for time synchronization
    WiFiUDP ntpUDP;
    NTPClient timeClient;
    
public:
    DeviceMQTTClient(const char* server, int port, const char* user, 
                     const char* password, const char* id) :
        mqttServer(server), mqttPort(port), mqttUser(user), 
        mqttPassword(password), deviceId(id),
        mqttClient(wifiClient), timeClient(ntpUDP, "pool.ntp.org") {}
    
    bool connectWiFi(const char* ssid, const char* password) {
        Serial.println("Connecting to WiFi...");
        WiFi.begin(ssid, password);
        
        int attempts = 0;
        while (WiFi.status() != WL_CONNECTED && attempts < 30) {
            delay(1000);
            Serial.print(".");
            attempts++;
        }
        
        if (WiFi.status() == WL_CONNECTED) {
            Serial.println("\nWiFi connected");
            Serial.print("IP address: ");
            Serial.println(WiFi.localIP());
            
            // Initialize NTP client
            timeClient.begin();
            timeClient.setTimeOffset(0); // UTC
            return true;
        }
        
        Serial.println("\nFailed to connect to WiFi");
        return false;
    }
    
    bool connectMQTT() {
        mqttClient.setServer(mqttServer, mqttPort);
        mqttClient.setCallback([this](char* topic, byte* payload, unsigned int length) {
            this->messageCallback(topic, payload, length);
        });
        
        Serial.println("Connecting to MQTT broker...");
        
        int attempts = 0;
        while (!mqttClient.connected() && attempts < 5) {
            String clientId = "device_";
            clientId += deviceId;
            
            if (mqttClient.connect(clientId.c_str(), mqttUser, mqttPassword)) {
                Serial.println("MQTT connected");
                
                // Subscribe to command topics
                String commandTopic = "valtronics/devices/";
                commandTopic += deviceId;
                commandTopic += "/commands/+";
                mqttClient.subscribe(commandTopic.c_str());
                
                // Publish online status
                publishStatus("online");
                
                return true;
            }
            
            Serial.print("Failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
            attempts++;
        }
        
        Serial.println("Failed to connect to MQTT broker");
        return false;
    }
    
    void loop() {
        if (!mqttClient.connected()) {
            connectMQTT();
        }
        mqttClient.loop();
        
        // Update time client
        timeClient.update();
    }
    
    void publishTelemetry(const char* metricName, float value, const char* unit) {
        String topic = "valtronics/devices/";
        topic += deviceId;
        topic += "/telemetry/";
        topic += metricName;
        
        StaticJsonDocument<256> doc;
        doc["value"] = value;
        doc["unit"] = unit;
        doc["timestamp"] = getCurrentTimestamp();
        
        char payload[256];
        serializeJson(doc, payload);
        
        mqttClient.publish(topic.c_str(), payload);
        Serial.print("Published telemetry: ");
        Serial.println(payload);
    }
    
    void publishStatus(const char* status) {
        String topic = "valtronics/devices/";
        topic += deviceId;
        topic += "/status/online";
        
        StaticJsonDocument<128> doc;
        doc["status"] = status;
        doc["timestamp"] = getCurrentTimestamp();
        doc["ip_address"] = WiFi.localIP().toString();
        
        char payload[128];
        serializeJson(doc, payload);
        
        mqttClient.publish(topic.c_str(), payload);
        Serial.print("Published status: ");
        Serial.println(payload);
    }
    
    void publishAlert(const char* severity, const char* message) {
        String topic = "valtronics/devices/";
        topic += deviceId;
        topic += "/status/error";
        
        StaticJsonDocument<256> doc;
        doc["severity"] = severity;
        doc["message"] = message;
        doc["timestamp"] = getCurrentTimestamp();
        
        char payload[256];
        serializeJson(doc, payload);
        
        mqttClient.publish(topic.c_str(), payload);
        Serial.print("Published alert: ");
        Serial.println(payload);
    }
    
private:
    void messageCallback(char* topic, byte* payload, unsigned int length) {
        Serial.print("Message arrived [");
        Serial.print(topic);
        Serial.print("] ");
        
        // Convert payload to string
        char message[length + 1];
        memcpy(message, payload, length);
        message[length] = '\0';
        Serial.println(message);
        
        // Parse JSON
        StaticJsonDocument<256> doc;
        DeserializationError error = deserializeJson(doc, message);
        
        if (error) {
            Serial.print("deserializeJson() failed: ");
            Serial.println(error.c_str());
            return;
        }
        
        // Handle command
        String topicStr = String(topic);
        if (topicStr.indexOf("/commands/") > 0) {
            handleCommand(doc);
        }
    }
    
    void handleCommand(JsonDocument& command) {
        const char* cmd = command["command"];
        Serial.print("Handling command: ");
        Serial.println(cmd);
        
        if (strcmp(cmd, "reboot") == 0) {
            Serial.println("Rebooting device...");
            delay(1000);
            ESP.restart();
        } else if (strcmp(cmd, "calibrate") == 0) {
            Serial.println("Calibrating sensor...");
            calibrateSensor();
        } else if (strcmp(cmd, "update_config") == 0) {
            Serial.println("Updating configuration...");
            updateConfiguration(command);
        }
    }
    
    void calibrateSensor() {
        // Sensor calibration logic
        Serial.println("Sensor calibration completed");
    }
    
    void updateConfiguration(JsonDocument& config) {
        // Configuration update logic
        Serial.println("Configuration updated");
    }
    
    const char* getCurrentTimestamp() {
        timeClient.update();
        unsigned long epochTime = timeClient.getEpochTime();
        
        static char timestamp[32];
        sprintf(timestamp, "%lu", epochTime);
        
        return timestamp;
    }
};
```

---

## Message Formats

### Telemetry Message Format
```json
{
  "value": 23.5,
  "unit": "°C",
  "timestamp": "2024-01-01T12:00:00Z",
  "metadata": {
    "sensor_type": "DS18B20",
    "location": "server_room",
    "quality": "good"
  }
}
```

### Status Message Format
```json
{
  "status": "online",
  "timestamp": "2024-01-01T12:00:00Z",
  "ip_address": "192.168.1.100",
  "firmware_version": "1.2.3",
  "battery_level": 85,
  "signal_strength": -45
}
```

### Command Message Format
```json
{
  "command": "calibrate",
  "timestamp": "2024-01-01T12:00:00Z",
  "params": {
    "sensor": "temperature",
    "reference_value": 25.0
  },
  "request_id": "cmd_12345"
}
```

### Alert Message Format
```json
{
  "severity": "warning",
  "message": "Temperature exceeds threshold",
  "timestamp": "2024-01-01T12:00:00Z",
  "device_id": "TEMP-001",
  "metric": "temperature",
  "value": 32.5,
  "threshold": 30.0
}
```

---

## IoT Protocol Integration

### CoAP (Constrained Application Protocol)
```python
# app/protocols/coap_client.py
import asyncio
from aiocoap import *
import json

class CoAPClient:
    def __init__(self):
        self.protocol = Context.create_client_context()
    
    async def get_resource(self, resource_path: str):
        """GET resource via CoAP"""
        request = Message(code=GET, uri=resource_path)
        
        try:
            response = await self.protocol.request(request).response
            return response.payload.decode()
        except Exception as e:
            print(f"CoAP GET error: {e}")
            return None
    
    async def post_resource(self, resource_path: str, data: dict):
        """POST data to resource via CoAP"""
        payload = json.dumps(data).encode()
        request = Message(code=POST, uri=resource_path, payload=payload)
        
        try:
            response = await self.protocol.request(request).response
            return response.payload.decode()
        except Exception as e:
            print(f"CoAP POST error: {e}")
            return None
    
    async def observe_resource(self, resource_path: str, callback):
        """Observe resource changes via CoAP"""
        request = Message(code=GET, uri=resource_path, observe=0)
        
        try:
            observation = await self.protocol.request(request).observation
            
            async for response in observation:
                if response.code.is_successful():
                    await callback(response.payload.decode())
                    
        except Exception as e:
            print(f"CoAP observe error: {e}")
```

### LoRaWAN Integration
```python
# app/protocols/lorawan_client.py
import requests
import json
from typing import Dict, Any

class LoRaWANClient:
    def __init__(self, app_server_url: str, app_id: str, app_key: str):
        self.app_server_url = app_server_url
        self.app_id = app_id
        self.app_key = app_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {app_key}',
            'Content-Type': 'application/json'
        })
    
    def send_downlink(self, device_eui: str, payload: Dict[str, Any]) -> bool:
        """Send downlink message to LoRaWAN device"""
        url = f"{self.app_server_url}/api/v3/applications/{self.app_id}/devices/{device_eui}/down"
        
        try:
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                print(f"Downlink sent to device {device_eui}")
                return True
            else:
                print(f"Failed to send downlink: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"LoRaWAN downlink error: {e}")
            return False
    
    def get_device_data(self, device_eui: str) -> Dict[str, Any]:
        """Get device data from LoRaWAN network server"""
        url = f"{self.app_server_url}/api/v3/applications/{self.app_id}/devices/{device_eui}"
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get device data: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"LoRaWAN device data error: {e}")
            return {}
```

### Zigbee Integration
```python
# app/protocols/zigbee_client.py
import zigpy
from zigpy import application
from zigpy.config import CONF_DEVICE
import asyncio

class ZigbeeClient:
    def __init__(self):
        self.app = None
        self.devices = {}
    
    async def start(self):
        """Start Zigbee coordinator"""
        config = {
            CONF_DEVICE: {
                "path": "/dev/ttyUSB0",
                "baudrate": 115200
            }
        }
        
        self.app = await application.ControllerApplication.new(
            config, auto_form=True
        )
        
        print("Zigbee coordinator started")
    
    async def permit_join(self, duration: int = 60):
        """Allow devices to join network"""
        await self.app.permit_join(duration)
        print(f"Joining permitted for {duration} seconds")
    
    async def send_command(self, ieee: str, command: dict):
        """Send command to Zigbee device"""
        try:
            device = self.app.get_device(ieee)
            await device.request(command)
            print(f"Command sent to device {ieee}")
        except Exception as e:
            print(f"Zigbee command error: {e}")
    
    async def get_devices(self):
        """Get all Zigbee devices"""
        return self.app.devices
```

---

## Device Communication Patterns

### Publish/Subscribe Pattern
```python
# app/communication/publish_subscribe.py
import asyncio
from app.mqtt.mqtt_client import ValtronicsMQTTClient

class PublishSubscribeManager:
    def __init__(self):
        self.mqtt_client = ValtronicsMQTTClient()
        self.subscribers = {}
        self.publishers = {}
    
    async def start(self):
        """Start the MQTT client and setup patterns"""
        self.mqtt_client.connect()
        
        # Setup device communication patterns
        await self.setup_device_patterns()
        await self.setup_system_patterns()
    
    async def setup_device_patterns(self):
        """Setup device communication patterns"""
        # Device telemetry publisher
        self.publishers['telemetry'] = TelemetryPublisher(self.mqtt_client)
        
        # Device status subscriber
        self.subscribers['status'] = StatusSubscriber(self.mqtt_client)
        
        # Device command handler
        self.subscribers['commands'] = CommandHandler(self.mqtt_client)
    
    async def setup_system_patterns(self):
        """Setup system communication patterns"""
        # System alert publisher
        self.publishers['alerts'] = AlertPublisher(self.mqtt_client)
        
        # System health subscriber
        self.subscribers['health'] = HealthSubscriber(self.mqtt_client)

class TelemetryPublisher:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
    
    def publish_telemetry(self, device_id: int, metrics: dict):
        """Publish device telemetry data"""
        for metric_name, value in metrics.items():
            topic = f"valtronics/devices/{device_id}/telemetry/{metric_name}"
            payload = {
                'value': value,
                'timestamp': datetime.utcnow().isoformat(),
                'unit': self.get_unit(metric_name)
            }
            
            self.mqtt_client.publish_message(topic, payload)
    
    def get_unit(self, metric_name: str) -> str:
        """Get unit for metric"""
        units = {
            'temperature': '°C',
            'humidity': '%',
            'pressure': 'hPa',
            'voltage': 'V',
            'current': 'A'
        }
        return units.get(metric_name, '')

class StatusSubscriber:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
    
    def handle_status_update(self, device_id: str, status: str):
        """Handle device status updates"""
        # Update device status in database
        # Trigger alerts if needed
        # Update dashboard
        pass

class CommandHandler:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.command_handlers = {
            'reboot': self.handle_reboot,
            'calibrate': self.handle_calibrate,
            'update_config': self.handle_update_config
        }
    
    def handle_command(self, device_id: str, command: str, params: dict):
        """Handle device command"""
        if command in self.command_handlers:
            handler = self.command_handlers[command]
            handler(device_id, params)
    
    def handle_reboot(self, device_id: str, params: dict):
        """Handle reboot command"""
        # Send reboot command to device
        topic = f"valtronics/devices/{device_id}/commands/reboot"
        payload = {
            'command': 'reboot',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.mqtt_client.publish_message(topic, payload)
    
    def handle_calibrate(self, device_id: str, params: dict):
        """Handle calibration command"""
        # Send calibration command to device
        topic = f"valtronics/devices/{device_id}/commands/calibrate"
        payload = {
            'command': 'calibrate',
            'params': params,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.mqtt_client.publish_message(topic, payload)
```

### Request/Response Pattern
```python
# app/communication/request_response.py
import asyncio
import uuid
from typing import Dict, Any, Callable

class RequestResponseManager:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.pending_requests = {}
        self.response_handlers = {}
    
    async def send_request(self, device_id: int, request_type: str, 
                          params: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        """Send request and wait for response"""
        request_id = str(uuid.uuid4())
        
        # Setup response handler
        response_topic = f"valtronics/devices/{device_id}/responses/{request_id}"
        self.mqtt_client.client.subscribe(response_topic)
        
        # Store request info
        self.pending_requests[request_id] = {
            'device_id': device_id,
            'request_type': request_type,
            'timestamp': datetime.utcnow(),
            'response': None,
            'completed': False
        }
        
        # Send request
        request_topic = f"valtronics/devices/{device_id}/requests/{request_type}"
        payload = {
            'request_id': request_id,
            'request_type': request_type,
            'params': params,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.mqtt_client.publish_message(request_topic, payload)
        
        # Wait for response
        start_time = asyncio.get_event_loop().time()
        while not self.pending_requests[request_id]['completed']:
            if asyncio.get_event_loop().time() - start_time > timeout:
                # Timeout
                del self.pending_requests[request_id]
                raise TimeoutError(f"Request {request_id} timed out")
            
            await asyncio.sleep(0.1)
        
        # Get response
        response = self.pending_requests[request_id]['response']
        del self.pending_requests[request_id]
        
        return response
    
    def handle_response(self, topic: str, payload: Dict[str, Any]):
        """Handle response message"""
        topic_parts = topic.split('/')
        if len(topic_parts) >= 5:
            request_id = topic_parts[4]
            
            if request_id in self.pending_requests:
                self.pending_requests[request_id]['response'] = payload
                self.pending_requests[request_id]['completed'] = True
```

---

## Security Implementation

### MQTT Security
```python
# app/security/mqtt_security.py
import ssl
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class MQTTSecurityManager:
    def __init__(self):
        self.certificates = {}
        self.encryption_keys = {}
    
    def generate_client_certificate(self, client_id: str):
        """Generate client certificate for MQTT TLS"""
        # Generate private key
        private_key = serialization.generate_private_key(
            algorithm=serialization.hazmat.primitives.asymmetric.rsa.RSA(),
            key_size=2048,
            backend=default_backend()
        )
        
        # Generate certificate
        subject = x509.Name([
            x509.NameAttribute(x509.NameOID.COMMON_NAME, client_id),
            x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "Valtronics"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            subject
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=365)
        ).sign(private_key, hashes.SHA256(), default_backend())
        
        return private_key, cert
    
    def create_ssl_context(self, cert_file: str, key_file: str, ca_file: str):
        """Create SSL context for MQTT"""
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        # Load client certificate
        context.load_cert_chain(cert_file, key_file)
        context.load_verify_locations(cafile=ca_file)
        
        return context
    
    def encrypt_payload(self, payload: str, key: bytes) -> bytes:
        """Encrypt MQTT payload"""
        from cryptography.fernet import Fernet
        
        f = Fernet(key)
        encrypted_payload = f.encrypt(payload.encode())
        
        return encrypted_payload
    
    def decrypt_payload(self, encrypted_payload: bytes, key: bytes) -> str:
        """Decrypt MQTT payload"""
        from cryptography.fernet import Fernet
        
        f = Fernet(key)
        decrypted_payload = f.decrypt(encrypted_payload)
        
        return decrypted_payload.decode()
```

### Device Authentication
```python
# app/security/device_auth.py
import hashlib
import hmac
from typing import Dict, Any

class DeviceAuthenticator:
    def __init__(self):
        self.device_keys = {}
        self.session_tokens = {}
    
    def register_device(self, device_id: str, device_secret: str):
        """Register device with authentication credentials"""
        # Generate device key
        device_key = hashlib.sha256(device_secret.encode()).hexdigest()
        self.device_keys[device_id] = device_key
        
        return device_key
    
    def authenticate_device(self, device_id: str, auth_data: Dict[str, Any]) -> bool:
        """Authenticate device connection"""
        if device_id not in self.device_keys:
            return False
        
        expected_key = self.device_keys[device_id]
        
        # Verify HMAC
        message = auth_data.get('message', '')
        signature = auth_data.get('signature', '')
        
        expected_signature = hmac.new(
            expected_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def generate_session_token(self, device_id: str) -> str:
        """Generate session token for device"""
        import uuid
        import secrets
        
        token = secrets.token_urlsafe(32)
        self.session_tokens[token] = {
            'device_id': device_id,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(hours=24)
        }
        
        return token
    
    def validate_session_token(self, token: str) -> bool:
        """Validate device session token"""
        if token not in self.session_tokens:
            return False
        
        session = self.session_tokens[token]
        
        if datetime.utcnow() > session['expires_at']:
            del self.session_tokens[token]
            return False
        
        return True
```

---

## Performance Optimization

### Message Batching
```python
# app/optimization/message_batching.py
import asyncio
from typing import List, Dict, Any
from collections import defaultdict

class MessageBatcher:
    def __init__(self, mqtt_client, batch_size: int = 10, batch_timeout: float = 1.0):
        self.mqtt_client = mqtt_client
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.message_queue = defaultdict(list)
        self.batch_timers = {}
        self.running = True
    
    async def start(self):
        """Start message batching service"""
        while self.running:
            await self.process_batches()
            await asyncio.sleep(0.1)
    
    def add_message(self, topic: str, payload: Dict[str, Any]):
        """Add message to batch queue"""
        self.message_queue[topic].append({
            'payload': payload,
            'timestamp': datetime.utcnow()
        })
        
        # Start batch timer if not running
        if topic not in self.batch_timers:
            self.batch_timers[topic] = asyncio.create_task(
                self.batch_timer(topic)
            )
        
        # Send batch if size limit reached
        if len(self.message_queue[topic]) >= self.batch_size:
            await self.send_batch(topic)
    
    async def batch_timer(self, topic: str):
        """Batch timeout timer"""
        await asyncio.sleep(self.batch_timeout)
        
        if topic in self.message_queue and self.message_queue[topic]:
            await self.send_batch(topic)
    
    async def send_batch(self, topic: str):
        """Send batched messages"""
        if topic not in self.message_queue or not self.message_queue[topic]:
            return
        
        messages = self.message_queue[topic]
        batch_topic = f"{topic}/batch"
        
        batch_payload = {
            'batch_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'message_count': len(messages),
            'messages': messages
        }
        
        self.mqtt_client.publish_message(batch_topic, batch_payload)
        
        # Clear queue and timer
        self.message_queue[topic].clear()
        if topic in self.batch_timers:
            self.batch_timers[topic].cancel()
            del self.batch_timers[topic]
    
    async def process_batches(self):
        """Process pending batches"""
        for topic in list(self.message_queue.keys()):
            if self.message_queue[topic]:
                await self.send_batch(topic)
```

### Connection Pooling
```python
# app/optimization/connection_pool.py
import asyncio
from typing import List, Optional
from paho.mqtt.client import Client as MQTTClient

class MQTTConnectionPool:
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connections: List[MQTTClient] = []
        self.available_connections = asyncio.Queue()
        self.connection_lock = asyncio.Lock()
    
    async def initialize(self, broker_host: str, broker_port: int, 
                         username: str, password: str):
        """Initialize connection pool"""
        for i in range(self.max_connections):
            client = MQTTClient()
            client.username_pw_set(username, password)
            
            # Connect to broker
            client.connect(broker_host, broker_port, 60)
            client.loop_start()
            
            self.connections.append(client)
            await self.available_connections.put(client)
    
    async def get_connection(self) -> MQTTClient:
        """Get connection from pool"""
        return await self.available_connections.get()
    
    async def return_connection(self, connection: MQTTClient):
        """Return connection to pool"""
        await self.available_connections.put(connection)
    
    async def close_all(self):
        """Close all connections"""
        for connection in self.connections:
            connection.loop_stop()
            connection.disconnect()
        
        self.connections.clear()
```

---

## Monitoring and Diagnostics

### MQTT Monitoring
```python
# app/monitoring/mqtt_monitor.py
import time
import threading
from typing import Dict, Any
from collections import defaultdict, deque

class MQTTMonitor:
    def __init__(self):
        self.metrics = {
            'messages_sent': 0,
            'messages_received': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'connection_errors': 0,
            'publish_errors': 0
        }
        
        self.message_rates = defaultdict(lambda: deque(maxlen=60))  # 1 minute window
        self.error_log = deque(maxlen=1000)
        self.performance_metrics = {}
        
        self.monitoring_thread = None
        self.running = False
    
    def start_monitoring(self):
        """Start monitoring thread"""
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitor_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring thread"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            # Update message rates
            current_time = time.time()
            
            # Calculate rates per second
            for metric in ['messages_sent', 'messages_received']:
                if metric in self.message_rates:
                    timestamps = self.message_rates[metric]
                    recent_count = sum(1 for t in timestamps if current_time - t < 60)
                    rate = recent_count / 60.0
                    self.performance_metrics[f'{metric}_rate'] = rate
            
            time.sleep(1)
    
    def record_message_sent(self, topic: str, size: int):
        """Record sent message"""
        self.metrics['messages_sent'] += 1
        self.metrics['bytes_sent'] += size
        self.message_rates['messages_sent'].append(time.time())
    
    def record_message_received(self, topic: str, size: int):
        """Record received message"""
        self.metrics['messages_received'] += 1
        self.metrics['bytes_received'] += size
        self.message_rates['messages_received'].append(time.time())
    
    def record_error(self, error_type: str, error_message: str):
        """Record error"""
        self.metrics[f'{error_type}_errors'] = self.metrics.get(f'{error_type}_errors', 0) + 1
        self.error_log.append({
            'timestamp': time.time(),
            'type': error_type,
            'message': error_message
        })
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            'basic_metrics': self.metrics.copy(),
            'performance_metrics': self.performance_metrics.copy(),
            'recent_errors': list(self.error_log)[-10:]
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get MQTT health status"""
        metrics = self.get_metrics()
        
        # Calculate health score
        health_score = 100
        
        # Deduct points for errors
        error_count = sum(metrics['basic_metrics'].get(f'{t}_errors', 0) 
                          for t in ['connection', 'publish'])
        health_score -= min(error_count * 5, 50)
        
        # Check message rates
        if metrics['performance_metrics'].get('messages_sent_rate', 0) == 0:
            health_score -= 20
        
        status = 'healthy'
        if health_score < 70:
            status = 'degraded'
        elif health_score < 50:
            status = 'unhealthy'
        
        return {
            'status': status,
            'health_score': max(0, health_score),
            'metrics': metrics
        }
```

---

## Troubleshooting

### Common MQTT Issues

#### Connection Problems
```python
# app/troubleshooting/mqtt_troubleshooting.py
import socket
import ssl
from typing import Dict, Any

class MQTTS troubleshooting:
    @staticmethod
    def test_mqtt_connection(broker_host: str, broker_port: int) -> Dict[str, Any]:
        """Test MQTT broker connectivity"""
        result = {
            'tcp_connection': False,
            'ssl_connection': False,
            'mqtt_connection': False,
            'error': None
        }
        
        try:
            # Test TCP connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            tcp_result = sock.connect_ex((broker_host, broker_port))
            result['tcp_connection'] = (tcp_result == 0)
            sock.close()
            
            if not result['tcp_connection']:
                result['error'] = 'TCP connection failed'
                return result
            
            # Test MQTT connection
            try:
                import paho.mqtt.client as mqtt
                client = mqtt.Client()
                client.connect(broker_host, broker_port, 5)
                result['mqtt_connection'] = True
                client.disconnect()
                
            except Exception as e:
                result['error'] = f'MQTT connection failed: {str(e)}'
                
        except Exception as e:
            result['error'] = f'Connection test failed: {str(e)}'
        
        return result
    
    @staticmethod
    def diagnose_mqtt_issue(error_message: str) -> Dict[str, Any]:
        """Diagnose MQTT issues based on error message"""
        diagnosis = {
            'issue_type': 'unknown',
            'possible_causes': [],
            'solutions': []
        }
        
        error_lower = error_message.lower()
        
        if 'connection refused' in error_lower:
            diagnosis['issue_type'] = 'connection_refused'
            diagnosis['possible_causes'] = [
                'MQTT broker not running',
                'Wrong port number',
                'Firewall blocking connection'
            ]
            diagnosis['solutions'] = [
                'Check if MQTT broker is running',
                'Verify broker port and address',
                'Check firewall settings'
            ]
        
        elif 'authentication' in error_lower:
            diagnosis['issue_type'] = 'authentication'
            diagnosis['possible_causes'] = [
                'Wrong username/password',
                'Invalid client certificate',
                'Account disabled'
            ]
            diagnosis['solutions'] = [
                'Verify MQTT credentials',
                'Check client certificate',
                'Contact MQTT administrator'
            ]
        
        elif 'timeout' in error_lower:
            diagnosis['issue_type'] = 'timeout'
            diagnosis['possible_causes'] = [
                'Network connectivity issues',
                'Broker overloaded',
                'DNS resolution problems'
            ]
            diagnosis['solutions'] = [
                'Check network connectivity',
                'Verify broker status',
                'Check DNS configuration'
            ]
        
        return diagnosis
```

---

## Best Practices

### MQTT Best Practices
- Use quality of service (QoS) levels appropriately
- Implement proper error handling and reconnection logic
- Use retained messages only when necessary
- Implement message batching for high-frequency data
- Use topic naming conventions consistently
- Implement proper security measures
- Monitor MQTT broker performance
- Use connection pooling for high-load scenarios

### Security Best Practices
- Always use TLS/SSL for production environments
- Implement proper authentication and authorization
- Use client certificates for device authentication
- Encrypt sensitive payload data
- Implement proper access control
- Regularly rotate certificates and keys
- Monitor for suspicious activity

### Performance Best Practices
- Use message batching for high-frequency data
- Implement connection pooling
- Optimize message payload size
- Use appropriate QoS levels
- Implement proper message retention policies
- Monitor broker performance metrics
- Use load balancing for high-load scenarios

---

## Support

For MQTT and IoT protocol support:
- **Documentation**: [API Overview](../03-api/api-overview.md)
- **Device API**: [Device API](../03-api/device-api.md)
- **WebSocket API**: [WebSocket API](../03-api/websocket-api.md)
- **Troubleshooting**: [Troubleshooting Guide](../10-reference/troubleshooting.md)
- **Email**: autobotsolution@gmail.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**MQTT and IoT Protocols Documentation v1.0**
