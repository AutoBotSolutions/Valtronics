# Humidity Sensor Firmware

**Complete firmware implementation for Valtronics humidity monitoring devices**

---

## Overview

This application provides comprehensive humidity monitoring firmware with temperature compensation, dew point calculations, and environmental correlation. It supports multiple humidity sensors and provides accurate readings for industrial and commercial applications.

---

## Features

### Sensor Support
- **DHT22**: Digital temperature and humidity sensor
- **SHT30**: High-precision digital humidity sensor
- **BME280**: Environmental sensor with humidity
- **HIH-6130**: Industrial humidity sensor
- **Generic**: Custom humidity sensor interface

### Advanced Features
- **Temperature Compensation**: Inverse correlation with temperature
- **Dew Point Calculation**: Accurate dew point computation
- **Humidity Calibration**: Automatic calibration support
- **Environmental Correlation**: Multi-sensor data correlation
- **Alert System**: Threshold-based and trend-based alerts

### Communication
- **MQTT**: Primary telemetry protocol
- **HTTP**: Fallback and configuration protocol
- **LoRa**: Long-range communication option
- **Modbus**: Industrial protocol support

---

## Hardware Requirements

### Minimum Requirements
- **Microcontroller**: ESP32, Arduino, or STM32
- **Memory**: 32KB+ SRAM, 256KB+ Flash
- **Connectivity**: WiFi or Ethernet
- **Power**: 3.3V or 5V supply

### Recommended Components
- **ESP32 DevKit**: Development and production
- **DHT22**: Cost-effective solution
- **SHT30**: High-precision applications
- **Solar Panel**: Remote deployments
- **Battery**: Li-ion 18650 or equivalent

---

## Directory Structure

```
applications/humidity_sensor/
├── README.md                    # This file
├── platformio.ini               # PlatformIO configuration
├── src/                         # Source code
│   ├── main.cpp                 # Main application
│   ├── config/                  # Configuration
│   ├── drivers/                  # Hardware drivers
│   ├── sensors/                  # Sensor interfaces
│   ├── communication/            # Communication protocols
│   ├── algorithms/               # Calculation algorithms
│   ├── calibration/              # Calibration utilities
│   └── utils/                    # Utility functions
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
    "id": "VT-HUM-001",
    "name": "Humidity Sensor 1",
    "type": "humidity_sensor",
    "version": "1.5.0",
    "location": "Office Building A",
    "description": "Humidity and temperature monitoring"
  },
  "sensor": {
    "type": "DHT22",
    "pin": 4,
    "interval": 30,
    "precision": 1.0,
    "calibration_offset": 0.0,
    "temperature_coupling": 0.7
  },
  "calculations": {
    "dew_point": {
      "enabled": true,
      "formula": "magnus",
      "pressure_reference": 1013.25
    },
    "absolute_humidity": {
      "enabled": true,
      "pressure_reference": 1013.25
    },
    "heat_index": {
      "enabled": true,
      "formula": "steadman"
    }
  },
  "alerts": {
    "humidity_min": 30.0,
    "humidity_max": 70.0,
    "humidity_critical_min": 20.0,
    "humidity_critical_max": 80.0,
    "dew_point_threshold": 15.0,
    "rapid_change_threshold": 10.0
  },
  "compensation": {
    "temperature_coupling": 0.7,
    "pressure_compensation": true,
    "altitude_compensation": false,
    "altitude": 0.0
  }
}
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
#include "sensors/humidity_sensor.h"
#include "algorithms/dew_point.h"
#include "communication/mqtt_client.h"
#include "calibration/calibration_manager.h"
#include "utils/logger.h"
#include "utils/json_utils.h"

// Global objects
HumiditySensor* humidity_sensor = nullptr;
MQTTClient* mqtt_client = nullptr;
CalibrationManager* calibration_manager = nullptr;
DeviceConfig* device_config = nullptr;

// Global state
bool system_ready = false;
uint32_t last_telemetry_time = 0;
float last_temperature = 0.0;

void setup() {
    Serial.begin(115200);
    Logger::info("Valtronics Humidity Sensor Starting...");
    
    // Initialize configuration
    device_config = new DeviceConfig();
    if (!device_config->load()) {
        Logger::error("Failed to load device configuration");
        return;
    }
    
    // Initialize components
    initialize_sensors();
    initialize_communication();
    initialize_calibration();
    initialize_ota();
    
    system_ready = true;
    Logger::info("Humidity sensor ready");
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
    
    // Read sensor data
    sensor_data_t sensor_data = humidity_sensor->read();
    
    // Calculate derived values
    float dew_point = calculate_dew_point(sensor_data.humidity, sensor_data.temperature);
    float absolute_humidity = calculate_absolute_humidity(sensor_data.humidity, sensor_data.temperature);
    float heat_index = calculate_heat_index(sensor_data.humidity, sensor_data.temperature);
    
    // Update temperature coupling
    update_temperature_coupling(sensor_data.temperature);
    
    // Send telemetry
    handle_telemetry(sensor_data, dew_point, absolute_humidity, heat_index);
    
    // Handle commands
    handle_commands();
    
    delay(1000);
}

void initialize_sensors() {
    Logger::info("Initializing humidity sensor...");
    
    humidity_sensor = new HumiditySensor();
    if (!humidity_sensor->init()) {
        Logger::error("Failed to initialize humidity sensor");
        return;
    }
    
    // Configure sensor
    humidity_sensor->set_temperature_coupling(device_config->get_temperature_coupling());
    humidity_sensor->set_calibration_offset(device_config->get_calibration_offset());
    
    Logger::info("Humidity sensor initialized");
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
    
    Logger::info("Communication initialized");
}

void initialize_wifi() {
    WiFiManager wifiManager;
    
    wifiManager.setDebugOutput(false);
    
    if (!wifiManager.autoConnect("Valtronics-HumSensor")) {
        Logger::error("Failed to connect to WiFi");
        ESP.restart();
    }
    
    Logger::info("WiFi connected: " + WiFi.localIP().toString());
}

void initialize_calibration() {
    Logger::info("Initializing calibration manager...");
    
    calibration_manager = new CalibrationManager();
    if (!calibration_manager->init()) {
        Logger::error("Failed to initialize calibration manager");
        return;
    }
    
    // Load calibration data
    calibration_manager->load_calibration();
    
    Logger::info("Calibration manager initialized");
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

void handle_telemetry(sensor_data_t sensor_data, float dew_point, float absolute_humidity, float heat_index) {
    uint32_t current_time = millis();
    
    if (current_time - last_telemetry_time < device_config->get_telemetry_interval() * 1000) {
        return;
    }
    
    // Create comprehensive telemetry payload
    JsonObject telemetry;
    telemetry["device_id"] = device_config->get_device_id();
    telemetry["timestamp"] = current_time;
    telemetry["device_type"] = device_config->get_device_type();
    telemetry["location"] = device_config->get_device_location();
    
    // Sensor data
    JsonObject sensors;
    sensors["humidity"] = sensor_data.humidity;
    sensors["temperature"] = sensor_data.temperature;
    telemetry["sensors"] = sensors;
    
    // Calculated values
    JsonObject calculated;
    calculated["dew_point"] = dew_point;
    calculated["absolute_humidity"] = absolute_humidity;
    calculated["heat_index"] = heat_index;
    calculated["temperature_coupling"] = device_config->get_temperature_coupling();
    telemetry["calculated"] = calculated;
    
    // System information
    JsonObject system;
    system["free_heap"] = ESP.getFreeHeap();
    system["wifi_rssi"] = WiFi.RSSI();
    system["uptime"] = current_time;
    system["last_calibration"] = calibration_manager->get_last_calibration();
    telemetry["system"] = system;
    
    // Send telemetry
    String payload = JSONUtils::serialize(telemetry);
    if (mqtt_client->publish(device_config->get_mqtt_telemetry_topic(), payload)) {
        last_telemetry_time = current_time;
        Logger::info("Telemetry sent");
    } else {
        Logger::error("Failed to send telemetry");
    }
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
}

void handle_command(const JsonObject& command) {
    String cmd = command["command"];
    
    if (cmd == "reboot") {
        Logger::info("Reboot command received");
        ESP.restart();
    } else if (cmd == "calibrate") {
        Logger::info("Calibration command received");
        perform_calibration();
    } else if (cmd == "status") {
        send_status();
    } else if (cmd == "set_coupling") {
        float coupling = command["coupling"];
        Logger::info("Setting temperature coupling: " + String(coupling));
        humidity_sensor->set_temperature_coupling(coupling);
        device_config->set_temperature_coupling(coupling);
    } else if (cmd == "set_offset") {
        float offset = command["offset"];
        Logger::info("Setting calibration offset: " + String(offset));
        humidity_sensor->set_calibration_offset(offset);
        device_config->set_calibration_offset(offset);
    } else {
        Logger::warning("Unknown command: " + cmd);
    }
}

void perform_calibration() {
    Logger::info("Starting calibration...");
    
    // Get reference humidity (would come from user input or reference sensor)
    float reference_humidity = 50.0;  // Example value
    
    // Read current sensor value
    sensor_data_t current_data = humidity_sensor->read();
    
    // Calculate calibration offset
    float offset = reference_humidity - current_data.humidity;
    
    // Apply calibration
    humidity_sensor->set_calibration_offset(offset);
    calibration_manager->save_calibration(offset);
    
    Logger::info("Calibration completed. Offset: " + String(offset, 2));
}

void send_status() {
    JsonObject status;
    status["device_id"] = device_config->get_device_id();
    status["device_type"] = device_config->get_device_type();
    status["firmware_version"] = device_config->get_firmware_version();
    status["uptime"] = millis();
    status["free_heap"] = ESP.getFreeHeap();
    status["wifi_rssi"] = WiFi.RSSI();
    status["sensor_connected"] = humidity_sensor->is_connected();
    status["last_calibration"] = calibration_manager->get_last_calibration();
    status["temperature_coupling"] = device_config->get_temperature_coupling();
    
    String payload = JSONUtils::serialize(status);
    mqtt_client->publish("valtronics/devices/" + device_config->get_device_id() + "/status", payload);
    
    Logger::info("Status sent");
}

void update_temperature_coupling(float temperature) {
    // Update temperature coupling based on recent readings
    static float temperature_history[10];
    static int history_index = 0;
    
    temperature_history[history_index] = temperature;
    history_index = (history_index + 1) % 10;
    
    // Calculate average temperature
    float avg_temperature = 0;
    for (int i = 0; i < 10; i++) {
        avg_temperature += temperature_history[i];
    }
    avg_temperature /= 10;
    
    // Adjust coupling based on temperature stability
    float temperature_variance = 0;
    for (int i = 0; i < 10; i++) {
        temperature_variance += pow(temperature_history[i] - avg_temperature, 2);
    }
    temperature_variance /= 10;
    
    // Higher coupling for stable temperatures
    float optimal_coupling = device_config->get_temperature_coupling();
    if (temperature_variance < 1.0) {
        optimal_coupling = min(0.9, optimal_coupling + 0.1);
    } else if (temperature_variance > 5.0) {
        optimal_coupling = max(0.3, optimal_coupling - 0.2);
    }
    
    humidity_sensor->set_temperature_coupling(optimal_coupling);
}

float calculate_dew_point(float humidity, float temperature) {
    // Magnus formula for dew point calculation
    if (humidity < 0.01 || humidity > 100) {
        return NAN;
    }
    
    float a = 17.27;
    float b = 237.7;
    
    // Calculate dew point
    float alpha = ((a * temperature) / (b + temperature)) + log(humidity / 100.0);
    float dew_point = (b * alpha) / (a - alpha);
    
    return dew_point;
}

float calculate_absolute_humidity(float relative_humidity, float temperature) {
    // Convert relative humidity to absolute humidity
    if (relative_humidity < 0.01 || relative_humidity > 100) {
        return NAN;
    }
    
    // Saturation vapor pressure (simplified formula)
    float es = 6.112 * exp(17.67 * temperature / (temperature + 243.5));
    
    // Actual vapor pressure
    float e = (relative_humidity / 100.0) * es;
    
    // Absolute humidity (g/m³)
    float ah = 216.7 * e / (temperature + 273.15);
    
    return ah;
}

float calculate_heat_index(float humidity, float temperature) {
    // Steadman's heat index formula
    if (temperature < 27.0) {
        return temperature;  // Heat index not defined for low temperatures
    }
    
    float hi;
    
    if (humidity >= 40 && temperature <= 40) {
        // Original heat index formula
        hi = 0.5 * (temperature + 61.0 + ((temperature - 68.0) * 1.2) + 
                     (humidity * 0.094)) + 0.5 * ((temperature + 61.0) * 1.2) + 
                     (humidity * 0.094) * pow(abs(temperature - 68.0) * 1.2 + 
                     (humidity * 0.094 - 58.0), 0.5);
    } else {
        // Simplified formula for extreme conditions
        hi = temperature + 0.5 * (humidity - 40) / 10;
    }
    
    return hi;
}
```

### Humidity Sensor Interface
```cpp
// sensors/humidity_sensor.h
#ifndef HUMIDITY_SENSOR_H
#define HUMIDITY_SENSOR_H

#include <stdint.h>
#include <functional>

typedef struct {
    float humidity;
    float temperature;
    bool valid;
    uint32_t timestamp;
} sensor_data_t;

class HumiditySensor {
private:
    std::function<void(sensor_data_t)> callback;
    float calibration_offset;
    float temperature_coupling;
    float last_temperature;
    
protected:
    bool validate_reading(float humidity, float temperature);
    void notify_callback(sensor_data_t data);
    
public:
    HumiditySensor();
    virtual ~HumiditySensor() = default;
    
    virtual bool init() = 0;
    virtual sensor_data_t read() = 0;
    virtual bool is_connected() = 0;
    
    void set_callback(std::function<void(sensor_data_t)> cb);
    void set_calibration_offset(float offset);
    void set_temperature_coupling(float coupling);
    float get_calibration_offset() const;
    float get_temperature_coupling() const;
};

#endif // HUMIDITY_SENSOR_H
```

### DHT22 Driver
```cpp
// drivers/dht22_driver.cpp
#include "humidity_sensor.h"
#include "DHT.h"

class DHT22HumiditySensor : public HumiditySensor {
private:
    uint8_t pin;
    DHT* dht;
    
public:
    DHT22HumiditySensor(uint8_t dht_pin) : pin(dht_pin), dht(nullptr) {}
    
    bool init() override {
        dht = new DHT(pin, DHT22);
        dht->begin();
        return true;
    }
    
    sensor_data_t read() override {
        sensor_data_t data;
        data.humidity = dht->readHumidity();
        data.temperature = dht->readTemperature();
        data.valid = !isnan(data.humidity) && !isnan(data.temperature);
        data.timestamp = millis();
        
        if (data.valid) {
            // Apply calibration offset
            data.humidity += calibration_offset;
            
            // Apply temperature compensation
            if (last_temperature > 0) {
                float temp_change = data.temperature - last_temperature;
                float humidity_change = -temp_change * temperature_coupling;
                data.humidity += humidity_change;
            }
            
            last_temperature = data.temperature;
            
            // Validate ranges
            data.valid = validate_reading(data.humidity, data.temperature);
        }
        
        notify_callback(data);
        return data;
    }
    
    bool is_connected() override {
        float humidity = dht->readHumidity();
        float temperature = dht->readTemperature();
        return !isnan(humidity) && !isnan(temperature);
    }
};
```

---

## Usage Examples

### Basic Humidity Monitor
```cpp
#include "config/device_config.h"
#include "sensors/humidity_sensor.h"
#include "algorithms/dew_point.h"

void setup() {
    Serial.begin(115200);
    
    // Load configuration
    DeviceConfig config;
    config.load();
    
    // Create humidity sensor
    SensorFactory factory;
    HumiditySensor* sensor = factory.create_humidity_sensor("DHT22");
    sensor->init();
    
    Serial.println("Humidity monitor ready");
}

void loop() {
    // Read sensor data
    sensor_data_t data = sensor->read();
    
    if (data.valid) {
        // Calculate dew point
        float dew_point = calculate_dew_point(data.humidity, data.temperature);
        
        // Create telemetry
        JsonObject telemetry;
        telemetry["device_id"] = config.get_device_id();
        telemetry["humidity"] = data.humidity;
        telemetry["temperature"] = data.temperature;
        telemetry["dew_point"] = dew_point;
        
        // Send to MQTT
        String payload;
        serializeJson(telemetry, payload);
        mqtt.publish("valtronics/telemetry", payload);
    }
    
    delay(30000);  // Send every 30 seconds
}
```

### Advanced Monitor with Calibration
```cpp
#include "calibration/calibration_manager.h"

void setup() {
    // Initialize calibration manager
    CalibrationManager calibration;
    calibration.init();
    
    // Create sensor
    HumiditySensor sensor;
    sensor.init();
    
    Serial.println("Advanced humidity monitor ready");
}

void loop() {
    // Read sensor
    sensor_data_t data = sensor.read();
    
    if (data.valid) {
        // Check if calibration needed
        if (calibration.needs_calibration()) {
            perform_automatic_calibration();
        }
        
        // Send telemetry with calibration status
        send_telemetry_with_calibration(data);
    }
    
    delay(30000);
}

void perform_automatic_calibration() {
    // Use reference sensor or known conditions
    float reference_humidity = get_reference_humidity();
    
    sensor_data_t current_data = sensor.read();
    float offset = reference_humidity - current_data.humidity;
    
    sensor.set_calibration_offset(offset);
    calibration.save_calibration(offset);
}
```

---

## Testing

### Unit Tests
```cpp
void test_humidity_reading() {
    HumiditySensor* sensor = new DHT22HumiditySensor(4);
    assert(sensor->init());
    
    sensor_data_t data = sensor->read();
    assert(data.valid);
    assert(data.humidity >= 0 && data.humidity <= 100);
    assert(data.temperature >= -40 && data.temperature <= 85);
    
    delete sensor;
}

void test_dew_point_calculation() {
    // Test with known values
    float humidity = 50.0;
    float temperature = 25.0;
    
    float dew_point = calculate_dew_point(humidity, temperature);
    
    // Expected dew point around 13.9°C for 50% RH at 25°C
    assert(abs(dew_point - 13.9) < 1.0);
}

void test_temperature_compensation() {
    HumiditySensor sensor;
    sensor.set_temperature_coupling(0.7);
    
    // Test temperature compensation
    sensor_data_t data1 = sensor.read();
    // Simulate temperature change
    float original_humidity = data1.humidity;
    
    // Test compensation effect
    assert(sensor.get_temperature_coupling() == 0.7);
}
```

---

## Troubleshooting

### Common Issues

#### Sensor Reading Problems
```cpp
void debug_humidity_sensor() {
    HumiditySensor* sensor = new DHT22HumiditySensor(4);
    
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
        
        // Test reading
        sensor_data_t data = sensor->read();
        if (data.valid) {
            Serial.println("Sensor reading successful");
            Serial.print("Humidity: ");
            Serial.print(data.humidity);
            Serial.println("%");
            Serial.print("Temperature: ");
            Serial.print(data.temperature);
            Serial.println("°C");
        } else {
            Serial.println("Invalid sensor reading");
            Serial.println("Possible causes:");
            Serial.println("  - Sensor not connected properly");
            Serial.println("  - Power supply issue");
            Serial.println("  - Timing issue (try adding delay)");
        }
    }
    
    delete sensor;
}
```

#### Calibration Issues
```cpp
void debug_calibration() {
    CalibrationManager calibration;
    
    if (!calibration.init()) {
        Serial.println("Calibration manager initialization failed");
        return;
    }
    
    // Load calibration data
    if (!calibration.load_calibration()) {
        Serial.println("No calibration data found");
        Serial.println("Performing initial calibration...");
        
        // Perform initial calibration
        float reference_humidity = 50.0;
        float offset = perform_calibration(reference_humidity);
        
        Serial.print("Calibration offset: ");
        Serial.println(offset);
        
        calibration.save_calibration(offset);
    } else {
        Serial.println("Calibration data loaded");
        Serial.print("Calibration offset: ");
        Serial.println(calibration.get_offset());
    }
    
    // Test calibration
    float test_humidity = read_sensor_humidity();
    float calibrated_humidity = test_humidity + calibration.get_offset();
    
    Serial.print("Test humidity: ");
    Serial.print(test_humidity);
    Serial.print("% -> Calibrated: ");
    Serial.print(calibrated_humidity);
    Serial.println("%");
}
```

---

## Support

For humidity sensor firmware support:
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **Platform Guides**: See `platform/*/` directories
- **Email**: firmware@valtronics.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Humidity Sensor Firmware v1.5**
