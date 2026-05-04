# Device API Documentation

**Complete API reference for device management**

---

## Overview

The Device API provides comprehensive functionality for managing IoT devices in the Valtronics system. This includes creating, reading, updating, and deleting devices, as well as managing device status and metadata.

---

## Base Endpoint
```
/api/v1/devices/
```

## Authentication
All Device API endpoints require JWT authentication:
```http
Authorization: Bearer <jwt-token>
```

---

## Endpoints

### 1. List All Devices
Retrieve a paginated list of all devices in the system.

**Endpoint**: `GET /api/v1/devices/`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (1-based) |
| `size` | integer | 20 | Items per page (1-100) |
| `status` | string | null | Filter by status (online/offline/warning/error) |
| `device_type` | string | null | Filter by device type |
| `location` | string | null | Filter by location |
| `manufacturer` | string | null | Filter by manufacturer |
| `sort` | string | `created_at` | Sort field |
| `order` | string | `desc` | Sort order (asc/desc) |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/devices/?page=1&size=10&status=online&sort=name&order=asc" \
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
      "size": 10,
      "total": 5,
      "pages": 1,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

---

### 2. Create New Device
Add a new device to the system.

**Endpoint**: `POST /api/v1/devices/`

**Request Body**:
```json
{
  "name": "string (required)",
  "device_id": "string (required, unique)",
  "device_type": "string (required)",
  "manufacturer": "string (optional)",
  "model": "string (optional)",
  "firmware_version": "string (optional)",
  "location": "string (optional)",
  "status": "string (optional, default: offline)",
  "is_active": "boolean (optional, default: true)",
  "metadata": "object (optional)",
  "configuration": "object (optional)"
}
```

**Example Request**:
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
    "status": "online",
    "metadata": {
      "installation_date": "2024-01-01",
      "warranty_expires": "2025-01-01"
    },
    "configuration": {
      "sampling_rate": 60,
      "alert_threshold": 25.0
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "New Temperature Sensor",
    "device_id": "TEMP-002",
    "device_type": "sensor",
    "manufacturer": "SensorTech",
    "model": "ST-T2000",
    "firmware_version": "3.0.0",
    "location": "Zone B - Office",
    "status": "online",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z",
    "last_seen": null,
    "metadata": {
      "installation_date": "2024-01-01",
      "warranty_expires": "2025-01-01"
    },
    "configuration": {
      "sampling_rate": 60,
      "alert_threshold": 25.0
    }
  },
  "message": "Device created successfully"
}
```

---

### 3. Get Device Details
Retrieve detailed information about a specific device.

**Endpoint**: `GET /api/v1/devices/{device_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `device_id` | integer | Device ID |

**Example Request**:
```bash
curl -X GET http://localhost:8000/api/v1/devices/1 \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
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
    "last_seen": "2024-01-01T12:00:00Z",
    "metadata": {
      "installation_date": "2024-01-01",
      "warranty_expires": "2025-01-01"
    },
    "configuration": {
      "sampling_rate": 60,
      "alert_threshold": 25.0
    },
    "telemetry_summary": {
      "total_data_points": 1440,
      "last_24h_points": 1440,
      "latest_values": {
        "temperature": 23.5,
        "humidity": 45.2
      }
    },
    "alert_summary": {
      "total_alerts": 3,
      "active_alerts": 1,
      "critical_alerts": 0
    }
  }
}
```

---

### 4. Update Device
Update information for an existing device.

**Endpoint**: `PUT /api/v1/devices/{device_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `device_id` | integer | Device ID |

**Request Body**:
```json
{
  "name": "string (optional)",
  "device_type": "string (optional)",
  "manufacturer": "string (optional)",
  "model": "string (optional)",
  "firmware_version": "string (optional)",
  "location": "string (optional)",
  "status": "string (optional)",
  "is_active": "boolean (optional)",
  "metadata": "object (optional)",
  "configuration": "object (optional)"
}
```

**Example Request**:
```bash
curl -X PUT http://localhost:8000/api/v1/devices/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Temperature Sensor",
    "location": "Zone C - Warehouse",
    "status": "warning",
    "firmware_version": "2.1.5",
    "configuration": {
      "sampling_rate": 30,
      "alert_threshold": 24.0
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Updated Temperature Sensor",
    "device_id": "TEMP-001",
    "device_type": "sensor",
    "manufacturer": "SensorTech",
    "model": "ST-T1000",
    "firmware_version": "2.1.5",
    "location": "Zone C - Warehouse",
    "status": "warning",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:30:00Z",
    "last_seen": "2024-01-01T12:00:00Z"
  },
  "message": "Device updated successfully"
}
```

---

### 5. Delete Device
Remove a device from the system.

**Endpoint**: `DELETE /api/v1/devices/{device_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `device_id` | integer | Device ID |

**Example Request**:
```bash
curl -X DELETE http://localhost:8000/api/v1/devices/1 \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": null,
  "message": "Device deleted successfully"
}
```

---

### 6. Get Device Statistics
Retrieve statistical information about devices.

**Endpoint**: `GET /api/v1/devices/stats`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `time_range` | string | `24h` | Time range (1h/24h/7d/30d) |
| `group_by` | string | `device_type` | Group by field (device_type/location/manufacturer/status) |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/devices/stats?time_range=24h&group_by=device_type" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "total_devices": 5,
    "online_devices": 4,
    "offline_devices": 1,
    "error_devices": 0,
    "warning_devices": 1,
    "devices_by_type": {
      "sensor": 4,
      "actuator": 1
    },
    "devices_by_location": {
      "Zone A": 1,
      "Zone B": 1,
      "Zone C": 1,
      "Zone D": 1,
      "Zone E": 1
    },
    "devices_by_status": {
      "online": 4,
      "offline": 1
    },
    "uptime_percentage": 95.2,
    "data_points_24h": 7200,
    "new_devices_24h": 0,
    "active_devices_24h": 5
  }
}
```

---

### 7. Get Devices by Status
Retrieve devices filtered by status.

**Endpoint**: `GET /api/v1/devices/status/{status}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Device status (online/offline/warning/error) |

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `size` | integer | 20 | Items per page |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/devices/status/online?page=1&size=10" \
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
        "name": "Temperature Sensor Alpha",
        "device_id": "TEMP-001",
        "device_type": "sensor",
        "status": "online",
        "last_seen": "2024-01-01T12:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 10,
      "total": 4,
      "pages": 1,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

---

### 8. Update Device Status
Update the status of a device.

**Endpoint**: `PUT /api/v1/devices/{device_id}/status`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `device_id` | integer | Device ID |

**Request Body**:
```json
{
  "status": "string (required)",
  "reason": "string (optional)",
  "metadata": "object (optional)"
}
```

**Example Request**:
```bash
curl -X PUT http://localhost:8000/api/v1/devices/1/status \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "offline",
    "reason": "Maintenance scheduled",
    "metadata": {
      "maintenance_start": "2024-01-01T12:00:00Z",
      "expected_duration": "2h"
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "status": "offline",
    "updated_at": "2024-01-01T12:00:00Z",
    "last_seen": "2024-01-01T11:45:00Z"
  },
  "message": "Device status updated successfully"
}
```

---

### 9. Get Device Configuration
Retrieve the configuration for a specific device.

**Endpoint**: `GET /api/v1/devices/{device_id}/configuration`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `device_id` | integer | Device ID |

**Example Request**:
```bash
curl -X GET http://localhost:8000/api/v1/devices/1/configuration \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "device_id": 1,
    "configuration": {
      "sampling_rate": 60,
      "alert_threshold": 25.0,
      "communication_protocol": "mqtt",
      "data_retention_days": 30,
      "backup_enabled": true,
      "auto_recovery": true
    },
    "metadata": {
      "last_configured": "2024-01-01T12:00:00Z",
      "configured_by": "admin",
      "config_version": "1.2"
    }
  }
}
```

---

### 10. Update Device Configuration
Update the configuration for a specific device.

**Endpoint**: `PUT /api/v1/devices/{device_id}/configuration`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `device_id` | integer | Device ID |

**Request Body**:
```json
{
  "configuration": "object (required)",
  "metadata": "object (optional)"
}
```

**Example Request**:
```bash
curl -X PUT http://localhost:8000/api/v1/devices/1/configuration \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "configuration": {
      "sampling_rate": 30,
      "alert_threshold": 24.0,
      "data_retention_days": 60
    },
    "metadata": {
      "configured_by": "admin",
      "change_reason": "Optimize data collection"
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "device_id": 1,
    "configuration": {
      "sampling_rate": 30,
      "alert_threshold": 24.0,
      "communication_protocol": "mqtt",
      "data_retention_days": 60,
      "backup_enabled": true,
      "auto_recovery": true
    },
    "metadata": {
      "last_configured": "2024-01-01T12:30:00Z",
      "configured_by": "admin",
      "config_version": "1.3"
    }
  },
  "message": "Device configuration updated successfully"
}
```

---

## Data Models

### Device Object
```json
{
  "id": "integer",
  "name": "string",
  "device_id": "string",
  "device_type": "string",
  "manufacturer": "string",
  "model": "string",
  "firmware_version": "string",
  "location": "string",
  "status": "string",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "last_seen": "datetime",
  "metadata": "object",
  "configuration": "object"
}
```

### Device Status Values
- `online` - Device is connected and responding
- `offline` - Device is not connected
- `warning` - Device has warnings but is operational
- `error` - Device has errors and may not be operational
- `maintenance` - Device is under maintenance

### Device Types
- `sensor` - Data collection device
- `actuator` - Control device
- `gateway` - Communication gateway
- `controller` - System controller
- `monitor` - Monitoring device

---

## Error Responses

### Validation Errors
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "device_id",
      "issue": "Device ID already exists"
    }
  }
}
```

### Not Found Error
```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Device not found",
    "details": {
      "device_id": 999
    }
  }
}
```

### Unauthorized Error
```json
{
  "success": false,
  "error": {
    "code": "AUTHORIZATION_ERROR",
    "message": "Insufficient permissions to access this device",
    "details": {
      "required_permission": "device:write",
      "user_permissions": ["device:read"]
    }
  }
}
```

---

## Rate Limiting

Device API endpoints are subject to rate limiting:
- **Read operations**: 100 requests per minute
- **Write operations**: 50 requests per minute
- **Bulk operations**: 10 requests per minute

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

---

## WebSocket Events

Device status changes are broadcast via WebSocket:

### Device Status Update
```json
{
  "type": "device_status_update",
  "device_id": 1,
  "old_status": "online",
  "new_status": "offline",
  "timestamp": "2024-01-01T12:00:00Z",
  "reason": "Connection lost"
}
```

### Device Configuration Update
```json
{
  "type": "device_config_update",
  "device_id": 1,
  "configuration": {
    "sampling_rate": 30
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## Best Practices

### Device Creation
- Use unique `device_id` values
- Provide meaningful `name` and `location` fields
- Include manufacturer and model information
- Set appropriate initial status

### Configuration Management
- Use structured configuration objects
- Include metadata for change tracking
- Validate configuration values
- Document configuration changes

### Status Updates
- Update status promptly when changes occur
- Include reason for status changes
- Use appropriate status values
- Track status change history

### Error Handling
- Handle validation errors gracefully
- Check for device existence before operations
- Implement proper error recovery
- Log error details for debugging

---

## Examples and Use Cases

### Bulk Device Creation
```python
import requests

devices = [
    {"name": "Sensor 1", "device_id": "SENS-001", "device_type": "sensor"},
    {"name": "Sensor 2", "device_id": "SENS-002", "device_type": "sensor"},
    {"name": "Actuator 1", "device_id": "ACT-001", "device_type": "actuator"}
]

for device in devices:
    response = requests.post(
        "http://localhost:8000/api/v1/devices/",
        json=device,
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Created device: {response.json()}")
```

### Device Health Monitoring
```python
def check_device_health(device_id):
    # Get device details
    response = requests.get(
        f"http://localhost:8000/api/v1/devices/{device_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    device = response.json()["data"]
    
    # Check if device is healthy
    if device["status"] != "online":
        print(f"Device {device_id} is not online")
        return False
    
    # Check last seen time
    last_seen = datetime.fromisoformat(device["last_seen"])
    if datetime.now() - last_seen > timedelta(minutes=5):
        print(f"Device {device_id} hasn't reported recently")
        return False
    
    return True
```

---

## Support

For Device API support:
- **Documentation**: [API Overview](api-overview.md)
- **Authentication**: [Authentication Guide](authentication.md)
- **Troubleshooting**: [Troubleshooting Guide](../10-reference/troubleshooting.md)
- **Email**: autobotsolution@gmail.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Device API Documentation v1.0**
