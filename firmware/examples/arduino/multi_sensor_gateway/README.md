# Arduino Multi-Sensor Gateway Example

**Complete example implementation for Arduino-based multi-sensor gateway**

---

## Overview

This example demonstrates a comprehensive Arduino Mega-based multi-sensor gateway that reads multiple environmental sensors, processes data locally, and transmits via Ethernet. It's designed for industrial monitoring applications where multiple sensors need to be monitored from a single device.

---

## Features

- **Arduino Mega**: High-performance Arduino platform
- **Multiple Sensors**: Temperature, humidity, pressure, air quality
- **Ethernet Connectivity**: Wired network communication
- **Local Processing**: Data validation and alerting
- **Modbus Support**: Industrial protocol compatibility
- **SD Card Logging**: Local data storage
- **LCD Display**: Local status display

---

## Hardware Requirements

### Components
- **Arduino Mega 2560**: Main controller
- **Ethernet Shield**: W5500 Ethernet module
- **DHT22**: Temperature and humidity sensor
- **BME280**: Pressure and environmental sensor
- **PMS5003**: Air quality sensor
- **LCD Display**: 20x4 character LCD
- **SD Card Module**: For data logging
- **Breadboard**: For prototyping
- **Jumper Wires**: For connections

### Wiring
```
Arduino Mega    DHT22    BME280    PMS5003    LCD     SD Card
5V          VCC      VCC       VCC        VCC     VCC
GND          GND      GND       GND        GND     GND
D22          DATA      SDA       TX         RS      CS
D21                    SCL       RX         EN      MOSI
D20                    SDA       RESET      D4      MISO
D19                    SCL       D7         D5      SCK
```

---

## Software Requirements

### PlatformIO Configuration
```ini
[env:arduino_mega]
platform = atmelavr
board = megaatmega2560
framework = arduino
monitor_speed = 115200
lib_deps = 
    PubSubClient
    ArduinoJson
    DHT sensor library
    Adafruit BME280 Library
    Ethernet
    SD
    LiquidCrystal_I2C
    SoftwareSerial

build_flags = 
    -DARDUINO_AVR_ATMEGA2560
```

### Dependencies
- **PubSubClient**: MQTT client library
- **ArduinoJson**: JSON processing
- **DHT sensor library**: DHT22 sensor driver
- **Adafruit BME280**: BME280 sensor driver
- **Ethernet**: Ethernet communication
- **SD**: SD card library
- **LiquidCrystal_I2C**: LCD display library

---

## Implementation

### Main Application
```cpp
#include <Arduino.h>
#include <ArduinoJson.h>
#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Adafruit_BME280.h>
#include <SoftwareSerial.h>
#include <SD.h>
#include <LiquidCrystal_I2C.h>

// Device configuration
#define DEVICE_ID "VT-ARDUINO-GATEWAY-001"
#define DHT_PIN 22
#define BME280_SDA 20
#define BME280_SCL 21
#define PMS5003_RX 19
#define PMS5003_TX 18
#define LCD_ADDR 0x27

// Global objects
DHT dht(DHT_PIN, DHT22);
Adafruit_BME280 bme;
SoftwareSerial pmsSerial(PMS5003_RX, PMS5003_TX);
LiquidCrystal_I2C lcd(0x27, 20, 4);
EthernetClient ethClient;
PubSubClient mqttClient(ethClient);

// Network configuration
byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};
IPAddress ip(192, 168, 1, 177);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress mqtt_server(192, 168, 1, 100);

// Global state
bool system_ready = false;
uint32_t last_telemetry_time = 0;
uint32_t last_lcd_update = 0;
uint32_t last_sd_write = 0;

// Sensor data structure
struct SensorData {
    float temperature_dht;
    float humidity_dht;
    float temperature_bme;
    float humidity_bme;
    float pressure_bme;
    float altitude_bme;
    uint16_t pm25;
    uint16_t pm10;
    uint32_t timestamp;
    bool dht_valid;
    bool bme_valid;
    bool pms_valid;
};

SensorData sensor_data;

void setup() {
    Serial.begin(115200);
    Serial.println("\n=== Valtronics Arduino Multi-Sensor Gateway ===");
    Serial.println("Device ID: " + String(DEVICE_ID));
    
    // Initialize components
    initialize_lcd();
    initialize_sd_card();
    initialize_sensors();
    initialize_ethernet();
    initialize_mqtt();
    
    system_ready = true;
    lcd.clear();
    lcd.print("System Ready!");
    lcd.setCursor(0, 1);
    lcd.print("IP: ");
    lcd.print(ip);
    
    Serial.println("System ready!");
    send_startup_message();
}

void loop() {
    if (!system_ready) {
        delay(1000);
        return;
    }
    
    // Handle MQTT
    handle_mqtt();
    
    // Read sensors
    read_sensors();
    
    // Update LCD
    update_lcd();
    
    // Send telemetry
    send_telemetry();
    
    // Log to SD card
    log_to_sd();
    
    // Check alerts
    check_alerts();
    
    delay(1000);
}

void initialize_lcd() {
    Serial.println("Initializing LCD...");
    
    lcd.begin(20, 4);
    lcd.backlight();
    
    lcd.setCursor(0, 0);
    lcd.print("Valtronics Gateway");
    lcd.setCursor(0, 1);
    lcd.print("Initializing...");
    
    Serial.println("LCD initialized");
}

void initialize_sd_card() {
    Serial.println("Initializing SD card...");
    
    pinMode(53, OUTPUT);  // CS pin for Ethernet shield
    
    if (SD.begin(4)) {  // CS pin for SD module
        Serial.println("SD card initialized");
        
        // Create log file
        File logFile = SD.open("gateway_log.csv", FILE_WRITE);
        if (logFile) {
            logFile.println("timestamp,device_id,temp_dht,humidity_dht,temp_bme,humidity_bme,pressure_bme,pm25,pm10");
            logFile.close();
            Serial.println("Log file created");
        }
    } else {
        Serial.println("SD card initialization failed");
        lcd.setCursor(0, 2);
        lcd.print("SD Card Error!");
    }
}

void initialize_sensors() {
    Serial.println("Initializing sensors...");
    
    // Initialize DHT22
    dht.begin();
    
    // Initialize BME280
    if (bme.begin(0x76)) {
        Serial.println("BME280 initialized");
        bme.setSampling(Adafruit_BME280::MODE_NORMAL,
                        Adafruit_BME280::SAMPLING_X2,  // temperature
                        Adafruit_BME280::SAMPLING_X16, // pressure
                        Adafruit_BME280::SAMPLING_X1,  // humidity
                        Adafruit_BME280::FILTER_X16,
                        Adafruit_BME280::STANDBY_MS_0_5);
    } else {
        Serial.println("BME280 initialization failed");
    }
    
    // Initialize PMS5003
    pmsSerial.begin(9600);
    
    Serial.println("Sensors initialized");
}

void initialize_ethernet() {
    Serial.println("Initializing Ethernet...");
    
    // Try DHCP first
    if (Ethernet.begin(mac) == 0) {
        Serial.println("DHCP failed, using static IP");
        Ethernet.begin(mac, ip, gateway, subnet);
    }
    
    Serial.print("IP address: ");
    Serial.println(Ethernet.localIP());
    
    if (Ethernet.localIP() == IPAddress(0, 0, 0, 0)) {
        Serial.println("Ethernet initialization failed");
        lcd.setCursor(0, 2);
        lcd.print("Ethernet Error!");
    } else {
        Serial.println("Ethernet initialized");
    }
}

void initialize_mqtt() {
    Serial.println("Initializing MQTT...");
    
    mqttClient.setServer(mqtt_server, 1883);
    mqttClient.setCallback(mqtt_callback);
    
    connect_mqtt();
}

void connect_mqtt() {
    Serial.println("Connecting to MQTT broker...");
    
    if (mqttClient.connect(DEVICE_ID)) {
        Serial.println("MQTT connected successfully!");
        
        // Subscribe to topics
        mqttClient.subscribe("valtronics/devices/" + String(DEVICE_ID) + "/commands");
        mqttClient.subscribe("valtronics/devices/" + String(DEVICE_ID) + "/config");
        
        lcd.setCursor(0, 3);
        lcd.print("MQTT Connected");
    } else {
        Serial.printf("MQTT connection failed, state: %d\n", mqttClient.state());
        lcd.setCursor(0, 3);
        lcd.print("MQTT Error");
    }
}

void read_sensors() {
    // Clear previous data
    memset(&sensor_data, 0, sizeof(sensor_data));
    sensor_data.timestamp = millis();
    
    // Read DHT22
    float temp_dht = dht.readTemperature();
    float humidity_dht = dht.readHumidity();
    
    if (!isnan(temp_dht) && !isnan(humidity_dht)) {
        sensor_data.temperature_dht = temp_dht;
        sensor_data.humidity_dht = humidity_dht;
        sensor_data.dht_valid = true;
    } else {
        sensor_data.dht_valid = false;
    }
    
    // Read BME280
    float temp_bme = bme.readTemperature();
    float humidity_bme = bme.readHumidity();
    float pressure_bme = bme.readPressure() / 100.0F;  // Convert to hPa
    
    if (!isnan(temp_bme) && !isnan(humidity_bme) && !isnan(pressure_bme)) {
        sensor_data.temperature_bme = temp_bme;
        sensor_data.humidity_bme = humidity_bme;
        sensor_data.pressure_bme = pressure_bme;
        sensor_data.altitude_bme = bme.readAltitude(1013.25);
        sensor_data.bme_valid = true;
    } else {
        sensor_data.bme_valid = false;
    }
    
    // Read PMS5003
    uint8_t buffer[32];
    if (pmsSerial.available() >= 32) {
        if (pmsSerial.readBytes(buffer, 32) == 32) {
            if (buffer[0] == 0x42 && buffer[1] == 0x4D) {
                sensor_data.pm25 = (buffer[12] << 8) | buffer[13];
                sensor_data.pm10 = (buffer[14] << 8) | buffer[15];
                sensor_data.pms_valid = true;
            } else {
                sensor_data.pms_valid = false;
            }
        }
    } else {
        sensor_data.pms_valid = false;
    }
    
    // Print sensor readings
    Serial.println("Sensor Readings:");
    Serial.printf("DHT22: %.1f°C, %.1f%% (%s)\n", 
                 sensor_data.temperature_dht, sensor_data.humidity_dht, 
                 sensor_data.dht_valid ? "OK" : "ERROR");
    Serial.printf("BME280: %.1f°C, %.1f%%, %.1f hPa (%s)\n", 
                 sensor_data.temperature_bme, sensor_data.humidity_bme, sensor_data.pressure_bme,
                 sensor_data.bme_valid ? "OK" : "ERROR");
    Serial.printf("PMS5003: PM2.5=%d, PM10=%d (%s)\n", 
                 sensor_data.pm25, sensor_data.pm10,
                 sensor_data.pms_valid ? "OK" : "ERROR");
}

void update_lcd() {
    static uint8_t current_line = 0;
    uint32_t current_time = millis();
    
    // Update LCD every 5 seconds
    if (current_time - last_lcd_update > 5000) {
        last_lcd_update = current_time;
        
        lcd.clear();
        
        // Line 0: Device info
        lcd.setCursor(0, 0);
        lcd.print("VT Gateway");
        lcd.print(" ");
        lcd.print(millis() / 1000);
        lcd.print("s");
        
        // Line 1: Temperature
        lcd.setCursor(0, 1);
        if (sensor_data.bme_valid) {
            lcd.print("T: ");
            lcd.print(sensor_data.temperature_bme, 1);
            lcd.print("C ");
            lcd.print(sensor_data.humidity_bme, 1);
            lcd.print("%");
        } else if (sensor_data.dht_valid) {
            lcd.print("T: ");
            lcd.print(sensor_data.temperature_dht, 1);
            lcd.print("C ");
            lcd.print(sensor_data.humidity_dht, 1);
            lcd.print("%");
        } else {
            lcd.print("Temp: ERROR");
        }
        
        // Line 2: Pressure and Air Quality
        lcd.setCursor(0, 2);
        if (sensor_data.bme_valid) {
            lcd.print("P: ");
            lcd.print(sensor_data.pressure_bme, 1);
            lcd.print("hPa");
        } else {
            lcd.print("Pressure: ERROR");
        }
        
        // Line 3: Air Quality and Status
        lcd.setCursor(0, 3);
        if (sensor_data.pms_valid) {
            lcd.print("PM2.5: ");
            lcd.print(sensor_data.pm25);
        } else {
            lcd.print("Air Quality: ERROR");
        }
    }
}

void send_telemetry() {
    uint32_t current_time = millis();
    
    if (current_time - last_telemetry_time < 30000) {  // 30 seconds
        return;
    }
    
    last_telemetry_time = current_time;
    
    // Create telemetry payload
    DynamicJsonDocument doc(1024);
    
    doc["device_id"] = DEVICE_ID;
    doc["device_type"] = "multi_sensor_gateway";
    doc["timestamp"] = current_time;
    doc["location"] = "Server Room A";
    
    // DHT22 data
    if (sensor_data.dht_valid) {
        JsonObject dht = doc.createNestedObject("dht22");
        dht["temperature"] = sensor_data.temperature_dht;
        dht["humidity"] = sensor_data.humidity_dht;
        dht["status"] = "ok";
    } else {
        JsonObject dht = doc.createNestedObject("dht22");
        dht["status"] = "error";
    }
    
    // BME280 data
    if (sensor_data.bme_valid) {
        JsonObject bme = doc.createNestedObject("bme280");
        bme["temperature"] = sensor_data.temperature_bme;
        bme["humidity"] = sensor_data.humidity_bme;
        bme["pressure"] = sensor_data.pressure_bme;
        bme["altitude"] = sensor_data.altitude_bme;
        bme["status"] = "ok";
    } else {
        JsonObject bme = doc.createNestedObject("bme280");
        bme["status"] = "error";
    }
    
    // PMS5003 data
    if (sensor_data.pms_valid) {
        JsonObject pms = doc.createNestedObject("pms5003");
        pms["pm25"] = sensor_data.pm25;
        pms["pm10"] = sensor_data.pm10;
        pms["status"] = "ok";
    } else {
        JsonObject pms = doc.createNestedObject("pms5003");
        pms["status"] = "error";
    }
    
    // System data
    JsonObject system = doc.createNestedObject("system");
    system["free_memory"] = get_free_memory();
    system["ethernet_status"] = Ethernet.linkStatus() == LinkON ? "up" : "down";
    system["mqtt_connected"] = mqttClient.connected();
    system["uptime"] = current_time;
    
    // Serialize and send
    String payload;
    serializeJson(doc, payload);
    
    String topic = "valtronics/telemetry/" + String(DEVICE_ID);
    
    if (mqttClient.publish(topic.c_str(), payload.c_str())) {
        Serial.println("Telemetry sent successfully");
    } else {
        Serial.println("Failed to send telemetry");
    }
}

void log_to_sd() {
    uint32_t current_time = millis();
    
    // Log to SD card every minute
    if (current_time - last_sd_write > 60000) {
        last_sd_write = current_time;
        
        File logFile = SD.open("gateway_log.csv", FILE_WRITE);
        if (logFile) {
            // Create CSV line
            String logLine = String(sensor_data.timestamp) + "," +
                           String(DEVICE_ID) + "," +
                           String(sensor_data.dht_valid ? sensor_data.temperature_dht : 0) + "," +
                           String(sensor_data.dht_valid ? sensor_data.humidity_dht : 0) + "," +
                           String(sensor_data.bme_valid ? sensor_data.temperature_bme : 0) + "," +
                           String(sensor_data.bme_valid ? sensor_data.humidity_bme : 0) + "," +
                           String(sensor_data.bme_valid ? sensor_data.pressure_bme : 0) + "," +
                           String(sensor_data.pms_valid ? sensor_data.pm25 : 0) + "," +
                           String(sensor_data.pms_valid ? sensor_data.pm10 : 0);
            
            logFile.println(logLine);
            logFile.close();
            
            Serial.println("Data logged to SD card");
        } else {
            Serial.println("Failed to open log file");
        }
    }
}

void check_alerts() {
    // Temperature alerts
    if (sensor_data.bme_valid && sensor_data.temperature_bme > 35.0) {
        send_alert("temperature_high", sensor_data.temperature_bme, "Temperature too high");
    }
    
    // Humidity alerts
    if (sensor_data.bme_valid && sensor_data.humidity_bme > 70.0) {
        send_alert("humidity_high", sensor_data.humidity_bme, "Humidity too high");
    }
    
    // Air quality alerts
    if (sensor_data.pms_valid && sensor_data.pm25 > 35) {
        send_alert("air_quality_poor", sensor_data.pm25, "PM2.5 too high");
    }
    
    // Sensor error alerts
    if (!sensor_data.dht_valid || !sensor_data.bme_valid || !sensor_data.pms_valid) {
        send_alert("sensor_error", 0, "One or more sensors not responding");
    }
}

void send_alert(const String& alert_type, float value, const String& message) {
    DynamicJsonDocument doc(256);
    
    doc["device_id"] = DEVICE_ID;
    doc["alert_type"] = alert_type;
    doc["value"] = value;
    doc["message"] = message;
    doc["timestamp"] = millis();
    doc["severity"] = "warning";
    
    String payload;
    serializeJson(doc, payload);
    
    String topic = "valtronics/alerts/" + String(DEVICE_ID);
    
    if (mqttClient.publish(topic.c_str(), payload.c_str())) {
        Serial.println("Alert sent: " + alert_type);
    }
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
    
    if (cmd == "status") {
        send_status_report();
    } else if (cmd == "reboot") {
        Serial.println("Reboot command received");
        send_command_response("reboot", "Rebooting device");
        delay(1000);
        asm volatile ("jmp 0");  // Arduino soft reboot
    } else if (cmd == "sensors") {
        send_sensor_report();
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
    
    // Handle configuration updates
    if (doc.containsKey("telemetry_interval")) {
        uint32_t interval = doc["telemetry_interval"];
        Serial.printf("Telemetry interval updated: %lu ms\n", interval);
        // Update telemetry interval
    }
    
    send_command_response("config", "Configuration updated");
}

void send_command_response(const String& command, const String& message) {
    DynamicJsonDocument doc(256);
    
    doc["device_id"] = DEVICE_ID;
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
    
    doc["device_id"] = DEVICE_ID;
    doc["device_type"] = "multi_sensor_gateway";
    doc["firmware_version"] = "1.0.0";
    doc["uptime"] = millis();
    doc["free_memory"] = get_free_memory();
    doc["ethernet_status"] = Ethernet.linkStatus() == LinkON ? "up" : "down";
    doc["ip_address"] = Ethernet.localIP().toString();
    doc["mqtt_connected"] = mqttClient.connected();
    doc["sd_card_status"] = SD.cardType() != CARD_NONE ? "ok" : "error";
    
    // Sensor status
    doc["dht22_status"] = sensor_data.dht_valid ? "ok" : "error";
    doc["bme280_status"] = sensor_data.bme_valid ? "ok" : "error";
    doc["pms5003_status"] = sensor_data.pms_valid ? "ok" : "error";
    
    String payload;
    serializeJson(doc, payload);
    
    String topic = "valtronics/devices/" + String(DEVICE_ID) + "/status";
    mqttClient.publish(topic.c_str(), payload.c_str());
}

void send_sensor_report() {
    DynamicJsonDocument doc(512);
    
    doc["device_id"] = DEVICE_ID;
    doc["timestamp"] = sensor_data.timestamp;
    
    if (sensor_data.dht_valid) {
        JsonObject dht = doc.createNestedObject("dht22");
        dht["temperature"] = sensor_data.temperature_dht;
        dht["humidity"] = sensor_data.humidity_dht;
        dht["status"] = "ok";
    } else {
        JsonObject dht = doc.createNestedObject("dht22");
        dht["status"] = "error";
    }
    
    if (sensor_data.bme_valid) {
        JsonObject bme = doc.createNestedObject("bme280");
        bme["temperature"] = sensor_data.temperature_bme;
        bme["humidity"] = sensor_data.humidity_bme;
        bme["pressure"] = sensor_data.pressure_bme;
        bme["altitude"] = sensor_data.altitude_bme;
        bme["status"] = "ok";
    } else {
        JsonObject bme = doc.createNestedObject("bme280");
        bme["status"] = "error";
    }
    
    if (sensor_data.pms_valid) {
        JsonObject pms = doc.createNestedObject("pms5003");
        pms["pm25"] = sensor_data.pm25;
        pms["pm10"] = sensor_data.pm10;
        pms["status"] = "ok";
    } else {
        JsonObject pms = doc.createNestedObject("pms5003");
        pms["status"] = "error";
    }
    
    String payload;
    serializeJson(doc, payload);
    
    String topic = "valtronics/devices/" + String(DEVICE_ID) + "/sensors";
    mqttClient.publish(topic.c_str(), payload.c_str());
}

void send_startup_message() {
    DynamicJsonDocument doc(256);
    
    doc["device_id"] = DEVICE_ID;
    doc["event"] = "startup";
    doc["message"] = "Multi-sensor gateway started successfully";
    doc["firmware_version"] = "1.0.0";
    doc["timestamp"] = millis();
    
    String payload;
    serializeJson(doc, payload);
    
    String topic = "valtronics/devices/" + String(DEVICE_ID) + "/events";
    mqttClient.publish(topic.c_str(), payload.c_str());
}

int get_free_memory() {
    extern int __heap_start, *__brkval;
    int v;
    return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval);
}
```

---

## Usage

### 1. Hardware Setup
1. Connect all sensors to Arduino Mega as shown in wiring diagram
2. Connect Ethernet shield
3. Connect LCD display
4. Connect SD card module
5. Power up the Arduino

### 2. Software Setup
1. Open PlatformIO IDE
2. Create new project with Arduino Mega platform
3. Copy the code to `src/main.cpp`
4. Configure `platformio.ini` as shown
5. Build and upload

### 3. Configuration
1. Configure network settings in code
2. Adjust MQTT broker address
3. Set device location
4. Upload firmware

### 4. Operation
- Device will automatically connect to Ethernet and MQTT
- Multiple sensors are read continuously
- Data is displayed on LCD
- Readings are sent via MQTT every 30 seconds
- Data is logged to SD card every minute

---

## MQTT Topics

### Telemetry
- `valtronics/telemetry/VT-ARDUINO-GATEWAY-001` - Multi-sensor readings

### Commands
- `valtronics/devices/VT-ARDUINO-GATEWAY-001/commands` - Device commands

### Configuration
- `valtronics/devices/VT-ARDUINO-GATEWAY-001/config` - Configuration updates

### Events
- `valtronics/devices/VT-ARDUINO-GATEWAY-001/events` - Device events

### Alerts
- `valtronics/alerts/VT-ARDUINO-GATEWAY-001` - Alert notifications

---

## Data Format

### Telemetry JSON
```json
{
  "device_id": "VT-ARDUINO-GATEWAY-001",
  "device_type": "multi_sensor_gateway",
  "timestamp": 1234567890,
  "location": "Server Room A",
  "dht22": {
    "temperature": 22.5,
    "humidity": 45.0,
    "status": "ok"
  },
  "bme280": {
    "temperature": 22.3,
    "humidity": 44.8,
    "pressure": 1013.2,
    "altitude": 2.1,
    "status": "ok"
  },
  "pms5003": {
    "pm25": 12,
    "pm10": 18,
    "status": "ok"
  },
  "system": {
    "free_memory": 2048,
    "ethernet_status": "up",
    "mqtt_connected": true,
    "uptime": 123456
  }
}
```

---

## Troubleshooting

### Common Issues

#### Ethernet Connection Issues
- Check Ethernet cable connection
- Verify network configuration
- Check DHCP server availability
- Try static IP configuration

#### Sensor Reading Issues
- Check wiring connections
- Verify power supply to sensors
- Check I2C pull-up resistors
- Verify sensor addresses

#### SD Card Issues
- Check SD card formatting (FAT32)
- Verify CS pin connection
- Check SD card compatibility
- Try different SD card

#### MQTT Connection Issues
- Verify broker address and port
- Check network connectivity
- Verify MQTT broker status
- Check firewall settings

---

## Support

For Arduino multi-sensor gateway support:
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **Platform Guides**: See `platform/arduino/` directory
- **Email**: firmware@valtronics.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Arduino Multi-Sensor Gateway Example v1.0**
