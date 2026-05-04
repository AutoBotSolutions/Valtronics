# Telemetry API Documentation

**Complete API reference for telemetry data management**

---

## Overview

The Telemetry API provides comprehensive functionality for collecting, storing, and retrieving time-series telemetry data from IoT devices. This API supports high-frequency data ingestion, efficient querying, and real-time data streaming.

---

## Base Endpoint
```
/api/v1/telemetry/
```

## Authentication
All Telemetry API endpoints require JWT authentication:
```http
Authorization: Bearer <jwt-token>
```

---

## Endpoints

### 1. Submit Telemetry Data
Submit new telemetry data for a device.

**Endpoint**: `POST /api/v1/telemetry/`

**Request Body**:
```json
{
  "device_id": "integer (required)",
  "metric_name": "string (required)",
  "metric_value": "number (required)",
  "unit": "string (optional)",
  "timestamp": "datetime (optional, ISO format)",
  "metadata": "object (optional)"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/telemetry/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "metric_name": "temperature",
    "metric_value": 23.5,
    "unit": "°C",
    "timestamp": "2024-01-01T12:00:00Z",
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
    "id": 12345,
    "device_id": 1,
    "metric_name": "temperature",
    "metric_value": 23.5,
    "unit": "°C",
    "timestamp": "2024-01-01T12:00:00Z",
    "created_at": "2024-01-01T12:00:01Z"
  },
  "message": "Telemetry data submitted successfully"
}
```

---

### 2. Batch Submit Telemetry Data
Submit multiple telemetry data points in a single request.

**Endpoint**: `POST /api/v1/telemetry/batch`

**Request Body**:
```json
{
  "telemetry_data": [
    {
      "device_id": 1,
      "metric_name": "temperature",
      "metric_value": 23.5,
      "unit": "°C"
    },
    {
      "device_id": 1,
      "metric_name": "humidity",
      "metric_value": 45.2,
      "unit": "%"
    }
  ]
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/telemetry/batch \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "telemetry_data": [
      {
        "device_id": 1,
        "metric_name": "temperature",
        "metric_value": 23.5,
        "unit": "°C"
      },
      {
        "device_id": 1,
        "metric_name": "humidity",
        "metric_value": 45.2,
        "unit": "%"
      },
      {
        "device_id": 2,
        "metric_name": "pressure",
        "metric_value": 1013.25,
        "unit": "hPa"
      }
    ]
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "submitted": 3,
    "failed": 0,
    "ids": [12345, 12346, 12347]
  },
  "message": "Batch telemetry data submitted successfully"
}
```

---

### 3. Get Telemetry Data
Retrieve telemetry data with filtering and pagination.

**Endpoint**: `GET /api/v1/telemetry/`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `device_id` | integer | null | Filter by device ID |
| `metric_name` | string | null | Filter by metric name |
| `start_time` | datetime | null | Start time (ISO format) |
| `end_time` | datetime | null | End time (ISO format) |
| `page` | integer | 1 | Page number |
| `size` | integer | 100 | Items per page (1-1000) |
| `sort` | string | `timestamp` | Sort field |
| `order` | string | `desc` | Sort order (asc/desc) |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/telemetry/?device_id=1&metric_name=temperature&start_time=2024-01-01T00:00:00Z&end_time=2024-01-01T23:59:59Z&page=1&size=50" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 12345,
        "device_id": 1,
        "metric_name": "temperature",
        "metric_value": 23.5,
        "unit": "°C",
        "timestamp": "2024-01-01T12:00:00Z",
        "created_at": "2024-01-01T12:00:01Z",
        "metadata": {
          "sensor_type": "DS18B20"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "size": 50,
      "total": 1440,
      "pages": 29,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

### 4. Get Latest Telemetry Values
Retrieve the most recent telemetry values for a device.

**Endpoint**: `GET /api/v1/telemetry/latest`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `device_id` | integer | null | Filter by device ID |
| `metrics` | string | null | Comma-separated list of metrics |
| `limit` | integer | 10 | Maximum number of metrics per device |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/telemetry/latest?device_id=1&metrics=temperature,humidity,pressure&limit=5" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "device_id": 1,
    "telemetry": {
      "temperature": {
        "value": 23.5,
        "unit": "°C",
        "timestamp": "2024-01-01T12:00:00Z",
        "id": 12345
      },
      "humidity": {
        "value": 45.2,
        "unit": "%",
        "timestamp": "2024-01-01T12:00:00Z",
        "id": 12346
      },
      "pressure": {
        "value": 1013.25,
        "unit": "hPa",
        "timestamp": "2024-01-01T12:00:00Z",
        "id": 12347
      }
    },
    "last_updated": "2024-01-01T12:00:00Z"
  }
}
```

---

### 5. Get Historical Telemetry Data
Retrieve historical telemetry data with aggregations.

**Endpoint**: `GET /api/v1/telemetry/history`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `device_id` | integer | required | Device ID |
| `metric` | string | required | Metric name |
| `start_time` | datetime | required | Start time (ISO format) |
| `end_time` | datetime | required | End time (ISO format) |
| `interval` | string | `1m` | Aggregation interval (1m/5m/15m/1h/1d) |
| `aggregation` | string | `avg` | Aggregation function (avg/min/max/count/sum) |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/telemetry/history?device_id=1&metric=temperature&start_time=2024-01-01T00:00:00Z&end_time=2024-01-01T23:59:59Z&interval=1h&aggregation=avg" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "device_id": 1,
    "metric": "temperature",
    "interval": "1h",
    "aggregation": "avg",
    "data_points": [
      {
        "timestamp": "2024-01-01T00:00:00Z",
        "value": 22.5,
        "count": 60
      },
      {
        "timestamp": "2024-01-01T01:00:00Z",
        "value": 23.1,
        "count": 60
      }
    ],
    "statistics": {
      "min": 22.5,
      "max": 23.1,
      "avg": 22.8,
      "count": 1440
    }
  }
}
```

---

### 6. Get Device Telemetry Summary
Get a summary of all telemetry data for a device.

**Endpoint**: `GET /api/v1/telemetry/device/{device_id}/summary`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `device_id` | integer | Device ID |

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `time_range` | string | `24h` | Time range (1h/6h/24h/7d/30d) |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/telemetry/device/1/summary?time_range=24h" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "device_id": 1,
    "time_range": "24h",
    "total_data_points": 1440,
    "metrics": {
      "temperature": {
        "count": 1440,
        "min": 18.5,
        "max": 28.9,
        "avg": 23.4,
        "stddev": 2.1,
        "latest_value": 23.5,
        "latest_timestamp": "2024-01-01T12:00:00Z"
      },
      "humidity": {
        "count": 1440,
        "min": 35.2,
        "max": 65.8,
        "avg": 48.7,
        "stddev": 8.3,
        "latest_value": 45.2,
        "latest_timestamp": "2024-01-01T12:00:00Z"
      }
    },
    "data_quality": {
      "expected_points": 1440,
      "actual_points": 1440,
      "completeness": 100.0,
      "gaps": []
    }
  }
}
```

---

### 7. Delete Telemetry Data
Delete telemetry data based on criteria.

**Endpoint**: `DELETE /api/v1/telemetry/`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `device_id` | integer | null | Filter by device ID |
| `metric_name` | string | null | Filter by metric name |
| `start_time` | datetime | null | Start time (ISO format) |
| `end_time` | datetime | null | End time (ISO format) |
| `confirm` | boolean | false | Confirmation required for bulk deletion |

**Example Request**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/telemetry/?device_id=1&start_time=2024-01-01T00:00:00Z&end_time=2024-01-01T23:59:59Z&confirm=true" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "deleted_count": 1440,
    "criteria": {
      "device_id": 1,
      "start_time": "2024-01-01T00:00:00Z",
      "end_time": "2024-01-01T23:59:59Z"
    }
  },
  "message": "Telemetry data deleted successfully"
}
```

---

### 8. Get Available Metrics
Get all available metrics for devices.

**Endpoint**: `GET /api/v1/telemetry/metrics`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `device_id` | integer | null | Filter by device ID |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/telemetry/metrics?device_id=1" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "metrics": [
      {
        "metric_name": "temperature",
        "unit": "°C",
        "device_count": 5,
        "total_data_points": 7200,
        "last_updated": "2024-01-01T12:00:00Z"
      },
      {
        "metric_name": "humidity",
        "unit": "%",
        "device_count": 5,
        "total_data_points": 7200,
        "last_updated": "2024-01-01T12:00:00Z"
      },
      {
        "metric_name": "pressure",
        "unit": "hPa",
        "device_count": 3,
        "total_data_points": 4320,
        "last_updated": "2024-01-01T12:00:00Z"
      }
    ]
  }
}
```

---

### 9. Get Telemetry Statistics
Get statistical information about telemetry data.

**Endpoint**: `GET /api/v1/telemetry/statistics`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `time_range` | string | `24h` | Time range (1h/6h/24h/7d/30d) |
| `group_by` | string | `device` | Group by field (device/metric) |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/telemetry/statistics?time_range=24h&group_by=device" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "time_range": "24h",
    "total_data_points": 36000,
    "unique_devices": 5,
    "unique_metrics": 8,
    "by_device": [
      {
        "device_id": 1,
        "device_name": "Temperature Sensor Alpha",
        "data_points": 7200,
        "metrics": ["temperature", "humidity"],
        "last_updated": "2024-01-01T12:00:00Z"
      },
      {
        "device_id": 2,
        "device_name": "Pressure Monitor Beta",
        "data_points": 7200,
        "metrics": ["pressure", "temperature"],
        "last_updated": "2024-01-01T12:00:00Z"
      }
    ],
    "by_metric": [
      {
        "metric_name": "temperature",
        "unit": "°C",
        "device_count": 5,
        "data_points": 14400,
        "avg_value": 23.4,
        "min_value": 18.5,
        "max_value": 28.9
      },
      {
        "metric_name": "humidity",
        "unit": "%",
        "device_count": 5,
        "data_points": 14400,
        "avg_value": 48.7,
        "min_value": 35.2,
        "max_value": 65.8
      }
    ]
  }
}
```

---

### 10. Export Telemetry Data
Export telemetry data in various formats.

**Endpoint**: `GET /api/v1/telemetry/export`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `device_id` | integer | null | Filter by device ID |
| `metric_name` | string | null | Filter by metric name |
| `start_time` | datetime | null | Start time (ISO format) |
| `end_time` | datetime | null | End time (ISO format) |
| `format` | string | `json` | Export format (json/csv/xlsx) |
| `limit` | integer | 10000 | Maximum records to export |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/telemetry/export?device_id=1&metric_name=temperature&format=csv&limit=1000" \
  -H "Authorization: Bearer <token>" \
  -o telemetry_data.csv
```

**Example Response (CSV)**:
```csv
timestamp,device_id,metric_name,metric_value,unit
2024-01-01T12:00:00Z,1,temperature,23.5,°C
2024-01-01T12:01:00Z,1,temperature,23.6,°C
2024-01-01T12:02:00Z,1,temperature,23.4,°C
```

---

## Data Models

### Telemetry Data Object
```json
{
  "id": "integer",
  "device_id": "integer",
  "metric_name": "string",
  "metric_value": "number",
  "unit": "string",
  "timestamp": "datetime (ISO format)",
  "created_at": "datetime (ISO format)",
  "metadata": "object"
}
```

### Telemetry Statistics Object
```json
{
  "count": "integer",
  "min": "number",
  "max": "number",
  "avg": "number",
  "stddev": "number",
  "latest_value": "number",
  "latest_timestamp": "datetime"
}
```

### Supported Metric Types
- **temperature**: Temperature measurements (°C, °F, K)
- **humidity**: Humidity measurements (%)
- **pressure**: Pressure measurements (Pa, hPa, bar, psi)
- **voltage**: Voltage measurements (V, mV)
- **current**: Current measurements (A, mA)
- **power**: Power measurements (W, kW)
- **flow_rate**: Flow rate measurements (L/min, m³/h)
- **position**: Position measurements (%, degrees)
- **speed**: Speed measurements (m/s, km/h)
- **frequency**: Frequency measurements (Hz, kHz, MHz)

---

## Rate Limiting

Telemetry API endpoints have specific rate limits:
- **Submit Data**: 1,000 requests per minute per device
- **Query Data**: 100 requests per minute per user
- **Batch Submit**: 100 requests per minute
- **Export Data**: 10 requests per hour

---

## WebSocket Integration

Telemetry data updates are broadcast via WebSocket:

### Real-time Telemetry Updates
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

// Subscribe to device telemetry
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'telemetry',
  device_id: 1
}));

// Receive telemetry updates
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'telemetry_update') {
    console.log('New telemetry:', data);
  }
};
```

### WebSocket Message Format
```json
{
  "type": "telemetry_update",
  "device_id": 1,
  "metric_name": "temperature",
  "metric_value": 23.5,
  "unit": "°C",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## Error Handling

### Common Error Codes
- `400 Bad Request` - Invalid telemetry data format
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Device not found
- `422 Unprocessable Entity` - Validation errors
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Validation Errors
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid telemetry data",
    "details": {
      "field": "metric_value",
      "issue": "Value must be a number"
    }
  }
}
```

---

## Best Practices

### Data Submission
- Use batch submission for multiple data points
- Include timestamps for accurate time series data
- Validate data before submission
- Handle rate limiting gracefully

### Data Retrieval
- Use appropriate time ranges to limit data volume
- Use pagination for large datasets
- Cache frequently accessed data
- Use aggregations for historical data

### Performance
- Submit data in real-time for immediate processing
- Use WebSocket for real-time updates
- Implement proper error handling
- Monitor API usage and performance

---

## Examples and Use Cases

### Real-time Data Submission
```python
import requests
import json
from datetime import datetime

def submit_telemetry_batch(device_id, readings):
    """Submit batch telemetry data"""
    telemetry_data = []
    
    for reading in readings:
        telemetry_data.append({
            "device_id": device_id,
            "metric_name": reading["metric"],
            "metric_value": reading["value"],
            "unit": reading["unit"],
            "timestamp": datetime.utcnow().isoformat()
        })
    
    response = requests.post(
        "http://localhost:8000/api/v1/telemetry/batch",
        json={"telemetry_data": telemetry_data},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    return response.json()

# Usage example
readings = [
    {"metric": "temperature", "value": 23.5, "unit": "°C"},
    {"metric": "humidity", "value": 45.2, "unit": "%"},
    {"metric": "pressure", "value": 1013.25, "unit": "hPa"}
]

result = submit_telemetry_batch(1, readings)
print(f"Submitted {result['data']['submitted']} data points")
```

### Historical Data Analysis
```python
def get_historical_analysis(device_id, metric, hours=24):
    """Get historical data with analysis"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    response = requests.get(
        f"http://localhost:8000/api/v1/telemetry/history",
        params={
            "device_id": device_id,
            "metric": metric,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "interval": "1h",
            "aggregation": "avg"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    return response.json()

# Usage example
analysis = get_historical_analysis(1, "temperature", 24)
data_points = analysis["data"]["data_points"]
statistics = analysis["data"]["statistics"]

print(f"Average temperature: {statistics['avg']}°C")
print(f"Temperature range: {statistics['min']}°C - {statistics['max']}°C")
```

---

## Support

For Telemetry API support:
- **Documentation**: [API Overview](api-overview.md)
- **Device API**: [Device API](device-api.md)
- **WebSocket API**: [WebSocket API](websocket-api.md)
- **Troubleshooting**: [Troubleshooting Guide](../10-reference/troubleshooting.md)
- **Email**: autobotsolution@gmail.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Telemetry API Documentation v1.0**
