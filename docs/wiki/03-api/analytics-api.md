# Analytics API Documentation

**Complete API reference for analytics and reporting system**

---

## Overview

The Analytics API provides comprehensive functionality for data analysis, reporting, and insights generation in the Valtronics system. This API supports real-time analytics, historical data analysis, and AI-powered insights.

---

## Base Endpoint
```
/api/v1/analytics/
```

## Authentication
All Analytics API endpoints require JWT authentication:
```http
Authorization: Bearer <jwt-token>
```

---

## Endpoints

### 1. System Analytics
Get comprehensive system-wide analytics and statistics.

**Endpoint**: `GET /api/v1/analytics/system`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `time_range` | string | `24h` | Time range (1h/6h/24h/7d/30d) |
| `include_device_details` | boolean | false | Include detailed device information |
| `include_telemetry` | boolean | true | Include telemetry statistics |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/system?time_range=24h&include_device_details=true" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "system_stats": {
      "total_devices": 5,
      "online_devices": 4,
      "offline_devices": 1,
      "error_devices": 0,
      "warning_devices": 1,
      "devices_by_type": {
        "sensor": 4,
        "actuator": 1
      },
      "devices_by_status": {
        "online": 4,
        "offline": 1
      }
    },
    "device_performance": [
      {
        "device_id": 1,
        "device_name": "Temperature Sensor Alpha",
        "device_type": "sensor",
        "status": "online",
        "data_points_24h": 1440,
        "last_seen": "2024-01-01T12:00:00Z",
        "uptime_percentage": 99.5,
        "avg_response_time": 0.05,
        "error_rate": 0.01
      }
    ],
    "telemetry_overview": {
      "total_points": 7200,
      "active_devices": 5,
      "device_types": {
        "sensor": 5760,
        "actuator": 1440
      },
      "metrics": {
        "temperature": {
          "count": 2880,
          "min": 18.0,
          "max": 28.9,
          "avg": 23.4,
          "stddev": 2.1,
          "trend": "stable"
        },
        "humidity": {
          "count": 2880,
          "min": 35.2,
          "max": 65.8,
          "avg": 48.7,
          "stddev": 8.3,
          "trend": "increasing"
        }
      }
    },
    "system_health": {
      "overall_score": 0.85,
      "device_health": 0.80,
      "data_health": 0.90,
      "status": "healthy"
    },
    "utilization_trends": {
      "trend": "stable",
      "current_utilization": 20.0,
      "hourly_distribution": {
        "0": 20,
        "1": 18,
        "2": 22,
        "3": 19,
        "4": 21,
        "5": 20,
        "6": 23,
        "7": 20,
        "8": 19,
        "9": 21,
        "10": 20,
        "11": 22,
        "12": 20,
        "13": 18,
        "14": 21,
        "15": 20,
        "16": 19,
        "17": 22,
        "18": 20,
        "19": 21,
        "20": 20,
        "21": 23,
        "22": 19,
        "23": 21
      }
    }
  }
}
```

---

### 2. Device Analytics
Get detailed analytics for specific devices.

**Endpoint**: `GET /api/v1/analytics/devices`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `device_ids` | string | null | Comma-separated device IDs |
| `device_type` | string | null | Filter by device type |
| `status` | string | null | Filter by status |
| `time_range` | string | `24h` | Time range (1h/6h/24h/7d/30d) |
| `metrics` | string | null | Comma-separated metrics to include |
| `include_telemetry` | boolean | true | Include telemetry data |
| `include_alerts` | boolean | true | Include alert statistics |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/devices?device_ids=1,2,3&time_range=24h&metrics=temperature,humidity" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "devices": [
      {
        "device_id": 1,
        "device_name": "Temperature Sensor Alpha",
        "device_type": "sensor",
        "status": "online",
        "location": "Zone A - Server Room",
        "performance": {
          "uptime_percentage": 99.5,
          "data_points_24h": 1440,
          "avg_response_time": 0.05,
          "error_rate": 0.01,
          "last_seen": "2024-01-01T12:00:00Z"
        },
        "telemetry": {
          "temperature": {
            "count": 1440,
            "min": 18.0,
            "max": 28.9,
            "avg": 23.4,
            "stddev": 2.1,
            "latest_value": 23.5,
            "trend": "stable"
          },
          "humidity": {
            "count": 1440,
            "min": 35.2,
            "max": 65.8,
            "avg": 48.7,
            "stddev": 8.3,
            "latest_value": 45.2,
            "trend": "decreasing"
          }
        },
        "alerts": {
          "total_alerts": 3,
          "active_alerts": 1,
          "critical_alerts": 0,
          "warning_alerts": 1,
          "info_alerts": 1,
          "resolved_alerts": 2
        },
        "health_score": 0.85
      }
    ],
    "summary": {
      "total_devices": 3,
      "avg_uptime": 98.7,
      "total_data_points": 4320,
      "total_alerts": 7
    }
  }
}
```

---

### 3. Performance Metrics
Get detailed performance metrics for the system.

**Endpoint**: `GET /api/v1/analytics/performance`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `time_range` | string | `24h` | Time range (1h/6h/24h/7d/30d) |
| `granularity` | string | `1h` | Data granularity (1m/5m/15m/1h/1d) |
| `metrics` | string | `all` | Comma-separated metrics |
| `include_system` | boolean | true | Include system metrics |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/performance?time_range=24h&granularity=1h&metrics=cpu,memory,network" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "time_range": "24h",
    "granularity": "1h",
    "system_metrics": {
      "cpu": {
        "data_points": 24,
        "min": 15.2,
        "max": 45.8,
        "avg": 28.7,
        "stddev": 8.3,
        "trend": "stable",
        "unit": "%"
      },
      "memory": {
        "data_points": 24,
        "min": 30.5,
        "max": 65.2,
        "avg": 45.8,
        "stddev": 10.2,
        "trend": "increasing",
        "unit": "%"
      },
      "network": {
        "data_points": 24,
        "min": 1024,
        "max": 5120,
        "avg": 2048,
        "stddev": 1024,
        "trend": "stable",
        "unit": "KB/s"
      },
      "disk": {
        "data_points": 24,
        "min": 15.2,
        "max": 85.6,
        "avg": 45.3,
        "stddev": 18.7,
        "trend": "increasing",
        "unit": "%"
      }
    },
    "application_metrics": {
      "api_response_time": {
        "data_points": 24,
        "min": 45,
        "max": 234,
        "avg": 89,
        "stddev": 35,
        "trend": "stable",
        "unit": "ms"
      },
      "database_query_time": {
        "data_points": 24,
        "min": 12,
        "max": 156,
        "avg": 45,
        "stddev": 28,
        "trend": "stable",
        "unit": "ms"
      },
      "websocket_connections": {
        "data_points": 24,
        "min": 0,
        "max": 15,
        "avg": 8,
        "stddev": 4,
        "trend": "stable",
        "unit": "connections"
      }
    },
    "performance_score": 0.82
  }
}
```

---

### 4. Trend Analysis
Get trend analysis for various metrics over time.

**Endpoint**: `GET /api/v1/analytics/trends`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `metric` | string | required | Metric to analyze |
| `device_id` | integer | null | Filter by device ID |
| `time_range` | string | `7d` | Time range (1h/6h/24h/7d/30d) |
| `granularity` | string | `1h` | Data granularity |
| `trend_type` | string | `linear` | Trend type (linear/exponential/seasonal) |
| `forecast_points` | integer | 0 | Number of forecast points |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/trends?metric=temperature&device_id=1&time_range=7d&granularity=1h&trend_type=linear&forecast_points=24" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "metric": "temperature",
    "device_id": 1,
    "time_range": "7d",
    "granularity": "1h",
    "trend_analysis": {
      "trend_type": "linear",
      "slope": 0.02,
      "intercept": 23.1,
      "r_squared": 0.87,
      "trend_direction": "increasing",
      "confidence": 0.85
    },
    "historical_data": [
      {
        "timestamp": "2024-01-01T00:00:00Z",
        "value": 23.1,
        "predicted": 23.1
      },
      {
        "timestamp": "2024-01-01T01:00:00Z",
        "value": 23.3,
        "predicted": 23.12
      }
    ],
    "forecast": [
      {
        "timestamp": "2024-01-08T00:00:00Z",
        "value": 24.5,
        "confidence_interval": {
          "lower": 23.8,
          "upper": 25.2
        }
      }
    ],
    "statistics": {
      "data_points": 168,
      "min": 18.5,
      "max": 28.9,
      "avg": 23.4,
      "stddev": 2.1,
      "seasonality": {
        "detected": false,
        "seasonal_period": null
      }
    },
    "anomalies": [
      {
        "timestamp": "2024-01-03T14:00:00Z",
        "value": 28.9,
        "anomaly_score": 0.92,
        "type": "spike"
      }
    ]
  }
}
```

---

### 5. Generate Reports
Generate various types of reports.

**Endpoint**: `POST /api/v1/analytics/reports`

**Request Body**:
```json
{
  "report_type": "string (required)",
  "time_range": "string (required)",
  "format": "string (required)",
  "device_ids": "array (optional)",
  "metrics": "array (optional)",
  "filters": "object (optional)",
  "options": "object (optional)"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/analytics/reports \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "device_performance",
    "time_range": "7d",
    "format": "json",
    "device_ids": [1, 2, 3],
    "metrics": ["temperature", "humidity", "pressure"],
    "filters": {
      "status": "online",
      "device_type": "sensor"
    },
    "options": {
      "include_charts": true,
      "include_summary": true,
      "include_recommendations": true
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "report_id": "report_12345",
    "report_type": "device_performance",
    "time_range": "7d",
    "generated_at": "2024-01-01T12:00:00Z",
    "format": "json",
    "summary": {
      "total_devices": 3,
      "avg_uptime": 98.7,
      "total_data_points": 3024,
      "total_alerts": 12,
      "performance_score": 0.85
    },
    "device_details": [
      {
        "device_id": 1,
        "device_name": "Temperature Sensor Alpha",
        "performance": {
          "uptime_percentage": 99.5,
          "data_points": 1008,
          "avg_response_time": 0.05,
          "health_score": 0.92
        },
        "metrics": {
          "temperature": {
            "avg": 23.4,
            "min": 18.5,
            "max": 28.9,
            "trend": "stable"
          }
        },
        "alerts": {
          "total": 4,
          "critical": 0,
          "warning": 2,
          "info": 2
        }
      }
    ],
    "charts": [
      {
        "chart_type": "line",
        "title": "Temperature Trend",
        "data": [
          {"timestamp": "2024-01-01T00:00:00Z", "value": 23.1},
          {"timestamp": "2024-01-01T01:00:00Z", "value": 23.3}
        ]
      }
    ],
    "recommendations": [
      {
        "type": "maintenance",
        "priority": "medium",
        "description": "Consider calibrating temperature sensor Alpha",
        "device_id": 1
      }
    ]
  },
  "message": "Report generated successfully"
}
```

---

### 6. Data Quality Analysis
Analyze data quality metrics.

**Endpoint**: `GET /api/v1/analytics/data-quality`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `device_id` | integer | null | Filter by device ID |
| `time_range` | string | `24h` | Time range (1h/6h/24h/7d/30d) |
| `metric` | string | null | Filter by metric name |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/data-quality?device_id=1&time_range=24h" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "device_id": 1,
    "time_range": "24h",
    "overall_quality_score": 0.92,
    "metrics": {
      "completeness": {
        "expected_points": 1440,
        "actual_points": 1435,
        "completeness_rate": 0.997,
        "missing_points": 5,
        "gaps": [
          {
            "start": "2024-01-01T03:00:00Z",
            "end": "2024-01-01T03:05:00Z",
            "duration": 300
          }
        ]
      },
      "accuracy": {
        "validation_errors": 2,
        "outlier_count": 3,
        "accuracy_score": 0.98,
        "outliers": [
          {
            "timestamp": "2024-01-01T14:00:00Z",
            "value": 28.9,
            "expected_range": [18.0, 30.0],
            "z_score": 2.6
          }
        ]
      },
      "timeliness": {
        "avg_delay": 30,
        "max_delay": 120,
        "timeliness_score": 0.95,
        "delay_distribution": {
          "p50": 25,
          "p95": 45,
          "p99": 85
        }
      },
      "consistency": {
        "variance": 2.1,
        "consistency_score": 0.89,
        "pattern_analysis": {
          "regular_pattern": true,
          "seasonal_pattern": false,
          "anomaly_count": 2
        }
      }
    },
    "recommendations": [
      {
        "type": "data_collection",
        "priority": "low",
        "description": "Investigate missing data points at 3:00 AM"
      },
      {
        "type": "sensor_calibration",
        "priority": "medium",
        "description": "Check sensor calibration for outlier values"
      }
    ]
  }
}
```

---

### 7. Usage Analytics
Get system usage analytics.

**Endpoint**: `GET /api/v1/analytics/usage`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `time_range` | string | `24h` | Time range (1h/6h/24h/7d/30d) |
| `granularity` | string | `1h` | Data granularity |
| `include_api` | boolean | true | Include API usage |
| `include_ui` | boolean | true | Include UI usage |
| `include_devices` | boolean | true | Include device usage |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/usage?time_range=24h&granularity=1h" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "time_range": "24h",
    "granularity": "1h",
    "api_usage": {
      "total_requests": 15420,
      "unique_users": 25,
      "avg_requests_per_hour": 642,
      "peak_hour": "14:00",
      "peak_requests": 892,
      "endpoints": {
        "/api/v1/devices/": 5120,
        "/api/v1/telemetry/": 3840,
        "/api/v1/alerts/": 2560,
        "/api/v1/analytics/": 1280,
        "/api/v1/health/": 2560
      },
      "response_times": {
        "p50": 45,
        "p95": 89,
        "p99": 156,
        "avg": 67
      }
    },
    "ui_usage": {
      "total_sessions": 180,
      "unique_users": 15,
      "avg_session_duration": 1800,
      "pages_visited": {
        "/dashboard": 890,
        "/devices": 450,
        "/analytics": 320,
        "/alerts": 280
      },
      "user_engagement": {
        "avg_page_views": 8.5,
        "bounce_rate": 0.15,
        "return_visits": 0.65
      }
    },
    "device_usage": {
      "total_devices": 5,
      "active_devices": 4,
      "data_points_submitted": 7200,
      "avg_data_points_per_hour": 300,
      "most_active_device": {
        "device_id": 1,
        "data_points": 2880,
        "percentage": 40.0
      }
    },
    "storage_usage": {
      "database_size": "2.5 GB",
      "telemetry_data_size": "1.8 GB",
      "growth_rate": "0.5 GB/day",
      "retention_days": 30
    }
  }
}
```

---

### 8. Comparative Analytics
Compare performance between devices or time periods.

**Endpoint**: `POST /api/v1/analytics/comparison`

**Request Body**:
```json
{
  "comparison_type": "string (required)",
  "entities": "array (required)",
  "time_range": "string (required)",
  "metrics": "array (required)",
  "options": "object (optional)"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/analytics/comparison \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "comparison_type": "device",
    "entities": [1, 2, 3],
    "time_range": "7d",
    "metrics": ["temperature", "humidity", "uptime"],
    "options": {
      "include_charts": true,
      "include_statistics": true
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "comparison_type": "device",
    "entities": [
      {
        "id": 1,
        "name": "Temperature Sensor Alpha",
        "metrics": {
          "temperature": {
            "avg": 23.4,
            "min": 18.5,
            "max": 28.9,
            "stddev": 2.1
          },
          "humidity": {
            "avg": 48.7,
            "min": 35.2,
            "max": 65.8,
            "stddev": 8.3
          },
          "uptime": {
            "percentage": 99.5
          }
        }
      },
      {
        "id": 2,
        "name": "Pressure Monitor Beta",
        "metrics": {
          "temperature": {
            "avg": 22.8,
            "min": 17.2,
            "max": 27.5,
            "stddev": 2.8
          },
          "humidity": {
            "avg": 46.2,
            "min": 32.1,
            "max": 62.3,
            "stddev": 7.9
          },
          "uptime": {
            "percentage": 98.2
          }
        }
      }
    ],
    "comparisons": {
      "temperature": {
        "best_device": 1,
        "worst_device": 2,
        "difference": 0.6,
        "percentage_difference": 2.6
      },
      "humidity": {
        "best_device": 2,
        "worst_device": 1,
        "difference": 2.5,
        "percentage_difference": 5.1
      },
      "uptime": {
        "best_device": 1,
        "worst_device": 2,
        "difference": 1.3,
        "percentage_difference": 1.3
      }
    },
    "ranking": {
      "overall": [
        {"device_id": 1, "score": 0.92},
        {"device_id": 2, "score": 0.85},
        {"device_id": 3, "score": 0.78}
      ]
    }
  },
  "message": "Comparison completed successfully"
}
```

---

### 9. Anomaly Detection
Detect anomalies in telemetry data.

**Endpoint**: `POST /api/v1/analytics/anomaly-detection`

**Request Body**:
```json
{
  "device_id": "integer (required)",
  "metric": "string (required)",
  "time_range": "string (required)",
  "sensitivity": "string (required)",
  "algorithm": "string (optional)",
  "options": "object (optional)"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/analytics/anomaly-detection \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "metric": "temperature",
    "time_range": "24h",
    "sensitivity": "medium",
    "algorithm": "statistical",
    "options": {
      "window_size": 24,
      "threshold": 2.0
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "device_id": 1,
    "metric": "temperature",
    "time_range": "24h",
    "algorithm": "statistical",
    "sensitivity": "medium",
    "anomalies": [
      {
        "timestamp": "2024-01-01T14:00:00Z",
        "value": 28.9,
        "expected_range": [18.0, 30.0],
        "z_score": 2.6,
        "anomaly_score": 0.92,
        "type": "spike",
        "severity": "medium",
        "description": "Temperature spike detected"
      },
      {
        "timestamp": "2024-01-01T22:00:00Z",
        "value": 17.8,
        "expected_range": [18.0, 30.0],
        "z_score": -2.1,
        "anomaly_score": 0.85,
        "type": "dip",
        "severity": "low",
        "description": "Temperature dip detected"
      }
    ],
    "statistics": {
      "total_points": 1440,
      "anomaly_count": 2,
      "anomaly_rate": 0.0014,
      "avg_z_score": 0.35,
      "max_z_score": 2.6
    },
    "recommendations": [
      {
        "type": "investigate",
        "priority": "medium",
        "description": "Investigate temperature spike at 14:00"
      }
    ]
  },
  "message": "Anomaly detection completed"
}
```

---

### 10. Export Analytics Data
Export analytics data in various formats.

**Endpoint**: `GET /api/v1/analytics/export`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `report_type` | string | `system` | Report type (system/devices/performance/usage) |
| `format` | string | `json` | Export format (json/csv/xlsx/pdf) |
| `time_range` | string | `24h` | Time range (1h/6h/24h/7d/30d) |
| `device_ids` | string | null | Comma-separated device IDs |
| `metrics` | string | null | Comma-separated metrics |
| `limit` | integer | 10000 | Maximum records to export |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/analytics/export?report_type=system&format=csv&time_range=24h" \
  -H "Authorization: Bearer <token>" \
  -o analytics_report.csv
```

**Example Response (CSV)**:
```csv
timestamp,device_id,device_name,metric_name,metric_value,unit,status
2024-01-01T12:00:00Z,1,Temperature Sensor Alpha,temperature,23.5,°C,online
2024-01-01T12:00:00Z,1,Temperature Sensor Alpha,humidity,45.2,%,online
2024-01-01T12:00:00Z,2,Pressure Monitor Beta,pressure,1013.25,hPa,online
```

---

## Data Models

### System Analytics Object
```json
{
  "system_stats": {
    "total_devices": "integer",
    "online_devices": "integer",
    "offline_devices": "integer",
    "error_devices": "integer",
    "devices_by_type": "object",
    "devices_by_status": "object"
  },
  "device_performance": "array",
  "telemetry_overview": "object",
  "system_health": "object",
  "utilization_trends": "object"
}
```

### Trend Analysis Object
```json
{
  "trend_analysis": {
    "trend_type": "string",
    "slope": "number",
    "intercept": "number",
    "r_squared": "number",
    "trend_direction": "string",
    "confidence": "number"
  },
  "historical_data": "array",
  "forecast": "array",
  "statistics": "object",
  "anomalies": "array"
}
```

### Report Object
```json
{
  "report_id": "string",
  "report_type": "string",
  "time_range": "string",
  "generated_at": "datetime (ISO format)",
  "format": "string",
  "summary": "object",
  "device_details": "array",
  "charts": "array",
  "recommendations": "array"
}
```

---

## Report Types

### Available Report Types
- **system**: System-wide performance report
- **device_performance**: Individual device performance report
- **usage**: System usage statistics report
- **data_quality**: Data quality analysis report
- **comparative**: Comparative analysis report
- **trend**: Trend analysis report
- **anomaly**: Anomaly detection report

### Export Formats
- **json**: Structured JSON format
- **csv**: Comma-separated values
- **xlsx**: Excel spreadsheet
- **pdf**: PDF document

---

## Rate Limiting

Analytics API endpoints have specific rate limits:
- **System Analytics**: 50 requests per minute
- **Device Analytics**: 100 requests per minute
- **Generate Reports**: 20 requests per minute
- **Trend Analysis**: 30 requests per minute
- **Export Data**: 10 requests per hour

---

## Performance Considerations

### Query Optimization
- Use appropriate time ranges to limit data volume
- Implement caching for frequently accessed analytics
- Use pagination for large datasets
- Optimize database queries with proper indexes

### Data Processing
- Process large datasets in batches
- Use streaming for real-time analytics
- Implement background processing for reports
- Monitor memory usage during analysis

---

## Best Practices

### Analytics Usage
- Use appropriate time ranges for analysis
- Cache frequently accessed analytics data
- Implement proper error handling for analytics requests
- Monitor analytics performance and optimize as needed

### Report Generation
- Use appropriate report types for specific needs
- Include relevant metrics and visualizations
- Provide actionable insights and recommendations
- Format reports appropriately for the audience

### Data Quality
- Monitor data quality metrics regularly
- Implement data validation and cleansing
- Track data completeness and accuracy
- Address data quality issues promptly

---

## Examples and Use Cases

### System Health Monitoring
```python
import requests

def get_system_health_analytics():
    """Get system health analytics"""
    response = requests.get(
        "http://localhost:8000/api/v1/analytics/system",
        params={
            "time_range": "24h",
            "include_device_details": True,
            "include_telemetry": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    analytics = response.json()["data"]
    
    # Check system health
    health_score = analytics["system_health"]["overall_score"]
    if health_score < 0.8:
        print(f"System health score: {health_score} - requires attention")
    
    # Check device status
    total_devices = analytics["system_stats"]["total_devices"]
    offline_devices = analytics["system_stats"]["offline_devices"]
    
    if offline_devices > 0:
        print(f"{offline_devices} of {total_devices} devices are offline")
    
    return analytics

# Usage example
health_analytics = get_system_health_analytics()
```

### Performance Trend Analysis
```python
def analyze_performance_trends(metric, days=7):
    """Analyze performance trends for a metric"""
    response = requests.get(
        "http://localhost:8000/api/v1/analytics/trends",
        params={
            "metric": metric,
            "time_range": f"{days}d",
            "granularity": "1h",
            "trend_type": "linear",
            "forecast_points": 24
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    trend_data = response.json()["data"]
    
    # Analyze trend
    trend_direction = trend_data["trend_analysis"]["trend_direction"]
    confidence = trend_data["trend_analysis"]["confidence"]
    
    print(f"Metric: {metric}")
    print(f"Trend: {trend_direction}")
    print(f"Confidence: {confidence:.2f}")
    
    # Check for anomalies
    anomalies = trend_data.get("anomalies", [])
    if anomalies:
        print(f"Found {len(anomalies)} anomalies")
        for anomaly in anomalies:
            print(f"  - {anomaly['timestamp']}: {anomaly['description']}")
    
    return trend_data

# Usage example
temp_trend = analyze_performance_trends("temperature", 7)
```

---

## Support

For Analytics API support:
- **Documentation**: [API Overview](api-overview.md)
- **Device API**: [Device API](device-api.md)
- **Telemetry API**: [Telemetry API](telemetry-api.md)
- **Alerts API**: [Alerts API](alerts-api.md)
- **Troubleshooting**: [Troubleshooting Guide](../10-reference/troubleshooting.md)
- **Email**: autobotsolution@gmail.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Analytics API Documentation v1.0**
