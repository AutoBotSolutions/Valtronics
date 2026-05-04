# Firmware Development Guide

**Comprehensive guide for developing Valtronics firmware**

---

## Overview

This guide provides comprehensive information for developing firmware for Valtronics IoT devices, including setup, development workflows, best practices, and troubleshooting.

---

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Debugging](#debugging)
7. [Performance Optimization](#performance-optimization)
8. [Security](#security)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

---

## Development Environment Setup

### Prerequisites

#### Software Requirements
- **IDE**: PlatformIO IDE or Arduino IDE
- **Python**: 3.8+ (for build scripts and tools)
- **Git**: Version control
- **PlatformIO**: Cross-platform build system
- **ESP-IDF**: For ESP32 development (optional)

#### Hardware Requirements
- **Development Board**: ESP32, Arduino, or STM32
- **Programmer**: USB cable, ISP programmer (if needed)
- **Sensors**: Target sensors for testing
- **Power Supply**: Stable power source

### Installation

#### PlatformIO Installation
```bash
# Install PlatformIO CLI
pip install platformio

# Install PlatformIO IDE extension for VS Code
# Or use standalone PlatformIO IDE
```

#### ESP-IDF Installation (Optional)
```bash
# Clone ESP-IDF repository
git clone --recursive https://github.com/espressif/esp-idf.git

# Install ESP-IDF
cd esp-idf
./install.sh
source ./export.sh
```

#### Arduino IDE Setup
```bash
# Download Arduino IDE from https://www.arduino.cc/en/software
# Install required libraries:
# - PubSubClient
# - ArduinoJson
# - DHT sensor library
# - WiFiManager
# - ArduinoOTA
```

### Configuration

#### PlatformIO Project Configuration
```ini
# platformio.ini
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
build_flags = 
    -DCORE_DEBUG_LEVEL=3
    -DCONFIG_ARDUHAL_LOG_COLORS

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
```

#### VS Code Configuration
```json
// .vscode/settings.json
{
    "platformio-ide.autoRebuildAutocomplete": true,
    "platformio-ide.useNewTerminal": true,
    "files.associations": {
        "*.h": "cpp",
        "*.hpp": "cpp"
    }
}
```

---

## Project Structure

### Standard Structure
```
firmware/
├── platformio.ini               # PlatformIO configuration
├── src/                         # Source code
│   ├── main.cpp                 # Main application file
│   ├── config/                  # Configuration files
│   ├── drivers/                  # Hardware drivers
│   ├── sensors/                  # Sensor interfaces
│   ├── communication/            # Communication protocols
│   ├── utils/                    # Utility functions
│   └── platform/                 # Platform-specific code
├── lib/                         # Libraries
├── include/                     # Header files
├── test/                        # Unit tests
├── examples/                    # Example code
├── docs/                        # Documentation
└── build/                       # Build output
```

### File Naming Conventions
- **Headers**: `snake_case.h` (e.g., `temperature_sensor.h`)
- **Source**: `snake_case.cpp` (e.g., `temperature_sensor.cpp`)
- **Classes**: `PascalCase` (e.g., `TemperatureSensor`)
- **Functions**: `snake_case` (e.g., `read_temperature`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_SENSORS`)

---

## Development Workflow

### 1. Project Initialization
```bash
# Create new project
pio project init --board esp32dev

# Create directory structure
mkdir -p src/{config,drivers,sensors,communication,utils,platform}
mkdir -p lib test examples docs
```

### 2. Basic Implementation
```cpp
// src/main.cpp
#include <Arduino.h>
#include <ArduinoJson.h>
#include "config/device_config.h"
#include "sensors/temperature_sensor.h"
#include "communication/mqtt_client.h"

void setup() {
    Serial.begin(115200);
    Serial.println("Valtronics Device Starting...");
    
    // Initialize components
    if (!initialize_components()) {
        Serial.println("Initialization failed");
        return;
    }
    
    Serial.println("Device ready");
}

void loop() {
    // Main application logic
    handle_telemetry();
    handle_commands();
    delay(1000);
}

bool initialize_components() {
    // Initialize all components
    return true;
}

void handle_telemetry() {
    // Handle telemetry
}

void handle_commands() {
    // Handle commands
}
```

### 3. Build and Test
```bash
# Build project
pio run

# Upload to device
pio run --target upload

# Monitor serial output
pio device monitor

# Run tests
pio test
```

### 4. Version Control
```bash
# Initialize Git repository
git init
git add .
git commit -m "Initial commit"

# Create feature branch
git checkout -b feature/temperature-sensor

# Commit changes
git add .
git commit -m "Add temperature sensor support"

# Push to remote
git push origin feature/temperature-sensor
```

---

## Coding Standards

### General Guidelines

#### 1. Code Style
```cpp
// Good example
class TemperatureSensor {
private:
    uint8_t pin_;
    float calibration_offset_;
    
public:
    TemperatureSensor(uint8_t pin) : pin_(pin), calibration_offset_(0.0) {}
    
    float read_temperature() {
        float raw_value = analogRead(pin_);
        return raw_value * 0.1 + calibration_offset_;
    }
    
    void set_calibration_offset(float offset) {
        calibration_offset_ = offset;
    }
};
```

#### 2. Error Handling
```cpp
// Use return values for error handling
bool init_sensor() {
    if (!sensor.begin()) {
        Serial.println("Failed to initialize sensor");
        return false;
    }
    return true;
}

// Use assertions for debugging
void validate_temperature(float temp) {
    assert(temp > -40 && temp < 85);  // Valid range for DHT22
}
```

#### 3. Memory Management
```cpp
// Use static allocation when possible
static uint8_t buffer[1024];

// Use RAII for dynamic allocation
class SensorManager {
private:
    TemperatureSensor* sensor_;
    
public:
    SensorManager() : sensor_(new TemperatureSensor(4)) {}
    ~SensorManager() { delete sensor_; }
};
```

### Documentation Standards

#### 1. Header Files
```cpp
/**
 * @file temperature_sensor.h
 * @brief Temperature sensor interface
 * @author Valtronics Team
 * @version 1.0.0
 * @date 2024-01-01
 */

#ifndef TEMPERATURE_SENSOR_H
#define TEMPERATURE_SENSOR_H

#include <stdint.h>

/**
 * @brief Temperature sensor class
 * 
 * This class provides interface for reading temperature
 * from various temperature sensors.
 */
class TemperatureSensor {
public:
    /**
     * @brief Constructor
     * @param pin Analog pin number
     */
    TemperatureSensor(uint8_t pin);
    
    /**
     * @brief Read temperature
     * @return Temperature in Celsius
     */
    float read_temperature();
    
private:
    uint8_t pin_;  ///< Analog pin number
};

#endif // TEMPERATURE_SENSOR_H
```

#### 2. Implementation Files
```cpp
/**
 * @file temperature_sensor.cpp
 * @brief Temperature sensor implementation
 */

#include "temperature_sensor.h"
#include "utils/logger.h"

TemperatureSensor::TemperatureSensor(uint8_t pin) : pin_(pin) {
    Logger::info("Temperature sensor initialized on pin " + String(pin));
}

float TemperatureSensor::read_temperature() {
    int raw_value = analogRead(pin_);
    float temperature = raw_value * 0.1;  // Convert to Celsius
    
    Logger::debug("Temperature: " + String(temperature) + "°C");
    return temperature;
}
```

---

## Testing

### Unit Testing

#### 1. Test Structure
```cpp
// test/test_temperature_sensor.cpp
#include <unity.h>
#include "sensors/temperature_sensor.h"

TemperatureSensor* sensor;

void setUp(void) {
    sensor = new TemperatureSensor(A0);
}

void tearDown(void) {
    delete sensor;
}

void test_temperature_reading(void) {
    float temp = sensor->read_temperature();
    TEST_ASSERT_TRUE(temp > -40 && temp < 85);  // Valid range
}

void test_calibration_offset(void) {
    sensor->set_calibration_offset(5.0);
    float temp = sensor->read_temperature();
    // Test calibration effect
    TEST_ASSERT_TRUE(temp > 0);  // Should be positive after offset
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_temperature_reading);
    RUN_TEST(test_calibration_offset);
    return UNITY_END();
}
```

#### 2. Test Configuration
```ini
# platformio.ini
[env:native]
platform = native
test_framework = unity
test_build_project_src = true
build_flags = 
    -DUNIT_TEST
```

### Integration Testing

#### 1. Integration Test Example
```cpp
// test/integration/test_sensor_to_mqtt.cpp
#include <unity.h>
#include "sensors/temperature_sensor.h"
#include "communication/mqtt_client.h"

void test_sensor_to_mqtt_integration(void) {
    // Initialize sensor
    TemperatureSensor sensor(A0);
    TEST_ASSERT_TRUE(sensor.init());
    
    // Initialize MQTT
    MQTTClient mqtt("test.mqtt.com", 1883, "test-device");
    TEST_ASSERT_TRUE(mqtt.connect());
    
    // Read sensor
    float temp = sensor.read_temperature();
    TEST_ASSERT_TRUE(temp > -40 && temp < 85);
    
    // Send telemetry
    bool sent = mqtt.publish("test/temperature", String(temp));
    TEST_ASSERT_TRUE(sent);
    
    // Cleanup
    mqtt.disconnect();
}

int main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_sensor_to_mqtt_integration);
    return UNITY_END();
}
```

### Hardware Testing

#### 1. Hardware Test Framework
```cpp
// test/hardware/test_hardware.cpp
#include "test_hardware.h"

bool test_sensor_hardware() {
    Serial.println("Testing sensor hardware...");
    
    // Test sensor connectivity
    if (!test_sensor_connectivity()) {
        Serial.println("Sensor connectivity test failed");
        return false;
    }
    
    // Test sensor readings
    if (!test_sensor_readings()) {
        Serial.println("Sensor readings test failed");
        return false;
    }
    
    Serial.println("Hardware tests passed");
    return true;
}

bool test_sensor_connectivity() {
    // Implementation depends on sensor type
    return true;
}

bool test_sensor_readings() {
    // Read multiple times and check for valid ranges
    for (int i = 0; i < 10; i++) {
        float reading = read_sensor();
        if (reading < -40 || reading > 85) {
            return false;
        }
        delay(100);
    }
    return true;
}
```

---

## Debugging

### Serial Debugging

#### 1. Debug Output
```cpp
#include "utils/logger.h"

void debug_function() {
    Logger::debug("Starting debug function");
    
    int value = 42;
    Logger::debug("Value: " + String(value));
    
    if (value > 40) {
        Logger::warning("Value is greater than 40");
    }
    
    Logger::debug("Debug function completed");
}
```

#### 2. Debug Macros
```cpp
// utils/debug.h
#ifndef DEBUG_H
#define DEBUG_H

#ifdef DEBUG
    #define DEBUG_PRINT(x) Serial.print(x)
    #define DEBUG_PRINTLN(x) Serial.println(x)
    #define DEBUG_ASSERT(x) assert(x)
#else
    #define DEBUG_PRINT(x)
    #define DEBUG_PRINTLN(x)
    #define DEBUG_ASSERT(x)
#endif

#endif // DEBUG_H
```

### Remote Debugging

#### 1. Web Debug Interface
```cpp
#include <WebServer.h>
#include <ArduinoJson.h>

WebServer server(80);

void setup_debug_server() {
    server.on("/debug", HTTP_GET, []() {
        JsonObject debug_info;
        debug_info["free_heap"] = ESP.getFreeHeap();
        debug_info["uptime"] = millis();
        debug_info["wifi_rssi"] = WiFi.RSSI();
        
        String response;
        serializeJson(debug_info, response);
        
        server.send(200, "application/json", response);
    });
    
    server.begin();
}

void loop() {
    server.handleClient();
}
```

#### 2. Remote Logging
```cpp
void send_debug_log(const String& message) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin("http://debug.valtronics.com/log");
        http.addHeader("Content-Type", "application/json");
        
        JsonObject log_entry;
        log_entry["device_id"] = "VT-DEVICE-001";
        log_entry["message"] = message;
        log_entry["timestamp"] = millis();
        
        String payload;
        serializeJson(log_entry, payload);
        
        int httpCode = http.POST(payload);
        http.end();
    }
}
```

---

## Performance Optimization

### Memory Optimization

#### 1. Memory Usage Monitoring
```cpp
#include "utils/memory_monitor.h"

void monitor_memory_usage() {
    uint32_t free_heap = ESP.getFreeHeap();
    uint32_t min_free_heap = ESP.getMinFreeHeap();
    
    Logger::info("Free heap: " + String(free_heap) + " bytes");
    Logger::info("Min free heap: " + String(min_free_heap) + " bytes");
    
    if (free_heap < 1000) {
        Logger::warning("Low memory detected");
    }
}
```

#### 2. Memory Optimization Techniques
```cpp
// Use static allocation
static uint8_t sensor_buffer[256];

// Use PROGMEM for constants
const char* const SENSOR_NAMES[] PROGMEM = {
    "Temperature",
    "Humidity",
    "Pressure"
};

// Use efficient data structures
struct CompactTelemetry {
    uint16_t temperature;  // 0.1°C resolution
    uint16_t humidity;     // 0.1% resolution
    uint32_t timestamp;
};
```

### CPU Optimization

#### 1. Task Scheduling
```cpp
#include "utils/task_scheduler.h"

void setup_tasks() {
    // Create tasks with different priorities
    xTaskCreate(
        sensor_task,      // Function
        "SensorTask",     // Name
        2048,             // Stack size
        NULL,             // Parameters
        1,                // Priority
        NULL              // Handle
    );
    
    xTaskCreate(
        mqtt_task,
        "MQTTTask",
        4096,
        NULL,
        2,
        NULL
    );
}

void sensor_task(void* parameters) {
    while (1) {
        // Read sensors
        read_sensors();
        
        // Yield to other tasks
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
```

#### 2. Efficient Algorithms
```cpp
// Use lookup tables instead of calculations
const float voltage_to_temp[] = {
    -40.0, -39.5, -39.0, ..., 85.0  // Pre-calculated values
};

float get_temperature_from_voltage(int voltage) {
    if (voltage >= 0 && voltage < 1024) {
        return voltage_to_temp[voltage];
    }
    return NAN;
}

// Use bit operations for flags
#define SENSOR_CONNECTED  (1 << 0)
#define SENSOR_CALIBRATED (1 << 1)
#define SENSOR_ERROR      (1 << 2)

uint8_t sensor_flags = 0;

bool is_sensor_connected() {
    return sensor_flags & SENSOR_CONNECTED;
}
```

---

## Security

### Secure Communication

#### 1. MQTT Security
```cpp
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

WiFiClientSecure wifi_client;
PubSubClient mqtt_client(wifi_client);

void setup_secure_mqtt() {
    // Set CA certificate
    wifi_client.setCACert(ca_cert);
    
    // Set client certificate
    wifi_client.setCertificate(client_cert);
    wifi_client.setPrivateKey(private_key);
    
    // Connect to secure MQTT broker
    mqtt_client.setServer("mqtts://mqtt.valtronics.com", 8883);
    
    if (mqtt_client.connect("VT-DEVICE-001")) {
        Logger::info("Connected to secure MQTT broker");
    }
}
```

#### 2. Data Encryption
```cpp
#include "utils/encryption.h"

void send_encrypted_telemetry(const String& data) {
    // Encrypt data
    String encrypted_data = encrypt_data(data);
    
    // Send encrypted data
    mqtt_client.publish("valtronics/telemetry/encrypted", encrypted_data);
}

String encrypt_data(const String& data) {
    // Simple XOR encryption (use proper encryption in production)
    String encrypted = "";
    for (int i = 0; i < data.length(); i++) {
        encrypted += (char)(data[i] ^ 0xAA);
    }
    return encrypted;
}
```

### Device Security

#### 1. Secure Boot
```cpp
void setup_secure_boot() {
    // Enable secure boot
    esp_secure_boot_enable();
    
    // Verify firmware signature
    if (!verify_firmware_signature()) {
        Logger::error("Firmware signature verification failed");
        ESP.restart();
    }
}

bool verify_firmware_signature() {
    // Implementation depends on platform
    return true;
}
```

#### 2. Access Control
```cpp
#include "utils/access_control.h"

bool authenticate_device(const String& token) {
    // Validate token with server
    HTTPClient http;
    http.begin("https://api.valtronics.com/auth/validate");
    http.addHeader("Authorization", "Bearer " + token);
    
    int httpCode = http.GET();
    bool valid = (httpCode == 200);
    
    http.end();
    return valid;
}
```

---

## Deployment

### Build Process

#### 1. Automated Build
```bash
#!/bin/bash
# build.sh

echo "Building Valtronics firmware..."

# Clean previous build
pio run --target clean

# Build for all platforms
pio run -e esp32
pio run -e arduino_mega

# Run tests
pio test

echo "Build completed successfully"
```

#### 2. Release Management
```bash
#!/bin/bash
# release.sh

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: ./release.sh <version>"
    exit 1
fi

echo "Creating release $VERSION..."

# Update version
echo "#define FIRMWARE_VERSION \"$VERSION\"" > src/version.h

# Build release
pio run --environment esp32

# Create release package
mkdir -p releases/$VERSION
cp .pio/build/esp32/firmware.bin releases/$VERSION/
cp platformio.ini releases/$VERSION/
cp README.md releases/$VERSION/

echo "Release $VERSION created"
```

### OTA Updates

#### 1. OTA Configuration
```cpp
#include <ArduinoOTA.h>

void setup_ota() {
    ArduinoOTA.setHostname("valtronics-device");
    ArduinoOTA.setPassword("secure_password");
    
    ArduinoOTA.onStart([]() {
        Logger::info("OTA update starting");
    });
    
    ArduinoOTA.onEnd([]() {
        Logger::info("OTA update completed");
        ESP.restart();
    });
    
    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        Logger::info("OTA progress: " + String(progress) + "%");
    });
    
    ArduinoOTA.onError([](ota_error_t error) {
        Logger::error("OTA error: " + String(error));
    });
    
    ArduinoOTA.begin();
}
```

#### 2. Update Server
```cpp
void check_for_updates() {
    HTTPClient http;
    http.begin("https://api.valtronics.com/firmware/check");
    http.addHeader("X-Device-ID", "VT-DEVICE-001");
    http.addHeader("X-Firmware-Version", FIRMWARE_VERSION);
    
    int httpCode = http.GET();
    if (httpCode == 200) {
        String response = http.getString();
        DynamicJsonDocument doc(256);
        deserializeJson(doc, response);
        
        if (doc["update_available"]) {
            String firmware_url = doc["firmware_url"];
            download_and_install_firmware(firmware_url);
        }
    }
    
    http.end();
}
```

---

## Troubleshooting

### Common Issues

#### 1. Build Errors
```bash
# Error: Library not found
# Solution: Install missing library
pio lib install "PubSubClient"

# Error: Out of memory
# Solution: Optimize memory usage
# - Reduce buffer sizes
# - Use PROGMEM for constants
# - Free unused objects

# Error: Upload failed
# Solution: Check hardware connections
# - Verify USB cable
# - Check driver installation
# - Try different USB port
```

#### 2. Runtime Errors
```cpp
// Memory corruption
void debug_memory_corruption() {
    // Add memory checks
    uint32_t* test_ptr = new uint32_t;
    *test_ptr = 0xDEADBEEF;
    
    if (*test_ptr != 0xDEADBEEF) {
        Logger::error("Memory corruption detected");
    }
    
    delete test_ptr;
}

// Stack overflow
void check_stack_usage() {
    uint32_t stack_size = uxTaskGetStackHighWaterMark(NULL);
    Logger::info("Stack usage: " + String(stack_size) + " bytes");
    
    if (stack_size < 100) {
        Logger::warning("Stack nearly full");
    }
}
```

#### 3. Communication Issues
```cpp
// MQTT connection issues
void debug_mqtt_connection() {
    Logger::info("MQTT connection debug:");
    Logger::info("Broker: " + mqtt_broker);
    Logger::info("Port: " + String(mqtt_port));
    Logger::info("Client ID: " + client_id);
    Logger::info("WiFi status: " + String(WiFi.status()));
    
    if (!mqtt_client.connected()) {
        Logger::error("MQTT not connected");
        Logger::error("MQTT state: " + String(mqtt_client.state()));
    }
}

// WiFi connection issues
void debug_wifi_connection() {
    Logger::info("WiFi connection debug:");
    Logger::info("SSID: " + WiFi.SSID());
    Logger::info("RSSI: " + String(WiFi.RSSI()));
    Logger::info("IP: " + WiFi.localIP().toString());
    
    if (WiFi.status() != WL_CONNECTED) {
        Logger::error("WiFi not connected");
        
        // Scan networks
        int n = WiFi.scanNetworks();
        Logger::info("Available networks:");
        for (int i = 0; i < n; i++) {
            Logger::info("  " + WiFi.SSID(i) + " (" + String(WiFi.RSSI(i)) + " dBm)");
        }
    }
}
```

### Debug Tools

#### 1. Logic Analyzer
```cpp
// Use GPIO pins for debugging
#define DEBUG_PIN_1 25
#define DEBUG_PIN_2 26

void setup_debug_pins() {
    pinMode(DEBUG_PIN_1, OUTPUT);
    pinMode(DEBUG_PIN_2, OUTPUT);
}

void debug_signal_start() {
    digitalWrite(DEBUG_PIN_1, HIGH);
}

void debug_signal_end() {
    digitalWrite(DEBUG_PIN_1, LOW);
}

void debug_pulse() {
    digitalWrite(DEBUG_PIN_2, HIGH);
    delayMicroseconds(10);
    digitalWrite(DEBUG_PIN_2, LOW);
}
```

#### 2. Performance Profiling
```cpp
#include "utils/profiler.h"

void profile_function() {
    Profiler profiler("function_name");
    
    // Function to profile
    expensive_operation();
    
    // Profiler automatically logs timing when it goes out of scope
}

class Profiler {
private:
    String name;
    uint32_t start_time;
    
public:
    Profiler(const String& func_name) : name(func_name) {
        start_time = millis();
    }
    
    ~Profiler() {
        uint32_t duration = millis() - start_time;
        Logger::info(name + " took " + String(duration) + " ms");
    }
};
```

---

## Best Practices

### 1. Code Organization
- Use clear directory structure
- Separate platform-specific code
- Use header guards properly
- Keep functions small and focused

### 2. Error Handling
- Check return values
- Use appropriate error codes
- Log errors with context
- Implement graceful degradation

### 3. Resource Management
- Use RAII for automatic cleanup
- Monitor memory usage
- Implement watchdog timer
- Handle power failures gracefully

### 4. Security
- Validate all inputs
- Use secure communication
- Implement access control
- Keep firmware updated

### 5. Testing
- Write unit tests for all functions
- Test error conditions
- Perform integration testing
- Test on actual hardware

---

## Support

For firmware development support:
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **Community**: GitHub Discussions
- **Email**: firmware@valtronics.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Firmware Development Guide v1.0**
