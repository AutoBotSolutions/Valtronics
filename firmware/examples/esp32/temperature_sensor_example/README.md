# ESP32 Temperature Sensor Example

**Complete example implementation for ESP32 temperature sensor**

---

## Overview

This example demonstrates a complete ESP32-based temperature sensor implementation with WiFi connectivity, MQTT communication, OTA updates, and comprehensive error handling.

---

## Features

- **ESP32 Platform**: Optimized for ESP32 with WiFi and Bluetooth
- **DHT22 Sensor**: Digital temperature and humidity sensor
- **WiFi Manager**: Automatic WiFi configuration
- **MQTT Communication**: Real-time telemetry transmission
- **OTA Updates**: Over-the-air firmware updates
- **Power Management**: Deep sleep for battery operation
- **Error Handling**: Comprehensive error recovery

---

## Hardware Requirements

### Components
- **ESP32 DevKit**: ESP32 development board
- **DHT22 Sensor**: Digital temperature and humidity sensor
- **Resistor**: 10kΩ pull-up resistor for DHT22
- **Breadboard**: For prototyping
- **Jumper Wires**: For connections

### Wiring
```
ESP32    DHT22
3.3V ---- VCC
GND  ---- GND
GPIO4 ---- DATA
```

Add 10kΩ pull-up resistor between DATA and 3.3V.

---

## Software Requirements

### PlatformIO Configuration
```ini
[env:esp32_temp_sensor]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200
upload_speed = 921600
lib_deps = 
    PubSubClient
    ArduinoJson
    DHT sensor library
    WiFiManager
    ArduinoOTA
    ESP32WebServer

build_flags = 
    -DCORE_DEBUG_LEVEL=3
    -DCONFIG_ARDUHAL_LOG_COLORS
```

### Dependencies
- **PubSubClient**: MQTT client library
- **ArduinoJson**: JSON processing
- **DHT sensor library**: DHT22 sensor driver
- **WiFiManager**: WiFi configuration portal
- **ArduinoOTA**: OTA update support

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
#include <DHT.h>
#include <ESP32WebServer.h>

// Device configuration
#define DEVICE_ID "VT-ESP32-TEMP-001"
#define DHT_PIN 4
#define DHT_TYPE DHT22
#define MQTT_CLIENT_ID "VT-ESP32-TEMP-001"
#define MQTT_BROKER "mqtt.valtronics.com"
#define MQTT_PORT 1883

// Global objects
DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
ESP32WebServer server(80);
WiFiManager wifiManager;

// Configuration
struct DeviceConfig {
    String device_id = DEVICE_ID;
    String device_name = "ESP32 Temperature Sensor";
    String device_type = "temperature_sensor";
    String location = "Office Room A";
    String mqtt_broker = MQTT_BROKER;
    uint16_t mqtt_port = MQTT_PORT;
    uint32_t telemetry_interval = 30000;  // 30 seconds
    bool enable_ota = true;
    bool enable_deep_sleep = false;
    uint32_t sleep_duration = 60;  // seconds
} config;

// Global state
bool system_ready = false;
uint32_t last_telemetry_time = 0;
uint32_t last_config_check = 0;
float temperature_offset = 0.0;

void setup() {
    Serial.begin(115200);
    Serial.println("\n=== Valtronics ESP32 Temperature Sensor ===");
    Serial.println("Device ID: " + String(DEVICE_ID));
    
    // Initialize DHT sensor
    initialize_sensor();
    
    // Load configuration
    load_configuration();
    
    // Initialize WiFi
    initialize_wifi();
    
    // Initialize MQTT
    initialize_mqtt();
    
    // Initialize web server
    initialize_web_server();
    
    // Initialize OTA
    initialize_ota();
    
    system_ready = true;
    Serial.println("System ready!");
    
    // Send startup message
    send_startup_message();
}

void loop() {
    if (!system_ready) {
        delay(1000);
        return;
    }
    
    // Handle web server
    server.handleClient();
    
    // Handle MQTT
    handle_mqtt();
    
    // Handle OTA
    ArduinoOTA.handle();
    
    // Read sensor data
    handle_sensor_reading();
    
    // Send telemetry
    handle_telemetry();
    
    // Handle configuration updates
    handle_config_updates();
    
    // Check for sleep mode
    if (config.enable_deep_sleep) {
        handle_deep_sleep();
    }
    
    delay(1000);
}

void initialize_sensor() {
    Serial.println("Initializing DHT22 sensor...");
    
    dht.begin();
    
    // Test sensor
    float temp = dht.readTemperature();
    float humidity = dht.readHumidity();
    
    if (isnan(temp) || isnan(humidity)) {
        Serial.println("DHT22 sensor not responding!");
        Serial.println("Check wiring and connections.");
        return;
    }
    
    Serial.println("DHT22 sensor initialized successfully");
    Serial.printf("Initial reading: %.1f°C, %.1f%%\n", temp, humidity);
}

void load_configuration() {
    Serial.println("Loading configuration...");
    
    // Try to load from SPIFFS
    if (SPIFFS.begin(true)) {
        File configFile = SPIFFS.open("/config.json", "r");
        if (configFile) {
            String content = configFile.readString();
            configFile.close();
            
            DynamicJsonDocument doc(1024);
            DeserializationError error = deserializeJson(doc, content);
            
            if (!error) {
                config.mqtt_broker = doc["mqtt_broker"] | config.mqtt_broker;
                config.telemetry_interval = doc["telemetry_interval"] | config.telemetry_interval;
                config.location = doc["location"] | config.location;
                config.enable_ota = doc["enable_ota"] | config.enable_ota;
                config.enable_deep_sleep = doc["enable_deep_sleep"] | config.enable_deep_sleep;
                
                Serial.println("Configuration loaded from file");
            } else {
                Serial.println("Failed to parse configuration file");
            }
        }
    } else {
        Serial.println("Failed to mount SPIFFS");
    }
    
    Serial.printf("MQTT Broker: %s\n", config.mqtt_broker.c_str());
    Serial.printf("Telemetry Interval: %lu ms\n", config.telemetry_interval);
}

void initialize_wifi() {
    Serial.println("Initializing WiFi...");
    
    // Set up WiFiManager
    wifiManager.setDebugOutput(false);
    wifiManager.setAPStaticIPConfig(IPAddress(192, 168, 1, 1),
                                    IPAddress(192, 168, 1, 1),
                                    IPAddress(255, 255, 255, 0));
    
    // Add custom parameters
    WiFiManagerParameter custom_mqtt_broker("mqtt_broker", "MQTT Broker", config.mqtt_broker.c_str(), 40);
    WiFiManagerParameter custom_interval("interval", "Telemetry Interval (ms)", String(config.telemetry_interval).c_str(), 10);
    WiFiManagerParameter custom_location("location", "Location", config.location.c_str(), 30);
    
    wifiManager.addParameter(&custom_mqtt_broker);
    wifiManager.addParameter(&custom_interval);
    wifiManager.addParameter(&custom_location);
    
    // Try to connect to WiFi
    if (!wifiManager.autoConnect("Valtronics-TempSensor")) {
        Serial.println("Failed to connect to WiFi");
        delay(3000);
        ESP.restart();
    }
    
    // Update configuration with WiFiManager parameters
    config.mqtt_broker = custom_mqtt_broker.getValue();
    config.telemetry_interval = atoi(custom_interval.getValue());
    config.location = custom_location.getValue();
    
    Serial.println("WiFi connected successfully!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("RSSI: ");
    Serial.println(WiFi.RSSI());
}

void initialize_mqtt() {
    Serial.println("Initializing MQTT...");
    
    mqttClient.setServer(config.mqtt_broker.c_str(), config.mqtt_port);
    mqttClient.setCallback(mqtt_callback);
    
    connect_mqtt();
}

void connect_mqtt() {
    Serial.printf("Connecting to MQTT broker: %s:%d\n", config.mqtt_broker.c_str(), config.mqtt_port);
    
    String client_id = MQTT_CLIENT_ID;
    client_id += "-";
    client_id += String(random(0xffff), HEX);
    
    if (mqttClient.connect(client_id.c_str())) {
        Serial.println("MQTT connected successfully!");
        
        // Subscribe to topics
        mqttClient.subscribe("valtronics/devices/" + String(DEVICE_ID) + "/commands");
        mqttClient.subscribe("valtronics/devices/" + String(DEVICE_ID) + "/config");
        
        // Send connection message
        send_connection_message();
    } else {
        Serial.printf("MQTT connection failed, state: %d\n", mqttClient.state());
        Serial.println("Will retry in 5 seconds...");
    }
}

void initialize_web_server() {
    Serial.println("Initializing web server...");
    
    // Main page
    server.on("/", HTTP_GET, []() {
        String html = generate_web_page();
        server.send(200, "text/html", html);
    });
    
    // API endpoints
    server.on("/api/status", HTTP_GET, handle_status_api);
    server.on("/api/config", HTTP_GET, handle_config_api);
    server.on("/api/config", HTTP_POST, handle_update_config_api);
    server.on("/api/sensor", HTTP_GET, handle_sensor_api);
    server.on("/api/reboot", HTTP_POST, handle_reboot_api);
    
    server.begin();
    Serial.println("Web server started");
    Serial.print("URL: http://");
    Serial.println(WiFi.localIP());
}

void initialize_ota() {
    if (!config.enable_ota) {
        Serial.println("OTA updates disabled");
        return;
    }
    
    Serial.println("Initializing OTA...");
    
    ArduinoOTA.setHostname(DEVICE_ID);
    ArduinoOTA.setPassword("valtronics");
    
    ArduinoOTA.onStart([]() {
        String type = (ArduinoOTA.getCommand() == U_FLASH) ? "sketch" : "filesystem";
        Serial.println("Start updating " + type);
    });
    
    ArduinoOTA.onEnd([]() {
        Serial.println("\nEnd");
    });
    
    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
    });
    
    ArduinoOTA.onError([](ota_error_t error) {
        Serial.printf("Error[%u]: ", error);
        if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
        else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
        else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
        else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
        else if (error == OTA_END_ERROR) Serial.println("End Failed");
    });
    
    ArduinoOTA.begin();
    Serial.println("OTA ready");
}

void handle_mqtt() {
    if (!mqttClient.connected()) {
        static uint32_t last_mqtt_attempt = 0;
        uint32_t current_time = millis();
        
        if (current_time - last_mqtt_attempt > 5000) {  // Retry every 5 seconds
            last_mqtt_attempt = current_time;
            connect_mqtt();
        }
    }
    
    mqttClient.loop();
}

void handle_sensor_reading() {
    static uint32_t last_sensor_read = 0;
    uint32_t current_time = millis();
    
    // Read sensor every 2 seconds
    if (current_time - last_sensor_read > 2000) {
        last_sensor_read = current_time;
        
        float temperature = dht.readTemperature();
        float humidity = dht.readHumidity();
        
        if (isnan(temperature) || isnan(humidity)) {
            Serial.println("Failed to read from DHT sensor!");
            return;
        }
        
        // Apply temperature offset
        temperature += temperature_offset;
        
        // Print reading
        Serial.printf("Sensor reading: %.1f°C, %.1f%%\n", temperature, humidity);
        
        // Check for alert conditions
        check_alerts(temperature, humidity);
    }
}

void handle_telemetry() {
    uint32_t current_time = millis();
    
    if (current_time - last_telemetry_time >= config.telemetry_interval) {
        last_telemetry_time = current_time;
        
        float temperature = dht.readTemperature();
        float humidity = dht.readHumidity();
        
        if (isnan(temperature) || isnan(humidity)) {
            Serial.println("Failed to read sensor data for telemetry");
            return;
        }
        
        // Apply temperature offset
        temperature += temperature_offset;
        
        // Create telemetry payload
        DynamicJsonDocument doc(512);
        
        doc["device_id"] = config.device_id;
        doc["device_name"] = config.device_name;
        doc["device_type"] = config.device_type;
        doc["location"] = config.location;
        doc["timestamp"] = current_time;
        
        // Sensor data
        JsonObject sensors = doc.createNestedObject("sensors");
        sensors["temperature"] = round(temperature * 10) / 10.0;  // Round to 1 decimal
        sensors["humidity"] = round(humidity * 10) / 10.0;
        sensors["temperature_offset"] = temperature_offset;
        
        // System data
        JsonObject system = doc.createNestedObject("system");
        system["free_heap"] = ESP.getFreeHeap();
        system["wifi_rssi"] = WiFi.RSSI();
        system["wifi_ssid"] = WiFi.SSID();
        system["uptime"] = current_time;
        system["mqtt_connected"] = mqttClient.connected();
        system["sensor_status"] = "ok";
        
        // Additional info
        JsonObject info = doc.createNestedObject("info");
        info["firmware_version"] = "1.0.0";
        info["hardware"] = "ESP32";
        info["sensor_type"] = "DHT22";
        info["telemetry_interval"] = config.telemetry_interval;
        
        // Serialize and send
        String payload;
        serializeJson(doc, payload);
        
        String topic = "valtronics/telemetry/" + config.device_id;
        
        if (mqttClient.publish(topic.c_str(), payload.c_str())) {
            Serial.println("Telemetry sent successfully");
        } else {
            Serial.println("Failed to send telemetry");
        }
    }
}

void handle_config_updates() {
    static uint32_t last_config_check = 0;
    uint32_t current_time = millis();
    
    // Check for config updates every hour
    if (current_time - last_config_check > 3600000) {
        last_config_check = current_time;
        
        // This would typically fetch config from a server
        // For now, we'll just log
        Serial.println("Checking for configuration updates...");
    }
}

void handle_deep_sleep() {
    static uint32_t last_sleep_attempt = 0;
    uint32_t current_time = millis();
    
    // Enter deep sleep after sending telemetry
    if (current_time - last_telemetry_time > 10000) {  // 10 seconds after telemetry
        if (current_time - last_sleep_attempt > 60000) {  // Don't sleep too frequently
            last_sleep_attempt = current_time;
            
            Serial.printf("Entering deep sleep for %lu seconds...\n", config.sleep_duration);
            
            // Configure wake-up source
            esp_sleep_enable_timer_wakeup(config.sleep_duration * 1000000);
            
            // Go to sleep
            esp_deep_sleep_start();
        }
    }
}

void check_alerts(float temperature, float humidity) {
    static bool high_temp_alert = false;
    static bool low_temp_alert = false;
    static bool high_humidity_alert = false;
    static bool low_humidity_alert = false;
    
    // Temperature alerts
    if (temperature > 35.0 && !high_temp_alert) {
        high_temp_alert = true;
        send_alert("temperature_high", temperature, "Temperature too high");
    } else if (temperature <= 35.0) {
        high_temp_alert = false;
    }
    
    if (temperature < 10.0 && !low_temp_alert) {
        low_temp_alert = true;
        send_alert("temperature_low", temperature, "Temperature too low");
    } else if (temperature >= 10.0) {
        low_temp_alert = false;
    }
    
    // Humidity alerts
    if (humidity > 70.0 && !high_humidity_alert) {
        high_humidity_alert = true;
        send_alert("humidity_high", humidity, "Humidity too high");
    } else if (humidity <= 70.0) {
        high_humidity_alert = false;
    }
    
    if (humidity < 30.0 && !low_humidity_alert) {
        low_humidity_alert = true;
        send_alert("humidity_low", humidity, "Humidity too low");
    } else if (humidity >= 30.0) {
        low_humidity_alert = false;
    }
}

void send_alert(const String& alert_type, float value, const String& message) {
    DynamicJsonDocument doc(256);
    
    doc["device_id"] = config.device_id;
    doc["alert_type"] = alert_type;
    doc["value"] = value;
    doc["message"] = message;
    doc["timestamp"] = millis();
    doc["severity"] = "warning";
    
    String payload;
    serializeJson(doc, payload);
    
    String topic = "valtronics/alerts/" + config.device_id;
    
    if (mqttClient.publish(topic.c_str(), payload.c_str())) {
        Serial.println("Alert sent: " + alert_type);
    }
}

void mqtt_callback(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.printf("MQTT message received [%s]: %s\n", topic, message.c_str());
    
    // Handle commands
    if (String(topic) == "valtronics/devices/" + String(DEVICE_ID) + "/commands") {
        handle_command(message);
    }
    
    // Handle configuration
    if (String(topic) == "valtronics/devices/" + String(DEVICE_ID) + "/config") {
        handle_config_update(message);
    }
}

void handle_command(const String& command) {
    DynamicJsonDocument doc(256);
    DeserializationError error = deserializeJson(doc, command);
    
    if (error) {
        Serial.println("Invalid command JSON");
        return;
    }
    
    String cmd = doc["command"];
    
    if (cmd == "reboot") {
        Serial.println("Reboot command received");
        send_command_response("reboot", "Rebooting device");
        delay(1000);
        ESP.restart();
    } else if (cmd == "sleep") {
        uint32_t duration = doc["duration"] | 60;
        Serial.printf("Sleep command received: %lu seconds\n", duration);
        send_command_response("sleep", "Entering sleep mode");
        
        esp_sleep_enable_timer_wakeup(duration * 1000000);
        esp_deep_sleep_start();
    } else if (cmd == "calibrate") {
        float offset = doc["offset"] | 0.0;
        Serial.printf("Calibration command received: %.1f\n", offset);
        temperature_offset = offset;
        send_command_response("calibrate", "Temperature offset updated");
    } else if (cmd == "status") {
        send_status_report();
    } else {
        Serial.println("Unknown command: " + cmd);
    }
}

void handle_config_update(const String& config_update) {
    DynamicJsonDocument doc(256);
    DeserializationError error = deserializeJson(doc, config_update);
    
    if (error) {
        Serial.println("Invalid config JSON");
        return;
    }
    
    // Update configuration
    if (doc.containsKey("telemetry_interval")) {
        config.telemetry_interval = doc["telemetry_interval"];
        Serial.printf("Telemetry interval updated: %lu ms\n", config.telemetry_interval);
    }
    
    if (doc.containsKey("mqtt_broker")) {
        config.mqtt_broker = doc["mqtt_broker"].as<String>();
        Serial.printf("MQTT broker updated: %s\n", config.mqtt_broker.c_str());
        // Reconnect MQTT with new broker
        mqttClient.disconnect();
        connect_mqtt();
    }
    
    if (doc.containsKey("location")) {
        config.location = doc["location"].as<String>();
        Serial.printf("Location updated: %s\n", config.location.c_str());
    }
    
    // Save configuration
    save_configuration();
    
    send_command_response("config", "Configuration updated");
}

void send_command_response(const String& command, const String& message) {
    DynamicJsonDocument doc(256);
    
    doc["device_id"] = config.device_id;
    doc["command"] = command;
    doc["response"] = message;
    doc["timestamp"] = millis();
    
    String payload;
    serializeJson(doc, payload);
    
    String topic = "valtronics/devices/" + String(DEVICE_ID) + "/responses";
    mqttClient.publish(topic.c_str(), payload.c_str());
}

void send_status_report() {
    DynamicJsonDocument doc(512);
    
    doc["device_id"] = config.device_id;
    doc["device_name"] = config.device_name;
    doc["device_type"] = config.device_type;
    doc["location"] = config.location;
    doc["firmware_version"] = "1.0.0";
    doc["uptime"] = millis();
    doc["free_heap"] = ESP.getFreeHeap();
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["wifi_ssid"] = WiFi.SSID();
    doc["mqtt_connected"] = mqttClient.connected();
    doc["ota_enabled"] = config.enable_ota;
    doc["deep_sleep_enabled"] = config.enable_deep_sleep;
    doc["telemetry_interval"] = config.telemetry_interval;
    doc["temperature_offset"] = temperature_offset;
    
    // Sensor status
    float temp = dht.readTemperature();
    float humidity = dht.readHumidity();
    doc["sensor_status"] = (!isnan(temp) && !isnan(humidity)) ? "ok" : "error";
    
    String payload;
    serializeJson(doc, payload);
    
    String topic = "valtronics/devices/" + String(DEVICE_ID) + "/status";
    mqttClient.publish(topic.c_str(), payload.c_str());
}

void send_startup_message() {
    DynamicJsonDocument doc(256);
    
    doc["device_id"] = config.device_id;
    doc["event"] = "startup";
    doc["message"] = "Device started successfully";
    doc["firmware_version"] = "1.0.0";
    doc["timestamp"] = millis();
    
    String payload;
    serializeJson(doc, payload);
    
    String topic = "valtronics/devices/" + String(DEVICE_ID) + "/events";
    mqttClient.publish(topic.c_str(), payload.c_str());
}

void send_connection_message() {
    DynamicJsonDocument doc(256);
    
    doc["device_id"] = config.device_id;
    doc["event"] = "mqtt_connected";
    doc["message"] = "MQTT connection established";
    doc["timestamp"] = millis();
    
    String payload;
    serializeJson(doc, payload);
    
    String topic = "valtronics/devices/" + String(DEVICE_ID) + "/events";
    mqttClient.publish(topic.c_str(), payload.c_str());
}

void save_configuration() {
    if (!SPIFFS.begin(true)) {
        Serial.println("Failed to mount SPIFFS for saving config");
        return;
    }
    
    DynamicJsonDocument doc(256);
    doc["mqtt_broker"] = config.mqtt_broker;
    doc["telemetry_interval"] = config.telemetry_interval;
    doc["location"] = config.location;
    doc["enable_ota"] = config.enable_ota;
    doc["enable_deep_sleep"] = config.enable_deep_sleep;
    
    String content;
    serializeJson(doc, content);
    
    File configFile = SPIFFS.open("/config.json", "w");
    if (configFile) {
        configFile.print(content);
        configFile.close();
        Serial.println("Configuration saved to SPIFFS");
    } else {
        Serial.println("Failed to save configuration");
    }
}

String generate_web_page() {
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    
    String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>Valtronics Temperature Sensor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .status { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .status-item { background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }
        .status-value { font-size: 24px; font-weight: bold; color: #007bff; }
        .status-label { color: #666; margin-top: 5px; }
        .button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .button:hover { background: #0056b3; }
        .button.danger { background: #dc3545; }
        .button.danger:hover { background: #c82333; }
        .config-form { margin: 20px 0; }
        .form-group { margin: 10px 0; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .alert { padding: 15px; margin: 10px 0; border-radius: 5px; }
        .alert.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌡️ Valtronics Temperature Sensor</h1>
        
        <div class="status">
            <div class="status-item">
                <div class="status-value">)" + String(temperature, 1) + R"(°C</div>
                <div class="status-label">Temperature</div>
            </div>
            <div class="status-item">
                <div class="status-value">)" + String(humidity, 1) + R"(%</div>
                <div class="status-label">Humidity</div>
            </div>
            <div class="status-item">
                <div class="status-value">)" + String(WiFi.RSSI()) + R"( dBm</div>
                <div class="status-label">WiFi RSSI</div>
            </div>
            <div class="status-item">
                <div class="status-value">)" + String(ESP.getFreeHeap()) + R"( bytes</div>
                <div class="status-label">Free Memory</div>
            </div>
        </div>
        
        <h2>Device Information</h2>
        <p><strong>ID:</strong> )" + config.device_id + R"(</p>
        <p><strong>Type:</strong> )" + config.device_type + R"(</p>
        <p><strong>Location:</strong> )" + config.location + R"(</p>
        <p><strong>Firmware:</strong> 1.0.0</p>
        <p><strong>Uptime:</strong> )" + String(millis() / 1000) + R"( seconds</p>
        
        <h2>Actions</h2>
        <button class="button" onclick="reboot()">Reboot Device</button>
        <button class="button" onclick="getStatus()">Get Status</button>
        <button class="button" onclick="getSensorData()">Get Sensor Data</button>)";
        
        if (config.enable_ota) {
            html += R"(<button class="button">Check for Updates</button>)";
        }
        
        html += R"(
        
        <h2>Configuration</h2>
        <form class="config-form" onsubmit="updateConfig(event)">
            <div class="form-group">
                <label for="mqtt_broker">MQTT Broker:</label>
                <input type="text" id="mqtt_broker" value=")" + config.mqtt_broker + R"(">
            </div>
            <div class="form-group">
                <label for="telemetry_interval">Telemetry Interval (ms):</label>
                <input type="number" id="telemetry_interval" value=")" + config.telemetry_interval + R"(">
            </div>
            <div class="form-group">
                <label for="location">Location:</label>
                <input type="text" id="location" value=")" + config.location + R"(">
            </div>
            <button type="submit" class="button">Update Configuration</button>
        </form>
        
        <div id="messages"></div>
    </div>
    
    <script>
        function showMessage(message, type = 'success') {
            const messagesDiv = document.getElementById('messages');
            const alert = document.createElement('div');
            alert.className = 'alert ' + type;
            alert.textContent = message;
            messagesDiv.appendChild(alert);
            setTimeout(() => alert.remove(), 5000);
        }
        
        async function reboot() {
            if (confirm('Are you sure you want to reboot the device?')) {
                try {
                    const response = await fetch('/api/reboot', { method: 'POST' });
                    if (response.ok) {
                        showMessage('Reboot command sent. Device will restart shortly.');
                    } else {
                        showMessage('Failed to send reboot command.', 'error');
                    }
                } catch (error) {
                    showMessage('Error: ' + error.message, 'error');
                }
            }
        }
        
        async function getStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                console.log('Status:', data);
                showMessage('Status data received. Check console for details.');
            } catch (error) {
                showMessage('Error getting status: ' + error.message, 'error');
            }
        }
        
        async function getSensorData() {
            try {
                const response = await fetch('/api/sensor');
                const data = await response.json();
                console.log('Sensor data:', data);
                showMessage('Sensor data received. Check console for details.');
            } catch (error) {
                showMessage('Error getting sensor data: ' + error.message, 'error');
            }
        }
        
        async function updateConfig(event) {
            event.preventDefault();
            
            const config = {
                mqtt_broker: document.getElementById('mqtt_broker').value,
                telemetry_interval: parseInt(document.getElementById('telemetry_interval').value),
                location: document.getElementById('location').value
            };
            
            try {
                const response = await fetch('/api/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(config)
                });
                
                if (response.ok) {
                    showMessage('Configuration updated successfully!');
                } else {
                    showMessage('Failed to update configuration.', 'error');
                }
            } catch (error) {
                showMessage('Error updating config: ' + error.message, 'error');
            }
        }
        
        // Auto-refresh sensor data every 10 seconds
        setInterval(() => {
            location.reload();
        }, 10000);
    </script>
</body>
</html>)";
    
    return html;
}

// Web API handlers
void handle_status_api() {
    DynamicJsonDocument doc(512);
    
    doc["device_id"] = config.device_id;
    doc["device_name"] = config.device_name;
    doc["device_type"] = config.device_type;
    doc["location"] = config.location;
    doc["firmware_version"] = "1.0.0";
    doc["uptime"] = millis();
    doc["free_heap"] = ESP.getFreeHeap();
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["wifi_ssid"] = WiFi.SSID();
    doc["mqtt_connected"] = mqttClient.connected();
    doc["ota_enabled"] = config.enable_ota;
    doc["deep_sleep_enabled"] = config.enable_deep_sleep;
    doc["telemetry_interval"] = config.telemetry_interval;
    doc["temperature_offset"] = temperature_offset;
    
    String response;
    serializeJson(doc, response);
    
    server.send(200, "application/json", response);
}

void handle_config_api() {
    DynamicJsonDocument doc(256);
    
    doc["mqtt_broker"] = config.mqtt_broker;
    doc["telemetry_interval"] = config.telemetry_interval;
    doc["location"] = config.location;
    doc["enable_ota"] = config.enable_ota;
    doc["enable_deep_sleep"] = config.enable_deep_sleep;
    doc["temperature_offset"] = temperature_offset;
    
    String response;
    serializeJson(doc, response);
    
    server.send(200, "application/json", response);
}

void handle_update_config_api() {
    String body = server.arg("plain");
    
    DynamicJsonDocument doc(256);
    DeserializationError error = deserializeJson(doc, body);
    
    if (error) {
        server.send(400, "application/json", "{\"error\":\"Invalid JSON\"}");
        return;
    }
    
    // Update configuration
    if (doc.containsKey("mqtt_broker")) {
        config.mqtt_broker = doc["mqtt_broker"].as<String>();
    }
    
    if (doc.containsKey("telemetry_interval")) {
        config.telemetry_interval = doc["telemetry_interval"];
    }
    
    if (doc.containsKey("location")) {
        config.location = doc["location"].as<String>();
    }
    
    // Save configuration
    save_configuration();
    
    server.send(200, "application/json", "{\"status\":\"success\"}");
}

void handle_sensor_api() {
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    
    DynamicJsonDocument doc(256);
    
    doc["temperature"] = isnan(temperature) ? nullptr : temperature;
    doc["humidity"] = isnan(humidity) ? nullptr : humidity;
    doc["timestamp"] = millis();
    doc["sensor_status"] = (!isnan(temperature) && !isnan(humidity)) ? "ok" : "error";
    
    String response;
    serializeJson(doc, response);
    
    server.send(200, "application/json", response);
}

void handle_reboot_api() {
    server.send(200, "application/json", "{\"status\":\"rebooting\"}");
    
    delay(1000);
    ESP.restart();
}
```

---

## Usage

### 1. Hardware Setup
1. Connect DHT22 sensor to ESP32 as shown in the wiring diagram
2. Add 10kΩ pull-up resistor
3. Power up the ESP32

### 2. Software Setup
1. Open PlatformIO IDE
2. Create new project with ESP32 platform
3. Copy the code to `src/main.cpp`
4. Configure `platformio.ini` as shown
5. Build and upload

### 3. Configuration
1. Connect to "Valtronics-TempSensor" WiFi network
2. Open browser to 192.168.1.1
3. Configure MQTT broker and other settings
4. Save configuration

### 4. Operation
- Device will automatically connect to WiFi and MQTT
- Sensor readings are sent every 30 seconds
- Access web interface at device IP address
- Monitor MQTT topics for real-time data

---

## MQTT Topics

### Telemetry
- `valtronics/telemetry/VT-ESP32-TEMP-001` - Sensor readings

### Commands
- `valtronics/devices/VT-ESP32-TEMP-001/commands` - Device commands

### Configuration
- `valtronics/devices/VT-ESP32-TEMP-001/config` - Configuration updates

### Events
- `valtronics/devices/VT-ESP32-TEMP-001/events` - Device events

### Alerts
- `valtronics/alerts/VT-ESP32-TEMP-001` - Alert notifications

---

## API Endpoints

### Web API
- `GET /` - Main web interface
- `GET /api/status` - Device status
- `GET /api/config` - Current configuration
- `POST /api/config` - Update configuration
- `GET /api/sensor` - Sensor data
- `POST /api/reboot` - Reboot device

---

## Troubleshooting

### Common Issues

#### DHT22 Not Responding
- Check wiring connections
- Verify pull-up resistor
- Ensure 3.3V power supply
- Check for loose connections

#### WiFi Connection Issues
- Check WiFi credentials
- Verify network availability
- Try resetting WiFi configuration
- Check signal strength

#### MQTT Connection Issues
- Verify broker address and port
- Check network connectivity
- Verify MQTT credentials
- Check broker status

#### Web Interface Not Accessible
- Verify WiFi connection
- Check device IP address
- Try refreshing browser
- Check for firewall issues

---

## Support

For ESP32 temperature sensor support:
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **Platform Guides**: See `platform/esp32/` directory
- **Email**: firmware@valtronics.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**ESP32 Temperature Sensor Example v1.0**
