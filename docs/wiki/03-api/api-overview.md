# Valtronics API Overview

**Complete API documentation for the Valtronics system**

---

## Overview

The Valtronics API provides a comprehensive RESTful interface for managing devices, telemetry data, alerts, and analytics. The API is built using FastAPI and follows OpenAPI 3.0 specifications.

---

## API Architecture

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.valtronics.com`
- **API Version**: `/api/v1`

### Authentication
- **Method**: JWT Bearer Token
- **Header**: `Authorization: Bearer <token>`
- **Expiration**: 30 minutes (configurable)
- **Refresh**: Token refresh available

### Rate Limiting
- **Standard**: 100 requests per minute
- **Premium**: 1,000 requests per minute
- **Enterprise**: Unlimited requests

---

## API Endpoints Summary

### Health and System
- `GET /api/v1/health/` - System health check
- `GET /api/v1/health/detailed` - Detailed health status

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/auth/me` - Current user info

### Device Management
- `GET /api/v1/devices/` - List all devices
- `POST /api/v1/devices/` - Create new device
- `GET /api/v1/devices/{id}` - Get device details
- `PUT /api/v1/devices/{id}` - Update device
- `DELETE /api/v1/devices/{id}` - Delete device
- `GET /api/v1/devices/stats` - Device statistics
- `GET /api/v1/devices/status/{status}` - Devices by status

### Telemetry Data
- `GET /api/v1/telemetry/` - Get telemetry data
- `POST /api/v1/telemetry/` - Submit telemetry data
- `GET /api/v1/telemetry/latest` - Latest telemetry values
- `GET /api/v1/telemetry/history` - Historical telemetry data
- `GET /api/v1/telemetry/device/{device_id}` - Device telemetry

### Alert Management
- `GET /api/v1/alerts/` - List all alerts
- `POST /api/v1/alerts/` - Create new alert
- `GET /api/v1/alerts/{id}` - Get alert details
- `PUT /api/v1/alerts/{id}` - Update alert
- `DELETE /api/v1/alerts/{id}` - Delete alert
- `GET /api/v1/alerts/rules` - Alert rules
- `POST /api/v1/alerts/rules` - Create alert rule

### Analytics and Reporting
- `GET /api/v1/analytics/system` - System analytics
- `GET /api/v1/analytics/devices` - Device analytics
- `GET /api/v1/analytics/performance` - Performance metrics
- `GET /api/v1/analytics/reports` - Generate reports
- `GET /api/v1/analytics/trends` - Trend analysis

### AI and Machine Learning
- `POST /api/v1/ai/insights` - AI insights
- `POST /api/v1/ai/anomaly-detection` - Anomaly detection
- `POST /api/v1/ai/predictive-maintenance` - Predictive maintenance
- `GET /api/v1/ai/health-score/{device_id}` - Device health score

### WebSocket Connections
- `WS /ws` - Real-time data stream
- `WS /ws/notifications` - Alert notifications
- `WS /ws/telemetry` - Live telemetry data
- `WS /ws/system` - System status updates

---

## Request/Response Format

### Standard Response Format
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "req_123456789"
}
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "device_id",
      "issue": "Required field missing"
    }
  },
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "req_123456789"
}
```

### Pagination Format
```json
{
  "success": true,
  "data": {
    "items": [
      // Array of items
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 100,
      "pages": 5,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

## Authentication

### Login Request
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

### Login Response
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@valtronics.com",
      "role": "admin"
    }
  }
}
```

### Using the Token
```bash
curl -X GET http://localhost:8000/api/v1/devices/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Device API Examples

### List All Devices
```bash
curl -X GET http://localhost:8000/api/v1/devices/ \
  -H "Authorization: Bearer <token>"
```

### Response
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "Temperature Sensor Alpha",
        "device_id": "TEMP-001",
        "device_type": "sensor",
        "manufacturer": "SensorTech",
        "model": "ST-T1000",
        "firmware_version": "2.1.4",
        "location": "Zone A - Server Room",
        "status": "online",
        "is_active": true,
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z",
        "last_seen": "2024-01-01T12:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 5,
      "pages": 1,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

### Create New Device
```bash
curl -X POST http://localhost:8000/api/v1/devices/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Temperature Sensor",
    "device_id": "TEMP-002",
    "device_type": "sensor",
    "manufacturer": "SensorTech",
    "model": "ST-T2000",
    "firmware_version": "3.0.0",
    "location": "Zone B - Office",
    "status": "online"
  }'
```

### Update Device
```bash
curl -X PUT http://localhost:8000/api/v1/devices/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Temperature Sensor",
    "location": "Zone C - Warehouse",
    "status": "warning"
  }'
```

---

## Telemetry API Examples

### Submit Telemetry Data
```bash
curl -X POST http://localhost:8000/api/v1/telemetry/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "metric_name": "temperature",
    "metric_value": 23.5,
    "unit": "°C",
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

### Get Latest Telemetry
```bash
curl -X GET "http://localhost:8000/api/v1/telemetry/latest?device_id=1&metrics=temperature,humidity" \
  -H "Authorization: Bearer <token>"
```

### Response
```json
{
  "success": true,
  "data": {
    "device_id": 1,
    "telemetry": {
      "temperature": {
        "value": 23.5,
        "unit": "°C",
        "timestamp": "2024-01-01T12:00:00Z"
      },
      "humidity": {
        "value": 45.2,
        "unit": "%",
        "timestamp": "2024-01-01T12:00:00Z"
      }
    }
  }
}
```

### Get Historical Data
```bash
curl -X GET "http://localhost:8000/api/v1/telemetry/history?device_id=1&metric=temperature&start_time=2024-01-01T00:00:00Z&end_time=2024-01-01T23:59:59Z" \
  -H "Authorization: Bearer <token>"
```

---

## Alert API Examples

### Create Alert
```bash
curl -X POST http://localhost:8000/api/v1/alerts/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "title": "High Temperature Alert",
    "description": "Temperature exceeds safe threshold",
    "severity": "warning",
    "alert_type": "threshold",
    "threshold_value": 25.0,
    "actual_value": 26.5,
    "metric_name": "temperature"
  }'
```

### List Active Alerts
```bash
curl -X GET "http://localhost:8000/api/v1/alerts/?status=active&severity=warning" \
  -H "Authorization: Bearer <token>"
```

### Acknowledge Alert
```bash
curl -X PUT http://localhost:8000/api/v1/alerts/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "acknowledged",
    "acknowledged_at": "2024-01-01T12:00:00Z",
    "acknowledged_by": "admin"
  }'
```

---

## Analytics API Examples

### System Analytics
```bash
curl -X GET http://localhost:8000/api/v1/analytics/system \
  -H "Authorization: Bearer <token>"
```

### Response
```json
{
  "success": true,
  "data": {
    "system_stats": {
      "total_devices": 5,
      "online_devices": 4,
      "offline_devices": 1,
      "error_devices": 0
    },
    "device_performance": [
      {
        "device_id": 1,
        "device_name": "Temperature Sensor Alpha",
        "uptime_percentage": 99.5,
        "data_points_24h": 1440,
        "last_seen": "2024-01-01T12:00:00Z"
      }
    ],
    "telemetry_overview": {
      "total_points": 7200,
      "active_devices": 5,
      "metrics": {
        "temperature": {
          "count": 1440,
          "min": 18.0,
          "max": 28.0,
          "avg": 23.5
        }
      }
    }
  }
}
```

### Generate Report
```bash
curl -X POST http://localhost:8000/api/v1/analytics/reports \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "device_performance",
    "date_range": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-01-01T23:59:59Z"
    },
    "device_ids": [1, 2, 3],
    "format": "json"
  }'
```

---

## AI API Examples

### Get AI Insights
```bash
curl -X POST http://localhost:8000/api/v1/ai/insights \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "analysis_type": "performance",
    "time_range": "24h"
  }'
```

### Anomaly Detection
```bash
curl -X POST http://localhost:8000/api/v1/ai/anomaly-detection \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "metrics": ["temperature", "humidity"],
    "time_range": "24h",
    "sensitivity": "medium"
  }'
```

### Predictive Maintenance
```bash
curl -X POST http://localhost:8000/api/v1/ai/predictive-maintenance \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "prediction_horizon": "7d",
    "include_recommendations": true
  }'
```

---

## WebSocket API

### Connect to WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

// Authentication
ws.onopen = function() {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your-jwt-token'
  }));
};

// Subscribe to device updates
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'device_telemetry',
  device_id: 1
}));

// Receive messages
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### WebSocket Message Formats

#### Authentication
```json
{
  "type": "auth",
  "token": "jwt-token"
}
```

#### Subscription
```json
{
  "type": "subscribe",
  "channel": "device_telemetry",
  "device_id": 1
}
```

#### Telemetry Update
```json
{
  "type": "telemetry_update",
  "device_id": 1,
  "metric": "temperature",
  "value": 23.5,
  "unit": "°C",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Alert Notification
```json
{
  "type": "alert",
  "alert_id": 123,
  "device_id": 1,
  "severity": "warning",
  "title": "High Temperature",
  "message": "Temperature exceeds threshold",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## Error Handling

### HTTP Status Codes
- `200 OK` - Request successful
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Error Codes
- `VALIDATION_ERROR` - Input validation failed
- `AUTHENTICATION_ERROR` - Authentication failed
- `AUTHORIZATION_ERROR` - Insufficient permissions
- `RESOURCE_NOT_FOUND` - Resource not found
- `RATE_LIMIT_EXCEEDED` - Rate limit exceeded
- `INTERNAL_ERROR` - Internal server error
- `EXTERNAL_SERVICE_ERROR` - External service error

---

## Rate Limiting

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### Rate Limit Response
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 100,
      "reset_time": "2024-01-01T12:00:00Z"
    }
  }
}
```

---

## API Versioning

### Version Strategy
- **URL Versioning**: `/api/v1/`, `/api/v2/`
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Backward Compatibility**: Maintain compatibility for previous versions
- **Deprecation Notice**: 6-month deprecation notice

### Version Information
```bash
curl -X GET http://localhost:8000/api/v1/version
```

### Response
```json
{
  "success": true,
  "data": {
    "version": "1.0.0",
    "api_version": "v1",
    "build_date": "2024-01-01T12:00:00Z",
    "git_commit": "abc123def456",
    "supported_versions": ["v1"],
    "deprecated_versions": []
  }
}
```

---

## OpenAPI Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### Download API Spec
```bash
curl -X GET http://localhost:8000/openapi.json > valtronics-api.json
```

---

## Testing the API

### Health Check
```bash
curl -X GET http://localhost:8000/api/v1/health/
```

### Test Authentication
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Use token
curl -X GET http://localhost:8000/api/v1/devices/ \
  -H "Authorization: Bearer <token>"
```

### Test Device Operations
```bash
# Create device
curl -X POST http://localhost:8000/api/v1/devices/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Device", "device_id": "TEST-001", "device_type": "sensor"}'

# List devices
curl -X GET http://localhost:8000/api/v1/devices/ \
  -H "Authorization: Bearer <token>"

# Get device details
curl -X GET http://localhost:8000/api/v1/devices/1 \
  -H "Authorization: Bearer <token>"
```

---

## SDKs and Libraries

### Python SDK
```python
from valtronics_client import ValtronicsClient

client = ValtronicsClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# List devices
devices = client.devices.list()

# Create device
device = client.devices.create({
    "name": "New Device",
    "device_id": "DEV-001",
    "device_type": "sensor"
})
```

### JavaScript SDK
```javascript
import { ValtronicsClient } from 'valtronics-js';

const client = new ValtronicsClient({
  baseURL: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

// List devices
const devices = await client.devices.list();

// Create device
const device = await client.devices.create({
  name: 'New Device',
  device_id: 'DEV-001',
  device_type: 'sensor'
});
```

---

## Best Practices

### Authentication
- Use HTTPS for all API calls
- Store tokens securely
- Implement token refresh
- Use short-lived tokens

### Error Handling
- Check HTTP status codes
- Parse error responses
- Implement retry logic
- Handle rate limits gracefully

### Performance
- Use pagination for large datasets
- Cache frequently accessed data
- Use WebSocket for real-time updates
- Optimize query parameters

### Security
- Validate input data
- Sanitize user input
- Implement proper authorization
- Monitor API usage

---

## Support

### Documentation
- **API Reference**: [Device API](device-api.md)
- **Authentication**: [Authentication Guide](authentication.md)
- **WebSocket**: [WebSocket API](websocket-api.md)

### Support Channels
- **Email**: autobotsolution@gmail.com
- **Documentation**: [Troubleshooting Guide](../10-reference/troubleshooting.md)
- **Community**: [Developer Forum] (coming soon)

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Valtronics API Overview v1.0**
