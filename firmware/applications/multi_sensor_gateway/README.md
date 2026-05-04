# Multi-Sensor Gateway Firmware

**Complete firmware implementation for Valtronics multi-sensor gateway devices**

---

## Overview

This application provides a comprehensive multi-sensor gateway that can read and process data from multiple different sensor types simultaneously. It supports environmental sensors, industrial sensors, and custom sensors, making it ideal for comprehensive monitoring deployments.

---

## Features

### Multi-Sensor Support
- **Environmental**: Temperature, humidity, pressure, air quality
- **Industrial**: Vibration, current, voltage, proximity
- **Custom**: Extensible sensor interface for custom sensors
- **Mixed Platforms**: Support for different sensor communication protocols

### Advanced Features
- **Data Fusion**: Combine data from multiple sensors
- **Cross-Correlation**: Analyze relationships between sensors
- **Adaptive Sampling**: Dynamic sampling rates based on sensor data
- **Local Processing**: Edge computing for real-time analysis
- **Redundancy**: Sensor redundancy and failover

### Communication
- **MQTT**: Primary telemetry protocol
- **HTTP/HTTPS**: RESTful API integration
- **Modbus**: Industrial protocol support
- **LoRa**: Long-range communication option

---

## Hardware Requirements

### Minimum Requirements
- **Microcontroller**: ESP32 or STM32F4/F7 series
- **Memory**: 128KB+ SRAM, 2MB+ Flash
- **Connectivity**: WiFi, Ethernet, or LoRa
- **Power**: 5V or 3.3V supply

### Recommended Components
- **ESP32 DevKit**: Development and production
- **STM32F429IGT6**: Industrial applications
- **Sensor Array**: Multiple sensors of different types
- **Power Supply**: 5V industrial power supply
- **Enclosure**: IP67 rated industrial enclosure

---

## Directory Structure

```
applications/multi_sensor_gateway/
├── README.md                    # This file
├── platformio.ini               # PlatformIO configuration
├── src/                         # Source code
│   ├── main.cpp                 # Main application
│   ├── config/                  # Configuration
│   ├── sensors/                  # Sensor interfaces
│   │   ├── sensor_manager.h      # Sensor manager
│   │   ├── sensor_factory.h      # Sensor factory
│   │   └── sensor_types.h        # Sensor type definitions
│   ├── data_fusion/              # Data fusion algorithms
│   │   ├── fusion_engine.h        # Fusion engine
│   │   ├── correlation.h          # Cross-correlation
│   │   └── adaptive_sampling.h    # Adaptive sampling
│   ├── communication/            # Communication protocols
│   │   ├── mqtt_client.h         # MQTT client
│   │   ├── http_server.h         # HTTP server
│   │   └── modbus_server.h       # Modbus server
│   ├── processing/                # Data processing
│   │   ├── edge_processor.h       # Edge computing
│   │   ├── analytics.h            # Analytics engine
│   │   └── redundancy.h           # Redundancy management
│   ├── alerts/                   # Alert system
│   │   ├── alert_manager.h       # Alert manager
│   │   └── multi_sensor_alerts.h  # Multi-sensor alerts
│   ├── utils/                    # Utility functions
│   │   ├── json_utils.h          # JSON utilities
│   │   ├── time_utils.h          # Time utilities
│   │   └── logger.h              # Logging utilities
│   └── config/                  # Configuration
│       ├── config_manager.h      # Configuration manager
│       └── device_config.json     # Device configuration
├── lib/                         # Libraries
├── test/                        # Tests
├── docs/                        # Documentation
└── examples/                    # Example implementations
```

---

## Configuration

### Device Configuration
```json
{
  "device": {
    "id": "VT-GATEWAY-001",
    "name": "Multi-Sensor Gateway 1",
    "type": "multi_sensor_gateway",
    "version": "2.0.0",
    "location": "Industrial Plant A",
    "description": "Comprehensive multi-sensor monitoring gateway"
  },
  "sensors": [
    {
      "id": "temp_01",
      "type": "temperature",
      "model": "DHT22",
      "pin": 4,
      "interval": 30,
      "priority": "high",
      "redundant_sensors": ["temp_02"]
    },
    {
      "id": "temp_02",
      "type": "temperature",
      "model": "BME280",
      "interface": "I2C",
      "address": "0x76",
      "interval": 30,
      "priority": "medium"
    },
    {
      "id": "humidity_01",
      "type": "humidity",
      "model": "DHT22",
      "pin": 4,
      "interval": 30,
      "priority": "high"
    },
    {
      "id": "pressure_01",
      "type": "pressure",
      "model": "BME280",
      "interface": "I2C",
      "address": "0x76",
      "interval": 60,
      "priority": "medium"
    },
    {
      "id": "air_quality_01",
      "type": "air_quality",
      "model": "PMS5003",
      "interface": "UART",
      "pin": 16,
      "interval": 120,
      "priority": "low"
    },
    {
      "id": "vibration_01",
      "type": "vibration",
      "model": "ADXL345",
      "interface": "I2C",
      "address": "0x53",
      "interval": 1000,
      "priority": "high"
    }
  ],
  "data_fusion": {
    "enabled": true,
    "algorithms": ["weighted_average", "kalman_filter", "correlation_analysis"],
    "correlation_threshold": 0.7,
    "fusion_interval": 60
  },
  "adaptive_sampling": {
    "enabled": true,
    "base_interval": 30,
    "min_interval": 10,
    "max_interval": 300,
    "change_threshold": 0.1,
    "variance_threshold": 0.05
  },
  "communication": {
    "mqtt": {
      "broker": "mqtt.valtronics.com",
      "port": 1883,
      "telemetry_interval": 30,
      "fused_data_interval": 60
    },
    "http": {
      "enabled": true,
      "port": 80,
      "api_endpoints": true
    },
    "modbus": {
      "enabled": true,
      "port": 502,
      "register_base": 4000
    }
  },
  "redundancy": {
    "enabled": true,
    "failover_timeout": 300,
    "health_check_interval": 60,
    "auto_recovery": true
  },
  "edge_processing": {
    "enabled": true,
    "analytics": ["trend_analysis", "anomaly_detection", "predictive_maintenance"],
    "local_storage": true,
    "compression": true
  }
}
```

### PlatformIO Configuration
```ini
[env:esp32_gateway]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200
upload_speed = 921600
lib_deps = 
    PubSubClient
    ArduinoJson
    DHT sensor library
    Adafruit BME280 Library
    Adafruit ADXL345
    SoftwareSerial
    WiFiManager
    ArduinoOTA
    ESP32WebServer
    ModbusMaster

build_flags = 
    -DCORE_DEBUG_LEVEL=3
    -DCONFIG_ARDUHAL_LOG_COLORS
    -DSENSOR_COUNT=6
    -DFUSION_ENABLED=1
```

---

## Implementation

### Main Application
```cpp
#include <Arduino.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiManager.h>
#include <ArduinoOTA.h>
#include <ESP32WebServer.h>

#include "config/device_config.h"
#include "sensors/sensor_manager.h"
#include "data_fusion/fusion_engine.h"
#include "communication/mqtt_client.h"
#include "processing/edge_processor.h"
#include "alerts/alert_manager.h"
#include "utils/logger.h"
#include "utils/json_utils.h"

// Global objects
SensorManager* sensor_manager = nullptr;
FusionEngine* fusion_engine = nullptr;
MQTTClient* mqtt_client = nullptr;
EdgeProcessor* edge_processor = nullptr;
AlertManager* alert_manager = nullptr;
DeviceConfig* device_config = nullptr;
ESP32WebServer* http_server = nullptr;

// Global state
bool system_ready = false;
uint32_t last_telemetry_time = 0;
uint32_t last_fusion_time = 0;
uint32_t last_health_check = 0;

void setup() {
    Serial.begin(115200);
    Logger::info("Valtronics Multi-Sensor Gateway Starting...");
    
    // Initialize configuration
    device_config = new DeviceConfig();
    if (!device_config->load()) {
        Logger::error("Failed to load device configuration");
        return;
    }
    
    // Initialize components
    initialize_sensors();
    initialize_fusion_engine();
    initialize_edge_processor();
    initialize_alerts();
    initialize_communication();
    initialize_http_server();
    initialize_ota();
    
    system_ready = true;
    Logger::info("Multi-sensor gateway ready");
    
    // Send startup message
    send_startup_message();
}

void loop() {
    if (!system_ready) {
        delay(1000);
        return;
    }
    
    // Handle HTTP server
    http_server->handleClient();
    
    // Handle MQTT
    mqtt_client->loop();
    
    // Handle OTA
    ArduinoOTA.handle();
    
    // Read sensors
    sensor_data_array_t sensor_data = sensor_manager->read_all_sensors();
    
    // Perform data fusion
    fused_data_t fused_data = fusion_engine->process(sensor_data);
    
    // Edge processing
    analytics_data_t analytics = edge_processor->process(sensor_data, fused_data);
    
    // Check alerts
    alert_manager->check_alerts(sensor_data, fused_data, analytics);
    
    // Handle redundancy
    handle_redundancy(sensor_data);
    
    // Send telemetry
    handle_telemetry(sensor_data, fused_data, analytics);
    
    // Handle commands
    handle_commands();
    
    // Health checks
    handle_health_checks();
    
    delay(1000);
}

void initialize_sensors() {
    Logger::info("Initializing sensor manager...");
    
    sensor_manager = new SensorManager();
    if (!sensor_manager->init()) {
        Logger::error("Failed to initialize sensor manager");
        return;
    }
    
    // Load sensor configuration
    sensor_config_array_t sensor_configs = device_config->get_sensor_configs();
    for (const auto& config : sensor_configs) {
        if (!sensor_manager->add_sensor(config)) {
            Logger::error("Failed to add sensor: " + config.id);
        }
    }
    
    Logger::info("Sensor manager initialized with " + String(sensor_manager->get_sensor_count()) + " sensors");
}

void initialize_fusion_engine() {
    Logger::info("Initializing fusion engine...");
    
    fusion_engine = new FusionEngine();
    if (!fusion_engine->init()) {
        Logger::error("Failed to initialize fusion engine");
        return;
    }
    
    // Configure fusion algorithms
    fusion_config_t fusion_config = device_config->get_fusion_config();
    fusion_engine->configure(fusion_config);
    
    Logger::info("Fusion engine initialized");
}

void initialize_edge_processor() {
    Logger::info("Initializing edge processor...");
    
    edge_processor = new EdgeProcessor();
    if (!edge_processor->init()) {
        Logger::error("Failed to initialize edge processor");
        return;
    }
    
    // Configure analytics
    edge_config_t edge_config = device_config->get_edge_config();
    edge_processor->configure(edge_config);
    
    Logger::info("Edge processor initialized");
}

void initialize_alerts() {
    Logger::info("Initializing alert manager...");
    
    alert_manager = new AlertManager();
    if (!alert_manager->init()) {
        Logger::error("Failed to initialize alert manager");
        return;
    }
    
    // Configure alerts
    alert_config_t alert_config = device_config->get_alert_config();
    alert_manager->configure(alert_config);
    
    Logger::info("Alert manager initialized");
}

void initialize_communication() {
    Logger::info("Initializing communication...");
    
    // Initialize WiFi
    initialize_wifi();
    
    // Initialize MQTT
    mqtt_client = new MQTTClient(
        device_config->get_mqtt_broker(),
        device_config->get_mqtt_port(),
        device_config->get_device_id()
    );
    
    mqtt_client->set_message_callback(handle_mqtt_message);
    
    if (!mqtt_client->connect()) {
        Logger::error("Failed to connect to MQTT broker");
        return;
    }
    
    // Subscribe to topics
    mqtt_client->subscribe(device_config->get_mqtt_commands_topic());
    mqtt_client->subscribe(device_config->get_mqtt_config_topic());
    
    Logger::info("Communication initialized");
}

void initialize_http_server() {
    if (!device_config->get_http_enabled()) {
        return;
    }
    
    Logger::info("Initializing HTTP server...");
    
    http_server = new ESP32WebServer(device_config->get_http_port());
    
    // Setup HTTP endpoints
    setup_http_endpoints();
    
    http_server->begin();
    Logger::info("HTTP server initialized");
}

void setup_http_endpoints() {
    // Status endpoint
    http_server->on("/api/status", HTTP_GET, []() {
        JsonObject status = create_status_json();
        String response = JSONUtils::serialize(status);
        http_server->send(200, "application/json", response);
    });
    
    // Sensors endpoint
    http_server->on("/api/sensors", HTTP_GET, []() {
        sensor_data_array_t data = sensor_manager->read_all_sensors();
        JsonObject sensors = create_sensors_json(data);
        String response = JSONUtils::serialize(sensors);
        http_server->send(200, "application/json", response);
    });
    
    // Fused data endpoint
    http_server->on("/api/fused", HTTP_GET, []() {
        sensor_data_array_t sensor_data = sensor_manager->read_all_sensors();
        fused_data_t fused_data = fusion_engine->process(sensor_data);
        JsonObject fused = create_fused_json(fused_data);
        String response = JSONUtils::serialize(fused);
        http_server->send(200, "application/json", response);
    });
    
    // Analytics endpoint
    http_server->on("/api/analytics", HTTP_GET, []() {
        sensor_data_array_t sensor_data = sensor_manager->read_all_sensors();
        fused_data_t fused_data = fusion_engine->process(sensor_data);
        analytics_data_t analytics = edge_processor->process(sensor_data, fused_data);
        JsonObject analytics_json = create_analytics_json(analytics);
        String response = JSONUtils::serialize(analytics_json);
        http_server->send(200, "application/json", response);
    });
    
    // Configuration endpoint
    http_server->on("/api/config", HTTP_GET, []() {
        JsonObject config = create_config_json();
        String response = JSONUtils::serialize(config);
        http_server->send(200, "application/json", response);
    });
    
    // Command endpoint
    http_server->on("/api/command", HTTP_POST, []() {
        String body = http_server->arg("plain");
        handle_http_command(body);
        http_server->send(200, "application/json", "{\"status\":\"ok\"}");
    });
}

void initialize_wifi() {
    Logger::info("Initializing WiFi...");
    
    WiFiManager wifiManager;
    
    wifiManager.setDebugOutput(false);
    
    if (!wifiManager.autoConnect("Valtronics-Gateway")) {
        Logger::error("Failed to connect to WiFi");
        ESP.restart();
    }
    
    Logger::info("WiFi connected: " + WiFi.localIP().toString());
}

void initialize_ota() {
    if (!device_config->get_ota_enabled()) {
        return;
    }
    
    Logger::info("Initializing OTA...");
    
    ArduinoOTA.setHostname(device_config->get_device_id().c_str());
    ArduinoOTA.setPassword(device_config->get_ota_password().c_str());
    
    ArduinoOTA.onStart([]() {
        String type = (ArduinoOTA.getCommand() == U_FLASH) ? "sketch" : "filesystem";
        Logger::info("Start updating " + type);
    });
    
    ArduinoOTA.onEnd([]() {
        Logger::info("OTA update completed");
    });
    
    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        Logger::info("OTA Progress: " + String(progress) + "%");
    });
    
    ArduinoOTA.onError([](ota_error_t error) {
        Logger::error("OTA Error: " + String(error));
    });
    
    ArduinoOTA.begin();
    Logger::info("OTA initialized");
}

void handle_telemetry(sensor_data_array_t sensor_data, fused_data_t fused_data, analytics_data_t analytics) {
    uint32_t current_time = millis();
    
    // Send basic telemetry
    if (current_time - last_telemetry_time >= device_config->get_telemetry_interval() * 1000) {
        send_sensor_telemetry(sensor_data);
        last_telemetry_time = current_time;
    }
    
    // Send fused data
    if (current_time - last_fusion_time >= device_config->get_fusion_interval() * 1000) {
        send_fused_telemetry(fused_data);
        last_fusion_time = current_time;
    }
    
    // Send analytics
    if (analytics.has_data) {
        send_analytics_telemetry(analytics);
    }
}

void send_sensor_telemetry(sensor_data_array_t sensor_data) {
    JsonObject telemetry;
    telemetry["device_id"] = device_config->get_device_id();
    telemetry["timestamp"] = millis();
    telemetry["device_type"] = device_config->get_device_type();
    telemetry["location"] = device_config->get_device_location();
    
    // Add sensor data
    JsonArray sensors = telemetry.createNestedArray("sensors");
    for (const auto& data : sensor_data) {
        JsonObject sensor = sensors.createNestedObject();
        sensor["id"] = data.sensor_id;
        sensor["type"] = data.sensor_type;
        sensor["value"] = data.value;
        sensor["unit"] = data.unit;
        sensor["timestamp"] = data.timestamp;
        sensor["valid"] = data.valid;
        sensor["quality"] = data.quality;
    }
    
    // System information
    JsonObject system = telemetry.createNestedObject("system");
    system["free_heap"] = ESP.getFreeHeap();
    system["wifi_rssi"] = WiFi.RSSI();
    system["uptime"] = millis();
    system["sensor_count"] = sensor_data.size();
    system["active_sensors"] = std::count_if(sensor_data.begin(), sensor_data.end(), 
                                          [](const sensor_data_t& d) { return d.valid; });
    
    // Send telemetry
    String payload = JSONUtils::serialize(telemetry);
    if (mqtt_client->publish(device_config->get_mqtt_telemetry_topic(), payload)) {
        Logger::info("Sensor telemetry sent");
    } else {
        Logger::error("Failed to send sensor telemetry");
    }
}

void send_fused_telemetry(fused_data_t fused_data) {
    JsonObject telemetry;
    telemetry["device_id"] = device_config->get_device_id();
    telemetry["timestamp"] = millis();
    telemetry["type"] = "fused_data";
    
    // Fused values
    JsonObject fused = telemetry.createNestedObject("fused");
    fused["temperature"] = fused_data.temperature;
    fused["humidity"] = fused_data.humidity;
    fused["pressure"] = fused_data.pressure;
    fused["air_quality_index"] = fused_data.air_quality_index;
    fused["vibration_level"] = fused_data.vibration_level;
    fused["confidence"] = fused_data.confidence;
    fused["algorithm"] = fused_data.algorithm_used;
    
    // Correlations
    JsonArray correlations = telemetry.createNestedArray("correlations");
    for (const auto& corr : fused_data.correlations) {
        JsonObject correlation = correlations.createNestedObject();
        correlation["sensor1"] = corr.sensor1_id;
        correlation["sensor2"] = corr.sensor2_id;
        correlation["coefficient"] = corr.coefficient;
        correlation["significance"] = corr.significance;
    }
    
    // Send telemetry
    String payload = JSONUtils::serialize(telemetry);
    if (mqtt_client->publish("valtronics/fused_data", payload)) {
        Logger::info("Fused telemetry sent");
    } else {
        Logger::error("Failed to send fused telemetry");
    }
}

void send_analytics_telemetry(analytics_data_t analytics) {
    JsonObject telemetry;
    telemetry["device_id"] = device_config->get_device_id();
    telemetry["timestamp"] = millis();
    telemetry["type"] = "analytics";
    
    // Analytics results
    JsonObject results = telemetry.createNestedObject("results");
    results["trend_analysis"] = analytics.trend_analysis;
    results["anomaly_detected"] = analytics.anomaly_detected;
    results["maintenance_prediction"] = analytics.maintenance_prediction;
    results["efficiency_score"] = analytics.efficiency_score;
    results["health_score"] = analytics.health_score;
    
    // Anomalies
    if (analytics.anomaly_detected) {
        JsonArray anomalies = telemetry.createNestedArray("anomalies");
        for (const auto& anomaly : analytics.anomalies) {
            JsonObject anomaly_obj = anomalies.createNestedObject();
            anomaly_obj["sensor_id"] = anomaly.sensor_id;
            anomaly_obj["type"] = anomaly.type;
            anomaly_obj["severity"] = anomaly.severity;
            anomaly_obj["description"] = anomaly.description;
            anomaly_obj["timestamp"] = anomaly.timestamp;
        }
    }
    
    // Send telemetry
    String payload = JSONUtils::serialize(telemetry);
    if (mqtt_client->publish("valtronics/analytics", payload)) {
        Logger::info("Analytics telemetry sent");
    } else {
        Logger::error("Failed to send analytics telemetry");
    }
}

void handle_redundancy(sensor_data_array_t sensor_data) {
    if (!device_config->get_redundancy_enabled()) {
        return;
    }
    
    redundancy_config_t redundancy_config = device_config->get_redundancy_config();
    
    // Check for failed sensors
    std::vector<String> failed_sensors;
    for (const auto& data : sensor_data) {
        if (!data.valid && data.priority == "high") {
            failed_sensors.push_back(data.sensor_id);
        }
    }
    
    // Handle failover
    for (const auto& failed_sensor : failed_sensors) {
        if (sensor_manager->has_redundant_sensor(failed_sensor)) {
            String redundant_sensor = sensor_manager->get_redundant_sensor(failed_sensor);
            Logger::info("Failover: " + failed_sensor + " -> " + redundant_sensor);
            
            // Send failover alert
            send_failover_alert(failed_sensor, redundant_sensor);
        }
    }
}

void send_failover_alert(const String& failed_sensor, const String& redundant_sensor) {
    JsonObject alert;
    alert["device_id"] = device_config->get_device_id();
    alert["alert_type"] = "sensor_failover";
    alert["failed_sensor"] = failed_sensor;
    alert["redundant_sensor"] = redundant_sensor;
    alert["timestamp"] = millis();
    alert["severity"] = "warning";
    alert["message"] = "Sensor failover activated: " + failed_sensor + " -> " + redundant_sensor;
    
    String payload = JSONUtils::serialize(alert);
    mqtt_client->publish("valtronics/alerts", payload);
}

void handle_health_checks() {
    uint32_t current_time = millis();
    
    if (current_time - last_health_check < device_config->get_health_check_interval() * 1000) {
        return;
    }
    
    last_health_check = current_time;
    
    // Check sensor health
    sensor_health_array_t health = sensor_manager->get_sensor_health();
    
    // Check system health
    system_health_t system_health = {
        .free_heap = ESP.getFreeHeap(),
        .wifi_rssi = WiFi.RSSI(),
        .mqtt_connected = mqtt_client->connected(),
        .uptime = millis(),
        .sensor_count = sensor_manager->get_sensor_count(),
        .active_sensors = std::count_if(health.begin(), health.end(), 
                                   [](const sensor_health_t& h) { return h.status == "ok"; })
    };
    
    // Send health telemetry
    send_health_telemetry(health, system_health);
}

void send_health_telemetry(sensor_health_array_t sensor_health, system_health_t system_health) {
    JsonObject health;
    health["device_id"] = device_config->get_device_id();
    health["timestamp"] = millis();
    health["type"] = "health_check";
    
    // System health
    JsonObject system = health.createNestedObject("system");
    system["free_heap"] = system_health.free_heap;
    system["wifi_rssi"] = system_health.wifi_rssi;
    system["mqtt_connected"] = system_health.mqtt_connected;
    system["uptime"] = system_health.uptime;
    system["sensor_count"] = system_health.sensor_count;
    system["active_sensors"] = system_health.active_sensors;
    system["health_score"] = (float)system_health.active_sensors / system_health.sensor_count * 100;
    
    // Sensor health
    JsonArray sensors = health.createNestedArray("sensors");
    for (const auto& h : sensor_health) {
        JsonObject sensor = sensors.createNestedObject();
        sensor["id"] = h.sensor_id;
        sensor["status"] = h.status;
        sensor["last_reading"] = h.last_reading;
        sensor["error_count"] = h.error_count;
        sensor["quality"] = h.quality;
    }
    
    // Send health telemetry
    String payload = JSONUtils::serialize(health);
    mqtt_client->publish("valtronics/health", payload);
}

void handle_mqtt_message(mqtt_message_t message) {
    Logger::info("MQTT message received: " + message.topic);
    
    // Parse JSON message
    DynamicJsonDocument doc(512);
    DeserializationError error = deserializeJson(doc, message.payload);
    
    if (error) {
        Logger::error("Invalid JSON message");
        return;
    }
    
    // Handle commands
    if (message.topic == device_config->get_mqtt_commands_topic()) {
        handle_command(doc);
    }
    
    // Handle configuration
    if (message.topic == device_config->get_mqtt_config_topic()) {
        handle_config_update(doc);
    }
}

void handle_command(const JsonObject& command) {
    String cmd = command["command"];
    
    if (cmd == "reboot") {
        Logger::info("Reboot command received");
        send_command_response("reboot", "Rebooting device");
        delay(1000);
        ESP.restart();
    } else if (cmd == "status") {
        send_status_report();
    } else if (cmd == "sensors") {
        send_sensor_report();
    } else if (cmd == "fusion") {
        send_fusion_report();
    } else if (cmd == "analytics") {
        send_analytics_report();
    } else if (cmd == "health") {
        send_health_report();
    } else if (cmd == "calibrate") {
        perform_calibration();
    } else if (cmd == "reset") {
        perform_reset();
    } else {
        Logger::warning("Unknown command: " + cmd);
    }
}

void handle_config_update(const JsonObject& config_update) {
    Logger::info("Configuration update received");
    
    // Update configuration
    if (config_update.containsKey("telemetry_interval")) {
        uint32_t interval = config_update["telemetry_interval"];
        device_config->set_telemetry_interval(interval);
        Logger::info("Telemetry interval updated: " + String(interval));
    }
    
    if (config_update.containsKey("fusion_interval")) {
        uint32_t interval = config_update["fusion_interval"];
        device_config->set_fusion_interval(interval);
        Logger::info("Fusion interval updated: " + String(interval));
    }
    
    if (config_update.containsKey("adaptive_sampling")) {
        bool enabled = config_update["adaptive_sampling"];
        device_config->set_adaptive_sampling(enabled);
        Logger::info("Adaptive sampling updated: " + String(enabled));
    }
    
    // Save configuration
    device_config->save();
    
    send_command_response("config", "Configuration updated");
}

void handle_commands() {
    // Handle local commands (buttons, etc.)
    // This would be implemented based on hardware
}

void send_command_response(const String& command, const String& message) {
    JsonObject response;
    response["device_id"] = device_config->get_device_id();
    response["command"] = command;
    response["response"] = message;
    response["timestamp"] = millis();
    
    String payload = JSONUtils::serialize(response);
    mqtt_client->publish("valtronics/devices/" + device_config->get_device_id() + "/responses", payload);
}

void send_startup_message() {
    JsonObject message;
    message["device_id"] = device_config->get_device_id();
    message["event"] = "startup";
    message["message"] = "Multi-sensor gateway started successfully";
    message["firmware_version"] = "2.0.0";
    message["sensor_count"] = sensor_manager->get_sensor_count();
    message["timestamp"] = millis();
    
    String payload = JSONUtils::serialize(message);
    mqtt_client->publish("valtronics/devices/" + device_config->get_device_id() + "/events", payload);
}

void perform_calibration() {
    Logger::info("Performing sensor calibration...");
    
    // Calibrate all sensors
    sensor_manager->calibrate_all_sensors();
    
    // Recalibrate fusion engine
    fusion_engine->recalibrate();
    
    Logger::info("Calibration completed");
    send_command_response("calibrate", "Calibration completed");
}

void perform_reset() {
    Logger::info("Performing system reset...");
    
    // Reset sensor manager
    sensor_manager->reset();
    
    // Reset fusion engine
    fusion_engine->reset();
    
    // Reset edge processor
    edge_processor->reset();
    
    // Clear alerts
    alert_manager->clear_all_alerts();
    
    Logger::info("System reset completed");
    send_command_response("reset", "System reset completed");
}

// JSON creation functions
JsonObject create_status_json() {
    JsonObject status;
    status["device_id"] = device_config->get_device_id();
    status["device_type"] = device_config->get_device_type();
    status["firmware_version"] = "2.0.0";
    status["uptime"] = millis();
    status["free_heap"] = ESP.getFreeHeap();
    status["wifi_rssi"] = WiFi.RSSI();
    status["mqtt_connected"] = mqtt_client->connected();
    status["sensor_count"] = sensor_manager->get_sensor_count();
    status["active_sensors"] = sensor_manager->get_active_sensor_count();
    status["fusion_enabled"] = fusion_engine->is_enabled();
    status["edge_processing_enabled"] = edge_processor->is_enabled();
    
    return status;
}

JsonObject create_sensors_json(sensor_data_array_t sensor_data) {
    JsonObject sensors;
    JsonArray sensor_array = sensors.createNestedArray("sensors");
    
    for (const auto& data : sensor_data) {
        JsonObject sensor = sensor_array.createNestedObject();
        sensor["id"] = data.sensor_id;
        sensor["type"] = data.sensor_type;
        sensor["value"] = data.value;
        sensor["unit"] = data.unit;
        sensor["timestamp"] = data.timestamp;
        sensor["valid"] = data.valid;
        sensor["quality"] = data.quality;
    }
    
    return sensors;
}

JsonObject create_fused_json(fused_data_t fused_data) {
    JsonObject fused;
    fused["temperature"] = fused_data.temperature;
    fused["humidity"] = fused_data.humidity;
    fused["pressure"] = fused_data.pressure;
    fused["air_quality_index"] = fused_data.air_quality_index;
    fused["vibration_level"] = fused_data.vibration_level;
    fused["confidence"] = fused_data.confidence;
    fused["algorithm"] = fused_data.algorithm_used;
    fused["timestamp"] = fused_data.timestamp;
    
    return fused;
}

JsonObject create_analytics_json(analytics_data_t analytics) {
    JsonObject analytics_json;
    analytics_json["trend_analysis"] = analytics.trend_analysis;
    analytics_json["anomaly_detected"] = analytics.anomaly_detected;
    analytics_json["maintenance_prediction"] = analytics.maintenance_prediction;
    analytics_json["efficiency_score"] = analytics.efficiency_score;
    analytics_json["health_score"] = analytics.health_score;
    analytics_json["timestamp"] = analytics.timestamp;
    
    return analytics_json;
}

JsonObject create_config_json() {
    JsonObject config;
    config["device_id"] = device_config->get_device_id();
    config["telemetry_interval"] = device_config->get_telemetry_interval();
    config["fusion_interval"] = device_config->get_fusion_interval();
    config["adaptive_sampling"] = device_config->get_adaptive_sampling();
    config["redundancy_enabled"] = device_config->get_redundancy_enabled();
    config["edge_processing_enabled"] = device_config->get_edge_processing_enabled();
    
    return config;
}
```

---

## Usage Examples

### Basic Multi-Sensor Gateway
```cpp
#include "config/device_config.h"
#include "sensors/sensor_manager.h"
#include "data_fusion/fusion_engine.h"

void setup() {
    Serial.begin(115200);
    
    // Load configuration
    DeviceConfig config;
    config.load();
    
    // Initialize sensor manager
    SensorManager sensor_manager;
    sensor_manager.init();
    
    // Add sensors from configuration
    sensor_config_array_t sensors = config.get_sensor_configs();
    for (const auto& sensor_config : sensors) {
        sensor_manager.add_sensor(sensor_config);
    }
    
    // Initialize fusion engine
    FusionEngine fusion;
    fusion.init();
    
    Serial.println("Multi-sensor gateway ready");
}

void loop() {
    // Read all sensors
    sensor_data_array_t sensor_data = sensor_manager.read_all_sensors();
    
    // Perform data fusion
    fused_data_t fused_data = fusion.process(sensor_data);
    
    // Send telemetry
    send_multi_sensor_telemetry(sensor_data, fused_data);
    
    delay(30000);  // Send every 30 seconds
}
```

### Advanced Gateway with Analytics
```cpp
#include "processing/edge_processor.h"
#include "alerts/alert_manager.h"

void setup() {
    // Initialize components
    SensorManager sensor_manager;
    sensor_manager.init();
    
    FusionEngine fusion;
    fusion.init();
    
    EdgeProcessor edge_processor;
    edge_processor.init();
    
    AlertManager alerts;
    alerts.init();
    
    Serial.println("Advanced multi-sensor gateway ready");
}

void loop() {
    // Read sensors
    sensor_data_array_t sensor_data = sensor_manager.read_all_sensors();
    
    // Data fusion
    fused_data_t fused_data = fusion.process(sensor_data);
    
    // Edge processing
    analytics_data_t analytics = edge_processor.process(sensor_data, fused_data);
    
    // Check alerts
    alerts.check_alerts(sensor_data, fused_data, analytics);
    
    // Send comprehensive telemetry
    send_comprehensive_telemetry(sensor_data, fused_data, analytics);
    
    delay(30000);
}
```

---

## Testing

### Unit Tests
```cpp
void test_sensor_manager() {
    SensorManager sensor_manager;
    assert(sensor_manager.init());
    
    // Add test sensors
    sensor_config_array_t configs = get_test_sensor_configs();
    for (const auto& config : configs) {
        assert(sensor_manager.add_sensor(config));
    }
    
    // Read sensors
    sensor_data_array_t data = sensor_manager.read_all_sensors();
    assert(data.size() > 0);
    
    // Validate data
    for (const auto& sensor_data : data) {
        assert(sensor_data.timestamp > 0);
        assert(!sensor_data.sensor_id.empty());
    }
}

void test_fusion_engine() {
    FusionEngine fusion;
    assert(fusion.init());
    
    // Create test sensor data
    sensor_data_array_t sensor_data = create_test_sensor_data();
    
    // Perform fusion
    fused_data_t fused_data = fusion.process(sensor_data);
    
    // Validate fused data
    assert(fused_data.timestamp > 0);
    assert(fused_data.confidence >= 0.0 && fused_data.confidence <= 1.0);
    assert(!fused_data.algorithm_used.empty());
}

void test_redundancy() {
    SensorManager sensor_manager;
    sensor_manager.init();
    
    // Add redundant sensors
    sensor_config_array_t configs = get_redundant_sensor_configs();
    for (const auto& config : configs) {
        sensor_manager.add_sensor(config);
    }
    
    // Test failover
    assert(sensor_manager.has_redundant_sensor("temp_01"));
    String redundant = sensor_manager.get_redundant_sensor("temp_01");
    assert(redundant == "temp_02");
}
```

---

## Troubleshooting

### Common Issues

#### Sensor Communication Problems
```cpp
void debug_sensor_communication() {
    SensorManager sensor_manager;
    sensor_manager.init();
    
    // Check sensor health
    sensor_health_array_t health = sensor_manager.get_sensor_health();
    
    for (const auto& h : health) {
        if (h.status != "ok") {
            Serial.println("Sensor " + h.sensor_id + " status: " + h.status);
            Serial.println("Error count: " + String(h.error_count));
            Serial.println("Last reading: " + String(h.last_reading));
        }
    }
}
```

#### Data Fusion Issues
```cpp
void debug_fusion_engine() {
    FusionEngine fusion;
    fusion.init();
    
    // Create test data
    sensor_data_array_t test_data = create_test_sensor_data();
    
    // Perform fusion
    fused_data_t result = fusion.process(test_data);
    
    Serial.println("Fusion Results:");
    Serial.println("Temperature: " + String(result.temperature));
    Serial.println("Humidity: " + String(result.humidity));
    Serial.println("Confidence: " + String(result.confidence));
    Serial.println("Algorithm: " + result.algorithm_used);
    
    // Check correlations
    for (const auto& corr : result.correlations) {
        Serial.println("Correlation " + corr.sensor1 + " <-> " + corr.sensor2 + 
                      ": " + String(corr.coefficient));
    }
}
```

---

## Support

For multi-sensor gateway firmware support:
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **Platform Guides**: See `platform/*/` directories
- **Email**: firmware@valtronics.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Multi-Sensor Gateway Firmware v2.0**
