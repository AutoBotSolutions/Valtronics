-- Valtronics Database Initialization Script
-- This script sets up the database with initial data and configurations

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create indexes for better performance
-- These will be created automatically by SQLAlchemy but we add them manually for clarity

-- Device indexes
CREATE INDEX IF NOT EXISTS idx_devices_device_id ON devices(device_id);
CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status);
CREATE INDEX IF NOT EXISTS idx_devices_device_type ON devices(device_type);
CREATE INDEX IF NOT EXISTS idx_devices_created_at ON devices(created_at);
CREATE INDEX IF NOT EXISTS idx_devices_last_seen ON devices(last_seen);

-- Telemetry data indexes
CREATE INDEX IF NOT EXISTS idx_telemetry_device_id ON telemetry_data(device_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_metric_name ON telemetry_data(metric_name);
CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_telemetry_device_timestamp ON telemetry_data(device_id, timestamp);

-- Device commands indexes
CREATE INDEX IF NOT EXISTS idx_commands_device_id ON device_commands(device_id);
CREATE INDEX IF NOT EXISTS idx_commands_status ON device_commands(status);
CREATE INDEX IF NOT EXISTS idx_commands_created_at ON device_commands(created_at);

-- Alert indexes
CREATE INDEX IF NOT EXISTS idx_alerts_device_id ON alerts(device_id);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);

-- Alert rules indexes
CREATE INDEX IF NOT EXISTS idx_alert_rules_device_id ON alert_rules(device_id);
CREATE INDEX IF NOT EXISTS idx_alert_rules_device_type ON alert_rules(device_type);
CREATE INDEX IF NOT EXISTS idx_alert_rules_metric_name ON alert_rules(metric_name);

-- Alert notifications indexes
CREATE INDEX IF NOT EXISTS idx_notifications_alert_id ON alert_notifications(alert_id);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON alert_notifications(status);

-- Create partitions for telemetry data (optional for large datasets)
-- This helps with performance when dealing with lots of time-series data
/*
CREATE TABLE telemetry_data_y2024m01 PARTITION OF telemetry_data
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE telemetry_data_y2024m02 PARTITION OF telemetry_data
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
-- Add more partitions as needed
*/

-- Create sample data for testing
INSERT INTO devices (name, device_id, device_type, manufacturer, model, firmware_version, location, status, is_active) VALUES
('Temperature Sensor 01', 'TEMP_SENSOR_001', 'sensor', 'Texas Instruments', 'TMP36', '1.2.3', 'Server Room A', 'online', true),
('Humidity Sensor 01', 'HUM_SENSOR_001', 'sensor', 'Sensirion', 'SHT31', '2.1.0', 'Server Room A', 'online', true),
('Pressure Sensor 01', 'PRESS_SENSOR_001', 'sensor', 'Bosch', 'BME280', '1.0.5', 'Server Room B', 'offline', true),
('Actuator 01', 'ACTUATOR_001', 'actuator', 'Siemens', 'SIRIUS', '3.4.1', 'Production Line 1', 'online', true),
('Gateway 01', 'GATEWAY_001', 'gateway', 'Raspberry Pi', 'Pi 4B', '1.0.0', 'Network Closet', 'online', true)
ON CONFLICT (device_id) DO NOTHING;

-- Insert sample telemetry data
INSERT INTO telemetry_data (device_id, metric_name, metric_value, unit, timestamp) VALUES
(1, 'temperature', 23.5, 'celsius', NOW() - INTERVAL '5 minutes'),
(1, 'temperature', 23.7, 'celsius', NOW() - INTERVAL '4 minutes'),
(1, 'temperature', 23.4, 'celsius', NOW() - INTERVAL '3 minutes'),
(1, 'temperature', 23.6, 'celsius', NOW() - INTERVAL '2 minutes'),
(1, 'temperature', 23.8, 'celsius', NOW() - INTERVAL '1 minute'),
(2, 'humidity', 45.2, 'percent', NOW() - INTERVAL '5 minutes'),
(2, 'humidity', 45.5, 'percent', NOW() - INTERVAL '4 minutes'),
(2, 'humidity', 45.1, 'percent', NOW() - INTERVAL '3 minutes'),
(2, 'humidity', 45.3, 'percent', NOW() - INTERVAL '2 minutes'),
(2, 'humidity', 45.6, 'percent', NOW() - INTERVAL '1 minute')
ON CONFLICT DO NOTHING;

-- Create sample alert rules
INSERT INTO alert_rules (name, description, device_type, metric_name, condition, threshold_value, severity, is_active, notification_enabled, cooldown_minutes) VALUES
('High Temperature Alert', 'Alert when temperature exceeds 30°C', 'sensor', 'temperature', 'gt', 30.0, 'warning', true, true, 30),
('Low Humidity Alert', 'Alert when humidity drops below 30%', 'sensor', 'humidity', 'lt', 30.0, 'warning', true, true, 30),
('Device Offline Alert', 'Alert when device goes offline', NULL, NULL, NULL, NULL, 'critical', true, true, 15)
ON CONFLICT DO NOTHING;

-- Create database functions for analytics
CREATE OR REPLACE FUNCTION update_device_last_seen()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE devices 
    SET last_seen = NEW.timestamp, updated_at = NOW()
    WHERE id = NEW.device_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update device last_seen
CREATE TRIGGER trigger_update_device_last_seen
    AFTER INSERT ON telemetry_data
    FOR EACH ROW
    EXECUTE FUNCTION update_device_last_seen();

-- Create function for device health calculation
CREATE OR REPLACE FUNCTION calculate_device_health(device_id_param INTEGER)
RETURNS NUMERIC AS $$
DECLARE
    last_telemetry_time TIMESTAMP;
    current_time TIMESTAMP := NOW();
    time_diff_minutes INTEGER;
    health_score NUMERIC;
BEGIN
    -- Get the latest telemetry time for this device
    SELECT MAX(timestamp) INTO last_telemetry_time
    FROM telemetry_data
    WHERE device_id = device_id_param;
    
    -- If no telemetry data, health is 0
    IF last_telemetry_time IS NULL THEN
        RETURN 0;
    END IF;
    
    -- Calculate time difference in minutes
    time_diff_minutes := EXTRACT(EPOCH FROM (current_time - last_telemetry_time)) / 60;
    
    -- Calculate health score based on data recency
    IF time_diff_minutes < 5 THEN
        health_score := 1.0;  -- Excellent
    ELSIF time_diff_minutes < 15 THEN
        health_score := 0.8;  -- Good
    ELSIF time_diff_minutes < 60 THEN
        health_score := 0.6;  -- Fair
    ELSIF time_diff_minutes < 180 THEN
        health_score := 0.4;  -- Poor
    ELSE
        health_score := 0.2;  -- Critical
    END IF;
    
    RETURN health_score;
END;
$$ LANGUAGE plpgsql;

-- Create view for device health monitoring
CREATE OR REPLACE VIEW device_health_view AS
SELECT 
    d.id,
    d.name,
    d.device_id,
    d.device_type,
    d.status,
    d.location,
    d.last_seen,
    calculate_device_health(d.id) as health_score,
    CASE 
        WHEN calculate_device_health(d.id) >= 0.8 THEN 'excellent'
        WHEN calculate_device_health(d.id) >= 0.6 THEN 'good'
        WHEN calculate_device_health(d.id) >= 0.4 THEN 'fair'
        WHEN calculate_device_health(d.id) >= 0.2 THEN 'poor'
        ELSE 'critical'
    END as health_status
FROM devices d
WHERE d.is_active = true;

-- Create materialized view for analytics (refresh periodically)
CREATE MATERIALIZED VIEW IF NOT EXISTS device_analytics_summary AS
SELECT 
    d.device_type,
    COUNT(*) as total_devices,
    COUNT(*) FILTER (WHERE d.status = 'online') as online_devices,
    COUNT(*) FILTER (WHERE d.status = 'offline') as offline_devices,
    COUNT(*) FILTER (WHERE d.status = 'error') as error_devices,
    AVG(calculate_device_health(d.id)) as avg_health_score,
    MAX(d.last_seen) as latest_activity
FROM devices d
WHERE d.is_active = true
GROUP BY d.device_type;

-- Create function to refresh the materialized view
CREATE OR REPLACE FUNCTION refresh_device_analytics()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY device_analytics_summary;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO valtronics;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO valtronics;

-- Output completion message
DO $$
BEGIN
    RAISE NOTICE 'Valtronics database initialization completed successfully!';
    RAISE NOTICE 'Sample data has been inserted for testing.';
    RAISE NOTICE 'Indexes and triggers have been created.';
    RAISE NOTICE 'Analytics views and functions are ready.';
END $$;
