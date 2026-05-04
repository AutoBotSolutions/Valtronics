# Air Quality Monitor Firmware

**Complete firmware implementation for Valtronics air quality monitoring devices**

---

## Overview

This application provides comprehensive air quality monitoring firmware that reads multiple air quality parameters (PM2.5, PM10, CO2, VOC, O3, NO2, SO2), calculates AQI, and sends detailed data to the Valtronics platform. It supports multiple sensor types and includes advanced features like pollution source tracking and health recommendations.

---

## Features

### Sensor Support
- **PM2.5/PM10**: Particulate matter sensors (PMS5003, SDS011)
- **CO2**: Carbon dioxide sensors (MH-Z19, SCD30)
- **VOC**: Volatile organic compounds (SGP30, MQ-135)
- **O3**: Ozone sensors (MiCS-6814)
- **NO2**: Nitrogen dioxide sensors (MiCS-2710)
- **SO2**: Sulfur dioxide sensors (MiCS-6814)
- **Multi-Gas**: Combined gas sensors (BME680, CCS811)

### AQI Calculation
- **US EPA AQI**: Standard AQI calculation
- **Custom AQI**: Configurable AQI thresholds
- **Health Recommendations**: Health-based recommendations
- **Trend Analysis**: Historical trend analysis
- **Alert Levels**: Multiple alert severity levels

### Advanced Features
- **Pollution Source Tracking**: Track pollution sources
- **Calibration**: Automatic sensor calibration
- **Data Validation**: Range validation and outlier detection
- **Power Management**: Optimized for battery operation
- **OTA Updates**: Over-the-air firmware updates
- **Local Display**: LCD display support
- **Buzzer/LED**: Visual/audio alerts

---

## Hardware Requirements

### Minimum Requirements
- **Microcontroller**: ESP32 (recommended) or Arduino Mega
- **Memory**: 32KB+ SRAM, 512KB+ Flash
- **Connectivity**: WiFi or Ethernet
- **Power**: 5V or 3.3V supply

### Recommended Components
- **ESP32 DevKit**: Main controller
- **PMS5003**: PM2.5/PM10 sensor
- **SGP30**: VOC/eCO2 sensor
- **MH-Z19**: CO2 sensor
- **LCD Display**: 16x2 or 20x4 character LCD
- **Buzzer**: Piezo buzzer for alerts
- **Battery**: Li-ion 18650 with solar panel

---

## Directory Structure

```
applications/air_quality_monitor/
├── README.md                    # This file
├── platformio.ini               # PlatformIO configuration
├── src/                         # Source code
│   ├── main.cpp                 # Main application
│   ├── config/                  # Configuration
│   │   ├── device_config.h     # Device configuration
│   │   ├── sensor_config.h      # Sensor configuration
│   │   └── aqi_config.h         # AQI configuration
│   ├── drivers/                  # Hardware drivers
│   │   ├── pms5003_driver.h      # PMS5003 driver
│   │   ├── sgp30_driver.h        # SGP30 driver
│   │   ├── mhz19_driver.h        # MH-Z19 driver
│   │   └── lcd_driver.h          # LCD driver
│   ├── sensors/                  # Sensor interfaces
│   │   ├── pm_sensor.h           # Particulate matter sensor
│   │   ├── gas_sensor.h          # Gas sensor
│   │   ├── aqi_calculator.h      # AQI calculator
│   │   └── sensor_manager.h      # Sensor manager
│   ├── communication/            # Communication
│   │   ├── mqtt_client.h         # MQTT client
│   │   ├── http_client.h         # HTTP client
│   │   └── data_formatter.h      # Data formatter
│   ├── display/                  # Display
│   │   ├── lcd_display.h         # LCD display
│   │   └── led_indicator.h        # LED indicators
│   ├── alerts/                   # Alert system
│   │   ├── alert_manager.h       # Alert manager
│   │   └── buzzer.h              # Buzzer control
│   ├── utils/                    # Utility functions
│   │   ├── json_utils.h          # JSON utilities
│   │   ├── math_utils.h          # Math utilities
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
    "id": "VT-AQ-001",
    "name": "Air Quality Monitor 1",
    "type": "air_quality_monitor",
    "version": "2.0.0",
    "location": "Office Building A",
    "description": "Comprehensive air quality monitoring"
  },
  "sensors": {
    "pm_sensor": {
      "type": "PMS5003",
      "pin": 4,
      "interval": 30,
      "calibration": {
        "pm25_offset": 0,
        "pm10_offset": 0,
        "auto_calibrate": true
      }
    },
    "gas_sensors": [
      {
        "type": "SGP30",
        "i2c_address": "0x58",
        "interval": 60,
        "enable_bsec": true
      },
      {
        "type": "MH-Z19",
        "uart_port": 2,
        "baud_rate": 9600,
        "interval": 120
      }
    ]
  },
  "aqi": {
    "standard": "EPA",
    "pm25_breakpoints": [12, 35.4, 55.4, 150.4, 250.4],
    "pm10_breakpoints": [54, 154, 254, 354, 424],
    "co2_breakpoints": [400, 1000, 5000, 10000, 40000],
    "enable_recommendations": true,
    "alert_thresholds": {
      "moderate": 100,
      "unhealthy": 150,
      "very_unhealthy": 200,
      "hazardous": 300
    }
  },
  "display": {
    "enabled": true,
    "type": "LCD",
    "backlight": true,
    "scroll_speed": 500
  },
  "alerts": {
    "buzzer": true,
    "led": true,
    "mqtt_alerts": true,
    "local_alerts": true,
    "alert_duration": 30
  },
  "power": {
    "mode": "normal",
    "battery_monitoring": true,
    "deep_sleep": false,
    "sleep_duration": 300,
    "low_battery_threshold": 15
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
    SoftwareSerial
    PMS5003
    SGP30
    MHZ19B
    LiquidCrystal
    Wire
    ESP8266WiFi
    WiFiManager
    ArduinoOTA

build_flags = 
    -DCORE_DEBUG_LEVEL=3
    -DCONFIG_ARDUHAL_LOG_COLORS
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
#include <LiquidCrystal.h>

#include "config/device_config.h"
#include "sensors/sensor_manager.h"
#include "communication/mqtt_client.h"
#include "display/lcd_display.h"
#include "alerts/alert_manager.h"
#include "utils/logger.h"
#include "utils/json_utils.h"

// Global objects
SensorManager* sensor_manager = nullptr;
MQTTClient* mqtt_client = nullptr;
LCDDisplay* lcd_display = nullptr;
AlertManager* alert_manager = nullptr;
DeviceConfig* device_config = nullptr;

// Global state
bool system_ready = false;
uint32_t last_telemetry_time = 0;

void setup() {
    Serial.begin(115200);
    Logger::info("Valtronics Air Quality Monitor Starting...");
    
    // Initialize configuration
    device_config = new DeviceConfig();
    if (!device_config->load()) {
        Logger::error("Failed to load device configuration");
        return;
    }
    
    // Initialize components
    initialize_sensors();
    initialize_display();
    initialize_alerts();
    initialize_communication();
    initialize_ota();
    
    system_ready = true;
    Logger::info("Air quality monitor ready");
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
    
    // Read sensors
    sensor_data_t sensor_data = sensor_manager->read_all_sensors();
    
    // Calculate AQI
    aqi_data_t aqi_data = sensor_manager->calculate_aqi(sensor_data);
    
    // Update display
    if (lcd_display) {
        lcd_display->update(sensor_data, aqi_data);
    }
    
    // Handle alerts
    alert_manager->check_alerts(sensor_data, aqi_data);
    
    // Send telemetry
    handle_telemetry(sensor_data, aqi_data);
    
    // Handle commands
    handle_commands();
    
    // Power management
    handle_power_management();
    
    delay(1000);
}

void initialize_sensors() {
    Logger::info("Initializing sensors...");
    
    sensor_manager = new SensorManager();
    if (!sensor_manager->init()) {
        Logger::error("Failed to initialize sensors");
        return;
    }
    
    Logger::info("Sensors initialized");
}

void initialize_display() {
    if (!device_config->get_display_enabled()) {
        return;
    }
    
    Logger::info("Initializing display...");
    
    lcd_display = new LCDDisplay();
    if (!lcd_display->init()) {
        Logger::error("Failed to initialize display");
        return;
    }
    
    lcd_display->show_welcome();
    Logger::info("Display initialized");
}

void initialize_alerts() {
    Logger::info("Initializing alerts...");
    
    alert_manager = new AlertManager();
    if (!alert_manager->init()) {
        Logger::error("Failed to initialize alerts");
        return;
    }
    
    Logger::info("Alerts initialized");
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
    
    if (!wifiManager.autoConnect("Valtronics-AQMonitor")) {
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

void handle_telemetry(sensor_data_t sensor_data, aqi_data_t aqi_data) {
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
    sensors["pm25"] = sensor_data.pm25;
    sensors["pm10"] = sensor_data.pm10;
    sensors["co2"] = sensor_data.co2;
    sensors["voc"] = sensor_data.voc;
    sensors["o3"] = sensor_data.o3;
    sensors["no2"] = sensor_data.no2;
    sensors["so2"] = sensor_data.so2;
    telemetry["sensors"] = sensors;
    
    // AQI data
    JsonObject aqi;
    aqi["value"] = aqi_data.value;
    aqi["level"] = aqi_data.level;
    aqi["dominant_pollutant"] = aqi_data.dominant_pollutant;
    aqi["health_recommendation"] = aqi_data.recommendation;
    telemetry["aqi"] = aqi;
    
    // System information
    JsonObject system;
    system["free_heap"] = ESP.getFreeHeap();
    system["wifi_rssi"] = WiFi.RSSI();
    system["uptime"] = current_time;
    system["battery_voltage"] = get_battery_voltage();
    system["sensor_count"] = sensor_data.sensor_count;
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
        sensor_manager->calibrate_sensors();
    } else if (cmd == "status") {
        send_status();
    } else if (cmd == "display") {
        String message = command["message"];
        if (lcd_display) {
            lcd_display->show_message(message);
        }
    } else if (cmd == "alert_test") {
        Logger::info("Alert test command received");
        alert_manager->test_alerts();
    } else {
        Logger::warning("Unknown command: " + cmd);
    }
}

void handle_commands() {
    // Handle local commands (buttons, etc.)
    if (digitalRead(BUTTON_PIN) == LOW) {
        // Button pressed
        delay(50);  // Debounce
        if (digitalRead(BUTTON_PIN) == LOW) {
            handle_button_press();
        }
    }
}

void handle_button_press() {
    static uint32_t last_press = 0;
    uint32_t current_time = millis();
    
    if (current_time - last_press < 1000) {  // 1 second debounce
        return;
    }
    
    last_press = current_time;
    
    // Toggle display
    if (lcd_display) {
        lcd_display->toggle_backlight();
    }
    
    // Send status
    send_status();
}

void send_status() {
    JsonObject status;
    status["device_id"] = device_config->get_device_id();
    status["device_type"] = device_config->get_device_type();
    status["firmware_version"] = device_config->get_firmware_version();
    status["uptime"] = millis();
    status["free_heap"] = ESP.getFreeHeap();
    status["wifi_rssi"] = WiFi.RSSI();
    status["sensor_count"] = sensor_manager->get_sensor_count();
    status["last_calibration"] = sensor_manager->get_last_calibration();
    
    String payload = JSONUtils::serialize(status);
    mqtt_client->publish("valtronics/devices/" + device_config->get_device_id() + "/status", payload);
    
    Logger::info("Status sent");
}

void handle_power_management() {
    // Check battery level
    float battery_voltage = get_battery_voltage();
    if (battery_voltage < 3.0) {  // Low battery threshold
        Logger::warning("Low battery: " + String(battery_voltage) + "V");
        
        // Reduce telemetry frequency
        if (device_config->get_telemetry_interval() < 60) {
            device_config->set_telemetry_interval(60);
            Logger::info("Reduced telemetry interval to 60 seconds");
        }
        
        // Turn off display backlight
        if (lcd_display) {
            lcd_display->set_backlight(false);
        }
    }
    
    // Handle deep sleep
    if (device_config->get_deep_sleep_enabled() && battery_voltage < 2.8) {
        Logger::info("Entering deep sleep due to low battery");
        ESP.deepSleep(device_config->get_sleep_duration() * 1000000);
    }
}

float get_battery_voltage() {
    // Read battery voltage (implementation depends on hardware)
    int raw_value = analogRead(BATTERY_PIN);
    return (raw_value / 1024.0) * 3.3;  // Example conversion
}
```

### AQI Calculator
```cpp
// sensors/aqi_calculator.h
#ifndef AQI_CALCULATOR_H
#define AQI_CALCULATOR_H

#include <stdint.h>
#include <string>

typedef struct {
    float value;
    std::string level;
    std::string dominant_pollutant;
    std::string recommendation;
    bool valid;
} aqi_data_t;

typedef struct {
    float pm25;
    float pm10;
    float co2;
    float voc;
    float o3;
    float no2;
    float so2;
} sensor_data_t;

class AQICalculator {
private:
    std::string standard;
    float pm25_breakpoints[6];
    float pm10_breakpoints[6];
    float co2_breakpoints[6];
    
    float calculate_aqi_for_pollutant(float concentration, float breakpoints[], const std::string& pollutant);
    std::string get_aqi_level(float aqi_value);
    std::string get_health_recommendation(float aqi_value, const std::string& dominant);
    
public:
    AQICalculator(const std::string& std = "EPA");
    
    aqi_data_t calculate_aqi(const sensor_data_t& sensor_data);
    void set_standard(const std::string& std);
    void set_pm25_breakpoints(float breakpoints[6]);
    void set_pm10_breakpoints(float breakpoints[6]);
    void set_co2_breakpoints(float breakpoints[6]);
};

#endif // AQI_CALCULATOR_H
```

```cpp
// sensors/aqi_calculator.cpp
#include "aqi_calculator.h"

AQICalculator::AQICalculator(const std::string& std) : standard(std) {
    // Set default EPA breakpoints
    float default_pm25[6] = {0, 12.0, 35.4, 55.4, 150.4, 250.4};
    float default_pm10[6] = {0, 54, 154, 254, 354, 424};
    float default_co2[6] = {0, 400, 1000, 5000, 10000, 40000};
    
    set_pm25_breakpoints(default_pm25);
    set_pm10_breakpoints(default_pm10);
    set_co2_breakpoints(default_co2);
}

aqi_data_t AQICalculator::calculate_aqi(const sensor_data_t& sensor_data) {
    aqi_data_t aqi_data;
    aqi_data.valid = true;
    
    // Calculate AQI for each pollutant
    float pm25_aqi = calculate_aqi_for_pollutant(sensor_data.pm25, pm25_breakpoints, "PM2.5");
    float pm10_aqi = calculate_aqi_for_pollutant(sensor_data.pm10, pm10_breakpoints, "PM10");
    float co2_aqi = calculate_aqi_for_pollutant(sensor_data.co2, co2_breakpoints, "CO2");
    
    // AQI is the maximum of individual AQI values
    aqi_data.value = std::max({pm25_aqi, pm10_aqi, co2_aqi});
    
    // Determine dominant pollutant
    if (aqi_data.value == pm25_aqi) {
        aqi_data.dominant_pollutant = "PM2.5";
    } else if (aqi_data.value == pm10_aqi) {
        aqi_data.dominant_pollutant = "PM10";
    } else if (aqi_data.value == co2_aqi) {
        aqi_data.dominant_pollutant = "CO2";
    } else {
        aqi_data.dominant_pollutant = "Unknown";
    }
    
    // Set level and recommendation
    aqi_data.level = get_aqi_level(aqi_data.value);
    aqi_data.recommendation = get_health_recommendation(aqi_data.value, aqi_data.dominant_pollutant);
    
    return aqi_data;
}

float AQICalculator::calculate_aqi_for_pollutant(float concentration, float breakpoints[], const std::string& pollutant) {
    if (concentration <= breakpoints[1]) {
        return (breakpoints[1] - breakpoints[0]) / breakpoints[0] * 50;
    } else if (concentration <= breakpoints[2]) {
        return 50 + (breakpoints[2] - breakpoints[1]) / (breakpoints[1] - breakpoints[0]) * 50;
    } else if (concentration <= breakpoints[3]) {
        return 100 + (breakpoints[3] - breakpoints[2]) / (breakpoints[2] - breakpoints[1]) * 50;
    } else if (concentration <= breakpoints[4]) {
        return 150 + (breakpoints[4] - breakpoints[3]) / (breakpoints[3] - breakpoints[2]) * 50;
    } else if (concentration <= breakpoints[5]) {
        return 200 + (breakpoints[5] - breakpoints[4]) / (breakpoints[4] - breakpoints[3]) * 100;
    } else {
        return 300 + (concentration - breakpoints[5]) / (breakpoints[5] - breakpoints[4]) * 100;
    }
}

std::string AQICalculator::get_aqi_level(float aqi_value) {
    if (aqi_value <= 50) return "Good";
    else if (aqi_value <= 100) return "Moderate";
    else if (aqi_value <= 150) return "Unhealthy for Sensitive Groups";
    else if (aqi_value <= 200) return "Unhealthy";
    else if (aqi_value <= 300) return "Very Unhealthy";
    else return "Hazardous";
}

std::string AQICalculator::get_health_recommendation(float aqi_value, const std::string& dominant) {
    if (aqi_value <= 50) {
        return "Air quality is satisfactory. Enjoy your outdoor activities!";
    } else if (aqi_value <= 100) {
        return "Air quality is acceptable for most people. Sensitive individuals should consider limiting prolonged outdoor exertion.";
    } else if (aqi_value <= 150) {
        return "Members of sensitive groups may experience health effects. General public is less likely to be affected.";
    } else if (aqi_value <= 200) {
        return "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects.";
    } else if (aqi_value <= 300) {
        return "Health warnings of emergency conditions. The entire population is more likely to be affected.";
    } else {
        return "Health alert: everyone may experience more serious health effects.";
    }
}
```

---

## Usage Examples

### Basic Air Quality Monitor
```cpp
#include "config/device_config.h"
#include "sensors/sensor_manager.h"
#include "communication/mqtt_client.h"

void setup() {
    Serial.begin(115200);
    
    // Load configuration
    DeviceConfig config;
    config.load();
    
    // Initialize sensor manager
    SensorManager sensor_manager;
    sensor_manager.init();
    
    // Create MQTT client
    MQTTClient mqtt(config.get_mqtt_broker(), 1883, config.get_device_id());
    mqtt.connect();
    
    Serial.println("Air quality monitor ready");
}

void loop() {
    // Read all sensors
    sensor_data_t sensor_data = sensor_manager.read_all_sensors();
    
    // Calculate AQI
    AQICalculator aqi_calc("EPA");
    aqi_data_t aqi_data = aqi_calc.calculate_aqi(sensor_data);
    
    // Create telemetry
    JsonObject telemetry;
    telemetry["device_id"] = config.get_device_id();
    telemetry["pm25"] = sensor_data.pm25;
    telemetry["pm10"] = sensor_data.pm10;
    telemetry["co2"] = sensor_data.co2;
    telemetry["aqi"] = aqi_data.value;
    telemetry["level"] = aqi_data.level;
    
    // Send to MQTT
    String payload;
    serializeJson(telemetry, payload);
    mqtt.publish("valtronics/telemetry", payload);
    
    delay(30000);  // Send every 30 seconds
}
```

### Advanced Monitor with Display
```cpp
#include "display/lcd_display.h"
#include "alerts/alert_manager.h"

void setup() {
    // Initialize display
    LCDDisplay lcd;
    lcd.init();
    lcd.show_welcome();
    
    // Initialize alerts
    AlertManager alerts;
    alerts.init();
    
    // Initialize sensors
    SensorManager sensors;
    sensors.init();
    
    Serial.println("Advanced air quality monitor ready");
}

void loop() {
    // Read sensors
    sensor_data_t data = sensors.read_all_sensors();
    
    // Calculate AQI
    AQICalculator aqi_calc;
    aqi_data_t aqi = aqi_calc.calculate_aqi(data);
    
    // Update display
    lcd.update(data, aqi);
    
    // Check alerts
    alerts.check_alerts(data, aqi);
    
    // Send telemetry
    send_telemetry(data, aqi);
    
    delay(30000);
}
```

---

## Testing

### Unit Tests
```cpp
void test_aqi_calculation() {
    AQICalculator aqi_calc("EPA");
    
    sensor_data_t test_data;
    test_data.pm25 = 25.0;
    test_data.pm10 = 45.0;
    test_data.co2 = 800.0;
    
    aqi_data_t aqi_data = aqi_calc.calculate_aqi(test_data);
    
    assert(aqi_data.valid);
    assert(aqi_data.value > 0);
    assert(!aqi_data.level.empty());
    assert(!aqi_data.dominant_pollutant.empty());
    assert(!aqi_data.recommendation.empty());
}

void test_sensor_reading() {
    SensorManager sensor_manager;
    assert(sensor_manager.init());
    
    sensor_data_t data = sensor_manager.read_all_sensors();
    assert(data.sensor_count > 0);
    assert(data.valid);
    
    // Validate ranges
    assert(data.pm25 >= 0 && data.pm25 <= 500);
    assert(data.pm10 >= 0 && data.pm10 <= 1000);
    assert(data.co2 >= 0 && data.co2 <= 5000);
}
```

### Integration Tests
```cpp
void test_end_to_end() {
    // Initialize all components
    DeviceConfig config;
    config.load();
    
    SensorManager sensors;
    sensors.init();
    
    MQTTC client(config.get_mqtt_broker(), 1883, config.get_device_id());
    client.connect();
    
    // Read sensors
    sensor_data_t data = sensors.read_all_sensors();
    
    // Calculate AQI
    AQICalculator aqi_calc;
    aqi_data_t aqi = aqi_calc.calculate_aqi(data);
    
    // Send telemetry
    JsonObject telemetry;
    telemetry["device_id"] = config.get_device_id();
    telemetry["pm25"] = data.pm25;
    telemetry["aqi"] = aqi.value;
    
    String payload;
    serializeJson(telemetry, payload);
    
    bool published = client.publish("test/telemetry", payload);
    assert(published);
    
    // Verify data
    assert(data.valid);
    assert(aqi.valid);
}
```

---

## Troubleshooting

### Common Issues

#### Sensor Communication Errors
```cpp
void debug_sensor_communication() {
    // Test I2C communication
    Wire.begin();
    
    // Scan for I2C devices
    byte error, address;
    for (address = 1; address < 127; address++) {
        Wire.beginTransmission(address);
        error = Wire.endTransmission();
        
        if (error == 0) {
            Serial.print("I2C device found at address: 0x");
            Serial.println(address, HEX);
        }
    }
    
    // Test UART communication
    Serial2.begin(9600);
    Serial2.println("AT");  // Test MH-Z19
    delay(1000);
    
    while (Serial2.available()) {
        char c = Serial2.read();
        Serial.print(c);
    }
}

void debug_sensor_data() {
    SensorManager sensors;
    sensors.init();
    
    sensor_data_t data = sensors.read_all_sensors();
    
    Serial.println("Sensor Data:");
    Serial.print("PM2.5: ");
    Serial.println(data.pm25);
    Serial.print("PM10: ");
    Serial.println(data.pm10);
    Serial.print("CO2: ");
    Serial.println(data.co2);
    
    // Validate ranges
    if (data.pm25 < 0 || data.pm25 > 500) {
        Serial.println("WARNING: PM2.5 out of range");
    }
    
    if (data.pm10 < 0 || data.pm10 > 1000) {
        Serial.println("WARNING: PM10 out of range");
    }
    
    if (data.co2 < 0 || data.co2 > 5000) {
        Serial.println("WARNING: CO2 out of range");
    }
}
```

#### AQI Calculation Issues
```cpp
void debug_aqi_calculation() {
    AQICalculator aqi_calc("EPA");
    
    // Test with known values
    sensor_data_t test_data;
    test_data.pm25 = 12.0;  // Should be AQI 50
    test_data.pm10 = 54.0;   // Should be AQI 50
    test_data.co2 = 400.0;   // Should be AQI 50
    
    aqi_data_t aqi = aqi_calc.calculate_aqi(test_data);
    
    Serial.println("AQI Test Results:");
    Serial.print("PM2.5: ");
    Serial.print(test_data.pm25);
    Serial.print(" -> AQI: ");
    Serial.println(aqi.value);
    Serial.print("Level: ");
    Serial.println(aqi.level);
    
    // Verify expected values
    assert(abs(aqi.value - 50) < 1);  // Allow small tolerance
    
    Serial.println("AQI calculation test passed");
}
```

---

## Support

For air quality monitor firmware support:
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **Platform Guides**: See `platform/*/` directories
- **Email**: firmware@valtronics.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Air Quality Monitor Firmware v2.0**
