# ESP32 Platform Firmware

**ESP32-based firmware for Valtronics IoT devices**

---

## Overview

ESP32 is the primary platform for Valtronics devices, offering built-in WiFi, Bluetooth, and extensive peripheral support. This platform provides the foundation for most Valtronics sensor devices and gateways.

---

## Features

### Hardware Features
- **WiFi**: 802.11 b/g/n, 2.4 GHz
- **Bluetooth**: BLE and Classic Bluetooth
- **CPU**: Dual-core Xtensa LX6, 240 MHz
- **Memory**: 520 KB SRAM, 4-16 MB Flash
- **Peripherals**: GPIO, ADC, DAC, I2C, SPI, UART, I2S
- **Power**: Deep sleep mode, ultra-low power coprocessor

### Software Features
- **Framework**: ESP-IDF, Arduino Framework
- **Connectivity**: WiFi, MQTT, HTTP, WebSocket
- **Security**: TLS/SSL, WPA2, Secure Boot
- **OTA Updates**: Over-the-air firmware updates
- **Power Management**: Deep sleep, light sleep

---

## Directory Structure

```
platform/esp32/
├── README.md                    # This file
├── platformio.ini               # PlatformIO configuration
├── src/                         # Source code
│   ├── main.cpp                 # Main application
│   ├── config/                  # Configuration
│   ├── drivers/                 # Hardware drivers
│   ├── sensors/                  # Sensor interfaces
│   ├── communication/            # Communication protocols
│   └── utils/                    # Utility functions
├── lib/                         # Libraries
├── test/                        # Tests
├── docs/                        # Documentation
└── examples/                    # Example applications
```

---

## Quick Start

### 1. Setup Development Environment
```bash
# Install ESP-IDF
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh
source ./export.sh

# Or use PlatformIO (recommended)
pip install platformio
```

### 2. Create New Project
```bash
# Using PlatformIO
pio project init --board esp32dev

# Using ESP-IDF
idf.py create-project valtronics-esp32
cd valtronics-esp32
```

### 3. Configure Project
```ini
# platformio.ini
[env:esp32dev]
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
    ESP32WebServer
    ArduinoOTA
    BSEC Software Library
    Adafruit BME280 Library
build_flags = 
    -DCORE_DEBUG_LEVEL=3
    -DCONFIG_ARDUHAL_LOG_COLORS
```

### 4. Write Firmware
```cpp
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <WiFiManager.h>
#include <ArduinoOTA.h>

// Device configuration
#define DEVICE_ID "VT-ESP32-001"
#define MQTT_CLIENT_ID "VT-ESP32-001"
#define MQTT_BROKER "mqtt.valtronics.com"
#define MQTT_PORT 1883

// Global variables
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
WiFiManager wifiManager;

void setup() {
    Serial.begin(115200);
    Serial.println("Valtronics ESP32 Device Starting...");
    
    // Setup WiFi
    setupWiFi();
    
    // Setup MQTT
    setupMQTT();
    
    // Setup OTA
    setupOTA();
    
    Serial.println("Device ready!");
}

void loop() {
    // Handle WiFi
    if (WiFi.status() != WL_CONNECTED) {
        setupWiFi();
    }
    
    // Handle MQTT
    if (!mqttClient.connected()) {
        setupMQTT();
    }
    mqttClient.loop();
    
    // Handle OTA
    ArduinoOTA.handle();
    
    // Main application logic
    handleApplication();
    
    delay(1000);
}

void setupWiFi() {
    // WiFiManager setup
    wifiManager.setDebugOutput(false);
    wifiManager.setAPStaticIPConfig(IPAddress(192, 168, 1, 1), 
                                    IPAddress(192, 168, 1, 1), 
                                    IPAddress(255, 255, 255, 0));
    
    // Connect to WiFi
    if (!wifiManager.autoConnect("Valtronics-Setup")) {
        Serial.println("Failed to connect to WiFi");
        ESP.restart();
    }
    
    Serial.println("WiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
}

void setupMQTT() {
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
    mqttClient.setCallback(mqttCallback);
    
    if (mqttClient.connect(MQTT_CLIENT_ID)) {
        Serial.println("Connected to MQTT broker");
        
        // Subscribe to topics
        mqttClient.subscribe("valtronics/devices/" DEVICE_ID "/commands");
        mqttClient.subscribe("valtronics/devices/" DEVICE_ID "/config");
    } else {
        Serial.println("Failed to connect to MQTT broker");
    }
}

void setupOTA() {
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
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.print("Message arrived [");
    Serial.print(topic);
    Serial.print("] ");
    Serial.println(message);
    
    // Handle commands
    if (String(topic) == "valtronics/devices/" DEVICE_ID "/commands") {
        handleCommand(message);
    }
    
    // Handle configuration
    if (String(topic) == "valtronics/devices/" DEVICE_ID "/config") {
        handleConfig(message);
    }
}

void handleCommand(String command) {
    StaticJsonDocument<200> doc;
    deserializeJson(doc, command);
    
    String cmd = doc["command"];
    
    if (cmd == "reboot") {
        Serial.println("Rebooting device...");
        ESP.restart();
    } else if (cmd == "sleep") {
        int duration = doc["duration"] | 30;
        Serial.printf("Entering deep sleep for %d seconds\n", duration);
        ESP.deepSleep(duration * 1000000);
    } else if (cmd == "update") {
        Serial.println("Starting OTA update...");
        // OTA update will be handled by ArduinoOTA
    }
}

void handleConfig(String config) {
    StaticJsonDocument<200> doc;
    deserializeJson(doc, config);
    
    // Update configuration
    if (doc.containsKey("telemetry_interval")) {
        int interval = doc["telemetry_interval"];
        // Update telemetry interval
    }
    
    if (doc.containsKey("mqtt_broker")) {
        String broker = doc["mqtt_broker"];
        // Update MQTT broker
    }
    
    Serial.println("Configuration updated");
}

void handleApplication() {
    // Read sensors
    float temperature = readTemperature();
    float humidity = readHumidity();
    
    // Create telemetry payload
    StaticJsonDocument<300> telemetry;
    telemetry["device_id"] = DEVICE_ID;
    telemetry["timestamp"] = millis();
    telemetry["temperature"] = temperature;
    telemetry["humidity"] = humidity;
    telemetry["wifi_rssi"] = WiFi.RSSI();
    telemetry["free_heap"] = ESP.getFreeHeap();
    
    // Publish telemetry
    char payload[300];
    serializeJson(telemetry, payload);
    mqttClient.publish("valtronics/telemetry", payload);
}

float readTemperature() {
    // Implement temperature sensor reading
    return 22.5 + (random(0, 100) - 50) / 10.0;
}

float readHumidity() {
    // Implement humidity sensor reading
    return 45.0 + (random(0, 100) - 50) / 10.0;
}
```

---

## Sensor Integration

### DHT22 Temperature/Humidity Sensor
```cpp
#include <DHT.h>

#define DHT_PIN 4
#define DHT_TYPE DHT22

DHT dht(DHT_PIN, DHT_TYPE);

void setupDHT() {
    dht.begin();
}

float readTemperature() {
    float temp = dht.readTemperature();
    if (isnan(temp)) {
        Serial.println("Failed to read temperature from DHT sensor!");
        return NAN;
    }
    return temp;
}

float readHumidity() {
    float humidity = dht.readHumidity();
    if (isnan(humidity)) {
        Serial.println("Failed to read humidity from DHT sensor!");
        return NAN;
    }
    return humidity;
}
```

### BME280 Environmental Sensor
```cpp
#include <Adafruit_BME280.h>
#include <Wire.h>

Adafruit_BME280 bme;

void setupBME280() {
    if (!bme.begin(0x76)) {
        Serial.println("Could not find a valid BME280 sensor, check wiring!");
        return;
    }
    
    bme.setSampling(Adafruit_BME280::MODE_NORMAL,
                    Adafruit_BME280::SAMPLING_X2,  // temperature
                    Adafruit_BME280::SAMPLING_X16, // pressure
                    Adafruit_BME280::SAMPLING_X1,  // humidity
                    Adafruit_BME280::FILTER_X16,
                    Adafruit_BME280::STANDBY_MS_0_5);
}

struct BME280Data readBME280() {
    BME280Data data;
    data.temperature = bme.readTemperature();
    data.humidity = bme.readHumidity();
    data.pressure = bme.readPressure() / 100.0F;  // Convert to hPa
    data.altitude = bme.readAltitude(1013.25);
    return data;
}
```

### PMS5003 Air Quality Sensor
```cpp
#include <SoftwareSerial.h>

#define PMS5003_RX 16
#define PMS5003_TX 17

SoftwareSerial pmsSerial(PMS5003_RX, PMS5003_TX);

struct PMS5003Data {
    uint16_t pm1_0;
    uint16_t pm2_5;
    uint16_t pm10;
};

void setupPMS5003() {
    pmsSerial.begin(9600);
}

PMS5003Data readPMS5003() {
    PMS5003Data data = {0, 0, 0};
    
    if (pmsSerial.available()) {
        uint8_t buffer[32];
        if (pmsSerial.readBytes(buffer, 32) == 32) {
            if (buffer[0] == 0x42 && buffer[1] == 0x4D) {
                data.pm1_0 = (buffer[10] << 8) | buffer[11];
                data.pm2_5 = (buffer[12] << 8) | buffer[13];
                data.pm10 = (buffer[14] << 8) | buffer[15];
            }
        }
    }
    
    return data;
}
```

---

## Power Management

### Deep Sleep Mode
```cpp
#include "esp_sleep.h"

#define DEEP_SLEEP_DURATION 30  // seconds

void enterDeepSleep() {
    Serial.println("Entering deep sleep...");
    
    // Configure wake up source
    esp_sleep_enable_timer_wakeup(DEEP_SLEEP_DURATION * 1000000);
    
    // Enter deep sleep
    esp_deep_sleep_start();
}

void setup() {
    Serial.begin(115200);
    
    // Check wake up reason
    esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();
    
    switch(wakeup_reason) {
        case ESP_SLEEP_WAKEUP_TIMER:
            Serial.println("Wakeup caused by timer");
            break;
        case ESP_SLEEP_WAKEUP_EXT0:
            Serial.println("Wakeup caused by external signal using RTC_IO");
            break;
        default:
            Serial.printf("Wakeup was not caused by deep sleep: %d\n", wakeup_reason);
            break;
    }
    
    // Main application logic
    handleApplication();
    
    // Enter deep sleep
    enterDeepSleep();
}
```

### Light Sleep Mode
```cpp
#include "esp_sleep.h"

void enterLightSleep() {
    Serial.println("Entering light sleep...");
    
    // Configure light sleep
    esp_sleep_enable_timer_wakeup(5000000);  // 5 seconds
    
    // Enter light sleep
    esp_light_sleep_start();
    
    // This code will execute after waking up
    Serial.println("Woke up from light sleep");
}
```

---

## OTA Updates

### Basic OTA Setup
```cpp
#include <ArduinoOTA.h>

void setupOTA() {
    ArduinoOTA.setHostname("valtronics-esp32");
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
}

void loop() {
    ArduinoOTA.handle();
    // Other loop code
}
```

---

## Security

### WiFi Security
```cpp
#include <WiFi.h>

void setupSecureWiFi() {
    // Use WPA2 Enterprise
    WiFi.begin("SSID", "password");
    
    // Set static IP
    IPAddress local_IP(192, 168, 1, 100);
    IPAddress gateway(192, 168, 1, 1);
    IPAddress subnet(255, 255, 255, 0);
    WiFi.config(local_IP, gateway, subnet);
    
    // Wait for connection
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
}
```

### MQTT Security
```cpp
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

WiFiClientSecure wifiClientSecure;
PubSubClient mqttClientSecure(wifiClientSecure);

void setupSecureMQTT() {
    // Set CA certificate
    wifiClientSecure.setCACert(ca_cert);
    
    // Set client certificate
    wifiClientSecure.setCertificate(client_cert);
    
    // Set private key
    wifiClientSecure.setPrivateKey(private_key);
    
    mqttClientSecure.setServer("mqtt.valtronics.com", 8883);
    
    if (mqttClientSecure.connect("VT-ESP32-001")) {
        Serial.println("Connected to secure MQTT broker");
    }
}
```

---

## Debugging

### Serial Debugging
```cpp
#include "esp_log.h"

#define TAG "VALTRONICS"

void setup() {
    Serial.begin(115200);
    ESP_LOGI(TAG, "Device starting...");
}

void loop() {
    ESP_LOGI(TAG, "Loop iteration");
    ESP_LOGD(TAG, "Debug information");
    ESP_LOGW(TAG, "Warning message");
    ESP_LOGE(TAG, "Error message");
    
    delay(1000);
}
```

### Remote Debugging
```cpp
#include <WebServer.h>
#include <ArduinoJson.h>

WebServer server(80);

void setupRemoteDebug() {
    server.on("/debug", HTTP_GET, []() {
        StaticJsonDocument<512> doc;
        
        // System information
        doc["chip_id"] = ESP.getChipId();
        doc["flash_size"] = ESP.getFlashChipSize();
        doc["free_heap"] = ESP.getFreeHeap();
        doc["cpu_freq"] = ESP.getCpuFreqMHz();
        doc["wifi_rssi"] = WiFi.RSSI();
        doc["uptime"] = millis();
        
        // Task information
        doc["task_count"] = uxTaskGetNumberOfTasks();
        
        String response;
        serializeJson(doc, response);
        
        server.send(200, "application/json", response);
    });
    
    server.begin();
}

void loop() {
    server.handleClient();
}
```

---

## Testing

### Unit Tests
```cpp
#include <unity.h>

void test_temperature_reading() {
    float temp = readTemperature();
    TEST_ASSERT_TRUE(temp > -40 && temp < 85);  // Valid range for DHT22
}

void test_mqtt_connection() {
    TEST_ASSERT_TRUE(mqttClient.connected());
}

void setup() {
    UNITY_BEGIN();
    RUN_TEST(test_temperature_reading);
    RUN_TEST(test_mqtt_connection);
    UNITY_END();
}

void loop() {
    // Tests run in setup()
}
```

### Integration Tests
```cpp
void test_sensor_integration() {
    // Test all sensors
    float temp = readTemperature();
    float humidity = readHumidity();
    
    TEST_ASSERT_FALSE(isnan(temp));
    TEST_ASSERT_FALSE(isnan(humidity));
    
    // Test MQTT publishing
    StaticJsonDocument<200> doc;
    doc["temperature"] = temp;
    doc["humidity"] = humidity;
    
    char payload[200];
    serializeJson(doc, payload);
    
    TEST_ASSERT_TRUE(mqttClient.publish("test/telemetry", payload));
}
```

---

## Performance Optimization

### Memory Management
```cpp
// Use static allocation for large objects
static uint8_t buffer[1024];

// Use PSRAM if available
#if CONFIG_SPIRAM_SUPPORT
  uint8_t* psram_buffer = (uint8_t*)ps_malloc(1024);
#endif

// Monitor memory usage
void printMemoryUsage() {
    Serial.printf("Free heap: %d bytes\n", ESP.getFreeHeap());
    Serial.printf("Min free heap: %d bytes\n", ESP.getMinFreeHeap());
    Serial.printf("Largest free block: %d bytes\n", ESP.getMaxAllocHeap());
}
```

### CPU Optimization
```cpp
// Use FreeRTOS tasks for concurrent operations
TaskHandle_t sensorTaskHandle;
TaskHandle_t mqttTaskHandle;

void sensorTask(void *parameter) {
    while (1) {
        // Read sensors
        handleSensors();
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void mqttTask(void *parameter) {
    while (1) {
        // Handle MQTT
        handleMQTT();
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void setup() {
    xTaskCreate(sensorTask, "SensorTask", 2048, NULL, 1, &sensorTaskHandle);
    xTaskCreate(mqttTask, "MQTTTask", 2048, NULL, 1, &mqttTaskHandle);
}
```

---

## Troubleshooting

### Common Issues

#### WiFi Connection Problems
```cpp
void debugWiFi() {
    Serial.println("WiFi Status:");
    Serial.printf("SSID: %s\n", WiFi.SSID().c_str());
    Serial.printf("RSSI: %d dBm\n", WiFi.RSSI());
    Serial.printf("Channel: %d\n", WiFi.channel());
    Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());
    
    // Scan networks
    int n = WiFi.scanNetworks();
    Serial.println("Available networks:");
    for (int i = 0; i < n; i++) {
        Serial.printf("%d: %s (%d dBm)\n", i + 1, WiFi.SSID(i).c_str(), WiFi.RSSI(i));
    }
}
```

#### MQTT Connection Issues
```cpp
void debugMQTT() {
    Serial.println("MQTT Status:");
    Serial.printf("Connected: %s\n", mqttClient.connected() ? "Yes" : "No");
    Serial.printf("Server: %s:%d\n", MQTT_BROKER, MQTT_PORT);
    Serial.printf("Client ID: %s\n", MQTT_CLIENT_ID);
    
    // Test connection
    if (!mqttClient.connected()) {
        Serial.println("Attempting to connect...");
        if (mqttClient.connect(MQTT_CLIENT_ID)) {
            Serial.println("Connection successful");
        } else {
            Serial.printf("Connection failed, state: %d\n", mqttClient.state());
        }
    }
}
```

---

## Support

For ESP32 firmware support:
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **Community**: ESP32 Forum
- **Email**: firmware@valtronics.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**ESP32 Platform Firmware v1.0**
