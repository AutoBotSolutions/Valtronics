# Alerts API Documentation

**Complete API reference for alert management and notification system**

---

## Overview

The Alerts API provides comprehensive functionality for managing alerts, alert rules, and notifications in the Valtronics system. This API supports real-time alert generation, rule-based alerting, and multi-channel notifications.

---

## Base Endpoint
```
/api/v1/alerts/
```

## Authentication
All Alerts API endpoints require JWT authentication:
```http
Authorization: Bearer <jwt-token>
```

---

## Endpoints

### 1. List All Alerts
Retrieve a paginated list of all alerts in the system.

**Endpoint**: `GET /api/v1/alerts/`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (1-based) |
| `size` | integer | 20 | Items per page (1-100) |
| `status` | string | null | Filter by status (active/acknowledged/resolved) |
| `severity` | string | null | Filter by severity (info/warning/critical) |
| `device_id` | integer | null | Filter by device ID |
| `alert_type` | string | null | Filter by alert type |
| `start_time` | datetime | null | Start time (ISO format) |
| `end_time` | datetime | null | End time (ISO format) |
| `sort` | string | `created_at` | Sort field |
| `order` | string | `desc` | Sort order (asc/desc) |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/alerts/?page=1&size=10&status=active&severity=critical&sort=created_at&order=desc" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "device_id": 1,
        "title": "High Temperature Alert",
        "description": "Temperature exceeds safe threshold",
        "severity": "critical",
        "alert_type": "threshold",
        "status": "active",
        "threshold_value": 30.0,
        "actual_value": 32.5,
        "metric_name": "temperature",
        "created_at": "2024-01-01T12:00:00Z",
        "acknowledged_at": null,
        "resolved_at": null,
        "acknowledged_by": null,
        "notes": null,
        "device": {
          "id": 1,
          "name": "Temperature Sensor Alpha",
          "device_id": "TEMP-001"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "size": 10,
      "total": 25,
      "pages": 3,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

### 2. Create New Alert
Create a new alert in the system.

**Endpoint**: `POST /api/v1/alerts/`

**Request Body**:
```json
{
  "device_id": "integer (required)",
  "title": "string (required)",
  "description": "string (optional)",
  "severity": "string (required)",
  "alert_type": "string (required)",
  "threshold_value": "number (optional)",
  "actual_value": "number (optional)",
  "metric_name": "string (optional)",
  "metadata": "object (optional)"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/alerts/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "title": "High Temperature Alert",
    "description": "Temperature exceeds safe threshold of 30°C",
    "severity": "critical",
    "alert_type": "threshold",
    "threshold_value": 30.0,
    "actual_value": 32.5,
    "metric_name": "temperature",
    "metadata": {
      "sensor_type": "DS18B20",
      "location": "server_room"
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "id": 2,
    "device_id": 1,
    "title": "High Temperature Alert",
    "description": "Temperature exceeds safe threshold of 30°C",
    "severity": "critical",
    "alert_type": "threshold",
    "status": "active",
    "threshold_value": 30.0,
    "actual_value": 32.5,
    "metric_name": "temperature",
    "created_at": "2024-01-01T12:00:00Z",
    "acknowledged_at": null,
    "resolved_at": null,
    "acknowledged_by": null,
    "notes": null,
    "metadata": {
      "sensor_type": "DS18B20",
      "location": "server_room"
    }
  },
  "message": "Alert created successfully"
}
```

---

### 3. Get Alert Details
Retrieve detailed information about a specific alert.

**Endpoint**: `GET /api/v1/alerts/{alert_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `alert_id` | integer | Alert ID |

**Example Request**:
```bash
curl -X GET http://localhost:8000/api/v1/alerts/1 \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "device_id": 1,
    "title": "High Temperature Alert",
    "description": "Temperature exceeds safe threshold",
    "severity": "critical",
    "alert_type": "threshold",
    "status": "active",
    "threshold_value": 30.0,
    "actual_value": 32.5,
    "metric_name": "temperature",
    "created_at": "2024-01-01T12:00:00Z",
    "acknowledged_at": null,
    "resolved_at": null,
    "acknowledged_by": null,
    "notes": null,
    "metadata": {
      "sensor_type": "DS18B20",
      "location": "server_room"
    },
    "device": {
      "id": 1,
      "name": "Temperature Sensor Alpha",
      "device_id": "TEMP-001",
      "device_type": "sensor",
      "location": "Zone A - Server Room"
    },
    "notifications": [
      {
        "id": 1,
        "notification_type": "email",
        "recipient": "admin@valtronics.com",
        "status": "sent",
        "sent_at": "2024-01-01T12:01:00Z"
      }
    ],
    "history": [
      {
        "action": "created",
        "timestamp": "2024-01-01T12:00:00Z",
        "user": "system"
      }
    ]
  }
}
```

---

### 4. Update Alert
Update information for an existing alert.

**Endpoint**: `PUT /api/v1/alerts/{alert_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `alert_id` | integer | Alert ID |

**Request Body**:
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "severity": "string (optional)",
  "status": "string (optional)",
  "notes": "string (optional)",
  "metadata": "object (optional)"
}
```

**Example Request**:
```bash
curl -X PUT http://localhost:8000/api/v1/alerts/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "acknowledged",
    "notes": "Investigating temperature sensor calibration",
    "metadata": {
      "investigation_priority": "high"
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "status": "acknowledged",
    "acknowledged_at": "2024-01-01T12:30:00Z",
    "acknowledged_by": 1,
    "notes": "Investigating temperature sensor calibration",
    "updated_at": "2024-01-01T12:30:00Z"
  },
  "message": "Alert updated successfully"
}
```

---

### 5. Delete Alert
Remove an alert from the system.

**Endpoint**: `DELETE /api/v1/alerts/{alert_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `alert_id` | integer | Alert ID |

**Example Request**:
```bash
curl -X DELETE http://localhost:8000/api/v1/alerts/1 \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": null,
  "message": "Alert deleted successfully"
}
```

---

### 6. Acknowledge Alert
Acknowledge an alert to indicate it has been seen.

**Endpoint**: `POST /api/v1/alerts/{alert_id}/acknowledge`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `alert_id` | integer | Alert ID |

**Request Body**:
```json
{
  "notes": "string (optional)",
  "metadata": "object (optional)"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/alerts/1/acknowledge \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Alert acknowledged, investigating the issue",
    "metadata": {
      "priority": "high",
      "estimated_resolution": "2 hours"
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "status": "acknowledged",
    "acknowledged_at": "2024-01-01T12:30:00Z",
    "acknowledged_by": 1,
    "notes": "Alert acknowledged, investigating the issue"
  },
  "message": "Alert acknowledged successfully"
}
```

---

### 7. Resolve Alert
Resolve an alert when the issue has been fixed.

**Endpoint**: `POST /api/v1/alerts/{alert_id}/resolve`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `alert_id` | integer | Alert ID |

**Request Body**:
```json
{
  "notes": "string (optional)",
  "resolution_details": "object (optional)",
  "metadata": "object (optional)"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/alerts/1/resolve \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Temperature sensor recalibrated, issue resolved",
    "resolution_details": {
      "action_taken": "sensor_calibration",
      "resolution_time": "2024-01-01T13:00:00Z",
      "technician": "John Doe"
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "status": "resolved",
    "resolved_at": "2024-01-01T13:00:00Z",
    "notes": "Temperature sensor recalibrated, issue resolved"
  },
  "message": "Alert resolved successfully"
}
```

---

### 8. Get Alert Rules
Retrieve all alert rules in the system.

**Endpoint**: `GET /api/v1/alerts/rules`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `device_id` | integer | null | Filter by device ID |
| `device_type` | string | null | Filter by device type |
| `metric_name` | string | null | Filter by metric name |
| `is_active` | boolean | null | Filter by active status |
| `page` | integer | 1 | Page number |
| `size` | integer | 20 | Items per page |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/alerts/rules?device_type=sensor&is_active=true" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "High Temperature Alert",
        "description": "Alert when temperature exceeds threshold",
        "device_id": null,
        "device_type": "sensor",
        "metric_name": "temperature",
        "condition": "gt",
        "threshold_value": 30.0,
        "severity": "warning",
        "is_active": true,
        "notification_enabled": true,
        "cooldown_minutes": 30,
        "updated_at": "2024-01-01T12:00:00Z"
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

---

### 9. Create Alert Rule
Create a new alert rule for automated alerting.

**Endpoint**: `POST /api/v1/alerts/rules`

**Request Body**:
```json
{
  "name": "string (required)",
  "description": "string (optional)",
  "device_id": "integer (optional)",
  "device_type": "string (optional)",
  "metric_name": "string (required)",
  "condition": "string (required)",
  "threshold_value": "number (required)",
  "severity": "string (required)",
  "is_active": "boolean (optional)",
  "notification_enabled": "boolean (optional)",
  "cooldown_minutes": "integer (optional)",
  "metadata": "object (optional)"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/alerts/rules \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Low Battery Alert",
    "description": "Alert when device battery is below 20%",
    "device_type": "sensor",
    "metric_name": "battery_level",
    "condition": "lt",
    "threshold_value": 20.0,
    "severity": "warning",
    "is_active": true,
    "notification_enabled": true,
    "cooldown_minutes": 60,
    "metadata": {
      "priority": "medium",
      "auto_resolve": false
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "Low Battery Alert",
    "description": "Alert when device battery is below 20%",
    "device_id": null,
    "device_type": "sensor",
    "metric_name": "battery_level",
    "condition": "lt",
    "threshold_value": 20.0,
    "severity": "warning",
    "is_active": true,
    "notification_enabled": true,
    "cooldown_minutes": 60,
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "message": "Alert rule created successfully"
}
```

---

### 10. Update Alert Rule
Update an existing alert rule.

**Endpoint**: `PUT /api/v1/alerts/rules/{rule_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `rule_id` | integer | Alert rule ID |

**Request Body**:
```json
{
  "name": "string (optional)",
  "description": "string (optional)",
  "threshold_value": "number (optional)",
  "severity": "string (optional)",
  "is_active": "boolean (optional)",
  "notification_enabled": "boolean (optional)",
  "cooldown_minutes": "integer (optional)",
  "metadata": "object (optional)"
}
```

**Example Request**:
```bash
curl -X PUT http://localhost:8000/api/v1/alerts/rules/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "threshold_value": 35.0,
    "severity": "critical",
    "cooldown_minutes": 15,
    "metadata": {
      "priority": "high",
      "escalation_enabled": true
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "threshold_value": 35.0,
    "severity": "critical",
    "cooldown_minutes": 15,
    "updated_at": "2024-01-01T12:30:00Z"
  },
  "message": "Alert rule updated successfully"
}
```

---

### 11. Delete Alert Rule
Delete an alert rule from the system.

**Endpoint**: `DELETE /api/v1/alerts/rules/{rule_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `rule_id` | integer | Alert rule ID |

**Example Request**:
```bash
curl -X DELETE http://localhost:8000/api/v1/alerts/rules/1 \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": null,
  "message": "Alert rule deleted successfully"
}
```

---

### 12. Get Alert Statistics
Retrieve statistical information about alerts.

**Endpoint**: `GET /api/v1/alerts/statistics`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `time_range` | string | `24h` | Time range (1h/6h/24h/7d/30d) |
| `group_by` | string | `severity` | Group by field (severity/device/alert_type) |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/alerts/statistics?time_range=24h&group_by=severity" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "time_range": "24h",
    "total_alerts": 25,
    "by_severity": {
      "critical": {
        "count": 3,
        "percentage": 12.0
      },
      "warning": {
        "count": 15,
        "percentage": 60.0
      },
      "info": {
        "count": 7,
        "percentage": 28.0
      }
    },
    "by_status": {
      "active": {
        "count": 18,
        "percentage": 72.0
      },
      "acknowledged": {
        "count": 5,
        "percentage": 20.0
      },
      "resolved": {
        "count": 2,
        "percentage": 8.0
      }
    },
    "by_type": {
      "threshold": {
        "count": 20,
        "percentage": 80.0
      },
      "anomaly": {
        "count": 3,
        "percentage": 12.0
      },
      "device": {
        "count": 2,
        "percentage": 8.0
      }
    },
    "trends": {
      "created_today": 15,
      "resolved_today": 8,
      "average_resolution_time": "2.5 hours",
      "escalation_rate": 0.12
    }
  }
}
```

---

### 13. Get Alert Notifications
Retrieve notification history for alerts.

**Endpoint**: `GET /api/v1/alerts/notifications`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `alert_id` | integer | null | Filter by alert ID |
| `notification_type` | string | null | Filter by notification type |
| `status` | string | null | Filter by status (sent/failed/pending) |
| `start_time` | datetime | null | Start time (ISO format) |
| `end_time` | datetime | null | End time (ISO format) |
| `page` | integer | 1 | Page number |
| `size` | integer | 20 | Items per page |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/alerts/notifications?notification_type=email&status=sent" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "alert_id": 1,
        "notification_type": "email",
        "recipient": "admin@valtronics.com",
        "status": "sent",
        "sent_at": "2024-01-01T12:01:00Z",
        "created_at": "2024-01-01T12:00:00Z",
        "metadata": {
          "subject": "Critical Alert: High Temperature",
          "template": "critical_alert"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 45,
      "pages": 3,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

### 14. Test Alert Rule
Test an alert rule with sample data.

**Endpoint**: `POST /api/v1/alerts/rules/{rule_id}/test`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `rule_id` | integer | Alert rule ID |

**Request Body**:
```json
{
  "test_value": "number (required)",
  "device_id": "integer (optional)",
  "metadata": "object (optional)"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/alerts/rules/1/test \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "test_value": 35.5,
    "device_id": 1,
    "metadata": {
      "test_timestamp": "2024-01-01T12:00:00Z"
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "rule_triggered": true,
    "test_result": {
      "condition": "gt",
      "threshold_value": 30.0,
      "test_value": 35.5,
      "result": "threshold exceeded"
    },
    "sample_alert": {
      "id": null,
      "title": "High Temperature Alert",
      "severity": "warning",
      "would_trigger": true
    }
  },
  "message": "Alert rule test completed"
}
```

---

## Data Models

### Alert Object
```json
{
  "id": "integer",
  "device_id": "integer",
  "title": "string",
  "description": "string",
  "severity": "string",
  "alert_type": "string",
  "status": "string",
  "threshold_value": "number",
  "actual_value": "number",
  "metric_name": "string",
  "created_at": "datetime (ISO format)",
  "acknowledged_at": "datetime (ISO format)",
  "resolved_at": "datetime (ISO format)",
  "acknowledged_by": "integer",
  "notes": "string",
  "metadata": "object"
}
```

### Alert Rule Object
```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "device_id": "integer",
  "device_type": "string",
  "metric_name": "string",
  "condition": "string",
  "threshold_value": "number",
  "severity": "string",
  "is_active": "boolean",
  "notification_enabled": "boolean",
  "cooldown_minutes": "integer",
  "updated_at": "datetime (ISO format)"
}
```

### Alert Notification Object
```json
{
  "id": "integer",
  "alert_id": "integer",
  "notification_type": "string",
  "recipient": "string",
  "status": "string",
  "sent_at": "datetime (ISO format)",
  "created_at": "datetime (ISO format)",
  "metadata": "object"
}
```

---

## Alert Severity Levels
- **info**: Informational alerts (blue)
- **warning**: Warning alerts (orange/yellow)
- **critical**: Critical alerts (red)

## Alert Types
- **threshold**: Threshold-based alerts
- **anomaly**: Anomaly detection alerts
- **device**: Device status alerts
- **system**: System-level alerts
- **manual**: Manually created alerts

## Alert Conditions
- **gt**: Greater than
- **gte**: Greater than or equal to
- **lt**: Less than
- **lte**: Less than or equal to
- **eq**: Equal to
- **ne**: Not equal to

## Notification Types
- **email**: Email notifications
- **sms**: SMS notifications
- **webhook**: Webhook notifications
- **push**: Push notifications
- **slack**: Slack notifications

---

## Rate Limiting

Alerts API endpoints have specific rate limits:
- **Create Alert**: 100 requests per minute
- **Update Alert**: 200 requests per minute
- **List Alerts**: 200 requests per minute
- **Acknowledge/Resolve**: 100 requests per minute
- **Alert Rules**: 50 requests per minute

---

## WebSocket Integration

Alert events are broadcast via WebSocket:

### Real-time Alert Notifications
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

// Subscribe to alert notifications
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'alerts'
}));

// Receive alert updates
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'alert') {
    console.log('New alert:', data);
  }
};
```

### WebSocket Message Format
```json
{
  "type": "alert",
  "alert_id": 123,
  "device_id": 1,
  "severity": "critical",
  "title": "High Temperature",
  "message": "Temperature exceeds threshold",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## Error Handling

### Common Error Codes
- `400 Bad Request` - Invalid alert data format
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Alert or rule not found
- `422 Unprocessable Entity` - Validation errors
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Validation Errors
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid alert data",
    "details": {
      "field": "severity",
      "issue": "Must be one of: info, warning, critical"
    }
  }
}
```

---

## Best Practices

### Alert Management
- Use descriptive titles and descriptions
- Set appropriate severity levels
- Include relevant metadata
- Acknowledge alerts promptly
- Document resolution steps

### Alert Rules
- Use meaningful names and descriptions
- Set appropriate threshold values
- Configure cooldown periods to prevent alert fatigue
- Test rules before enabling in production
- Regularly review and update rules

### Notifications
- Configure appropriate notification channels
- Set up escalation procedures
- Include relevant context in notifications
- Monitor notification delivery
- Handle failed notifications gracefully

---

## Examples and Use Cases

### Automated Alert Creation
```python
import requests
from datetime import datetime

def create_threshold_alert(device_id, metric, threshold, actual_value):
    """Create a threshold alert"""
    alert_data = {
        "device_id": device_id,
        "title": f"{metric.title()} Threshold Alert",
        "description": f"{metric.title()} exceeds threshold of {threshold}",
        "severity": "warning" if actual_value < threshold * 1.2 else "critical",
        "alert_type": "threshold",
        "threshold_value": threshold,
        "actual_value": actual_value,
        "metric_name": metric,
        "metadata": {
            "threshold_type": "fixed",
            "created_by": "system"
        }
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/alerts/",
        json=alert_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    return response.json()

# Usage example
alert = create_threshold_alert(1, "temperature", 30.0, 32.5)
print(f"Created alert: {alert['data']['id']}")
```

### Alert Rule Management
```python
def create_temperature_alert_rule():
    """Create a temperature alert rule"""
    rule_data = {
        "name": "High Temperature Alert",
        "description": "Alert when temperature exceeds 30°C",
        "device_type": "sensor",
        "metric_name": "temperature",
        "condition": "gt",
        "threshold_value": 30.0,
        "severity": "warning",
        "is_active": True,
        "notification_enabled": True,
        "cooldown_minutes": 30,
        "metadata": {
            "priority": "medium",
            "auto_escalate": False
        }
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/alerts/rules",
        json=rule_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    return response.json()

# Usage example
rule = create_temperature_alert_rule()
print(f"Created alert rule: {rule['data']['id']}")
```

---

## Support

For Alerts API support:
- **Documentation**: [API Overview](api-overview.md)
- **Device API**: [Device API](device-api.md)
- **Telemetry API**: [Telemetry API](telemetry-api.md)
- **WebSocket API**: [WebSocket API](websocket-api.md)
- **Troubleshooting**: [Troubleshooting Guide](../10-reference/troubleshooting.md)
- **Email**: autobotsolution@gmail.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Alerts API Documentation v1.0**
