# Vibration Sensor Firmware

**Complete firmware implementation for Valtronics industrial vibration monitoring devices**

---

## Overview

This application provides comprehensive vibration monitoring firmware for industrial equipment, supporting multiple vibration sensors, frequency analysis, fault detection, and predictive maintenance capabilities. It's designed for monitoring motors, pumps, compressors, and other rotating equipment.

---

## Features

### Sensor Support
- **Accelerometers**: ADXL345, MPU6050, LIS3DH, BMA400
- **Vibration Sensors**: Industrial vibration sensors with analog output
- **Multi-Axis**: 3-axis vibration monitoring
- **Frequency Range**: 10 Hz to 10 kHz coverage
- **Resolution**: High-resolution ADC for precise measurements

### Analysis Capabilities
- **FFT Analysis**: Real-time frequency spectrum analysis
- **Time Domain**: Peak, RMS, crest factor calculations
- **Frequency Domain**: Harmonic analysis, bearing frequencies
- **Fault Detection**: Bearing, misalignment, unbalance, looseness
- **Health Scoring**: Equipment health assessment

### Advanced Features
- **Real-time Processing**: On-device FFT and analysis
- **Alert System**: Multi-level alerting based on severity
- **Data Compression**: Efficient data transmission
- **Wireless**: WiFi and LoRa support
- **Power Management**: Optimized for industrial environments
- **Industrial Protocols**: Modbus, CAN bus support

---

## Hardware Requirements

### Minimum Requirements
- **Microcontroller**: ESP32 or STM32F4/F7 series
- **Memory**: 64KB+ SRAM, 1MB+ Flash
- **ADC**: 12-bit or better ADC
- **Connectivity**: WiFi, Ethernet, or LoRa
- **Power**: 5V or 3.3V industrial power supply

### Recommended Components
- **ESP32 DevKit**: Development and production
- **STM32F429IGT6**: Industrial applications
- **ADXL345**: 3-axis accelerometer
- **MPU6050**: 6-axis IMU with accelerometer
- **Industrial Enclosure**: IP67 rated enclosure
- **Power Supply**: 24V DC industrial power supply

---

## Directory Structure

```
applications/vibration_sensor/
├── README.md                    # This file
├── platformio.ini               # PlatformIO configuration
├── src/                         # Source code
│   ├── main.cpp                 # Main application
│   ├── config/                  # Configuration
│   ├── drivers/                  # Hardware drivers
│   │   ├── adxl345_driver.h      # ADXL345 driver
│   │   ├── mpu6050_driver.h      # MPU6050 driver
│   │   └── analog_vibration.h     # Analog vibration sensor
│   ├── sensors/                  # Sensor interfaces
│   │   ├── vibration_sensor.h     # Vibration sensor interface
│   │   ├── fft_analyzer.h         # FFT analysis
│   │   ├── fault_detector.h       # Fault detection
│   │   └── health_scorer.h        # Health scoring
│   ├── communication/            # Communication
│   │   ├── mqtt_client.h         # MQTT client
│   │   ├── modbus_client.h       # Modbus client
│   │   └── data_compressor.h     # Data compression
│   ├── analysis/                 # Data analysis
│   │   ├── time_domain.h         # Time domain analysis
│   │   ├── frequency_domain.h     # Frequency domain analysis
│   │   └── signal_processing.h    # Signal processing
│   ├── alerts/                   # Alert system
│   │   ├── alert_manager.h       # Alert manager
│   │   └── industrial_alerts.h     # Industrial alerts
│   ├── utils/                    # Utility functions
│   │   ├── math_utils.h          # Math utilities
│   │   ├── signal_utils.h        # Signal utilities
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
    "id": "VT-VIB-001",
    "name": "Vibration Sensor 1",
    "type": "vibration_sensor",
    "version": "2.0.0",
    "location": "Motor A-01",
    "equipment_type": "motor",
    "rated_speed": 1800
  },
  "sensor": {
    "type": "ADXL345",
    "interface": "I2C",
    "address": "0x53",
    "range": "±16g",
    "sample_rate": 3200,
    "axes": ["x", "y", "z"]
  },
  "analysis": {
    "fft_size": 1024,
    "window_size": 256,
    "overlap": 0.5,
    "frequency_range": [10, 1000],
    "frequency_resolution": 2.0
  },
  "fault_detection": {
    "bearing_fault": {
      "enabled": true,
      "frequencies": [1, 2, 3],
      "threshold": 0.3
    },
    "misalignment": {
      "enabled": true,
      "frequencies": [1, 2],
      "threshold": 0.2
    },
    "unbalance": {
      "enabled": true,
      "frequency": 1,
      "threshold": 0.4
    },
    "looseness": {
      "enabled": true,
      "frequencies": [1, 2, 3, 4, 5],
      "threshold": 0.5
    }
  },
  "alerts": {
    "vibration_warning": 5.0,
    "vibration_critical": 10.0,
    "crest_factor_warning": 3.0,
    "health_score_warning": 70,
    "health_score_critical": 50
  },
  "communication": {
    "mqtt": {
      "broker": "mqtt.valtronics.com",
      "port": 1883,
      "telemetry_interval": 30,
      "spectrum_interval": 300
    },
    "modbus": {
      "enabled": true,
      "register_base": 4000
    }
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
    Adafruit ADXL345
    Adafruit MPU6050
    ArduinoFFT
    WiFiManager
    ArduinoOTA
    ModbusMaster

build_flags = 
    -DCORE_DEBUG_LEVEL=3
    -DCONFIG_ARDUHAL_LOG_COLORS
    -DFFT_MAX_SAMPLES=1024
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
#include <ArduinoFFT.h>

#include "config/device_config.h"
#include "sensors/vibration_sensor.h"
#include "analysis/fft_analyzer.h"
#include "analysis/fault_detector.h"
#include "communication/mqtt_client.h"
#include "alerts/alert_manager.h"
#include "utils/logger.h"
#include "utils/json_utils.h"

// Global objects
VibrationSensor* vibration_sensor = nullptr;
FFTAnalyzer* fft_analyzer = nullptr;
FaultDetector* fault_detector = nullptr;
MQTTClient* mqtt_client = nullptr;
AlertManager* alert_manager = nullptr;
DeviceConfig* device_config = nullptr;

// Global state
bool system_ready = false;
uint32_t last_telemetry_time = 0;
uint32_t last_spectrum_time = 0;

void setup() {
    Serial.begin(115200);
    Logger::info("Valtronics Vibration Sensor Starting...");
    
    // Initialize configuration
    device_config = new DeviceConfig();
    if (!device_config->load()) {
        Logger::error("Failed to load device configuration");
        return;
    }
    
    // Initialize components
    initialize_sensors();
    initialize_analysis();
    initialize_alerts();
    initialize_communication();
    initialize_ota();
    
    system_ready = true;
    Logger::info("Vibration sensor ready");
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
    
    // Read vibration data
    vibration_data_t vibration_data = vibration_sensor->read();
    
    // Perform FFT analysis
    spectrum_data_t spectrum_data = fft_analyzer->analyze(vibration_data);
    
    // Detect faults
    fault_data_t fault_data = fault_detector->detect(vibration_data, spectrum_data);
    
    // Calculate health score
    health_score_t health_score = calculate_health_score(vibration_data, spectrum_data, fault_data);
    
    // Update display
    update_display(vibration_data, health_score);
    
    // Handle alerts
    alert_manager->check_alerts(vibration_data, spectrum_data, fault_data, health_score);
    
    // Send telemetry
    handle_telemetry(vibration_data, spectrum_data, fault_data, health_score);
    
    // Handle commands
    handle_commands();
    
    delay(1000);
}

void initialize_sensors() {
    Logger::info("Initializing vibration sensor...");
    
    vibration_sensor = new VibrationSensor();
    if (!vibration_sensor->init()) {
        Logger::error("Failed to initialize vibration sensor");
        return;
    }
    
    // Configure sensor
    vibration_sensor->set_sample_rate(device_config->get_sample_rate());
    vibration_sensor->set_range(device_config->get_range());
    
    Logger::info("Vibration sensor initialized");
}

void initialize_analysis() {
    Logger::info("Initializing analysis components...");
    
    // Initialize FFT analyzer
    fft_analyzer = new FFTAnalyzer(device_config->get_fft_size());
    fft_analyzer->set_window_size(device_config->get_window_size());
    fft_analyzer->set_overlap(device_config->get_overlap());
    
    // Initialize fault detector
    fault_detector = new FaultDetector();
    fault_detector->set_equipment_speed(device_config->get_equipment_speed());
    fault_detector->configure_fault_detection(device_config->get_fault_config());
    
    Logger::info("Analysis components initialized");
}

void initialize_alerts() {
    Logger::info("Initializing alert system...");
    
    alert_manager = new AlertManager();
    if (!alert_manager->init()) {
        Logger::error("Failed to initialize alert system");
        return;
    }
    
    // Configure alert thresholds
    alert_manager->set_vibration_thresholds(
        device_config->get_vibration_warning_threshold(),
        device_config->get_vibration_critical_threshold()
    );
    
    Logger::info("Alert system initialized");
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
    
    if (!wifiManager.autoConnect("Valtronics-VibSensor")) {
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

void handle_telemetry(vibration_data_t vibration_data, spectrum_data_t spectrum_data, 
                      fault_data_t fault_data, health_score_t health_score) {
    uint32_t current_time = millis();
    
    // Send basic telemetry
    if (current_time - last_telemetry_time >= device_config->get_telemetry_interval() * 1000) {
        send_basic_telemetry(vibration_data, health_score);
        last_telemetry_time = current_time;
    }
    
    // Send spectrum data
    if (current_time - last_spectrum_time >= device_config->get_spectrum_interval() * 1000) {
        send_spectrum_telemetry(spectrum_data, fault_data);
        last_spectrum_time = current_time;
    }
}

void send_basic_telemetry(vibration_data_t vibration_data, health_score_t health_score) {
    JsonObject telemetry;
    telemetry["device_id"] = device_config->get_device_id();
    telemetry["timestamp"] = millis();
    telemetry["device_type"] = device_config->get_device_type();
    telemetry["location"] = device_config->get_device_location();
    
    // Vibration data
    JsonObject vibration;
    vibration["rms_x"] = vibration_data.rms_x;
    vibration["rms_y"] = vibration_data.rms_y;
    vibration["rms_z"] = vibration_data.rms_z;
    vibration["peak_x"] = vibration_data.peak_x;
    vibration["peak_y"] = vibration_data.peak_y;
    vibration["peak_z"] = vibration_data.peak_z;
    vibration["crest_factor"] = vibration_data.crest_factor;
    telemetry["vibration"] = vibration;
    
    // Health score
    JsonObject health;
    health["overall"] = health_score.overall;
    health["bearing"] = health_score.bearing;
    health["alignment"] = health_score.alignment;
    health["balance"] = health_score.balance;
    health["mechanical"] = health_score.mechanical;
    telemetry["health"] = health;
    
    // System information
    JsonObject system;
    system["free_heap"] = ESP.getFreeHeap();
    system["wifi_rssi"] = WiFi.RSSI();
    system["uptime"] = millis();
    system["sample_rate"] = vibration_data.sample_rate;
    telemetry["system"] = system;
    
    // Send telemetry
    String payload = JSONUtils::serialize(telemetry);
    if (mqtt_client->publish(device_config->get_mqtt_telemetry_topic(), payload)) {
        Logger::info("Basic telemetry sent");
    } else {
        Logger::error("Failed to send basic telemetry");
    }
}

void send_spectrum_telemetry(spectrum_data_t spectrum_data, fault_data_t fault_data) {
    JsonObject spectrum;
    spectrum["device_id"] = device_config->get_device_id();
    spectrum["timestamp"] = millis();
    spectrum["fft_size"] = spectrum_data.fft_size;
    spectrum["frequency_resolution"] = spectrum_data.frequency_resolution;
    
    // Frequency spectrum (compressed)
    JsonArray frequencies;
    JsonArray amplitudes;
    
    // Send only significant peaks to save bandwidth
    for (int i = 0; i < spectrum_data.num_peaks; i++) {
        if (spectrum_data.peaks[i].amplitude > 0.01) {  // Threshold
            frequencies.add(spectrum_data.peaks[i].frequency);
            amplitudes.add(spectrum_data.peaks[i].amplitude);
        }
    }
    
    spectrum["frequencies"] = frequencies;
    spectrum["amplitudes"] = amplitudes;
    
    // Fault data
    JsonObject faults;
    faults["bearing_fault"] = fault_data.bearing_fault;
    faults["misalignment"] = fault_data.misalignment;
    faults["unbalance"] = fault_data.unbalance;
    faults["looseness"] = fault_data.looseness;
    spectrum["faults"] = faults;
    
    // Send spectrum data
    String payload = JSONUtils::serialize(spectrum);
    if (mqtt_client->publish("valtronics/spectrum", payload)) {
        Logger::info("Spectrum telemetry sent");
    } else {
        Logger::error("Failed to send spectrum telemetry");
    }
}

health_score_t calculate_health_score(vibration_data_t vibration_data, spectrum_data_t spectrum_data, fault_data_t fault_data) {
    health_score_t health_score;
    
    // Calculate equipment speed
    float equipment_speed = get_dominant_frequency(spectrum_data);
    
    // Calculate individual health scores
    health_score.bearing = calculate_bearing_health(fault_data.bearing_fault, equipment_speed);
    health_score.alignment = calculate_alignment_health(fault_data.misalignment, equipment_speed);
    health_score.balance = calculate_balance_health(fault_data.unbalance, equipment_speed);
    health_score.mechanical = calculate_mechanical_health(vibration_data, equipment_speed);
    
    // Calculate overall health score
    health_score.overall = (health_score.bearing + health_score.alignment + 
                           health_score.balance + health_score.mechanical) / 4.0;
    
    return health_score;
}

float get_dominant_frequency(spectrum_data_t spectrum_data) {
    float max_amplitude = 0;
    float dominant_frequency = 0;
    
    for (int i = 0; i < spectrum_data.num_peaks; i++) {
        if (spectrum_data.peaks[i].amplitude > max_amplitude) {
            max_amplitude = spectrum_data.peaks[i].amplitude;
            dominant_frequency = spectrum_data.peaks[i].frequency;
        }
    }
    
    return dominant_frequency;
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
        vibration_sensor->calibrate();
    } else if (cmd == "status") {
        send_status();
    } else if (cmd == "analyze") {
        Logger::info("Analyze command received");
        trigger_immediate_analysis();
    } else if (cmd == "set_speed") {
        float speed = command["speed"];
        Logger::info("Setting equipment speed: " + String(speed));
        fault_detector->set_equipment_speed(speed);
    } else {
        Logger::warning("Unknown command: " + cmd);
    }
}

void trigger_immediate_analysis() {
    // Read vibration data
    vibration_data_t vibration_data = vibration_sensor->read();
    
    // Perform immediate analysis
    spectrum_data_t spectrum_data = fft_analyzer->analyze(vibration_data);
    fault_data_t fault_data = fault_detector->detect(vibration_data, spectrum_data);
    
    // Send results immediately
    send_spectrum_telemetry(spectrum_data, fault_data);
}

void update_display(vibration_data_t vibration_data, health_score_t health_score) {
    // Update local display if available
    if (device_config->get_display_enabled()) {
        // Update LCD display
        update_lcd_display(vibration_data, health_score);
    }
}

void update_lcd_display(vibration_data_t vibration_data, health_score_t health_score) {
    // Format display data
    String line1 = "Vib: " + String(vibration_data.rms_x, 2) + "g";
    String line2 = "Health: " + String(health_score.overall, 1) + "%";
    
    // Send to display
    lcd_display.update(line1, line2);
}

void send_status() {
    JsonObject status;
    status["device_id"] = device_config->get_device_id();
    status["device_type"] = device_config->get_device_type();
    status["firmware_version"] = device_config->get_firmware_version();
    status["uptime"] = millis();
    status["free_heap"] = ESP.getFreeHeap();
    status["wifi_rssi"] = WiFi.RSSI();
    status["sensor_connected"] = vibration_sensor->is_connected();
    status["last_calibration"] = vibration_sensor->get_last_calibration();
    
    String payload = JSONUtils::serialize(status);
    mqtt_client->publish("valtronics/devices/" + device_config->get_device_id() + "/status", payload);
    
    Logger::info("Status sent");
}
```

### FFT Analyzer
```cpp
// analysis/fft_analyzer.h
#ifndef FFT_ANALYZER_H
#define FFT_ANALYZER_H

#include <ArduinoFFT.h>
#include "sensors/vibration_sensor.h"

typedef struct {
    float frequency;
    float amplitude;
} frequency_peak_t;

typedef struct {
    frequency_peak_t* peaks;
    int num_peaks;
    int fft_size;
    float frequency_resolution;
} spectrum_data_t;

class FFTAnalyzer {
private:
    int fft_size;
    int window_size;
    float overlap;
    arduinoFFT fft;
    double* fft_input;
    double* fft_output;
    float sample_rate;
    
public:
    FFTAnalyzer(int size = 512);
    ~FFTAnalyzer();
    
    bool init();
    spectrum_data_t analyze(vibration_data_t vibration_data);
    
    void set_sample_rate(float rate);
    void set_window_size(int size);
    void set_overlap(float overlap_ratio);
    
private:
    void apply_window(float* data, int size);
    void find_peaks(double* spectrum, frequency_peak_t* peaks, int* num_peaks);
    float calculate_frequency(int bin);
};

#endif // FFT_ANALYZER_H
```

```cpp
// analysis/fft_analyzer.cpp
#include "fft_analyzer.h"
#include "utils/math_utils.h"

FFTAnalyzer::FFTAnalyzer(int size) : fft_size(size), window_size(256), overlap(0.5) {
    fft_input = new double[fft_size];
    fft_output = new double[fft_size];
    sample_rate = 3200.0;
}

FFTAnalyzer::~FFTAnalyzer() {
    delete[] fft_input;
    delete[] fft_output;
}

bool FFTAnalyzer::init() {
    fft = arduinoFFT(fft_size, fft_size);
    return true;
}

spectrum_data_t FFTAnalyzer::analyze(vibration_data_t vibration_data) {
    spectrum_data_t spectrum_data;
    
    // Copy vibration data to FFT input
    for (int i = 0; i < fft_size; i++) {
        if (i < vibration_data.num_samples) {
            fft_input[i] = vibration_data.samples[i];
        } else {
            fft_input[i] = 0.0;
        }
    }
    
    // Apply window function
    apply_window(fft_input, fft_size);
    
    // Perform FFT
    fft.Windowing(fft_input, fft_output, fft_size, FFT_FORWARD);
    fft.Compute(fft_output, fft_input, fft_output, fft_size);
    
    // Find peaks in spectrum
    frequency_peak_t peaks[50];  // Maximum 50 peaks
    int num_peaks = 0;
    find_peaks(fft_output, peaks, &num_peaks);
    
    // Prepare spectrum data
    spectrum_data.peaks = new frequency_peak_t[num_peaks];
    spectrum_data.num_peaks = num_peaks;
    spectrum_data.fft_size = fft_size;
    spectrum_data.frequency_resolution = sample_rate / fft_size;
    
    for (int i = 0; i < num_peaks; i++) {
        spectrum_data.peaks[i] = peaks[i];
    }
    
    return spectrum_data;
}

void FFTAnalyzer::apply_window(float* data, int size) {
    // Apply Hanning window
    for (int i = 0; i < size; i++) {
        data[i] *= 0.5 * (1.0 - cos(2.0 * PI * i / (size - 1)));
    }
}

void FFTAnalyzer::find_peaks(double* spectrum, frequency_peak_t* peaks, int* num_peaks) {
    *num_peaks = 0;
    
    // Find peaks in spectrum
    for (int i = 1; i < fft_size / 2 - 1; i++) {
        if (spectrum[i] > spectrum[i-1] && spectrum[i] > spectrum[i+1]) {
            // Check if this is a significant peak
            float threshold = 0.01;  // Threshold for peak detection
            
            if (spectrum[i] > threshold && *num_peaks < 50) {
                peaks[*num_peaks].frequency = calculate_frequency(i);
                peaks[*num_peaks].amplitude = spectrum[i];
                (*num_peaks)++;
            }
        }
    }
    
    // Sort peaks by amplitude
    for (int i = 0; i < *num_peaks - 1; i++) {
        for (int j = i + 1; j < *num_peaks; j++) {
            if (peaks[j].amplitude > peaks[i].amplitude) {
                frequency_peak_t temp = peaks[i];
                peaks[i] = peaks[j];
                peaks[j] = temp;
            }
        }
    }
}

float FFTAnalyzer::calculate_frequency(int bin) {
    return bin * sample_rate / fft_size;
}
```

---

## Usage Examples

### Basic Vibration Monitor
```cpp
#include "config/device_config.h"
#include "sensors/vibration_sensor.h"
#include "analysis/fft_analyzer.h"

void setup() {
    Serial.begin(115200);
    
    // Load configuration
    DeviceConfig config;
    config.load();
    
    // Initialize vibration sensor
    VibrationSensor sensor;
    sensor.init();
    
    // Initialize FFT analyzer
    FFTAnalyzer fft_analyzer(1024);
    fft_analyzer.init();
    
    Serial.println("Vibration monitor ready");
}

void loop() {
    // Read vibration data
    vibration_data_t data = sensor.read();
    
    // Perform FFT analysis
    spectrum_data_t spectrum = fft_analyzer.analyze(data);
    
    // Send results
    send_telemetry(data, spectrum);
    
    delay(30000);  // Send every 30 seconds
}
```

### Industrial Motor Monitor
```cpp
#include "sensors/vibration_sensor.h"
#include "analysis/fault_detector.h"
#include "alerts/alert_manager.h"

void setup() {
    // Initialize components
    VibrationSensor sensor;
    sensor.init();
    
    FaultDetector fault_detector;
    fault_detector.set_equipment_speed(1800);  // Motor speed in RPM
    
    AlertManager alerts;
    alerts.init();
    
    Serial.println("Industrial motor monitor ready");
}

void loop() {
    // Read vibration data
    vibration_data_t data = sensor.read();
    
    // Perform FFT analysis
    FFTAnalyzer fft_analyzer;
    spectrum_data_t spectrum = fft_analyzer.analyze(data);
    
    // Detect faults
    fault_data_t faults = fault_detector.detect(data, spectrum);
    
    // Check for alerts
    if (faults.bearing_fault > 0.5) {
        alerts.trigger_alert("bearing_fault", faults.bearing_fault);
    }
    
    if (faults.unbalance > 0.4) {
        alerts.trigger_alert("unbalance", faults.unbalance);
    }
    
    // Send data
    send_industrial_telemetry(data, spectrum, faults);
    
    delay(30000);
}
```

---

## Testing

### Unit Tests
```cpp
void test_vibration_reading() {
    VibrationSensor sensor;
    assert(sensor.init());
    
    vibration_data_t data = sensor.read();
    assert(data.valid);
    assert(data.num_samples > 0);
    assert(data.rms_x >= 0);
    assert(data.rms_y >= 0);
    assert(data.rms_z >= 0);
}

void test_fft_analysis() {
    FFTAnalyzer fft_analyzer(512);
    assert(fft_analyzer.init());
    
    // Create test signal
    vibration_data_t test_data;
    test_data.num_samples = 512;
    test_data.samples = new float[512];
    
    // Generate test signal with known frequency
    for (int i = 0; i < 512; i++) {
        test_data.samples[i] = sin(2 * PI * 50 * i / 512);  // 50 Hz signal
    }
    
    spectrum_data_t spectrum = fft_analyzer.analyze(test_data);
    assert(spectrum.num_peaks > 0);
    
    // Check if 50 Hz peak is found
    bool found_50hz = false;
    for (int i = 0; i < spectrum.num_peaks; i++) {
        if (abs(spectrum.peaks[i].frequency - 50) < 2) {
            found_50hz = true;
            break;
        }
    }
    assert(found_50hz);
    
    delete[] test_data.samples;
}
```

### Integration Tests
```cpp
void test_sensor_to_analysis() {
    VibrationSensor sensor;
    FFTAnalyzer fft_analyzer;
    
    // Initialize components
    assert(sensor.init());
    assert(fft_analyzer.init());
    
    // Read sensor data
    vibration_data_t data = sensor.read();
    assert(data.valid);
    
    // Perform analysis
    spectrum_data_t spectrum = fft_analyzer.analyze(data);
    assert(spectrum.num_peaks > 0);
    
    // Validate results
    assert(spectrum.fft_size > 0);
    assert(spectrum.frequency_resolution > 0);
}

void test_fault_detection() {
    VibrationSensor sensor;
    FaultDetector fault_detector;
    
    // Initialize components
    assert(sensor.init());
    fault_detector.set_equipment_speed(1800);
    
    // Read sensor data
    vibration_data_t data = sensor.read();
    
    // Perform FFT analysis
    FFTAnalyzer fft_analyzer;
    spectrum_data_t spectrum = fft_analyzer.analyze(data);
    
    // Detect faults
    fault_data_t faults = fault_detector.detect(data, spectrum);
    
    // Validate fault data
    assert(faults.bearing_fault >= 0 && faults.bearing_fault <= 1);
    assert(faults.misalignment >= 0 && faults.misalignment <= 1);
    assert(faults.unbalance >= 0 && faults.unbalance <= 1);
    assert(faults.looseness >= 0 && faults.looseness <= 1);
}
```

---

## Troubleshooting

### Common Issues

#### Sensor Communication Problems
```cpp
void debug_vibration_sensor() {
    VibrationSensor sensor;
    
    if (!sensor.init()) {
        Serial.println("Sensor initialization failed");
        return;
    }
    
    if (!sensor.is_connected()) {
        Serial.println("Sensor not connected");
        Serial.println("Check wiring:");
        Serial.println("  - I2C connections (SDA, SCL)");
        Serial.println("  - Power supply (3.3V or 5V)");
        Serial.println("  - Pull-up resistors (if required)");
    } else {
        Serial.println("Sensor connected successfully");
        
        // Test reading
        vibration_data_t data = sensor.read();
        if (data.valid) {
            Serial.println("Sensor reading successful");
            Serial.print("RMS X: ");
            Serial.println(data.rms_x);
            Serial.print("RMS Y: ");
            Serial.println(data.rms_y);
            Serial.print("RMS Z: ");
            Serial.println(data.rms_z);
        } else {
            Serial.println("Invalid sensor reading");
        }
    }
}
```

#### FFT Analysis Issues
```cpp
void debug_fft_analysis() {
    FFTAnalyzer fft_analyzer(512);
    
    if (!fft_analyzer.init()) {
        Serial.println("FFT analyzer initialization failed");
        return;
    }
    
    // Test with known signal
    vibration_data_t test_data;
    test_data.num_samples = 512;
    test_data.samples = new float[512];
    
    // Generate test signal
    for (int i = 0; i < 512; i++) {
        test_data.samples[i] = sin(2 * PI * 100 * i / 512);  // 100 Hz signal
    }
    
    spectrum_data_t spectrum = fft_analyzer.analyze(test_data);
    
    Serial.println("FFT Analysis Results:");
    Serial.print("FFT size: ");
    Serial.println(spectrum.fft_size);
    Serial.print("Frequency resolution: ");
    Serial.println(spectrum.frequency_resolution);
    Serial.print("Number of peaks: ");
    Serial.println(spectrum.num_peaks);
    
    // Check for 100 Hz peak
    for (int i = 0; i < spectrum.num_peaks; i++) {
        Serial.print("Peak ");
        Serial.print(i);
        Serial.print(": ");
        Serial.print(spectrum.peaks[i].frequency);
        Serial.print(" Hz, ");
        Serial.print(spectrum.peaks[i].amplitude);
        Serial.println(" amplitude");
    }
    
    delete[] test_data.samples;
}
```

---

## Support

For vibration sensor firmware support:
- **Documentation**: See `docs/` directory
- **Examples**: See `examples/` directory
- **Platform Guides**: See `platform/*/` directories
- **Email**: firmware@valtronics.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Vibration Sensor Firmware v2.0**
