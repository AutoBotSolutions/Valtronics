#include <unity.h>
#include <Arduino.h>
#include <ArduinoJson.h>
#include "communication/mqtt_client.h"
#include "utils/logger.h"
#include "utils/json_utils.h"

// Test fixtures
MQTTClient* mqtt_client = nullptr;
DeviceConfig* device_config = nullptr;

// Mock WiFi for testing
class MockWiFi {
public:
    static bool connected;
    static String ssid;
    static int rssi;
    
    static bool begin() { return true; }
    static bool status() { return connected; }
    static String SSID() { return ssid; }
    static int RSSI() { return rssi; }
};

// Mock PubSubClient for testing
class MockPubSubClient {
public:
    static bool connected;
    static String last_topic;
    static String last_payload;
    static int callback_count;
    
    static bool connect(const char* client_id) {
        connected = true;
        return true;
    }
    
    static bool disconnect() {
        connected = false;
        return true;
    }
    
    static bool loop() { return true; }
    
    static bool publish(const char* topic, const char* payload) {
        last_topic = String(topic);
        last_payload = String(payload);
        return true;
    }
    
    static bool subscribe(const char* topic) {
        return true;
    }
    
    static void setCallback(void (*callback)(char*, byte*, unsigned int)) {
        callback_count++;
    }
};

bool MockWiFi::connected = false;
String MockWiFi::ssid = "test_network";
int MockWiFi::rssi = -45;

bool MockPubSubClient::connected = false;
String MockPubSubClient::last_topic = "";
String MockPubSubClient::last_payload = "";
int MockPubSubClient::callback_count = 0;

// Test helper functions
void setUp(void) {
    // Initialize test environment
    Serial.begin(115200);
    
    // Create test objects
    device_config = new DeviceConfig();
    mqtt_client = new MQTTClient("test.mqtt.com", 1883, "test-device");
    
    // Initialize components
    mqtt_client->init();
}

void tearDown(void) {
    // Cleanup test environment
    delete mqtt_client;
    delete device_config;
    
    // Reset mocks
    MockWiFi::connected = false;
    MockPubSubClient::connected = false;
    MockPubSubClient::last_topic = "";
    MockPubSubClient::last_payload = "";
    MockPubSubClient::callback_count = 0;
}

// Test MQTT client initialization
void test_mqtt_client_init(void) {
    TEST_ASSERT_NOT_NULL(mqtt_client);
    TEST_ASSERT_EQUAL("test.mqtt.com", mqtt_client->get_broker_host());
    TEST_ASSERT_EQUAL(1883, mqtt_client->get_broker_port());
    TEST_ASSERT_EQUAL("test-device", mqtt_client->get_client_id());
}

// Test MQTT client connection
void test_mqtt_client_connection(void) {
    // Test connection
    bool connected = mqtt_client->connect();
    TEST_ASSERT_TRUE(connected);
    TEST_ASSERT_TRUE(mqtt_client->is_connected());
    
    // Test disconnection
    bool disconnected = mqtt_client->disconnect();
    TEST_ASSERT_TRUE(disconnected);
    TEST_ASSERT_FALSE(mqtt_client->is_connected());
}

// Test MQTT client reconnection
void test_mqtt_client_reconnection(void) {
    // Initial connection
    TEST_ASSERT_TRUE(mqtt_client->connect());
    
    // Simulate disconnection
    MockPubSubClient::connected = false;
    TEST_ASSERT_FALSE(mqtt_client->is_connected());
    
    // Reconnect
    bool reconnected = mqtt_client->connect();
    TEST_ASSERT_TRUE(reconnected);
    TEST_ASSERT_TRUE(mqtt_client->is_connected());
}

// Test MQTT client publishing
void test_mqtt_client_publish(void) {
    // Connect first
    TEST_ASSERT_TRUE(mqtt_client->connect());
    
    // Publish test message
    String topic = "test/telemetry";
    String payload = "{\"temperature\": 25.5}";
    
    bool published = mqtt_client->publish(topic, payload);
    TEST_ASSERT_TRUE(published);
    
    // Verify published data
    TEST_ASSERT_EQUAL(topic, MockPubSubClient::last_topic);
    TEST_ASSERT_EQUAL(payload, MockPubSubClient::last_payload);
}

// Test MQTT client subscription
void test_mqtt_client_subscription(void) {
    // Connect first
    TEST_ASSERT_TRUE(mqtt_client->connect());
    
    // Subscribe to topic
    String topic = "test/commands";
    bool subscribed = mqtt_client->subscribe(topic);
    TEST_ASSERT_TRUE(subscribed);
    
    // Verify callback was set
    TEST_ASSERT_TRUE(MockPubSubClient::callback_count > 0);
}

// Test MQTT client message handling
void test_mqtt_client_message_handling(void) {
    // Set up message callback
    static bool message_received = false;
    static String received_topic = "";
    static String received_payload = "";
    
    mqtt_client->set_message_callback([](const String& topic, const String& payload) {
        message_received = true;
        received_topic = topic;
        received_payload = payload;
    });
    
    // Simulate incoming message
    char topic[] = "test/commands";
    char payload[] = "{\"command\": \"status\"}";
    byte* payload_bytes = (byte*)payload;
    
    // Call callback manually (simulate MQTT message)
    mqtt_client->handle_message(topic, payload_bytes, strlen(payload));
    
    // Verify message was received
    TEST_ASSERT_TRUE(message_received);
    TEST_ASSERT_EQUAL(String(topic), received_topic);
    TEST_ASSERT_EQUAL(String(payload), received_payload);
}

// Test MQTT client telemetry publishing
void test_mqtt_client_telemetry_publishing(void) {
    // Connect first
    TEST_ASSERT_TRUE(mqtt_client->connect());
    
    // Create telemetry data
    JsonObject telemetry;
    telemetry["device_id"] = "test-device";
    telemetry["sensor_type"] = "temperature";
    telemetry["value"] = 25.5;
    telemetry["unit"] = "C";
    telemetry["timestamp"] = millis();
    
    // Publish telemetry
    String payload = JSONUtils::serialize(telemetry);
    bool published = mqtt_client->publish("valtronics/telemetry", payload);
    
    TEST_ASSERT_TRUE(published);
    TEST_ASSERT_FALSE(payload.isEmpty());
}

// Test MQTT client command handling
void test_mqtt_client_command_handling(void) {
    static bool command_handled = false;
    static String command_type = "";
    
    // Set up command handler
    mqtt_client->set_command_handler([](const String& command) {
        command_handled = true;
        command_type = command;
    });
    
    // Simulate command message
    char topic[] = "valtronics/devices/test-device/commands";
    char payload[] = "{\"command\": \"reboot\"}";
    byte* payload_bytes = (byte*)payload;
    
    mqtt_client->handle_message(topic, payload_bytes, strlen(payload));
    
    // Verify command was handled
    TEST_ASSERT_TRUE(command_handled);
    TEST_ASSERT_EQUAL("reboot", command_type);
}

// Test MQTT client configuration handling
void test_mqtt_client_config_handling(void) {
    static bool config_updated = false;
    static String config_key = "";
    static String config_value = "";
    
    // Set up configuration handler
    mqtt_client->set_config_handler([](const String& key, const String& value) {
        config_updated = true;
        config_key = key;
        config_value = value;
    });
    
    // Simulate config message
    char topic[] = "valtronics/devices/test-device/config";
    char payload[] = "{\"telemetry_interval\": 60000}";
    byte* payload_bytes = (byte*)payload;
    
    mqtt_client->handle_message(topic, payload_bytes, strlen(payload));
    
    // Verify config was handled
    TEST_ASSERT_TRUE(config_updated);
    TEST_ASSERT_EQUAL("telemetry_interval", config_key);
}

// Test MQTT client error handling
void test_mqtt_client_error_handling(void) {
    // Test connection error
    MockPubSubClient::connected = false;
    TEST_ASSERT_FALSE(mqtt_client->is_connected());
    
    // Test publishing without connection
    String payload = "{\"test\": \"data\"}";
    bool published = mqtt_client->publish("test/topic", payload);
    TEST_ASSERT_FALSE(published);
    
    // Test connection recovery
    MockPubSubClient::connected = true;
    TEST_ASSERT_TRUE(mqtt_client->connect());
    TEST_ASSERT_TRUE(mqtt_client->is_connected());
}

// Test MQTT client quality of service
void test_mqtt_client_qos(void) {
    // Connect first
    TEST_ASSERT_TRUE(mqtt_client->connect());
    
    // Test QoS 0
    bool qos0_published = mqtt_client->publish_qos("test/qos0", "{\"qos\": 0}", 0);
    TEST_ASSERT_TRUE(qos0_published);
    
    // Test QoS 1
    bool qos1_published = mqtt_client->publish_qos("test/qos1", "{\"qos\": 1}", 1);
    TEST_ASSERT_TRUE(qos1_published);
    
    // Test QoS 2
    bool qos2_published = mqtt_client->publish_qos("test/qos2", "{\"qos\": 2}", 2);
    TEST_ASSERT_TRUE(qos2_published);
}

// Test MQTT client retain flag
void test_mqtt_client_retain(void) {
    // Connect first
    TEST_ASSERT_TRUE(mqtt_client->connect());
    
    // Test retained message
    bool retained_published = mqtt_client->publish_retain("test/retain", "{\"retained\": true}");
    TEST_ASSERT_TRUE(retained_published);
    
    // Test non-retained message
    bool normal_published = mqtt_client->publish_retain("test/normal", "{\"retained\": false}", false);
    TEST_ASSERT_TRUE(normal_published);
}

// Test MQTT client last will
void test_mqtt_client_last_will(void) {
    // Set last will message
    bool last_will_set = mqtt_client->set_last_will("test/lastwill", "{\"status\": \"offline\"}", 1, true);
    TEST_ASSERT_TRUE(last_will_set);
    
    // Test last will properties
    TEST_ASSERT_EQUAL("test/lastwill", mqtt_client->get_last_will_topic());
    TEST_ASSERT_EQUAL(1, mqtt_client->get_last_will_qos());
    TEST_ASSERT_TRUE(mqtt_client->get_last_will_retain());
}

// Test MQTT client keep alive
void test_mqtt_client_keep_alive(void) {
    // Set keep alive interval
    mqtt_client->set_keep_alive(60);
    TEST_ASSERT_EQUAL(60, mqtt_client->get_keep_alive());
    
    // Test keep alive handling
    bool keep_alive_sent = mqtt_client->send_keep_alive();
    TEST_ASSERT_TRUE(keep_alive_sent);
}

// Test MQTT client authentication
void test_mqtt_client_authentication(void) {
    // Set credentials
    mqtt_client->set_credentials("test_user", "test_pass");
    
    TEST_ASSERT_EQUAL("test_user", mqtt_client->get_username());
    TEST_ASSERT_EQUAL("test_pass", mqtt_client->get_password());
    
    // Test connection with credentials
    bool connected = mqtt_client->connect();
    TEST_ASSERT_TRUE(connected);
}

// Test MQTT client SSL/TLS
void test_mqtt_client_ssl(void) {
    // Enable SSL
    mqtt_client->set_ssl(true);
    TEST_ASSERT_TRUE(mqtt_client->get_ssl_enabled());
    
    // Set SSL certificates
    mqtt_client->set_ca_cert("test_ca_cert");
    mqtt_client->set_client_cert("test_client_cert");
    mqtt_client->set_private_key("test_private_key");
    
    TEST_ASSERT_EQUAL("test_ca_cert", mqtt_client->get_ca_cert());
    TEST_ASSERT_EQUAL("test_client_cert", mqtt_client->get_client_cert());
    TEST_ASSERT_EQUAL("test_private_key", mqtt_client->get_private_key());
    
    // Test SSL connection
    bool connected = mqtt_client->connect();
    TEST_ASSERT_TRUE(connected);
}

// Test MQTT client large payload
void test_mqtt_client_large_payload(void) {
    // Connect first
    TEST_ASSERT_TRUE(mqtt_client->connect());
    
    // Create large payload
    String large_payload = "{\"data\": \"" + String(1000, 'x') + "\"}";
    
    // Test publishing large payload
    bool published = mqtt_client->publish("test/large", large_payload);
    TEST_ASSERT_TRUE(published);
    
    // Check payload size
    TEST_ASSERT_TRUE(large_payload.length() > 1000);
}

// Test MQTT client multiple topics
void test_mqtt_client_multiple_topics(void) {
    // Connect first
    TEST_ASSERT_TRUE(mqtt_client->connect());
    
    // Publish to multiple topics
    String topics[] = {"test/topic1", "test/topic2", "test/topic3"};
    String payloads[] = {"{\"id\": 1}", "{\"id\": 2}", "{\"id\": 3}"};
    
    for (int i = 0; i < 3; i++) {
        bool published = mqtt_client->publish(topics[i], payloads[i]);
        TEST_ASSERT_TRUE(published);
    }
    
    // Verify all messages were published
    TEST_ASSERT_EQUAL(3, MockPubSubClient::callback_count);
}

// Test MQTT client wildcard subscription
void test_mqtt_client_wildcard_subscription(void) {
    // Connect first
    TEST_ASSERT_TRUE(mqtt_client->connect());
    
    // Subscribe to wildcard topic
    bool subscribed = mqtt_client->subscribe("test/+/data");
    TEST_ASSERT_TRUE(subscribed);
    
    // Test wildcard matching
    bool topic1_matches = mqtt_client->topic_matches("test/1/data", "test/+/data");
    bool topic2_matches = mqtt_client->topic_matches("test/2/data", "test/+/data");
    bool topic3_matches = mqtt_client->topic_matches("test/other/data", "test/+/data");
    
    TEST_ASSERT_TRUE(topic1_matches);
    TEST_ASSERT_TRUE(topic2_matches);
    TEST_ASSERT_FALSE(topic3_matches);
}

// Test MQTT client message queue
void test_mqtt_client_message_queue(void) {
    // Set message queue size
    mqtt_client->set_message_queue_size(100);
    TEST_ASSERT_EQUAL(100, mqtt_client->get_message_queue_size());
    
    // Test queue overflow handling
    for (int i = 0; i < 150; i++) {
        String topic = "test/queue/" + String(i);
        String payload = "{\"id\": " + String(i) + "}";
        mqtt_client->publish(topic, payload);
    }
    
    // Check queue handling
    TEST_ASSERT_TRUE(mqtt_client->get_queue_overflow_handled());
}

// Test MQTT client statistics
void test_mqtt_client_statistics(void) {
    // Connect first
    TEST_ASSERT_TRUE(mqtt_client->connect());
    
    // Send some messages
    for (int i = 0; i < 10; i++) {
        mqtt_client->publish("test/stats", "{\"id\": " + String(i) + "}");
    }
    
    // Get statistics
    mqtt_stats_t stats = mqtt_client->get_statistics();
    
    TEST_ASSERT_TRUE(stats.messages_sent >= 10);
    TEST_ASSERT_TRUE(stats.bytes_sent > 0);
    TEST_ASSERT_TRUE(stats.connection_time > 0);
    TEST_ASSERT_TRUE(stats.last_message_time > 0);
}

// Test MQTT client disconnect handling
void test_mqtt_client_disconnect_handling(void) {
    // Connect first
    TEST_ASSERT_TRUE(mqtt_client->connect());
    
    // Simulate unexpected disconnection
    MockPubSubClient::connected = false;
    
    // Test automatic reconnection
    bool reconnected = mqtt_client->reconnect();
    TEST_ASSERT_TRUE(reconnected);
    
    // Verify connection is restored
    TEST_ASSERT_TRUE(mqtt_client->is_connected());
}

// Test MQTT client memory management
void test_mqtt_client_memory_management(void) {
    size_t initial_heap = ESP.getFreeHeap();
    
    // Create and destroy multiple MQTT clients
    for (int i = 0; i < 5; i++) {
        MQTTClient* temp_client = new MQTTClient("test.mqtt.com", 1883, "test-device");
        temp_client->init();
        delete temp_client;
    }
    
    size_t final_heap = ESP.getFreeHeap();
    
    // Check for memory leaks
    TEST_ASSERT_TRUE(final_heap >= initial_heap - 1000);  // Allow some tolerance
}

// Test MQTT client performance
void test_mqtt_client_performance(void) {
    // Connect first
    TEST_ASSERT_TRUE(mqtt_client->connect());
    
    // Measure publish performance
    uint32_t start_time = micros();
    
    for (int i = 0; i < 100; i++) {
        mqtt_client->publish("test/perf", "{\"id\": " + String(i) + "}");
    }
    
    uint32_t end_time = micros();
    uint32_t total_time = end_time - start_time;
    
    // Check performance (should be less than 5 seconds for 100 messages)
    TEST_ASSERT_TRUE(total_time < 5000000);
    
    float avg_time_per_message = (float)total_time / 100.0;
    TEST_ASSERT_TRUE(avg_time_per_message < 50000);  // Less than 50ms per message
}

// Test MQTT client error recovery
void test_mqtt_client_error_recovery(void) {
    // Simulate connection error
    MockPubSubClient::connected = false;
    
    // Test error handling
    bool recovered = mqtt_client->handle_connection_error();
    TEST_ASSERT_TRUE(recovered);
    
    // Verify connection is restored
    TEST_ASSERT_TRUE(mqtt_client->is_connected());
}

// Test MQTT client configuration validation
void test_mqtt_client_config_validation(void) {
    // Test invalid broker host
    MQTTClient* invalid_client = new MQTTClient("", 1883, "test-device");
    bool valid = invalid_client->validate_config();
    TEST_ASSERT_FALSE(valid);
    delete invalid_client;
    
    // Test invalid port
    invalid_client = new MQTTClient("test.mqtt.com", 0, "test-device");
    valid = invalid_client->validate_config();
    TEST_ASSERT_FALSE(valid);
    delete invalid_client;
    
    // Test valid configuration
    MQTTClient* valid_client = new MQTTClient("test.mqtt.com", 1883, "test-device");
    valid = valid_client->validate_config();
    TEST_ASSERT_TRUE(valid);
    delete valid_client;
}

// Main test runner
int main(void) {
    UNITY_BEGIN();
    
    // Run all tests
    RUN_TEST(test_mqtt_client_init);
    RUN_TEST(test_mqtt_client_connection);
    RUN_TEST(test_mqtt_client_reconnection);
    RUN_TEST(test_mqtt_client_publish);
    RUN_TEST(test_mqtt_client_subscription);
    RUN_TEST(test_mqtt_client_message_handling);
    RUN_TEST(test_mqtt_client_telemetry_publishing);
    RUN_TEST(test_mqtt_client_command_handling);
    RUN_TEST(test_mqtt_client_config_handling);
    RUN_TEST(test_mqtt_client_error_handling);
    RUN_TEST(test_mqtt_client_qos);
    RUN_TEST(test_mqtt_client_retain);
    RUN_TEST(test_mqtt_client_last_will);
    RUN_TEST(test_mqtt_client_keep_alive);
    RUN_TEST(test_mqtt_client_authentication);
    RUN_TEST(test_mqtt_client_ssl);
    RUN_TEST(test_mqtt_client_large_payload);
    RUN_TEST(test_mqtt_client_multiple_topics);
    RUN_TEST(test_mqtt_client_wildcard_subscription);
    RUN_TEST(test_mqtt_client_message_queue);
    RUN_TEST(test_mqtt_client_statistics);
    RUN_TEST(test_mqtt_client_disconnect_handling);
    RUN_TEST(test_mqtt_client_memory_management);
    RUN_TEST(test_mqtt_client_performance);
    RUN_TEST(test_mqtt_client_error_recovery);
    RUN_TEST(test_mqtt_client_config_validation);
    
    return UNITY_END();
}
