# Pressure Sensor Firmware

**Complete firmware implementation for Valtronics pressure monitoring devices**

---

## Overview

This application provides comprehensive pressure monitoring firmware with altitude compensation, weather pattern analysis, and barometric pressure tracking. It supports multiple pressure sensors and provides accurate readings for industrial and meteorological applications.

---

## Features

### Sensor Support
- **BMP280**: Digital pressure sensor with temperature
- **BME280**: Environmental sensor with pressure
- **MPX5700**: Analog pressure sensor
- **MS5611**: High-precision barometric pressure sensor
- **Generic**: Custom pressure sensor interface

### Advanced Features
- **Altitude Compensation**: Pressure adjustment for altitude
- **Weather Patterns**: Weather trend analysis and forecasting
- **Sea Level Pressure**: Standardized pressure calculations
- **Temperature Compensation**: Pressure correction for temperature
- **Storm Detection**: Barometric pressure drop detection

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
- **BME280**: Integrated environmental sensor
- **MS5611**: High-precision applications
- **Solar Panel**: Remote deployments
- **Battery**: Li-ion 18650 or equivalent

---

## Directory Structure

```
applications/pressure_sensor/
├── README.md                    # This file
├── platformio.ini               # PlatformIO configuration
├── src/                         # Source code
│   ├── main.cpp                 # Main application
│   ├── config/                  # Configuration
│   ├── drivers/                  # Hardware drivers
│   ├── sensors/                  # Sensor interfaces
│   ├── communication/            # Communication protocols
│   ├── algorithms/               # Calculation algorithms
│   ├── weather/                  # Weather analysis
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
    "id": "VT-PRES-001",
    "name": "Pressure Sensor 1",
    "type": "pressure_sensor",
    "version": "1.5.0",
    "location": "Weather Station A",
    "description": "Barometric pressure monitoring"
  },
  "sensor": {
    "type": "BME280",
    "interface": "I2C",
    "address": "0x76",
    "interval": 30,
    "precision": 0.1,
    "calibration_offset": 0.0
  },
  "altitude": {
    "enabled": true,
    "altitude": 500.0,
    "altitude_coefficient": 0.12,
    "sea_level_reference": 1013.25
  },
  "weather": {
    "trend_analysis": true,
    "trend_period": 3600,
    "storm_detection": true,
    "storm_threshold": -5.0,
    "forecast_enabled": true
  },
  "compensation": {
    "temperature_compensation": true,
    "humidity_compensation": false,
    "pressure_coefficient": 0.00012
  },
  "alerts": {
    "pressure_min": 980.0,
    "pressure_max": 1050.0,
    "pressure_critical_min": 950.0,
    "pressure_critical_max": 1080.0,
    "rapid_change_threshold": 3.0,
    "storm_alert_threshold": -8.0
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
#include "sensors/pressure_sensor.h"
#include "algorithms/altitude_compensation.h"
#include "weather/weather_analyzer.h"
#include "communication/mqtt_client.h"
#include "utils/logger.h"
#include "utils/json_utils.h"

// Global objects
PressureSensor* pressure_sensor = nullptr;
AltitudeCompensation* altitude_compensation = nullptr;
WeatherAnalyzer* weather_analyzer = nullptr;
MQTTClient* mqtt_client = nullptr;
DeviceConfig* device_config = nullptr;

// Global state
bool system_ready = false;
uint32_t last_telemetry_time = 0;
float pressure_history[24];  // 24 hours of hourly readings
int history_index = 0;

void setup() {
    Serial.begin(115200);
    Logger::info("Valtronics Pressure Sensor Starting...");
    
    // Initialize configuration
    device_config = new DeviceConfig();
    if (!device_config->load()) {
        Logger::error("Failed to load device configuration");
        return;
    }
    
    // Initialize components
    initialize_sensors();
    initialize_compensation();
    initialize_weather_analysis();
    initialize_communication();
    initialize_ota();
    
    system_ready = true;
    Logger::info("Pressure sensor ready");
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
    sensor_data_t sensor_data = pressure_sensor->read();
    
    // Apply altitude compensation
    float sea_level_pressure = calculate_sea_level_pressure(sensor_data.pressure, sensor_data.temperature);
    
    // Analyze weather patterns
    weather_data_t weather_data = weather_analyzer->analyze(sensor_data.pressure);
    
    // Update pressure history
    update_pressure_history(sensor_data.pressure);
    
    // Send telemetry
    handle_telemetry(sensor_data, sea_level_pressure, weather_data);
    
    // Handle commands
    handle_commands();
    
    delay(1000);
}

void initialize_sensors() {
    Logger::info("Initializing pressure sensor...");
    
    pressure_sensor = new PressureSensor();
    if (!pressure_sensor->init()) {
        Logger::error("Failed to initialize pressure sensor");
        return;
    }
    
    // Configure sensor
    pressure_sensor->set_calibration_offset(device_config->get_calibration_offset());
    
    Logger::info("Pressure sensor initialized");
}

void initialize_compensation() {
    Logger::info("Initializing altitude compensation...");
    
    altitude_compensation = new AltitudeCompensation();
    altitude_compensation->set_altitude(device_config->get_altitude());
    altitude_compensation->set_sea_level_reference(device_config->get_sea_level_reference());
    
    Logger::info("Altitude compensation initialized");
}

void initialize_weather_analysis() {
    Logger::info("Initializing weather analyzer...");
    
    weather_analyzer = new WeatherAnalyzer();
    weather_analyzer->set_trend_period(device_config->get_trend_period());
    weather_analyzer->set_storm_threshold(device_config->get_storm_threshold());
    
    Logger::info("Weather analyzer initialized");
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
    
    if (!wifiManager.autoConnect("Valtronics-PressureSensor")) {
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

void handle_telemetry(sensor_data_t sensor_data, float sea_level_pressure, weather_data_t weather_data) {
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
    sensors["pressure"] = sensor_data.pressure;
    sensors["temperature"] = sensor_data.temperature;
    sensors["sea_level_pressure"] = sea_level_pressure;
    telemetry["sensors"] = sensors;
    
    // Altitude compensation
    JsonObject altitude;
    altitude["device_altitude"] = device_config->get_altitude();
    altitude["compensation_applied"] = true;
    altitude["sea_level_reference"] = device_config->get_sea_level_reference();
    telemetry["altitude"] = altitude;
    
    // Weather data
    JsonObject weather;
    weather["trend"] = weather_data.trend;
    weather["trend_rate"] = weather_data.trend_rate;
    weather["forecast"] = weather_data.forecast;
    weather["storm_warning"] = weather_data.storm_warning;
    telemetry["weather"] = weather;
    
    // Pressure history
    JsonArray history;
    for (int i = 0; i < 24; i++) {
        history.add(pressure_history[i]);
    }
    telemetry["pressure_history"] = history;
    
    // System information
    JsonObject system;
    system["free_heap"] = ESP.getFreeHeap();
    system["wifi_rssi"] = WiFi.RSSI();
    system["uptime"] = current_time;
    system["sensor_connected"] = pressure_sensor->is_connected();
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
    } else if (cmd == "set_altitude") {
        float altitude = command["altitude"];
        Logger::info("Setting altitude: " + String(altitude));
        altitude_compensation->set_altitude(altitude);
        device_config->set_altitude(altitude);
    } else if (cmd == "set_reference") {
        float reference = command["reference"];
        Logger::info("Setting sea level reference: " + String(reference));
        altitude_compensation->set_sea_level_reference(reference);
        device_config->set_sea_level_reference(reference);
    } else {
        Logger::warning("Unknown command: " + cmd);
    }
}

void perform_calibration() {
    Logger::info("Starting pressure calibration...");
    
    // Get reference pressure (would come from user input or reference sensor)
    float reference_pressure = 1013.25;  // Standard atmospheric pressure
    
    // Read current sensor value
    sensor_data_t current_data = pressure_sensor->read();
    
    // Calculate calibration offset
    float offset = reference_pressure - current_data.pressure;
    
    // Apply calibration
    pressure_sensor->set_calibration_offset(offset);
    
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
    status["sensor_connected"] = pressure_sensor->is_connected();
    status["altitude"] = device_config->get_altitude();
    status["sea_level_reference"] = device_config->get_sea_level_reference();
    
    String payload = JSONUtils::serialize(status);
    mqtt_client->publish("valtronics/devices/" + device_config->get_device_id() + "/status", payload);
    
    Logger::info("Status sent");
}

void update_pressure_history(float pressure) {
    // Update pressure history (hourly readings)
    static uint32_t last_update = 0;
    uint32_t current_time = millis();
    
    // Update every hour (3600000 ms)
    if (current_time - last_update >= 3600000) {
        pressure_history[history_index] = pressure;
        history_index = (history_index + 1) % 24;
        last_update = current_time;
        
        Logger::info("Pressure history updated: " + String(pressure, 2) + " hPa");
    }
}

float calculate_sea_level_pressure(float pressure, float temperature) {
    // International Standard Atmosphere formula
    float altitude = device_config->get_altitude();
    float sea_level_reference = device_config->get_sea_level_reference();
    
    // Temperature compensation
    float temperature_kelvin = temperature + 273.15;
    float lapse_rate = 0.0065;  // Standard atmospheric lapse rate (K/m)
    
    // Calculate sea level pressure
    float sea_level_pressure = pressure * pow(1 - (lapse_rate * altitude) / temperature_kelvin, 
                                          -(9.80665 * 0.0289644) / (8.31432 * lapse_rate));
    
    // Apply calibration offset
    sea_level_pressure += pressure_sensor->get_calibration_offset();
    
    return sea_level_pressure;
}
```

### Pressure Sensor Interface
```cpp
// sensors/pressure_sensor.h
#ifndef PRESSURE_SENSOR_H
#define PRESSURE_SENSOR_H

#include <stdint.h>
#include <functional>

typedef struct {
    float pressure;
    float temperature;
    bool valid;
    uint32_t timestamp;
} sensor_data_t;

class PressureSensor {
private:
    std::function<void(sensor_data_t)> callback;
    float calibration_offset;
    
protected:
    bool validate_reading(float pressure, float temperature);
    void notify_callback(sensor_data_t data);
    
public:
    PressureSensor();
    virtual ~PressureSensor() = default;
    
    virtual bool init() = 0;
    virtual sensor_data_t read() = 0;
    virtual bool is_connected() = 0;
    
    void set_callback(std::function<void(sensor_data_t)> cb);
    void set_calibration_offset(float offset);
    float get_calibration_offset() const;
};

#endif // PRESSURE_SENSOR_H
```

### BME280 Driver
```cpp
// drivers/bme280_driver.cpp
#include "pressure_sensor.h"
#include "Adafruit_BME280.h"

class BME280PressureSensor : public PressureSensor {
private:
    uint8_t i2c_address;
    Adafruit_BME280* bme;
    
public:
    BME280PressureSensor(uint8_t address = 0x76) : i2c_address(address), bme(nullptr) {}
    
    bool init() override {
        bme = new Adafruit_BME280();
        
        if (!bme->begin(i2c_address)) {
            return false;
        }
        
        // Configure sensor
        bme->setSampling(Adafruit_BME280::MODE_NORMAL,
                        Adafruit_BME280::SAMPLING_X2,  // temperature
                        Adafruit_BME280::SAMPLING_X16, // pressure
                        Adafruit_BME280::SAMPLING_X1,  // humidity
                        Adafruit_BME280::FILTER_X16,
                        Adafruit_BME280::STANDBY_MS_0_5);
        
        return true;
    }
    
    sensor_data_t read() override {
        sensor_data_t data;
        data.pressure = bme->readPressure() / 100.0F;  // Convert to hPa
        data.temperature = bme->readTemperature();
        data.valid = !isnan(data.pressure) && !isnan(data.temperature);
        data.timestamp = millis();
        
        if (data.valid) {
            // Apply calibration offset
            data.pressure += calibration_offset;
            
            // Validate ranges
            data.valid = validate_reading(data.pressure, data.temperature);
        }
        
        notify_callback(data);
        return data;
    }
    
    bool is_connected() override {
        float pressure = bme->readPressure();
        float temperature = bme->readTemperature();
        return !isnan(pressure) && !isnan(temperature);
    }
};
```

### Weather Analyzer
```cpp
// weather/weather_analyzer.h
#ifndef WEATHER_ANALYZER_H
#define WEATHER_ANALYZER_H

#include <stdint.h>

typedef enum {
    WEATHER_STABLE,
    WEATHER_RISING,
    WEATHER_FALLING,
    WEATHER_STORM_WARNING
} weather_trend_t;

typedef struct {
    weather_trend_t trend;
    float trend_rate;        // hPa per hour
    String forecast;
    bool storm_warning;
    uint32_t timestamp;
} weather_data_t;

class WeatherAnalyzer {
private:
    float pressure_history[12];  // 12 hours of readings
    int history_index;
    uint32_t trend_period;
    float storm_threshold;
    
    weather_trend_t analyze_trend();
    float calculate_trend_rate();
    String generate_forecast(weather_trend_t trend, float rate);
    
public:
    WeatherAnalyzer();
    
    void set_trend_period(uint32_t period);
    void set_storm_threshold(float threshold);
    
    weather_data_t analyze(float current_pressure);
    
    void add_pressure_reading(float pressure);
    void reset_history();
};

#endif // WEATHER_ANALYZER_H
```

---

## Usage Examples

### Basic Pressure Monitor
```cpp
#include "config/device_config.h"
#include "sensors/pressure_sensor.h"
#include "algorithms/altitude_compensation.h"

void setup() {
    Serial.begin(115200);
    
    // Load configuration
    DeviceConfig config;
    config.load();
    
    // Create pressure sensor
    SensorFactory factory;
    PressureSensor* sensor = factory.create_pressure_sensor("BME280");
    sensor->init();
    
    // Initialize altitude compensation
    AltitudeCompensation altitude;
    altitude.set_altitude(config.get_altitude());
    
    Serial.println("Pressure monitor ready");
}

void loop() {
    // Read sensor data
    sensor_data_t data = sensor->read();
    
    if (data.valid) {
        // Calculate sea level pressure
        float sea_level = altitude.calculate_sea_level_pressure(data.pressure, data.temperature);
        
        // Create telemetry
        JsonObject telemetry;
        telemetry["device_id"] = config.get_device_id();
        telemetry["pressure"] = data.pressure;
        telemetry["sea_level_pressure"] = sea_level;
        telemetry["temperature"] = data.temperature;
        
        // Send to MQTT
        String payload;
        serializeJson(telemetry, payload);
        mqtt.publish("valtronics/telemetry", payload);
    }
    
    delay(30000);  // Send every 30 seconds
}
```

### Weather Station Monitor
```cpp
#include "weather/weather_analyzer.h"

void setup() {
    // Initialize components
    PressureSensor sensor;
    sensor.init();
    
    WeatherAnalyzer weather;
    weather.set_trend_period(3600);  // 1 hour
    weather.set_storm_threshold(-5.0);
    
    Serial.println("Weather station ready");
}

void loop() {
    // Read pressure
    sensor_data_t data = sensor.read();
    
    if (data.valid) {
        // Analyze weather
        weather_data_t weather = weather.analyze(data.pressure);
        
        // Check for storm warning
        if (weather.storm_warning) {
            trigger_storm_alert(weather);
        }
        
        // Send weather data
        send_weather_telemetry(data, weather);
    }
    
    delay(30000);
}

void trigger_storm_alert(weather_data_t weather) {
    // Send storm alert
    JsonObject alert;
    alert["type"] = "storm_warning";
    alert["trend"] = weather.trend;
    alert["trend_rate"] = weather.trend_rate;
    alert["forecast"] = weather.forecast;
    
    String payload;
    serializeJson(alert, payload);
    mqtt.publish("valtronics/alerts", payload);
}
```

---

## Testing

### Unit Tests
```cpp
void test_pressure_reading() {
    PressureSensor* sensor = new BME280PressureSensor();
    assert(sensor->init());
    
    sensor_data_t data = sensor->read();
    assert(data.valid);
    assert(data.pressure >= 900 && data.pressure <= 1100);  // Valid range
    assert(data.temperature >= -40 && data.temperature <= 85);
    
    delete sensor;
}

void test_altitude_compensation() {
    AltitudeCompensation altitude;
    altitude.set_altitude(500.0);
    
    float sea_level = altitude.calculate_sea_level_pressure(951.0, 15.0);
    
    // Sea level pressure should be higher at altitude
    assert(sea_level > 951.0);
    assert(abs(sea_level - 1013.25) < 10.0);  // Should be close to standard
}

void test_weather_analysis() {
    WeatherAnalyzer weather;
    weather.set_trend_period(3600);
    
    // Add falling pressure readings
    for (int i = 0; i < 12; i++) {
        weather.add_pressure_reading(1013.25 - i * 0.5);
    }
    
    weather_data_t result = weather.analyze(1006.25);
    
    assert(result.trend == WEATHER_FALLING);
    assert(result.trend_rate < 0);
    assert(result.storm_warning == false);  // Not yet storm warning
}
```

---

## Troubleshooting

### Common Issues

#### Sensor Reading Problems
```cpp
void debug_pressure_sensor() {
    PressureSensor* sensor = new BME280PressureSensor();
    
    if (!sensor->init()) {
        Serial.println("Sensor initialization failed");
        return;
    }
    
    if (!sensor->is_connected()) {
        Serial.println("Sensor not connected");
        Serial.println("Check wiring:");
        Serial.println("  - I2C connections (SDA, SCL)");
        Serial.println("  - Power supply 3.3V");
        Serial.println("  - I2C address (0x76 or 0x77)");
    } else {
        Serial.println("Sensor connected successfully");
        
        // Test reading
        sensor_data_t data = sensor->read();
        if (data.valid) {
            Serial.println("Sensor reading successful");
            Serial.print("Pressure: ");
            Serial.print(data.pressure);
            Serial.println(" hPa");
            Serial.print("Temperature: ");
            Serial.print(data.temperature);
            Serial.println("°C");
        } else {
            Serial.println("Invalid sensor reading");
        }
    }
    
    delete sensor;
}
```

#### Altitude Compensation Issues
```cpp
void debug_altitude_compensation() {
    AltitudeCompensation altitude;
    altitude.set_altitude(500.0);
    altitude.set_sea_level_reference(1013.25);
    
    // Test compensation
    float local_pressure = 951.0;  # Expected at 500m altitude
    float sea_level = altitude.calculate_sea_level_pressure(local_pressure, 15.0);
    
    Serial.println("Altitude Compensation Debug:");
    Serial.print("Local pressure: ");
    Serial.print(local_pressure);
    Serial.println(" hPa");
    Serial.print("Sea level pressure: ");
    Serial.print(sea_level);
    Serial.println(" hPa");
    Serial.print("Altitude: ");
    Serial.print(altitude.get_altitude());
    Serial.println(" m");
    
    // Verify compensation
    if (abs(sea_level - 1013.25) < 5.0) {
        Serial.println("Altitude compensation working correctly");
    } else {
        Serial.println("Altitude compensation may need adjustment");
    }
}
```

---

## Support

For pressure sensor firmware support:
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **Platform Guides**: See `platform/*/` directories
- **Email**: firmware@valtronics.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Pressure Sensor Firmware v1.5**
