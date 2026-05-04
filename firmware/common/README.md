# Common Firmware Components

**Shared components and utilities for Valtronics firmware**

---

## Overview

This directory contains common firmware components that can be used across different platforms (ESP32, Arduino, STM32, etc.). These components provide standardized interfaces for sensors, communication, power management, and utility functions.

---

## Directory Structure

```
common/
├── README.md                    # This file
├── hal/                         # Hardware Abstraction Layer
│   ├── gpio/                    # GPIO abstraction
│   ├── adc/                     # ADC abstraction
│   ├── i2c/                     # I2C abstraction
│   ├── spi/                     # SPI abstraction
│   └── uart/                    # UART abstraction
├── drivers/                     # Device drivers
│   ├── sensors/                  # Sensor drivers
│   ├── communications/           # Communication drivers
│   ├── storage/                  # Storage drivers
│   └── power/                    # Power management drivers
├── sensors/                      # Sensor interfaces
│   ├── temperature/              # Temperature sensors
│   ├── humidity/                 # Humidity sensors
│   ├── pressure/                 # Pressure sensors
│   ├── air_quality/              # Air quality sensors
│   └── industrial/                # Industrial sensors
├── communication/                # Communication protocols
│   ├── mqtt/                     # MQTT client
│   ├── http/                     # HTTP client
│   ├── coap/                     # CoAP client
│   └── websocket/                # WebSocket client
├── utils/                        # Utility functions
│   ├── json/                     # JSON utilities
│   ├── time/                     # Time utilities
│   ├── math/                     # Math utilities
│   └── logging/                  # Logging utilities
└── config/                       # Configuration management
```

---

## Hardware Abstraction Layer (HAL)

### GPIO Abstraction
```cpp
// hal/gpio/gpio_hal.h
#ifndef GPIO_HAL_H
#define GPIO_HAL_H

#include <stdint.h>

typedef enum {
    GPIO_MODE_INPUT,
    GPIO_MODE_OUTPUT,
    GPIO_MODE_INPUT_PULLUP,
    GPIO_MODE_INPUT_PULLDOWN
} gpio_mode_t;

typedef enum {
    GPIO_LEVEL_LOW = 0,
    GPIO_LEVEL_HIGH = 1
} gpio_level_t;

class GPIO_HAL {
public:
    virtual void init(uint8_t pin, gpio_mode_t mode) = 0;
    virtual void write(uint8_t pin, gpio_level_t level) = 0;
    virtual gpio_level_t read(uint8_t pin) = 0;
    virtual void toggle(uint8_t pin) = 0;
    virtual ~GPIO_HAL() = default;
};

#endif // GPIO_HAL_H
```

```cpp
// hal/gpio/esp32_gpio.h
#include "gpio_hal.h"
#include <driver/gpio.h>

class ESP32_GPIO : public GPIO_HAL {
public:
    void init(uint8_t pin, gpio_mode_t mode) override;
    void write(uint8_t pin, gpio_level_t level) override;
    gpio_level_t read(uint8_t pin) override;
    void toggle(uint8_t pin) override;
};

void ESP32_GPIO::init(uint8_t pin, gpio_mode_t mode) {
    gpio_config_t io_conf = {};
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.pin_bit_mask = (1ULL << pin);
    
    switch (mode) {
        case GPIO_MODE_INPUT:
            io_conf.mode = GPIO_MODE_INPUT;
            break;
        case GPIO_MODE_OUTPUT:
            io_conf.mode = GPIO_MODE_OUTPUT;
            break;
        case GPIO_MODE_INPUT_PULLUP:
            io_conf.mode = GPIO_MODE_INPUT;
            io_conf.pull_up_en = GPIO_PULLUP_ENABLE;
            break;
        case GPIO_MODE_INPUT_PULLDOWN:
            io_conf.mode = GPIO_MODE_INPUT;
            io_conf.pull_down_en = GPIO_PULLDOWN_ENABLE;
            break;
    }
    
    gpio_config(&io_conf);
}
```

### ADC Abstraction
```cpp
// hal/adc/adc_hal.h
#ifndef ADC_HAL_H
#define ADC_HAL_H

#include <stdint.h>

typedef enum {
    ADC_RESOLUTION_12BIT = 12,
    ADC_RESOLUTION_10BIT = 10,
    ADC_RESOLUTION_8BIT = 8
} adc_resolution_t;

class ADC_HAL {
public:
    virtual void init(uint8_t pin, adc_resolution_t resolution) = 0;
    virtual uint16_t read(uint8_t pin) = 0;
    virtual float read_voltage(uint8_t pin, float reference_voltage) = 0;
    virtual ~ADC_HAL() = default;
};

#endif // ADC_HAL_H
```

---

## Sensor Drivers

### Temperature Sensor Driver
```cpp
// drivers/sensors/temperature_driver.h
#ifndef TEMPERATURE_DRIVER_H
#define TEMPERATURE_DRIVER_H

#include <stdint.h>
#include <functional>

typedef struct {
    float temperature;
    bool valid;
    uint32_t timestamp;
} temperature_data_t;

class TemperatureDriver {
public:
    virtual bool init() = 0;
    virtual temperature_data_t read() = 0;
    virtual bool is_connected() = 0;
    virtual void set_callback(std::function<void(temperature_data_t)> callback) = 0;
    virtual ~TemperatureDriver() = default;
};

#endif // TEMPERATURE_DRIVER_H
```

```cpp
// drivers/sensors/dht22_driver.cpp
#include "temperature_driver.h"
#include "DHT.h"

class DHT22Driver : public TemperatureDriver {
private:
    uint8_t pin;
    DHT* dht;
    std::function<void(temperature_data_t)> callback;
    
public:
    DHT22Driver(uint8_t dht_pin) : pin(dht_pin), dht(nullptr) {}
    
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
        return data;
    }
    
    bool is_connected() override {
        float temp = dht->readTemperature();
        return !isnan(temp);
    }
    
    void set_callback(std::function<void(temperature_data_t)> cb) override {
        callback = cb;
    }
};
```

### Multi-Sensor Driver
```cpp
// drivers/sensors/multi_sensor_driver.h
#ifndef MULTI_SENSOR_DRIVER_H
#define MULTI_SENSOR_DRIVER_H

#include "temperature_driver.h"
#include "humidity_driver.h"
#include "pressure_driver.h"

typedef struct {
    float temperature;
    float humidity;
    float pressure;
    bool valid;
    uint32_t timestamp;
} multi_sensor_data_t;

class MultiSensorDriver {
private:
    TemperatureDriver* temp_driver;
    HumidityDriver* humidity_driver;
    PressureDriver* pressure_driver;
    std::function<void(multi_sensor_data_t)> callback;
    
public:
    MultiSensorDriver(TemperatureDriver* temp, HumidityDriver* humidity, PressureDriver* pressure);
    bool init();
    multi_sensor_data_t read();
    bool is_connected();
    void set_callback(std::function<void(multi_sensor_data_t)> cb);
};

#endif // MULTI_SENSOR_DRIVER_H
```

---

## Communication Protocols

### MQTT Client
```cpp
// communication/mqtt/mqtt_client.h
#ifndef MQTT_CLIENT_H
#define MQTT_CLIENT_H

#include <string>
#include <functional>
#include <vector>

typedef struct {
    std::string topic;
    std::string payload;
    uint32_t timestamp;
} mqtt_message_t;

class MQTTClient {
private:
    std::string broker_host;
    uint16_t broker_port;
    std::string client_id;
    std::string username;
    std::string password;
    
    std::function<void(mqtt_message_t)> message_callback;
    std::vector<std::string> subscribed_topics;
    
public:
    MQTTClient(const std::string& host, uint16_t port, const std::string& client_id);
    
    bool connect();
    bool disconnect();
    bool is_connected();
    
    bool publish(const std::string& topic, const std::string& payload);
    bool subscribe(const std::string& topic);
    bool unsubscribe(const std::string& topic);
    
    void set_message_callback(std::function<void(mqtt_message_t)> callback);
    void set_credentials(const std::string& user, const std::string& pass);
    
    void loop();
};

#endif // MQTT_CLIENT_H
```

```cpp
// communication/mqtt/esp32_mqtt_client.cpp
#include "mqtt_client.h"
#include <WiFi.h>
#include <PubSubClient.h>

class ESP32MQTTClient : public MQTTClient {
private:
    WiFiClient wifi_client;
    PubSubClient pub_sub_client;
    
public:
    ESP32MQTTClient(const std::string& host, uint16_t port, const std::string& client_id)
        : MQTTClient(host, port, client_id), pub_sub_client(wifi_client) {
        pub_sub_client.setServer(host.c_str(), port);
    }
    
    bool connect() override {
        if (username.length() > 0) {
            return pub_sub_client.connect(client_id.c_str(), username.c_str(), password.c_str());
        } else {
            return pub_sub_client.connect(client_id.c_str());
        }
    }
    
    bool publish(const std::string& topic, const std::string& payload) override {
        return pub_sub_client.publish(topic.c_str(), payload.c_str());
    }
    
    bool subscribe(const std::string& topic) override {
        subscribed_topics.push_back(topic);
        return pub_sub_client.subscribe(topic.c_str());
    }
    
    void loop() override {
        if (!pub_sub_client.connected()) {
            connect();
        }
        pub_sub_client.loop();
    }
};
```

### HTTP Client
```cpp
// communication/http/http_client.h
#ifndef HTTP_CLIENT_H
#define HTTP_CLIENT_H

#include <string>
#include <map>

typedef enum {
    HTTP_GET,
    HTTP_POST,
    HTTP_PUT,
    HTTP_DELETE
} http_method_t;

typedef struct {
    int status_code;
    std::string body;
    std::map<std::string, std::string> headers;
} http_response_t;

class HTTPClient {
private:
    std::string base_url;
    std::map<std::string, std::string> default_headers;
    
public:
    HTTPClient(const std::string& base_url);
    
    http_response_t get(const std::string& path);
    http_response_t post(const std::string& path, const std::string& body);
    http_response_t put(const std::string& path, const std::string& body);
    http_response_t del(const std::string& path);
    
    void set_header(const std::string& key, const std::string& value);
    void set_auth_token(const std::string& token);
};

#endif // HTTP_CLIENT_H
```

---

## Utility Functions

### JSON Utilities
```cpp
// utils/json/json_utils.h
#ifndef JSON_UTILS_H
#define JSON_UTILS_H

#include <ArduinoJson.h>
#include <string>

class JSONUtils {
public:
    // Serialization
    static std::string serialize(const JsonObject& obj);
    static std::string serialize(const JsonArray& arr);
    
    // Deserialization
    static JsonObject deserialize_object(const std::string& json_str);
    static JsonArray deserialize_array(const std::string& json_str);
    
    // Validation
    static bool is_valid_json(const std::string& json_str);
    
    // Convenience methods
    static JsonObject create_telemetry_object(const std::string& device_id, 
                                                const std::string& metric_name, 
                                                float value);
    static JsonObject create_device_info_object(const std::string& device_id,
                                                 const std::string& device_type,
                                                 const std::string& firmware_version);
};

#endif // JSON_UTILS_H
```

```cpp
// utils/json/json_utils.cpp
#include "json_utils.h"

std::string JSONUtils::serialize(const JsonObject& obj) {
    String json_str;
    serializeJson(obj, json_str);
    return json_str.c_str();
}

std::string JSONUtils::serialize(const JsonArray& arr) {
    String json_str;
    serializeJson(arr, json_str);
    return json_str.c_str();
}

bool JSONUtils::is_valid_json(const std::string& json_str) {
    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, json_str);
    return error == DeserializationError::Ok;
}

JsonObject JSONUtils::create_telemetry_object(const std::string& device_id, 
                                                   const std::string& metric_name, 
                                                   float value) {
    JsonObject obj;
    obj["device_id"] = device_id;
    obj["metric_name"] = metric_name;
    obj["value"] = value;
    obj["timestamp"] = millis();
    return obj;
}
```

### Time Utilities
```cpp
// utils/time/time_utils.h
#ifndef TIME_UTILS_H
#define TIME_UTILS_H

#include <cstdint>
#include <string>

class TimeUtils {
public:
    // Timestamp functions
    static uint32_t get_timestamp();
    static uint32_t get_uptime();
    static std::string format_timestamp(uint32_t timestamp);
    
    // Time conversion
    static uint32_t seconds_to_millis(uint32_t seconds);
    static uint32_t minutes_to_millis(uint32_t minutes);
    static uint32_t hours_to_millis(uint32_t hours);
    
    // Time calculations
    static uint32_t elapsed_time(uint32_t start_time);
    static bool has_elapsed(uint32_t start_time, uint32_t duration);
    
    // RTC functions (if available)
    static bool set_rtc_time(uint32_t timestamp);
    static uint32_t get_rtc_time();
    
    // NTP functions (if available)
    static bool sync_ntp_time(const std::string& ntp_server);
    static bool is_time_synced();
};

#endif // TIME_UTILS_H
```

### Logging Utilities
```cpp
// utils/logging/logger.h
#ifndef LOGGER_H
#define LOGGER_H

#include <string>
#include <Print.h>

typedef enum {
    LOG_LEVEL_DEBUG,
    LOG_LEVEL_INFO,
    LOG_LEVEL_WARNING,
    LOG_LEVEL_ERROR
} log_level_t;

class Logger {
private:
    static log_level_t current_level;
    static Print* output;
    
public:
    static void init(Print* out, log_level_t level = LOG_LEVEL_INFO);
    
    static void debug(const std::string& message);
    static void info(const std::string& message);
    static void warning(const std::string& message);
    static void error(const std::string& message);
    
    static void log(log_level_t level, const std::string& message);
    static void set_level(log_level_t level);
    
    // Convenience macros
    #define LOG_DEBUG(msg) Logger::debug(msg)
    #define LOG_INFO(msg) Logger::info(msg)
    #define LOG_WARN(msg) Logger::warning(msg)
    #define LOG_ERROR(msg) Logger::error(msg)
};

#endif // LOGGER_H
```

---

## Configuration Management

### Configuration Manager
```cpp
// config/config_manager.h
#ifndef CONFIG_MANAGER_H
#define CONFIG_MANAGER_H

#include <ArduinoJson.h>
#include <string>
#include <functional>

typedef struct {
    std::string device_id;
    std::string device_name;
    std::string device_type;
    std::string firmware_version;
    std::string mqtt_broker;
    uint16_t mqtt_port;
    std::string wifi_ssid;
    std::string wifi_password;
    uint32_t telemetry_interval;
    bool enable_ota;
} device_config_t;

class ConfigManager {
private:
    device_config_t config;
    std::string config_file_path;
    std::function<void()> save_callback;
    
public:
    ConfigManager(const std::string& file_path = "/config.json");
    
    bool load_config();
    bool save_config();
    bool reset_config();
    
    // Getters
    device_config_t get_config() const;
    std::string get_device_id() const;
    std::string get_mqtt_broker() const;
    uint32_t get_telemetry_interval() const;
    
    // Setters
    void set_device_id(const std::string& device_id);
    void set_mqtt_broker(const std::string& broker);
    void set_telemetry_interval(uint32_t interval);
    
    // Validation
    bool is_config_valid() const;
    bool validate_config(const JsonObject& config_obj);
    
    // Callbacks
    void set_save_callback(std::function<void()> callback);
    
    // Factory reset
    void factory_reset();
};

#endif // CONFIG_MANAGER_H
```

---

## Power Management

### Power Manager
```cpp
// drivers/power/power_manager.h
#ifndef POWER_MANAGER_H
#define POWER_MANAGER_H

#include <stdint.h>

typedef enum {
    POWER_MODE_NORMAL,
    POWER_MODE_LOW_POWER,
    POWER_MODE_DEEP_SLEEP,
    POWER_MODE_HIBERNATE
} power_mode_t;

typedef struct {
    float battery_voltage;
    uint8_t battery_percentage;
    bool is_charging;
    bool is_low_battery;
    uint32_t uptime_seconds;
} power_status_t;

class PowerManager {
private:
    power_mode_t current_mode;
    uint8_t battery_pin;
    float reference_voltage;
    
public:
    PowerManager(uint8_t battery_adc_pin = A0, float ref_voltage = 3.3);
    
    // Power mode control
    void set_power_mode(power_mode_t mode);
    power_mode_t get_power_mode() const;
    
    // Battery monitoring
    power_status_t get_power_status();
    float read_battery_voltage();
    uint8_t get_battery_percentage();
    bool is_low_battery();
    bool is_charging();
    
    // Sleep functions
    void sleep(uint32_t duration_ms);
    void deep_sleep(uint32_t duration_seconds);
    
    // Power optimization
    void optimize_power_usage();
    void enter_low_power_mode();
    void exit_low_power_mode();
    
    // Watchdog
    void enable_watchdog(uint32_t timeout_ms);
    void reset_watchdog();
};

#endif // POWER_MANAGER_H
```

---

## Storage Management

### Storage Manager
```cpp
// drivers/storage/storage_manager.h
#ifndef STORAGE_MANAGER_H
#define STORAGE_MANAGER_H

#include <string>
#include <vector>

typedef enum {
    STORAGE_TYPE_FLASH,
    STORAGE_TYPE_EEPROM,
    STORAGE_TYPE_SD_CARD,
    STORAGE_TYPE_SPIFFS
} storage_type_t;

class StorageManager {
private:
    storage_type_t storage_type;
    bool is_initialized;
    
public:
    StorageManager(storage_type_t type);
    
    // Initialization
    bool init();
    bool format();
    bool is_available();
    
    // File operations
    bool write_file(const std::string& filename, const std::string& data);
    std::string read_file(const std::string& filename);
    bool delete_file(const std::string& filename);
    bool file_exists(const std::string& filename);
    
    // Directory operations
    std::vector<std::string> list_files(const std::string& directory = "/");
    bool create_directory(const std::string& path);
    
    // Storage info
    uint32_t get_free_space();
    uint32_t get_total_space();
    
    // Configuration storage
    bool save_config(const std::string& config_data);
    std::string load_config();
};

#endif // STORAGE_MANAGER_H
```

---

## Usage Examples

### Multi-Platform Device
```cpp
#include "hal/gpio/gpio_hal.h"
#include "sensors/temperature_driver.h"
#include "communication/mqtt/mqtt_client.h"
#include "config/config_manager.h"
#include "utils/logging/logger.h"

class ValtronicsDevice {
private:
    GPIO_HAL* gpio;
    TemperatureDriver* temp_sensor;
    MQTTClient* mqtt_client;
    ConfigManager* config;
    PowerManager* power_manager;
    
public:
    ValtronicsDevice() {
        // Platform-specific initialization
        #ifdef ESP32
            gpio = new ESP32_GPIO();
            temp_sensor = new DHT22Driver(4);
            mqtt_client = new ESP32MQTTClient("mqtt.valtronics.com", 1883, "VT-DEVICE-001");
        #elif defined(ARDUINO)
            gpio = new Arduino_GPIO();
            temp_sensor = new Arduino_DHT22Driver(2);
            mqtt_client = new Arduino_MQTTClient("mqtt.valtronics.com", 1883, "VT-DEVICE-001");
        #endif
        
        config = new ConfigManager();
        power_manager = new PowerManager();
        
        Logger::init(&Serial, LOG_LEVEL_INFO);
    }
    
    bool init() {
        Logger::info("Initializing Valtronics device...");
        
        // Load configuration
        if (!config->load_config()) {
            Logger::error("Failed to load configuration");
            return false;
        }
        
        // Initialize hardware
        gpio->init(LED_BUILTIN, GPIO_MODE_OUTPUT);
        temp_sensor->init();
        
        // Connect to MQTT
        mqtt_client->connect();
        
        Logger::info("Device initialized successfully");
        return true;
    }
    
    void run() {
        while (true) {
            // Check power status
            power_status_t power_status = power_manager->get_power_status();
            if (power_status.is_low_battery) {
                Logger::warning("Low battery detected");
                power_manager->set_power_mode(POWER_MODE_LOW_POWER);
            }
            
            // Read sensor data
            temperature_data_t temp_data = temp_sensor->read();
            if (temp_data.valid) {
                // Create telemetry
                JsonObject telemetry = JSONUtils::create_telemetry_object(
                    config->get_device_id(),
                    "temperature",
                    temp_data.temperature
                );
                
                // Send to MQTT
                std::string payload = JSONUtils::serialize(telemetry);
                mqtt_client->publish("valtronics/telemetry", payload);
                
                Logger::info("Telemetry sent");
            }
            
            // Handle MQTT
            mqtt_client->loop();
            
            // Sleep based on power mode
            uint32_t sleep_time = config->get_telemetry_interval() * 1000;
            if (power_manager->get_power_mode() == POWER_MODE_LOW_POWER) {
                sleep_time *= 2;  // Double interval in low power mode
            }
            
            delay(sleep_time);
        }
    }
};
```

---

## Platform Compatibility

### Supported Platforms
- **ESP32**: Full support for all components
- **Arduino**: Most components supported (limited by hardware)
- **STM32**: Full support with HAL implementation
- **Raspberry Pi**: Full support with Linux drivers

### Feature Matrix
| Component | ESP32 | Arduino | STM32 | Raspberry Pi |
|-----------|-------|---------|-------|--------------|
| GPIO HAL | ✓ | ✓ | ✓ | ✓ |
| ADC HAL | ✓ | ✓ | ✓ | ✓ |
| MQTT Client | ✓ | ✓ | ✓ | ✓ |
| HTTP Client | ✓ | ✓ | ✓ | ✓ |
| Temperature Drivers | ✓ | ✓ | ✓ | ✓ |
| Power Management | ✓ | Limited | ✓ | ✓ |
| Storage Manager | ✓ | Limited | ✓ | ✓ |
| JSON Utils | ✓ | ✓ | ✓ | ✓ |

---

## Testing

### Unit Tests
```cpp
// tests/test_gpio_hal.cpp
#include "hal/gpio/gpio_hal.h"

void test_gpio_output() {
    GPIO_HAL* gpio = create_gpio_hal();  // Platform-specific factory
    
    gpio->init(LED_BUILTIN, GPIO_MODE_OUTPUT);
    gpio->write(LED_BUILTIN, GPIO_LEVEL_HIGH);
    
    assert(gpio->read(LED_BUILTIN) == GPIO_LEVEL_HIGH);
    
    gpio->toggle(LED_BUILTIN);
    assert(gpio->read(LED_BUILTIN) == GPIO_LEVEL_LOW);
    
    delete gpio;
}

void test_temperature_driver() {
    TemperatureDriver* temp_driver = new DHT22Driver(4);
    assert(temp_driver->init());
    
    temperature_data_t data = temp_driver->read();
    assert(data.valid);
    assert(data.temperature > -40 && data.temperature < 85);
    
    delete temp_driver;
}
```

### Integration Tests
```cpp
// tests/test_integration.cpp
void test_sensor_to_mqtt() {
    // Initialize components
    ConfigManager config;
    MQTTClient mqtt("test.mqtt.com", 1883, "test-device");
    TemperatureDriver temp_driver(4);
    
    // Setup
    config.load_config();
    mqtt.connect();
    temp_driver.init();
    
    // Test sensor reading and MQTT publishing
    temperature_data_t temp_data = temp_driver.read();
    assert(temp_data.valid);
    
    JsonObject telemetry = JSONUtils::create_telemetry_object(
        config.get_device_id(),
        "temperature",
        temp_data.temperature
    );
    
    std::string payload = JSONUtils::serialize(telemetry);
    bool published = mqtt.publish("test/telemetry", payload);
    assert(published);
}
```

---

## Support

For common components support:
- **Documentation**: See individual component directories
- **Examples**: See `examples/` directory
- **Platform Guides**: See `platform/*/` directories
- **Email**: firmware@valtronics.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Common Firmware Components v1.0**
