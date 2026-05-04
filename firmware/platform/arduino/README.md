# Arduino Platform Firmware

**Arduino-based firmware for Valtronics IoT devices**

---

## Overview

Arduino provides an accessible entry point for Valtronics devices, ideal for simple sensors, prototypes, and educational purposes. This platform supports various Arduino boards including Uno, Nano, Mega, and compatible boards with WiFi shields.

---

## Supported Boards

### Arduino Uno/Nano
- **CPU**: ATmega328P (8-bit, 16 MHz)
- **Memory**: 2 KB SRAM, 32 KB Flash
- **Peripherals**: 14 digital I/O, 6 analog inputs, UART, I2C, SPI
- **Use Cases**: Simple sensors, prototypes, educational projects

### Arduino Mega
- **CPU**: ATmega2560 (8-bit, 16 MHz)
- **Memory**: 8 KB SRAM, 256 KB Flash
- **Peripherals**: 54 digital I/O, 16 analog inputs, 4 UART, I2C, SPI
- **Use Cases**: Multi-sensor devices, complex prototypes

### ESP8266 (Arduino Compatible)
- **CPU**: Tensilica L106 (32-bit, 80/160 MHz)
- **Memory**: 80 KB SRAM, 4-16 MB Flash
- **Peripherals**: WiFi, GPIO, ADC, I2C, SPI, UART
- **Use Cases**: WiFi-enabled sensors, IoT devices

---

## Directory Structure

```
platform/arduino/
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
├── examples/                    # Example applications
│   ├── uno/                     # Arduino Uno examples
│   ├── mega/                    # Arduino Mega examples
│   └── esp8266/                  # ESP8266 examples
└── docs/                        # Documentation
```

---

## Quick Start

### 1. Setup Development Environment
```bash
# Install Arduino IDE
# Download from https://www.arduino.cc/en/software

# Or use PlatformIO
pip install platformio
```

### 2. Create New Project
```bash
# Using PlatformIO
pio project init --board uno

# Using Arduino IDE
# File -> New -> Save as valtronics-arduino
```

### 3. Configure Project
```ini
# platformio.ini
[env:uno]
platform = atmelavr
board = uno
framework = arduino
lib_deps = 
    PubSubClient
    ArduinoJson
    DHT sensor library
    Ethernet
    SD

[env:mega]
platform = atmelavr
board = megaatmega2560
framework = arduino
lib_deps = 
    PubSubClient
    ArduinoJson
    DHT sensor library
    Ethernet
    SD

[env:nodemcuv2]
platform = espressif8266
board = nodemcuv2
framework = arduino
lib_deps = 
    PubSubClient
    ArduinoJson
    DHT sensor library
    ESP8266WiFi
    WiFiManager
```

### 4. Write Firmware
```cpp
#include <Arduino.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <Ethernet.h>
#include <PubSubClient.h>

// Device configuration
#define DEVICE_ID "VT-ARDUINO-001"
#define DHT_PIN 2
#define DHT_TYPE DHT22

// Ethernet configuration
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 1, 177);
IPAddress server(192, 168, 1, 100);

// Global variables
DHT dht(DHT_PIN, DHT_TYPE);
EthernetClient ethClient;
PubSubClient mqttClient(ethClient);

void setup() {
    Serial.begin(9600);
    Serial.println("Valtronics Arduino Device Starting...");
    
    // Initialize sensors
    dht.begin();
    
    // Initialize Ethernet
    setupEthernet();
    
    // Initialize MQTT
    setupMQTT();
    
    Serial.println("Device ready!");
}

void loop() {
    // Handle MQTT
    if (!mqttClient.connected()) {
        setupMQTT();
    }
    mqttClient.loop();
    
    // Main application logic
    handleApplication();
    
    delay(30000);  // Send every 30 seconds
}

void setupEthernet() {
    Serial.println("Initializing Ethernet...");
    
    // Try to get IP address from DHCP
    if (Ethernet.begin(mac) == 0) {
        Serial.println("Failed to configure Ethernet using DHCP");
        // Try to configure using IP address
        Ethernet.begin(mac, ip);
    }
    
    Serial.print("IP address: ");
    Serial.println(Ethernet.localIP());
    
    // Give the Ethernet shield a second to initialize
    delay(1000);
}

void setupMQTT() {
    mqttClient.setServer(server, 1883);
    mqttClient.setCallback(mqttCallback);
    
    if (mqttClient.connect(DEVICE_ID)) {
        Serial.println("Connected to MQTT broker");
        
        // Subscribe to topics
        mqttClient.subscribe("valtronics/devices/" DEVICE_ID "/commands");
    } else {
        Serial.println("Failed to connect to MQTT broker");
    }
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
}

void handleCommand(String command) {
    StaticJsonDocument<200> doc;
    deserializeJson(doc, command);
    
    String cmd = doc["command"];
    
    if (cmd == "reboot") {
        Serial.println("Rebooting device...");
        asm volatile ("jmp 0");  // Arduino soft reboot
    }
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
    telemetry["free_memory"] = getFreeMemory();
    
    // Publish telemetry
    char payload[300];
    serializeJson(telemetry, payload);
    mqttClient.publish("valtronics/telemetry", payload);
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

int getFreeMemory() {
    extern int __heap_start, *__brkval;
    int v;
    return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval);
}
```

---

## Sensor Integration

### DHT22 Temperature/Humidity Sensor
```cpp
#include <DHT.h>

#define DHT_PIN 2
#define DHT_TYPE DHT22

DHT dht(DHT_PIN, DHT_TYPE);

void setupDHT() {
    dht.begin();
    Serial.println("DHT22 sensor initialized");
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

void printSensorData() {
    float temp = readTemperature();
    float humidity = readHumidity();
    
    Serial.print("Temperature: ");
    Serial.print(temp);
    Serial.println(" °C");
    
    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.println(" %");
}
```

### BMP180 Pressure Sensor
```cpp
#include <Wire.h>
#include <BMP180.h>

BMP180 bmp;

void setupBMP180() {
    if (!bmp.begin()) {
        Serial.println("Could not find a valid BMP180 sensor, check wiring!");
        return;
    }
    
    bmp.setSeaLevelPressure(101325);  // Set sea level pressure
    Serial.println("BMP180 sensor initialized");
}

float readPressure() {
    float pressure = bmp.readPressure();
    if (pressure == 0) {
        Serial.println("Failed to read pressure from BMP180 sensor!");
        return NAN;
    }
    return pressure / 100.0F;  // Convert to hPa
}

float readAltitude() {
    float altitude = bmp.readAltitude();
    return altitude;
}

void printPressureData() {
    float pressure = readPressure();
    float altitude = readAltitude();
    
    Serial.print("Pressure: ");
    Serial.print(pressure);
    Serial.println(" hPa");
    
    Serial.print("Altitude: ");
    Serial.print(altitude);
    Serial.println(" meters");
}
```

### MQ-135 Air Quality Sensor
```cpp
#define MQ135_PIN A0

void setupMQ135() {
    pinMode(MQ135_PIN, INPUT);
    Serial.println("MQ-135 sensor initialized");
}

int readAirQuality() {
    int sensorValue = analogRead(MQ135_PIN);
    return sensorValue;
}

float getPPM(int sensorValue) {
    // Convert analog reading to PPM (calibration required)
    float ppm = sensorValue * 0.1;  // Example conversion factor
    return ppm;
}

void printAirQuality() {
    int sensorValue = readAirQuality();
    float ppm = getPPM(sensorValue);
    
    Serial.print("Air Quality: ");
    Serial.print(sensorValue);
    Serial.print(" (");
    Serial.print(ppm);
    Serial.println(" PPM)");
}
```

---

## Communication

### Ethernet Communication
```cpp
#include <SPI.h>
#include <Ethernet.h>
#include <PubSubClient.h>

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 1, 177);
IPAddress server(192, 168, 1, 100);

EthernetClient ethClient;
PubSubClient mqttClient(ethClient);

void setupEthernet() {
    Serial.println("Initializing Ethernet...");
    
    if (Ethernet.begin(mac) == 0) {
        Serial.println("Failed to configure Ethernet using DHCP");
        Ethernet.begin(mac, ip);
    }
    
    Serial.print("IP address: ");
    Serial.println(Ethernet.localIP());
    
    delay(1000);  // Allow Ethernet to initialize
}

void setupMQTT() {
    mqttClient.setServer(server, 1883);
    mqttClient.setCallback(mqttCallback);
    
    if (mqttClient.connect("VT-ARDUINO-001")) {
        Serial.println("Connected to MQTT broker");
        mqttClient.subscribe("valtronics/devices/VT-ARDUINO-001/commands");
    } else {
        Serial.println("Failed to connect to MQTT broker");
    }
}

void publishTelemetry() {
    StaticJsonDocument<200> doc;
    doc["device_id"] = "VT-ARDUINO-001";
    doc["temperature"] = readTemperature();
    doc["humidity"] = readHumidity();
    doc["timestamp"] = millis();
    
    char payload[200];
    serializeJson(doc, payload);
    
    mqttClient.publish("valtronics/telemetry", payload);
}
```

### WiFi Communication (ESP8266)
```cpp
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <WiFiManager.h>

#define MQTT_SERVER "mqtt.valtronics.com"
#define MQTT_PORT 1883

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
WiFiManager wifiManager;

void setupWiFi() {
    wifiManager.setDebugOutput(false);
    
    if (!wifiManager.autoConnect("Valtronics-Setup")) {
        Serial.println("Failed to connect to WiFi");
        ESP.restart();
    }
    
    Serial.println("WiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
}

void setupMQTT() {
    mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
    mqttClient.setCallback(mqttCallback);
    
    if (mqttClient.connect("VT-ESP8266-001")) {
        Serial.println("Connected to MQTT broker");
        mqttClient.subscribe("valtronics/devices/VT-ESP8266-001/commands");
    } else {
        Serial.println("Failed to connect to MQTT broker");
    }
}
```

### Serial Communication
```cpp
void setupSerial() {
    Serial.begin(9600);
    Serial.println("Valtronics Arduino Device");
}

void sendSerialData() {
    StaticJsonDocument<200> doc;
    doc["device_id"] = "VT-ARDUINO-001";
    doc["temperature"] = readTemperature();
    doc["humidity"] = readHumidity();
    doc["timestamp"] = millis();
    
    serializeJson(doc, Serial);
    Serial.println();  // Add newline
}

String receiveSerialCommand() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();
        return command;
    }
    return "";
}

void handleSerialCommands() {
    String command = receiveSerialCommand();
    if (command.length() > 0) {
        if (command == "status") {
            printStatus();
        } else if (command == "sensors") {
            printSensorData();
        } else if (command == "reboot") {
            Serial.println("Rebooting...");
            asm volatile ("jmp 0");
        }
    }
}
```

---

## Data Storage

### SD Card Storage
```cpp
#include <SPI.h>
#include <SD.h>

#define CS_PIN 10

File dataFile;

void setupSDCard() {
    Serial.print("Initializing SD card...");
    
    if (!SD.begin(CS_PIN)) {
        Serial.println("Initialization failed!");
        return;
    }
    
    Serial.println("Initialization done.");
}

void logToSDCard(String data) {
    dataFile = SD.open("data.log", FILE_WRITE);
    
    if (dataFile) {
        dataFile.println(data);
        dataFile.close();
        Serial.println("Data logged to SD card");
    } else {
        Serial.println("Error opening data.log");
    }
}

void readFromSDCard() {
    dataFile = SD.open("data.log", FILE_READ);
    
    if (dataFile) {
        Serial.println("data.log:");
        while (dataFile.available()) {
            Serial.write(dataFile.read());
        }
        dataFile.close();
    } else {
        Serial.println("Error opening data.log");
    }
}
```

### EEPROM Storage
```cpp
#include <EEPROM.h>

#define EEPROM_SIZE 512

void setupEEPROM() {
    EEPROM.begin(EEPROM_SIZE);
    Serial.println("EEPROM initialized");
}

void saveToEEPROM(int address, String data) {
    for (int i = 0; i < data.length(); ++i) {
        EEPROM.write(address + i, data[i]);
    }
    EEPROM.write(address + data.length(), '\0');  // Null terminator
    EEPROM.commit();
    
    Serial.println("Data saved to EEPROM");
}

String readFromEEPROM(int address) {
    String data = "";
    char c = EEPROM.read(address);
    
    while (c != '\0' && address < EEPROM_SIZE) {
        data += c;
        address++;
        c = EEPROM.read(address);
    }
    
    return data;
}

void clearEEPROM() {
    for (int i = 0; i < EEPROM_SIZE; i++) {
        EEPROM.write(i, 0);
    }
    EEPROM.commit();
    Serial.println("EEPROM cleared");
}
```

---

## Power Management

### Battery Monitoring
```cpp
#define BATTERY_PIN A0

void setupBatteryMonitor() {
    pinMode(BATTERY_PIN, INPUT);
    Serial.println("Battery monitor initialized");
}

float readBatteryVoltage() {
    int sensorValue = analogRead(BATTERY_PIN);
    float voltage = sensorValue * (5.0 / 1023.0);  // Convert to voltage
    
    // Apply voltage divider factor if used
    voltage *= 2.0;  // Example: 1:1 voltage divider
    
    return voltage;
}

int getBatteryPercentage(float voltage) {
    // Convert voltage to percentage (calibration required)
    if (voltage >= 4.2) return 100;
    if (voltage <= 3.0) return 0;
    
    // Linear approximation
    return (voltage - 3.0) / (4.2 - 3.0) * 100;
}

void printBatteryStatus() {
    float voltage = readBatteryVoltage();
    int percentage = getBatteryPercentage(voltage);
    
    Serial.print("Battery: ");
    Serial.print(voltage);
    Serial.print("V (");
    Serial.print(percentage);
    Serial.println("%)");
}
```

### Low Power Mode
```cpp
#include <LowPower.h>

void enterLowPowerMode() {
    Serial.println("Entering low power mode");
    
    // Put Arduino to sleep for 8 seconds
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
    
    // Code continues after wake up
    Serial.println("Woke up from low power mode");
}

void setupLowPower() {
    // Disable unnecessary peripherals
    ADCSRA = 0;  // Disable ADC
    power_adc_disable();
    power_spi_disable();
    power_twi_disable();
    
    Serial.println("Low power mode configured");
}

void periodicSleep() {
    // Sleep for 1 minute
    for (int i = 0; i < 7; i++) {
        LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
    }
    
    // Wake up and handle tasks
    handleApplication();
}
```

---

## Error Handling

### Watchdog Timer
```cpp
#include <avr/wdt.h>

void setupWatchdog() {
    wdt_enable(WDTO_8S);  // 8 second watchdog
    Serial.println("Watchdog timer enabled");
}

void resetWatchdog() {
    wdt_reset();
}

void handleWatchdog() {
    // Reset watchdog in main loop
    resetWatchdog();
    
    // Handle long operations
    handleLongOperation();
    
    // Reset watchdog again
    resetWatchdog();
}

void handleLongOperation() {
    // For operations that might take longer than watchdog timeout
    wdt_disable();
    
    // Perform long operation
    performLongOperation();
    
    // Re-enable watchdog
    wdt_enable(WDTO_8S);
}
```

### Error Recovery
```cpp
#include <avr/wdt.h>

void handleError(String error) {
    Serial.print("Error: ");
    Serial.println(error);
    
    // Log error to EEPROM
    saveToEEPROM(0, "ERROR: " + error);
    
    // Blink LED to indicate error
    for (int i = 0; i < 10; i++) {
        digitalWrite(LED_BUILTIN, HIGH);
        delay(100);
        digitalWrite(LED_BUILTIN, LOW);
        delay(100);
    }
    
    // Reset after error
    delay(1000);
    wdt_enable(WDTO_15MS);
    while (1);  // Wait for watchdog reset
}

void checkSystemHealth() {
    // Check free memory
    int freeMemory = getFreeMemory();
    if (freeMemory < 100) {
        handleError("Low memory");
    }
    
    // Check sensor connectivity
    float temp = readTemperature();
    if (isnan(temp)) {
        handleError("Sensor disconnected");
    }
    
    // Check network connectivity
    if (!mqttClient.connected()) {
        handleError("Network disconnected");
    }
}
```

---

## Testing

### Unit Tests
```cpp
void testTemperatureSensor() {
    float temp = readTemperature();
    assert(!isnan(temp));
    assert(temp > -40 && temp < 85);  // Valid range for DHT22
    Serial.println("Temperature sensor test passed");
}

void testMQTTConnection() {
    assert(mqttClient.connected());
    Serial.println("MQTT connection test passed");
}

void testEEPROM() {
    String testData = "test";
    saveToEEPROM(0, testData);
    String readData = readFromEEPROM(0);
    assert(readData == testData);
    Serial.println("EEPROM test passed");
}

void runTests() {
    Serial.println("Running tests...");
    testTemperatureSensor();
    testMQTTConnection();
    testEEPROM();
    Serial.println("All tests passed");
}
```

### Integration Tests
```cpp
void testSensorToMQTT() {
    // Read sensor
    float temp = readTemperature();
    assert(!isnan(temp));
    
    // Publish to MQTT
    StaticJsonDocument<200> doc;
    doc["temperature"] = temp;
    char payload[200];
    serializeJson(doc, payload);
    
    bool success = mqttClient.publish("test/temperature", payload);
    assert(success);
    
    Serial.println("Sensor to MQTT test passed");
}

void testPowerManagement() {
    float voltage = readBatteryVoltage();
    assert(voltage > 0);
    
    int percentage = getBatteryPercentage(voltage);
    assert(percentage >= 0 && percentage <= 100);
    
    Serial.println("Power management test passed");
}
```

---

## Examples

### Basic Temperature Sensor
```cpp
#include <Arduino.h>
#include <DHT.h>
#include <Ethernet.h>
#include <PubSubClient.h>

#define DHT_PIN 2
#define DHT_TYPE DHT22

DHT dht(DHT_PIN, DHT_TYPE);
EthernetClient ethClient;
PubSubClient mqttClient(ethClient);

void setup() {
    Serial.begin(9600);
    dht.begin();
    setupEthernet();
    setupMQTT();
}

void loop() {
    if (!mqttClient.connected()) {
        setupMQTT();
    }
    mqttClient.loop();
    
    float temp = dht.readTemperature();
    if (!isnan(temp)) {
        mqttClient.publish("valtronics/temperature", String(temp).c_str());
    }
    
    delay(30000);
}
```

### Multi-Sensor Device
```cpp
#include <Arduino.h>
#include <DHT.h>
#include <BMP180.h>
#include <MQ135.h>

#define DHT_PIN 2
#define MQ135_PIN A0

DHT dht(DHT_PIN, DHT22);
BMP180 bmp;

void setup() {
    Serial.begin(9600);
    dht.begin();
    bmp.begin();
    pinMode(MQ135_PIN, INPUT);
}

void loop() {
    // Read all sensors
    float temp = dht.readTemperature();
    float humidity = dht.readHumidity();
    float pressure = bmp.readPressure() / 100.0F;
    int airQuality = analogRead(MQ135_PIN);
    
    // Print all data
    Serial.print("Temperature: ");
    Serial.print(temp);
    Serial.println(" °C");
    
    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.println(" %");
    
    Serial.print("Pressure: ");
    Serial.print(pressure);
    Serial.println(" hPa");
    
    Serial.print("Air Quality: ");
    Serial.println(airQuality);
    
    delay(5000);
}
```

---

## Troubleshooting

### Common Issues

#### Memory Issues
```cpp
int getFreeMemory() {
    extern int __heap_start, *__brkval;
    int v;
    return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval);
}

void printMemoryUsage() {
    Serial.print("Free memory: ");
    Serial.print(getFreeMemory());
    Serial.println(" bytes");
}
```

#### Sensor Issues
```cpp
void debugSensors() {
    Serial.println("Debugging sensors...");
    
    // Test DHT sensor
    float temp = dht.readTemperature();
    if (isnan(temp)) {
        Serial.println("DHT sensor not responding");
        Serial.println("Check wiring and power supply");
    } else {
        Serial.print("DHT sensor OK: ");
        Serial.print(temp);
        Serial.println(" °C");
    }
}
```

#### Network Issues
```cpp
void debugNetwork() {
    Serial.println("Debugging network...");
    
    // Check Ethernet
    if (Ethernet.hardwareStatus() == EthernetNoHardware) {
        Serial.println("Ethernet shield not found");
    } else if (Ethernet.linkStatus() == LinkOFF) {
        Serial.println("Ethernet cable not connected");
    } else {
        Serial.println("Ethernet OK");
        Serial.print("IP: ");
        Serial.println(Ethernet.localIP());
    }
    
    // Check MQTT
    if (!mqttClient.connected()) {
        Serial.println("MQTT not connected");
        Serial.print("MQTT state: ");
        Serial.println(mqttClient.state());
    } else {
        Serial.println("MQTT OK");
    }
}
```

---

## Support

For Arduino firmware support:
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **Community**: Arduino Forum
- **Email**: firmware@valtronics.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Arduino Platform Firmware v1.0**
