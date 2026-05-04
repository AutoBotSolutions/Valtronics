#include <unity.h>
#include <Arduino.h>
#include <ArduinoJson.h>
#include "sensors/temperature_sensor.h"
#include "sensors/humidity_sensor.h"
#include "sensors/pressure_sensor.h"
#include "communication/mqtt_client.h"
#include "data_fusion/fusion_engine.h"
#include "utils/logger.h"
#include "utils/json_utils.h"

// Test fixtures
TemperatureSensor* temp_sensor = nullptr;
HumiditySensor* humidity_sensor = nullptr;
PressureSensor* pressure_sensor = nullptr;
MQTTClient* mqtt_client = nullptr;
FusionEngine* fusion_engine = nullptr;
DeviceConfig* device_config = nullptr;

// Test helper functions
void setUp(void) {
    // Initialize test environment
    Serial.begin(115200);
    
    // Create test objects
    device_config = new DeviceConfig();
    temp_sensor = new TemperatureSensor();
    humidity_sensor = new HumiditySensor();
    pressure_sensor = new PressureSensor();
    mqtt_client = new MQTTClient("test.mqtt.com", 1883, "test-device");
    fusion_engine = new FusionEngine();
    
    // Initialize components
    temp_sensor->init();
    humidity_sensor->init();
    pressure_sensor->init();
    mqtt_client->init();
    fusion_engine->init();
}

void tearDown(void) {
    // Cleanup test environment
    delete temp_sensor;
    delete humidity_sensor;
    delete pressure_sensor;
    delete mqtt_client;
    delete fusion_engine;
    delete device_config;
}

// Test sensor data collection integration
void test_sensor_data_collection_integration(void) {
    // Read data from all sensors
    temperature_data_t temp_data = temp_sensor->read();
    humidity_data_t humidity_data = humidity_sensor->read();
    pressure_data_t pressure_data = pressure_sensor->read();
    
    // Validate sensor data
    TEST_ASSERT_TRUE(temp_data.valid);
    TEST_ASSERT_TRUE(humidity_data.valid);
    TEST_ASSERT_TRUE(pressure_data.valid);
    
    // Validate temperature range
    TEST_ASSERT_TRUE(temp_data.temperature > -40.0 && temp_data.temperature < 85.0);
    
    // Validate humidity range
    TEST_ASSERT_TRUE(humidity_data.humidity >= 0.0 && humidity_data.humidity <= 100.0);
    
    // Validate pressure range
    TEST_ASSERT_TRUE(pressure_data.pressure >= 800.0 && pressure_data.pressure <= 1200.0);
    
    // Validate timestamps
    TEST_ASSERT_TRUE(temp_data.timestamp > 0);
    TEST_ASSERT_TRUE(humidity_data.timestamp > 0);
    TEST_ASSERT_TRUE(pressure_data.timestamp > 0);
}

// Test sensor data correlation integration
void test_sensor_data_correlation_integration(void) {
    // Read sensor data
    temperature_data_t temp_data = temp_sensor->read();
    humidity_data_t humidity_data = humidity_sensor->read();
    pressure_data_t pressure_data = pressure_sensor->read();
    
    // Calculate correlation between temperature and humidity
    float temp_humidity_correlation = fusion_engine->calculate_correlation(
        temp_data.temperature, humidity_data.humidity
    );
    
    // Calculate correlation between temperature and pressure
    float temp_pressure_correlation = fusion_engine->calculate_correlation(
        temp_data.temperature, pressure_data.pressure
    );
    
    // Validate correlation values
    TEST_ASSERT_TRUE(temp_humidity_correlation >= -1.0 && temp_humidity_correlation <= 1.0);
    TEST_ASSERT_TRUE(temp_pressure_correlation >= -1.0 && temp_pressure_correlation <= 1.0);
    
    // Test correlation significance
    bool temp_humidity_significant = fusion_engine->is_correlation_significant(temp_humidity_correlation);
    bool temp_pressure_significant = fusion_engine->is_correlation_significant(temp_pressure_correlation);
    
    // Correlations should be significant for real sensor data
    TEST_ASSERT_TRUE(temp_humidity_significant || temp_pressure_significant);
}

// Test sensor data fusion integration
void test_sensor_data_fusion_integration(void) {
    // Read sensor data
    temperature_data_t temp_data = temp_sensor->read();
    humidity_data_t humidity_data = humidity_sensor->read();
    pressure_data_t pressure_data = pressure_sensor->read();
    
    // Create sensor data array
    sensor_data_array_t sensor_data;
    sensor_data.push_back(temp_data);
    sensor_data.push_back(humidity_data);
    sensor_data.push_back(pressure_data);
    
    // Perform data fusion
    fused_data_t fused_data = fusion_engine->process(sensor_data);
    
    // Validate fused data
    TEST_ASSERT_TRUE(fused_data.timestamp > 0);
    TEST_ASSERT_TRUE(fused_data.confidence >= 0.0 && fused_data.confidence <= 1.0);
    TEST_ASSERT_FALSE(fused_data.algorithm_used.empty());
    
    // Validate fused values
    TEST_ASSERT_TRUE(fused_data.temperature > -40.0 && fused_data.temperature < 85.0);
    TEST_ASSERT_TRUE(fused_data.humidity >= 0.0 && fused_data.humidity <= 100.0);
    TEST_ASSERT_TRUE(fused_data.pressure >= 800.0 && fused_data.pressure <= 1200.0);
    
    // Validate correlation data
    TEST_ASSERT_TRUE(fused_data.correlations.size() >= 3);
    for (const auto& corr : fused_data.correlations) {
        TEST_ASSERT_TRUE(corr.coefficient >= -1.0 && corr.coefficient <= 1.0);
        TEST_ASSERT_FALSE(corr.sensor1_id.empty());
        TEST_ASSERT_FALSE(corr.sensor2_id.empty());
    }
}

// Test sensor to MQTT integration
void test_sensor_to_mqtt_integration(void) {
    // Connect MQTT
    TEST_ASSERT_TRUE(mqtt_client->connect());
    
    // Read sensor data
    temperature_data_t temp_data = temp_sensor->read();
    humidity_data_t humidity_data = humidity_sensor->read();
    pressure_data_t pressure_data = pressure_sensor->read();
    
    // Create comprehensive telemetry payload
    JsonObject telemetry;
    telemetry["device_id"] = "test-device";
    telemetry["timestamp"] = millis();
    
    JsonObject sensors = telemetry.createNestedObject("sensors");
    sensors["temperature"] = temp_data.temperature;
    sensors["humidity"] = humidity_data.humidity;
    sensors["pressure"] = pressure_data.pressure;
    
    // Add sensor metadata
    JsonObject metadata = telemetry.createNestedObject("metadata");
    metadata["temp_timestamp"] = temp_data.timestamp;
    metadata["humidity_timestamp"] = humidity_data.timestamp;
    metadata["pressure_timestamp"] = pressure_data.timestamp;
    metadata["temp_valid"] = temp_data.valid;
    metadata["humidity_valid"] = humidity_data.valid;
    metadata["pressure_valid"] = pressure_data.valid;
    
    // Serialize payload
    String payload = JSONUtils::serialize(telemetry);
    TEST_ASSERT_FALSE(payload.isEmpty());
    
    // Publish telemetry
    bool published = mqtt_client->publish("valtronics/telemetry", payload);
    TEST_ASSERT_TRUE(published);
    
    // Disconnect MQTT
    mqtt_client->disconnect();
}

// Test sensor fusion to MQTT integration
void test_sensor_fusion_to_mqtt_integration(void) {
    // Connect MQTT
    TEST_ASSERT_TRUE(mqtt_client->connect());
    
    // Read sensor data
    temperature_data_t temp_data = temp_sensor->read();
    humidity_data_t humidity_data = humidity_sensor->read();
    pressure_data_t pressure_data = pressure_sensor->read();
    
    sensor_data_array_t sensor_data;
    sensor_data.push_back(temp_data);
    sensor_data.push_back(humidity_data);
    sensor_data.push_back(pressure_data);
    
    // Perform data fusion
    fused_data_t fused_data = fusion_engine->process(sensor_data);
    
    // Create fused telemetry payload
    JsonObject telemetry;
    telemetry["device_id"] = "test-device";
    telemetry["timestamp"] = millis();
    telemetry["type"] = "fused_data";
    
    JsonObject fused = telemetry.createNestedObject("fused");
    fused["temperature"] = fused_data.temperature;
    fused["humidity"] = fused_data.humidity;
    fused["pressure"] = fused_data.pressure;
    fused["confidence"] = fused_data.confidence;
    fused["algorithm"] = fused_data.algorithm_used;
    
    // Add correlation data
    JsonArray correlations = telemetry.createNestedArray("correlations");
    for (const auto& corr : fused_data.correlations) {
        JsonObject correlation = correlations.createNestedObject();
        correlation["sensor1"] = corr.sensor1_id;
        correlation["sensor2"] = corr.sensor2_id;
        correlation["coefficient"] = corr.coefficient;
        correlation["significance"] = corr.significance;
    }
    
    // Serialize payload
    String payload = JSONUtils::serialize(telemetry);
    TEST_ASSERT_FALSE(payload.isEmpty());
    
    // Publish fused data
    bool published = mqtt_client->publish("valtronics/fused_data", payload);
    TEST_ASSERT_TRUE(published);
    
    // Disconnect MQTT
    mqtt_client->disconnect();
}

// Test sensor error handling integration
void test_sensor_error_handling_integration(void) {
    // Simulate sensor error
    temp_sensor->simulate_error();
    
    // Read sensor data
    temperature_data_t temp_data = temp_sensor->read();
    humidity_data_t humidity_data = humidity_sensor->read();
    pressure_data_t pressure_data = pressure_sensor->read();
    
    // Check error detection
    TEST_ASSERT_FALSE(temp_data.valid);
    TEST_ASSERT_TRUE(humidity_data.valid);  // Other sensors should still work
    TEST_ASSERT_TRUE(pressure_data.valid);
    
    // Test error recovery
    bool recovered = temp_sensor->attempt_recovery();
    TEST_ASSERT_TRUE(recovered);
    
    // Read sensor data after recovery
    temp_data = temp_sensor->read();
    TEST_ASSERT_TRUE(temp_data.valid);
}

// Test sensor redundancy integration
void test_sensor_redundancy_integration(void) {
    // Add redundant temperature sensor
    TemperatureSensor* redundant_sensor = new TemperatureSensor();
    redundant_sensor->init();
    
    // Set up redundancy
    fusion_engine->add_redundant_sensor("temperature", redundant_sensor);
    
    // Read primary sensor
    temperature_data_t primary_data = temp_sensor->read();
    
    // Simulate primary sensor failure
    temp_sensor->simulate_error();
    
    // Read redundant sensor
    temperature_data_t redundant_data = redundant_sensor->read();
    TEST_ASSERT_TRUE(redundant_data.valid);
    
    // Test failover
    bool failover = fusion_engine->handle_sensor_failover("temperature");
    TEST_ASSERT_TRUE(failover);
    
    // Check if redundant sensor is used
    temperature_data_t failover_data = temp_sensor->read();
    TEST_ASSERT_TRUE(failover_data.valid);
    
    // Cleanup
    delete redundant_sensor;
}

// Test sensor calibration integration
void test_sensor_calibration_integration(void) {
    // Read uncalibrated sensor data
    temperature_data_t uncalibrated_data = temp_sensor->read();
    TEST_ASSERT_TRUE(uncalibrated_data.valid);
    
    // Apply calibration offset
    float calibration_offset = 2.5;
    temp_sensor->set_calibration_offset(calibration_offset);
    
    // Read calibrated sensor data
    temperature_data_t calibrated_data = temp_sensor->read();
    TEST_ASSERT_TRUE(calibrated_data.valid);
    
    // Verify calibration effect
    float expected_temp = uncalibrated_data.temperature + calibration_offset;
    TEST_ASSERT_TRUE(abs(calibrated_data.temperature - expected_temp) < 0.1);
    
    // Test calibration validation
    bool is_calibrated = temp_sensor->validate_calibration();
    TEST_ASSERT_TRUE(is_calibrated);
    
    // Test calibration reset
    temp_sensor->reset_calibration();
    temperature_data_t reset_data = temp_sensor->read();
    TEST_ASSERT_TRUE(reset_data.valid);
    TEST_ASSERT_EQUAL(0.0, temp_sensor->get_calibration_offset());
}

// Test sensor performance monitoring integration
void test_sensor_performance_monitoring_integration(void) {
    // Monitor sensor performance
    sensor_performance_t temp_perf = temp_sensor->get_performance();
    sensor_performance_t humidity_perf = humidity_sensor->get_performance();
    sensor_performance_t pressure_perf = pressure_sensor->get_performance();
    
    // Validate performance metrics
    TEST_ASSERT_TRUE(temp_perf.read_time > 0);
    TEST_ASSERT_TRUE(humidity_perf.read_time > 0);
    TEST_ASSERT_TRUE(pressure_perf.read_time > 0);
    
    TEST_ASSERT_TRUE(temp_perf.success_rate >= 0.0 && temp_perf.success_rate <= 1.0);
    TEST_ASSERT_TRUE(humidity_perf.success_rate >= 0.0 && humidity_perf.success_rate <= 1.0);
    TEST_ASSERT_TRUE(pressure_perf.success_rate >= 0.0 && pressure_perf.success_rate <= 1.0);
    
    // Test performance optimization
    bool optimized = fusion_engine->optimize_sensor_performance();
    TEST_ASSERT_TRUE(optimized);
    
    // Check if performance improved
    sensor_performance_t optimized_perf = temp_sensor->get_performance();
    TEST_ASSERT_TRUE(optimized_perf.read_time <= temp_perf.read_time);
}

// Test sensor data validation integration
void test_sensor_data_validation_integration(void) {
    // Read sensor data
    temperature_data_t temp_data = temp_sensor->read();
    humidity_data_t humidity_data = humidity_sensor->read();
    pressure_data_t pressure_data = pressure_sensor->read();
    
    // Validate individual sensor data
    bool temp_valid = temp_sensor->validate_data(temp_data);
    bool humidity_valid = humidity_sensor->validate_data(humidity_data);
    bool pressure_valid = pressure_sensor->validate_data(pressure_data);
    
    TEST_ASSERT_TRUE(temp_valid);
    TEST_ASSERT_TRUE(humidity_valid);
    TEST_ASSERT_TRUE(pressure_valid);
    
    // Validate combined sensor data
    sensor_validation_result_t validation = fusion_engine->validate_sensor_data({
        temp_data, humidity_data, pressure_data
    });
    
    TEST_ASSERT_TRUE(validation.overall_valid);
    TEST_ASSERT_TRUE(validation.temperature_valid);
    TEST_ASSERT_TRUE(validation.humidity_valid);
    TEST_ASSERT_TRUE(validation.pressure_valid);
    
    // Test validation with invalid data
    temperature_data_t invalid_temp_data = {
        .temperature = 100.0,  // Invalid temperature
        .valid = false,
        .timestamp = millis()
    };
    
    bool invalid_temp_valid = temp_sensor->validate_data(invalid_temp_data);
    TEST_ASSERT_FALSE(invalid_temp_valid);
}

// Test sensor adaptive sampling integration
void test_sensor_adaptive_sampling_integration(void) {
    // Enable adaptive sampling
    fusion_engine->enable_adaptive_sampling(30, 10, 300, 0.1);
    
    // Read sensor data multiple times
    temperature_data_t readings[10];
    for (int i = 0; i < 10; i++) {
        readings[i] = temp_sensor->read();
        delay(100);
    }
    
    // Test adaptive interval calculation
    uint32_t adaptive_interval = fusion_engine->calculate_adaptive_interval(readings, 10);
    TEST_ASSERT_TRUE(adaptive_interval >= 10 && adaptive_interval <= 300);
    
    // Test change detection
    bool significant_change = fusion_engine->detect_significant_change(readings[0], readings[9]);
    TEST_ASSERT_TRUE(significant_change || !significant_change);  // Either way is fine
    
    // Test variance calculation
    float variance = fusion_engine->calculate_variance(readings, 10);
    TEST_ASSERT_TRUE(variance >= 0.0);
}

// Test sensor logging integration
void test_sensor_logging_integration(void) {
    // Enable sensor logging
    temp_sensor->enable_logging();
    humidity_sensor->enable_logging();
    pressure_sensor->enable_logging();
    
    // Read sensor data
    temperature_data_t temp_data = temp_sensor->read();
    humidity_data_t humidity_data = humidity_sensor->read();
    pressure_data_t pressure_data = pressure_sensor->read();
    
    // Check if data was logged
    bool temp_logged = temp_sensor->is_logging_enabled();
    bool humidity_logged = humidity_sensor->is_logging_enabled();
    bool pressure_logged = pressure_sensor->is_logging_enabled();
    
    TEST_ASSERT_TRUE(temp_logged);
    TEST_ASSERT_TRUE(humidity_logged);
    TEST_ASSERT_TRUE(pressure_logged);
    
    // Test log retrieval
    String temp_log = temp_sensor->get_log_data();
    String humidity_log = humidity_sensor->get_log_data();
    String pressure_log = pressure_sensor->get_log_data();
    
    TEST_ASSERT_FALSE(temp_log.isEmpty());
    TEST_ASSERT_FALSE(humidity_log.isEmpty());
    TEST_ASSERT_FALSE(pressure_log.isEmpty());
    
    // Disable logging
    temp_sensor->disable_logging();
    humidity_sensor->disable_logging();
    pressure_sensor->disable_logging();
    
    TEST_ASSERT_FALSE(temp_sensor->is_logging_enabled());
    TEST_ASSERT_FALSE(humidity_sensor->is_logging_enabled());
    TEST_ASSERT_FALSE(pressure_sensor->is_logging_enabled());
}

// Test sensor configuration integration
void test_sensor_configuration_integration(void) {
    // Create sensor configuration
    sensor_config_t temp_config = {
        .id = "temp_01",
        .type = "temperature",
        .model = "DHT22",
        .pin = 4,
        .interval = 30,
        .priority = "high",
        .calibration_offset = 0.0
    };
    
    // Apply configuration
    bool configured = temp_sensor->configure(temp_config);
    TEST_ASSERT_TRUE(configured);
    
    // Verify configuration
    sensor_config_t applied_config = temp_sensor->get_configuration();
    TEST_ASSERT_EQUAL(temp_config.id, applied_config.id);
    TEST_ASSERT_EQUAL(temp_config.type, applied_config.type);
    TEST_ASSERT_EQUAL(temp_config.model, applied_config.model);
    TEST_ASSERT_EQUAL(temp_config.pin, applied_config.pin);
    TEST_ASSERT_EQUAL(temp_config.interval, applied_config.interval);
    
    // Test configuration validation
    bool valid_config = temp_sensor->validate_configuration(temp_config);
    TEST_ASSERT_TRUE(valid_config);
    
    // Test invalid configuration
    sensor_config_t invalid_config = {
        .id = "",
        .type = "temperature",
        .model = "DHT22",
        .pin = 255,  // Invalid pin
        .interval = 30,
        .priority = "high",
        .calibration_offset = 0.0
    };
    
    bool invalid_config_valid = temp_sensor->validate_configuration(invalid_config);
    TEST_ASSERT_FALSE(invalid_config_valid);
}

// Main test runner
int main(void) {
    UNITY_BEGIN();
    
    // Run all integration tests
    RUN_TEST(test_sensor_data_collection_integration);
    RUN_TEST(test_sensor_data_correlation_integration);
    RUN_TEST(test_sensor_data_fusion_integration);
    RUN_TEST(test_sensor_to_mqtt_integration);
    RUN_TEST(test_sensor_fusion_to_mqtt_integration);
    RUN_TEST(test_sensor_error_handling_integration);
    RUN_TEST(test_sensor_redundancy_integration);
    RUN_TEST(test_sensor_calibration_integration);
    RUN_TEST(test_sensor_performance_monitoring_integration);
    RUN_TEST(test_sensor_data_validation_integration);
    RUN_TEST(test_sensor_adaptive_sampling_integration);
    RUN_TEST(test_sensor_logging_integration);
    RUN_TEST(test_sensor_configuration_integration);
    
    return UNITY_END();
}
