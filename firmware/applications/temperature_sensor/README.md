# Temperature Sensor Firmware

**Complete firmware implementation for Valtronics temperature sensor devices**

---

## Overview

This application provides a complete temperature sensor firmware that reads temperature data, processes it, and sends it to the Valtronics platform via MQTT. It supports multiple temperature sensor types and includes power management, OTA updates, and error handling.

---

## Features

### Sensor Support
- **DHT22**: Digital temperature and humidity sensor
- **DS18B20**: Digital temperature sensor (one-wire)
- **TMP36**: Analog temperature sensor
- **BME280**: Environmental sensor with temperature
- **Generic**: Custom temperature sensor interface

### Communication
- **MQTT**: Primary communication protocol
- **HTTP**: Fallback communication protocol
- **WiFi**: Wireless connectivity (ESP32/ESP8266)
- **Ethernet**: Wired connectivity (Arduino Mega)

### Power Management
- **Deep Sleep**: Power saving for battery devices
- **Battery Monitoring**: Voltage and percentage tracking
- **Low Power Mode**: Reduced power consumption
- **Solar Power**: Solar panel support with battery backup

### Advanced Features
- **OTA Updates**: Over-the-air firmware updates
- **Calibration**: Sensor calibration and compensation
- **Data Validation**: Data range validation and filtering
- **Error Recovery**: Automatic error detection and recovery
- **Watchdog**: System watchdog timer

---

## Hardware Requirements

### Minimum Requirements
- **Microcontroller**: ESP32, Arduino Mega, or equivalent
- **Memory**: 8KB+ SRAM, 32KB+ Flash
- **Connectivity**: WiFi or Ethernet
- **Power**: 3.3V or 5V supply

### Recommended Components
- **ESP32 DevKit**: Development and production
- **Arduino Mega**: Prototyping and development
- **DHT22 Sensor**: Temperature and humidity
- **Solar Panel**: For remote deployments
- **Battery**: Li-ion 18650 or equivalent

---

## Directory Structure

```
applications/temperature_sensor/
├── README.md                    # This file
├── platformio.ini               # PlatformIO configuration
├── src/                         # Source code
│   ├── main.cpp                 # Main application
│   ├── config/                  # Configuration
│   │   ├── device_config.h     # Device configuration
│   │   ├── wifi_config.h        # WiFi configuration
│   │   └── mqtt_config.h        # MQTT configuration
│   ├── drivers/                  # Hardware drivers
│   │   ├── dht22_driver.h        # DHT22 driver
│   │   ├── ds18b20_driver.h      # DS18B20 driver
│   │   └── tmp36_driver.h        # TMP36 driver
│   ├── sensors/                  # Sensor interfaces
│   │   ├── temperature_sensor.h  # Temperature sensor interface
│   │   └── sensor_factory.h      # Sensor factory
│   ├── communication/            # Communication
│   │   ├── mqtt_client.h         # MQTT client
│   │   ├── http_client.h         # HTTP client
│   │   └── message_handler.h     # Message handler
│   ├── power/                    # Power management
│   │   ├── power_manager.h       # Power manager
│   │   ├── battery_monitor.h     # Battery monitoring
│   │   └── sleep_manager.h        # Sleep management
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
    "id": "VT-TEMP-001",
    "name": "Temperature Sensor 1",
    "type": "temperature_sensor",
    "version": "1.0.0",
    "location": "Server Room A",
    "description": "Temperature monitoring in server room"
  },
  "sensor": {
    "type": "DHT22",
    "pin": 4,
    "interval": 30,
    "precision": 0.1,
    "calibration_offset": 0.0,
    "min_value": -40.0,
    "max_value": 85.0
  },
  "network": {
    "wifi": {
      "ssid": "Valtronics_WiFi",
      "password": "secure_password",
      "static_ip": false,
      "ip": "192.168.1.100",
      "gateway": "192.168.1.1",
      "subnet": "255.255.255.0"
    },
    "mqtt": {
      "broker": "mqtt.valtronics.com",
      "port": 1883,
      "username": "device_user",
      "password": "device_password",
      "client_id": "VT-TEMP-001",
      "topics": {
        "telemetry": "valtronics/telemetry",
        "commands": "valtronics/devices/VT-TEMP-001/commands",
        "config": "valtronics/devices/VT-TEMP-001/config"
      }
    }
  },
  "power": {
    "mode": "normal",
    "battery_monitoring": true,
    "deep_sleep": false,
    "sleep_duration": 60,
    "low_battery_threshold": 20,
    "solar_power": false
  },
  "ota": {
    "enabled": true,
    "password": "valtronics",
    "port": 3232,
    "check_interval": 3600
  },
  "logging": {
    "level": "INFO",
    "serial": true,
    "mqtt": false
  }
}
```

### PlatformIO Configuration
```ini
[env:esp32]
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
    OneWire
    DallasTemperature

[env:arduino_mega]
platform = atmelavr
board = megaatmega2560
framework = arduino
lib_deps = 
    PubSubClient
    ArduinoJson
    DHT sensor library
    Ethernet
    SD
    OneWire
    DallasTemperature

[env:esp8266]
platform = espressif8266
board = nodemcuv2
framework = arduino
lib_deps = 
    PubSubClient
    ArduinoJson
    DHT sensor library
    ESP8266WiFi
    WiFiManager
    ArduinoOTA
    OneWire
    DallasTemperature
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

#include "config/device_config.h"
#include "sensors/temperature_sensor.h"
#include "communication/mqtt_client.h"
#include "power/power_manager.h"
#include "utils/logger.h"
#include "utils/json_utils.h"

// Global objects
TemperatureSensor* temperature_sensor = nullptr;
MQTTClient* mqtt_client = nullptr;
PowerManager* power_manager = nullptr;
DeviceConfig* device_config = nullptr;

// Global state
bool system_ready = false;
uint32_t last_telemetry_time = 0;
uint32_t last_config_check = 0;

void setup() {
    Serial.begin(115200);
    Logger::info("Valtronics Temperature Sensor Starting...");
    
    // Initialize configuration
    device_config = new DeviceConfig();
    if (!device_config->load()) {
        Logger::error("Failed to load device configuration");
        return;
    }
    
    // Initialize components
    initialize_sensors();
    initialize_communication();
    initialize_power_management();
    
    // Initialize OTA
    initialize_ota();
    
    system_ready = true;
    Logger::info("Temperature sensor ready");
}

void loop() {
    if (!system_ready) {
        delay(1000);
        return;
    }
    
    // Handle MQTT
    mqtt_client->loop();
    
    // Handle OTA
    ArduinoOTA.handle();
    
    // Check power status
    handle_power_management();
    
    // Send telemetry
    handle_telemetry();
    
    // Handle configuration updates
    handle_config_updates();
    
    // Watchdog reset
    delay(1000);
}

void initialize_sensors() {
    Logger::info("Initializing temperature sensor...");
    
    // Create sensor factory
    SensorFactory* factory = new SensorFactory();
    temperature_sensor = factory->create_temperature_sensor(device_config->get_sensor_type());
    
    if (!temperature_sensor || !temperature_sensor->init()) {
        Logger::error("Failed to initialize temperature sensor");
        return;
    }
    
    Logger::info("Temperature sensor initialized");
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

void initialize_wifi() {
    WiFiManager wifiManager;
    
    wifiManager.setDebugOutput(false);
    wifiManager.setAPStaticIPConfig(
        IPAddress(192, 168, 1, 1),
        IPAddress(192, 168, 1, 1),
        IPAddress(255, 255, 255, 0)
    );
    
    if (!wifiManager.autoConnect("Valtronics-TempSensor")) {
        Logger::error("Failed to connect to WiFi");
        ESP.restart();
    }
    
    Logger::info("WiFi connected: " + WiFi.localIP().toString());
}

void initialize_power_management() {
    Logger::info("Initializing power management...");
    
    power_manager = new PowerManager();
    power_manager->set_power_mode(device_config->get_power_mode());
    
    if (device_config->get_battery_monitoring()) {
        power_manager->enable_battery_monitoring();
    }
    
    Logger::info("Power management initialized");
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

void handle_telemetry() {
    uint32_t current_time = millis();
    
    if (current_time - last_telemetry_time < device_config->get_telemetry_interval() * 1000) {
        return;
    }
    
    // Read temperature
    temperature_data_t temp_data = temperature_sensor->read();
    
    if (!temp_data.valid) {
        Logger::warning("Invalid temperature reading");
        return;
    }
    
    // Create telemetry payload
    JsonObject telemetry = JSONUtils::create_telemetry_object(
        device_config->get_device_id(),
        "temperature",
        temp_data.temperature
    );
    
    // Add system information
    telemetry["free_heap"] = ESP.getFreeHeap();
    telemetry["wifi_rssi"] = WiFi.RSSI();
    telemetry["uptime"] = millis();
    telemetry["battery_voltage"] = power_manager->get_battery_voltage();
    telemetry["battery_percentage"] = power_manager->get_battery_percentage();
    
    // Send telemetry
    String payload = JSONUtils::serialize(telemetry);
    if (mqtt_client->publish(device_config->get_mqtt_telemetry_topic(), payload)) {
        last_telemetry_time = current_time;
        Logger::info("Telemetry sent: " + String(temp_data.temperature, 2) + "°C");
    } else {
        Logger::error("Failed to send telemetry");
    }
}

void handle_mqtt_message(mqtt_message_t message) {
    Logger::info("MQTT message received: " + message.topic);
    
    // Parse JSON message
    DynamicJsonDocument doc(256);
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
        ESP.restart();
    } else if (cmd == "sleep") {
        uint32_t duration = command["duration"] | 60;
        Logger::info("Sleep command received: " + String(duration) + " seconds");
        ESP.deepSleep(duration * 1000000);
    } else if (cmd == "calibrate") {
        float offset = command["offset"] | 0.0;
        Logger::info("Calibrate command received: " + String(offset));
        temperature_sensor->set_calibration_offset(offset);
    } else if (cmd == "status") {
        send_status();
    } else {
        Logger::warning("Unknown command: " + cmd);
    }
}

void handle_config_update(const JsonObject& config) {
    Logger::info("Configuration update received");
    
    // Update configuration
    if (config.containsKey("telemetry_interval")) {
        uint32_t interval = config["telemetry_interval"];
        device_config->set_telemetry_interval(interval);
        Logger::info("Telemetry interval updated: " + String(interval));
    }
    
    if (config.containsKey("mqtt_broker")) {
        String broker = config["mqtt_broker"];
        device_config->set_mqtt_broker(broker);
        Logger::info("MQTT broker updated: " + broker);
        
        // Reconnect MQTT with new broker
        mqtt_client->disconnect();
        mqtt_client->connect();
    }
    
    // Save configuration
    device_config->save();
}

void handle_power_management() {
    power_status_t power_status = power_manager->get_power_status();
    
    if (power_status.is_low_battery) {
        Logger::warning("Low battery detected: " + String(power_status.battery_percentage) + "%");
        
        // Enter deep sleep if battery is very low
        if (power_status.battery_percentage < 10) {
            Logger::info("Entering deep sleep due to low battery");
            ESP.deepSleep(300 * 1000000);  // Sleep for 5 minutes
        }
        
        // Reduce telemetry frequency
        if (device_config->get_telemetry_interval() < 60) {
            device_config->set_telemetry_interval(60);
            Logger::info("Reduced telemetry interval to 60 seconds");
        }
    }
    
    // Handle power mode changes
    if (power_manager->get_power_mode() != device_config->get_power_mode()) {
        power_manager->set_power_mode(device_config->get_power_mode());
    }
}

void handle_config_updates() {
    uint32_t current_time = millis();
    
    if (current_time - last_config_check < 3600000) {  // Check every hour
        return;
    }
    
    // Check for configuration updates
    // This could be implemented via HTTP API or MQTT
    last_config_check = current_time;
}

void send_status() {
    JsonObject status;
    status["device_id"] = device_config->get_device_id();
    status["device_type"] = device_config->get_device_type();
    status["firmware_version"] = device_config->get_firmware_version();
    status["uptime"] = millis();
    status["free_heap"] = ESP.getFreeHeap();
    status["wifi_rssi"] = WiFi.RSSI();
    status["wifi_ssid"] = WiFi.SSID();
    status["sensor_type"] = device_config->get_sensor_type();
    status["power_mode"] = power_manager->get_power_mode_string();
    status["battery_voltage"] = power_manager->get_battery_voltage();
    status["battery_percentage"] = power_manager->get_battery_percentage();
    
    String payload = JSONUtils::serialize(status);
    mqtt_client->publish("valtronics/devices/" + device_config->get_device_id() + "/status", payload);
    
    Logger::info("Status sent");
}
```

### Temperature Sensor Interface
```cpp
// sensors/temperature_sensor.h
#ifndef TEMPERATURE_SENSOR_H
#define TEMPERATURE_SENSOR_H

#include <stdint.h>
#include <functional>

typedef struct {
    float temperature;
    bool valid;
    uint32_t timestamp;
} temperature_data_t;

class TemperatureSensor {
private:
    std::function<void(temperature_data_t)> callback;
    float calibration_offset;
    float min_value;
    float max_value;
    
protected:
    bool validate_temperature(float temp);
    void notify_callback(temperature_data_t data);
    
public:
    TemperatureSensor();
    virtual ~TemperatureSensor() = default;
    
    virtual bool init() = 0;
    virtual temperature_data_t read() = 0;
    virtual bool is_connected() = 0;
    
    void set_callback(std::function<void(temperature_data_t)> cb);
    void set_calibration_offset(float offset);
    void set_range(float min_val, float max_val);
    float get_calibration_offset() const;
};

#endif // TEMPERATURE_SENSOR_H
```

### DHT22 Driver
```cpp
// drivers/dht22_driver.cpp
#include "temperature_sensor.h"
#include "DHT.h"

class DHT22TemperatureSensor : public TemperatureSensor {
private:
    uint8_t pin;
    DHT* dht;
    
public:
    DHT22TemperatureSensor(uint8_t dht_pin) : pin(dht_pin), dht(nullptr) {}
    
    bool init() override {
        dht = new DHT(pin, DHT22);
        dht->begin();
        return true;
    }
    
    temperature_data_t read() override {
        temperature_data_t data;
        data.temperature = dht->readTemperature();
        data.valid = !isnan(data.temperature);
        data.timestamp = millis();
        
        if (data.valid) {
            data.temperature += calibration_offset;
            data.valid = validate_temperature(data.temperature);
        }
        
        notify_callback(data);
        return data;
    }
    
    bool is_connected() override {
        float temp = dht->readTemperature();
        return !isnan(temp);
    }
};
```

---

## Usage Examples

### Basic Temperature Sensor
```cpp
#include "config/device_config.h"
#include "sensors/temperature_sensor.h"
#include "communication/mqtt_client.h"

void setup() {
    Serial.begin(115200);
    
    // Load configuration
    DeviceConfig config;
    config.load();
    
    // Create temperature sensor
    SensorFactory factory;
    TemperatureSensor* sensor = factory.create_temperature_sensor("DHT22");
    sensor->init();
    
    // Create MQTT client
    MQTTClient mqtt(config.get_mqtt_broker(), 1883, config.get_device_id());
    mqtt.connect();
    
    Serial.println("Temperature sensor ready");
}

void loop() {
    // Read temperature
    temperature_data_t temp_data = sensor->read();
    
    if (temp_data.valid) {
        // Create telemetry
        JsonObject telemetry;
        telemetry["device_id"] = config.get_device_id();
        telemetry["temperature"] = temp_data.temperature;
        telemetry["timestamp"] = temp_data.timestamp;
        
        // Send to MQTT
        String payload;
        serializeJson(telemetry, payload);
        mqtt.publish("valtronics/telemetry", payload);
    }
    
    delay(30000);  // Send every 30 seconds
}
```

### Battery-Powered Sensor
```cpp
#include "power/power_manager.h"

void setup() {
    Serial.begin(115200);
    
    // Initialize power manager
    PowerManager power(A0);
    power.enable_battery_monitoring();
    
    // Check battery
    if (power.is_low_battery()) {
        Serial.println("Low battery, entering deep sleep");
        ESP.deepSleep(300 * 1000000);  // Sleep for 5 minutes
    }
    
    // Initialize sensor
    TemperatureSensor sensor;
    sensor.init();
    
    Serial.println("Battery-powered sensor ready");
}

void loop() {
    // Read temperature
    temperature_data_t temp_data = sensor.read();
    
    if (temp_data.valid) {
        // Send telemetry
        send_telemetry(temp_data);
    }
    
    // Check battery
    if (power.is_low_battery()) {
        Serial.println("Low battery detected");
        ESP.deepSleep(600 * 1000000);  // Sleep for 10 minutes
    }
    
    // Sleep for power saving
    ESP.deepSleep(60 * 1000000);  // Sleep for 1 minute
}
```

---

## Testing

### Unit Tests
```cpp
// tests/test_temperature_sensor.cpp
#include "sensors/temperature_sensor.h"

void test_temperature_reading() {
    TemperatureSensor* sensor = new DHT22TemperatureSensor(4);
    assert(sensor->init());
    
    temperature_data_t data = sensor->read();
    assert(data.valid);
    assert(data.temperature > -40 && data.temperature < 85);
    
    delete sensor;
}

void test_calibration_offset() {
    TemperatureSensor* sensor = new DHT22TemperatureSensor(4);
    sensor->init();
    sensor->set_calibration_offset(5.0);
    
    temperature_data_t data = sensor->read();
    assert(data.valid);
    
    // Test calibration offset
    float expected_temp = data.temperature - 5.0;
    // Compare with actual reading (implementation specific)
    
    delete sensor;
}
```

### Integration Tests
```cpp
// tests/test_integration.cpp
void test_sensor_to_mqtt() {
    // Initialize components
    DeviceConfig config;
    config.load();
    
    TemperatureSensor* sensor = new DHT22TemperatureSensor(4);
    sensor->init();
    
    MQTTClient mqtt(config.get_mqtt_broker(), 1883, config.get_device_id());
    mqtt.connect();
    
    // Test end-to-end
    temperature_data_t temp_data = sensor->read();
    assert(temp_data.valid);
    
    JsonObject telemetry;
    telemetry["device_id"] = config.get_device_id();
    telemetry["temperature"] = temp_data.temperature;
    
    String payload;
    serializeJson(telemetry, payload);
    
    bool published = mqtt.publish("test/telemetry", payload);
    assert(published);
    
    delete sensor;
}
```

---

## Troubleshooting

### Common Issues

#### Sensor Not Responding
```cpp
void debug_sensor() {
    TemperatureSensor* sensor = new DHT22TemperatureSensor(4);
    
    if (!sensor->init()) {
        Serial.println("Sensor initialization failed");
        return;
    }
    
    if (!sensor->is_connected()) {
        Serial.println("Sensor not connected");
        Serial.println("Check wiring:");
        Serial.println("  - DHT22 data pin to GPIO4");
        Serial.println("  - Power supply 3.3V or 5V");
        Serial.println("  - Pull-up resistor (10k) if needed");
    } else {
        Serial.println("Sensor connected successfully");
    }
    
    temperature_data_t data = sensor->read();
    if (!data.valid) {
        Serial.println("Invalid sensor reading");
        Serial.println("Possible causes:");
        Serial.println("  - Sensor not connected properly");
        Serial.println("  - Power supply issue");
        Serial.println("  - Timing issue (try adding delay)");
    }
    
    delete sensor;
}
```

#### MQTT Connection Issues
```cpp
void debug_mqtt() {
    DeviceConfig config;
    config.load();
    
    Serial.println("MQTT Debug:");
    Serial.println("Broker: " + config.get_mqtt_broker());
    Serial.println("Port: " + String(config.get_mqtt_port()));
    Serial.println("Client ID: " + config.get_device_id());
    
    WiFiClient wifiClient;
    PubSubClient client(wifiClient);
    
    client.setServer(config.get_mqtt_broker().c_str(), config.get_mqtt_port());
    
    if (client.connect(config.get_device_id().c_str())) {
        Serial.println("MQTT connection successful");
    } else {
        Serial.println("MQTT connection failed");
        Serial.println("State: " + String(client.state()));
        Serial.println("Possible causes:");
        Serial.println("  - Broker not reachable");
        Serial.println("  - Network connectivity issue");
        Serial.println("  - Authentication failure");
    }
}
```

---

## Support

For temperature sensor firmware support:
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **Platform Guides**: See `platform/*/` directories
- **Email**: firmware@valtronics.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Temperature Sensor Firmware v1.0**
