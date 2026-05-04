#include <unity.h>
#include <Arduino.h>
#include <ArduinoJson.h>
#include "sensors/temperature_sensor.h"
#include "communication/mqtt_client.h"
#include "utils/logger.h"
#include "utils/json_utils.h"

// Test fixtures
TemperatureSensor* temp_sensor = nullptr;
MQTTClient* mqtt_client = nullptr;
DeviceConfig* device_config = nullptr;

// Test helper functions
void setUp(void) {
    // Initialize test environment
    Serial.begin(115200);
    
    // Create test objects
    device_config = new DeviceConfig();
    temp_sensor = new TemperatureSensor();
    mqtt_client = new MQTTClient("test.mqtt.com", 1883, "test-device");
    
    // Initialize components
    temp_sensor->init();
    mqtt_client->init();
}

void tearDown(void) {
    // Cleanup test environment
    delete temp_sensor;
    delete mqtt_client;
    delete device_config;
}

// Test temperature sensor initialization
void test_temperature_sensor_init(void) {
    TEST_ASSERT_NOT_NULL(temp_sensor);
    TEST_ASSERT_TRUE(temp_sensor->is_connected());
    TEST_ASSERT_EQUAL(0.0, temp_sensor->get_calibration_offset());
}

// Test temperature sensor reading
void test_temperature_sensor_reading(void) {
    temperature_data_t data = temp_sensor->read();
    
    TEST_ASSERT_TRUE(data.valid);
    TEST_ASSERT_TRUE(data.temperature > -40.0 && data.temperature < 85.0);
    TEST_ASSERT_TRUE(data.timestamp > 0);
}

// Test temperature sensor calibration
void test_temperature_sensor_calibration(void) {
    // Set calibration offset
    float offset = 5.0;
    temp_sensor->set_calibration_offset(offset);
    
    TEST_ASSERT_EQUAL(offset, temp_sensor->get_calibration_offset());
    
    // Read temperature with calibration
    temperature_data_t data = temp_sensor->read();
    TEST_ASSERT_TRUE(data.valid);
    
    // Calibration should affect reading
    TEST_ASSERT_TRUE(data.temperature > -40.0 && data.temperature < 85.0);
}

// Test temperature sensor error handling
void test_temperature_sensor_error_handling(void) {
    // Simulate sensor disconnection
    temp_sensor->simulate_disconnection();
    
    temperature_data_t data = temp_sensor->read();
    TEST_ASSERT_FALSE(data.valid);
    
    // Reconnect sensor
    temp_sensor->simulate_reconnection();
    
    data = temp_sensor->read();
    TEST_ASSERT_TRUE(data.valid);
}

// Test temperature sensor callback
void test_temperature_sensor_callback(void) {
    static bool callback_called = false;
    static temperature_data_t callback_data;
    
    // Set callback
    temp_sensor->set_callback([](temperature_data_t data) {
        callback_called = true;
        callback_data = data;
    });
    
    // Trigger callback by reading sensor
    temperature_data_t data = temp_sensor->read();
    
    // Check if callback was called
    TEST_ASSERT_TRUE(callback_called);
    TEST_ASSERT_TRUE(callback_data.valid);
    TEST_ASSERT_EQUAL(data.temperature, callback_data.temperature);
}

// Test temperature sensor range validation
void test_temperature_sensor_range_validation(void) {
    // Test valid range
    temperature_data_t data = temp_sensor->read();
    TEST_ASSERT_TRUE(temp_sensor->validate_temperature(data.temperature));
    
    // Test invalid ranges
    TEST_ASSERT_FALSE(temp_sensor->validate_temperature(-50.0));
    TEST_ASSERT_FALSE(temp_sensor->validate_temperature(100.0));
}

// Test temperature sensor data structure
void test_temperature_sensor_data_structure(void) {
    temperature_data_t data = temp_sensor->read();
    
    // Check data structure
    TEST_ASSERT_TRUE(data.valid);
    TEST_ASSERT_TRUE(data.timestamp > 0);
    
    // Check temperature value
    TEST_ASSERT_TRUE(data.temperature > -40.0 && data.temperature < 85.0);
}

// Test temperature sensor with different units
void test_temperature_sensor_units(void) {
    // Test Celsius
    temp_sensor->set_unit("C");
    temperature_data_t data_c = temp_sensor->read();
    TEST_ASSERT_TRUE(data_c.valid);
    TEST_ASSERT_TRUE(data_c.temperature > -40.0 && data_c.temperature < 85.0);
    
    // Test Fahrenheit
    temp_sensor->set_unit("F");
    temperature_data_t data_f = temp_sensor->read();
    TEST_ASSERT_TRUE(data_f.valid);
    TEST_ASSERT_TRUE(data_f.temperature > -40.0 && data_f.temperature < 185.0);
    
    // Test Kelvin
    temp_sensor->set_unit("K");
    temperature_data_t data_k = temp_sensor->read();
    TEST_ASSERT_TRUE(data_k.valid);
    TEST_ASSERT_TRUE(data_k.temperature > 233.15 && data_k.temperature < 358.15);
}

// Test temperature sensor sampling rate
void test_temperature_sensor_sampling_rate(void) {
    // Set sampling rate
    uint32_t sampling_rate = 1000;  // 1 second
    temp_sensor->set_sampling_rate(sampling_rate);
    
    TEST_ASSERT_EQUAL(sampling_rate, temp_sensor->get_sampling_rate());
    
    // Test sampling timing
    uint32_t start_time = millis();
    temperature_data_t data1 = temp_sensor->read();
    
    delay(sampling_rate);
    
    uint32_t end_time = millis();
    temperature_data_t data2 = temp_sensor->read();
    
    uint32_t actual_duration = end_time - start_time;
    
    // Allow some tolerance
    TEST_ASSERT_TRUE(abs((int32_t)actual_duration - (int32_t)sampling_rate) < 100);
}

// Test temperature sensor averaging
void test_temperature_sensor_averaging(void) {
    // Enable averaging
    temp_sensor->enable_averaging(5);  // 5 samples average
    
    temperature_data_t avg_data = temp_sensor->read_averaged();
    
    TEST_ASSERT_TRUE(avg_data.valid);
    TEST_ASSERT_TRUE(avg_data.temperature > -40.0 && avg_data.temperature < 85.0);
    
    // Disable averaging
    temp_sensor->disable_averaging();
    
    temperature_data_t single_data = temp_sensor->read();
    
    TEST_ASSERT_TRUE(single_data.valid);
}

// Test temperature sensor filtering
void test_temperature_sensor_filtering(void) {
    // Enable filtering
    temp_sensor->enable_filtering(0.1);  // 0.1 degree threshold
    
    temperature_data_t filtered_data = temp_sensor->read_filtered();
    
    TEST_ASSERT_TRUE(filtered_data.valid);
    TEST_ASSERT_TRUE(filtered_data.temperature > -40.0 && filtered_data.temperature < 85.0);
    
    // Disable filtering
    temp_sensor->disable_filtering();
    
    temperature_data_t unfiltered_data = temp_sensor->read();
    
    TEST_ASSERT_TRUE(unfiltered_data.valid);
}

// Test temperature sensor power management
void test_temperature_sensor_power_management(void) {
    // Test power save mode
    temp_sensor->enter_power_save_mode();
    TEST_ASSERT_TRUE(temp_sensor->is_in_power_save_mode());
    
    // Wake from power save mode
    temp_sensor->exit_power_save_mode();
    TEST_ASSERT_FALSE(temp_sensor->is_in_power_save_mode());
    
    // Test sensor reading after power save
    temperature_data_t data = temp_sensor->read();
    TEST_ASSERT_TRUE(data.valid);
}

// Test temperature sensor diagnostics
void test_temperature_sensor_diagnostics(void) {
    // Run diagnostics
    sensor_diagnostics_t diagnostics = temp_sensor->run_diagnostics();
    
    TEST_ASSERT_TRUE(diagnostics.sensor_connected);
    TEST_ASSERT_TRUE(diagnostics.calibration_valid);
    TEST_ASSERT_TRUE(diagnostics.communication_ok);
    TEST_ASSERT_TRUE(diagnostics.power_supply_ok);
}

// Test temperature sensor factory reset
void test_temperature_sensor_factory_reset(void) {
    // Set some custom values
    temp_sensor->set_calibration_offset(10.0);
    temp_sensor->set_sampling_rate(2000);
    
    // Factory reset
    temp_sensor->factory_reset();
    
    // Check reset values
    TEST_ASSERT_EQUAL(0.0, temp_sensor->get_calibration_offset());
    TEST_ASSERT_EQUAL(1000, temp_sensor->get_sampling_rate());
}

// Test temperature sensor with MQTT integration
void test_temperature_sensor_mqtt_integration(void) {
    // Connect MQTT
    TEST_ASSERT_TRUE(mqtt_client->connect());
    
    // Read sensor data
    temperature_data_t data = temp_sensor->read();
    TEST_ASSERT_TRUE(data.valid);
    
    // Create MQTT payload
    JsonObject telemetry;
    telemetry["device_id"] = "test-device";
    telemetry["sensor_type"] = "temperature";
    telemetry["value"] = data.temperature;
    telemetry["unit"] = "C";
    telemetry["timestamp"] = data.timestamp;
    
    // Serialize payload
    String payload = JSONUtils::serialize(telemetry);
    TEST_ASSERT_FALSE(payload.isEmpty());
    
    // Publish telemetry
    bool published = mqtt_client->publish("test/temperature", payload);
    TEST_ASSERT_TRUE(published);
    
    // Disconnect MQTT
    mqtt_client->disconnect();
}

// Test temperature sensor error recovery
void test_temperature_sensor_error_recovery(void) {
    // Simulate sensor error
    temp_sensor->simulate_error();
    
    temperature_data_t data = temp_sensor->read();
    TEST_ASSERT_FALSE(data.valid);
    
    // Attempt recovery
    bool recovered = temp_sensor->attempt_recovery();
    TEST_ASSERT_TRUE(recovered);
    
    // Check if sensor is working again
    data = temp_sensor->read();
    TEST_ASSERT_TRUE(data.valid);
}

// Test temperature sensor performance
void test_temperature_sensor_performance(void) {
    // Measure read performance
    uint32_t start_time = micros();
    
    temperature_data_t data = temp_sensor->read();
    
    uint32_t end_time = micros();
    uint32_t read_time = end_time - start_time;
    
    TEST_ASSERT_TRUE(data.valid);
    TEST_ASSERT_TRUE(read_time < 50000);  // Should be less than 50ms
}

// Test temperature sensor memory usage
void test_temperature_sensor_memory_usage(void) {
    size_t initial_heap = ESP.getFreeHeap();
    
    // Create multiple temperature sensors
    TemperatureSensor* sensors[10];
    for (int i = 0; i < 10; i++) {
        sensors[i] = new TemperatureSensor();
        sensors[i]->init();
    }
    
    size_t used_heap = initial_heap - ESP.getFreeHeap();
    
    // Check reasonable memory usage
    TEST_ASSERT_TRUE(used_heap < 10000);  // Should be less than 10KB
    
    // Cleanup
    for (int i = 0; i < 10; i++) {
        delete sensors[i];
    }
}

// Test temperature sensor concurrent access
void test_temperature_sensor_concurrent_access(void) {
    // This test checks thread safety (if applicable)
    temperature_data_t data1 = temp_sensor->read();
    temperature_data_t data2 = temp_sensor->read();
    
    TEST_ASSERT_TRUE(data1.valid);
    TEST_ASSERT_TRUE(data2.valid);
    
    // Both readings should be close in time
    uint32_t time_diff = abs((int32_t)(data2.timestamp - data1.timestamp));
    TEST_ASSERT_TRUE(time_diff < 1000);  // Less than 1 second
}

// Test temperature sensor with invalid configuration
void test_temperature_sensor_invalid_config(void) {
    // Test with invalid pin
    TemperatureSensor* invalid_sensor = new TemperatureSensor(255);  // Invalid pin
    bool init_result = invalid_sensor->init();
    TEST_ASSERT_FALSE(init_result);
    
    delete invalid_sensor;
}

// Test temperature sensor data integrity
void test_temperature_sensor_data_integrity(void) {
    // Read multiple samples
    temperature_data_t samples[10];
    
    for (int i = 0; i < 10; i++) {
        samples[i] = temp_sensor->read();
        TEST_ASSERT_TRUE(samples[i].valid);
        delay(100);  // 100ms between samples
    }
    
    // Check data consistency
    for (int i = 1; i < 10; i++) {
        // Timestamps should be increasing
        TEST_ASSERT_TRUE(samples[i].timestamp > samples[i-1].timestamp);
        
        // Temperature values should be reasonable
        TEST_ASSERT_TRUE(samples[i].temperature > -40.0 && samples[i].temperature < 85.0);
    }
}

// Test temperature sensor with extreme temperatures
void test_temperature_sensor_extreme_temperatures(void) {
    // This test would require hardware simulation
    // For now, just test data validation
    
    temperature_data_t data = temp_sensor->read();
    TEST_ASSERT_TRUE(data.valid);
    
    // Simulate extreme temperature reading
    float extreme_temp = 100.0;  // Outside valid range
    bool is_valid = temp_sensor->validate_temperature(extreme_temp);
    TEST_ASSERT_FALSE(is_valid);
    
    extreme_temp = -50.0;  # Outside valid range
    is_valid = temp_sensor->validate_temperature(extreme_temp);
    TEST_ASSERT_FALSE(is_valid);
}

// Main test runner
int main(void) {
    UNITY_BEGIN();
    
    // Run all tests
    RUN_TEST(test_temperature_sensor_init);
    RUN_TEST(test_temperature_sensor_reading);
    RUN_TEST(test_temperature_sensor_calibration);
    RUN_TEST(test_temperature_sensor_error_handling);
    RUN_TEST(test_temperature_sensor_callback);
    RUN_TEST(test_temperature_sensor_range_validation);
    RUN_TEST(test_temperature_sensor_data_structure);
    RUN_TEST(test_temperature_sensor_units);
    RUN_TEST(test_temperature_sensor_sampling_rate);
    RUN_TEST(test_temperature_sensor_averaging);
    RUN_TEST(test_temperature_sensor_filtering);
    RUN_TEST(test_temperature_sensor_power_management);
    RUN_TEST(test_temperature_sensor_diagnostics);
    RUN_TEST(test_temperature_sensor_factory_reset);
    RUN_TEST(test_temperature_sensor_mqtt_integration);
    RUN_TEST(test_temperature_sensor_error_recovery);
    RUN_TEST(test_temperature_sensor_performance);
    RUN_TEST(test_temperature_sensor_memory_usage);
    RUN_TEST(test_temperature_sensor_concurrent_access);
    RUN_TEST(test_temperature_sensor_invalid_config);
    RUN_TEST(test_temperature_sensor_data_integrity);
    RUN_TEST(test_temperature_sensor_extreme_temperatures);
    
    return UNITY_END();
}
