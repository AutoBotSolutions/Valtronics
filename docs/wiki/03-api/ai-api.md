# AI API Documentation

**Complete API reference for AI and machine learning features**

---

## Overview

The AI API provides comprehensive functionality for artificial intelligence and machine learning capabilities in the Valtronics system. This API supports predictive analytics, anomaly detection, device health scoring, and AI-powered insights.

---

## Base Endpoint
```
/api/v1/ai/
```

## Authentication
All AI API endpoints require JWT authentication:
```http
Authorization: Bearer <jwt-token>
```

---

## Endpoints

### 1. Get AI Insights
Generate AI-powered insights for devices and system performance.

**Endpoint**: `POST /api/v1/ai/insights`

**Request Body**:
```json
{
  "device_id": "integer (optional)",
  "device_type": "string (optional)",
  "time_range": "string (required)",
  "analysis_type": "string (required)",
  "options": "object (optional)"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/insights \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "time_range": "24h",
    "analysis_type": "performance",
    "options": {
      "include_predictions": true,
      "include_recommendations": true,
      "confidence_threshold": 0.8
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "insight_id": "insight_12345",
    "device_id": 1,
    "analysis_type": "performance",
    "time_range": "24h",
    "generated_at": "2024-01-01T12:00:00Z",
    "insights": [
      {
        "type": "performance_optimization",
        "title": "Temperature Sensor Performance Optimization",
        "description": "Device shows consistent performance with potential for optimization",
        "confidence": 0.92,
        "severity": "low",
        "recommendations": [
          {
            "action": "adjust_sampling_rate",
            "description": "Reduce sampling rate from 1 minute to 2 minutes to save energy",
            "impact": "medium",
            "estimated_savings": "15% energy consumption"
          }
        ],
        "metrics_analyzed": ["temperature", "humidity", "response_time"],
        "key_findings": [
          "Temperature readings are highly consistent (stddev: 0.2°C)",
          "Response time averages 45ms with low variance",
          "No significant performance degradation detected"
        ]
      }
    ],
    "predictions": [
      {
        "metric": "temperature",
        "prediction_type": "forecast",
        "predicted_values": [
          {
            "timestamp": "2024-01-01T13:00:00Z",
            "value": 23.7,
            "confidence": 0.85
          }
        ],
        "trend": "stable",
        "confidence": 0.87
      }
    ],
    "overall_health_score": 0.91,
    "ai_model_version": "v1.2.0"
  },
  "message": "AI insights generated successfully"
}
```

---

### 2. Anomaly Detection
Detect anomalies in device telemetry data using machine learning.

**Endpoint**: `POST /api/v1/ai/anomaly-detection`

**Request Body**:
```json
{
  "device_id": "integer (required)",
  "metrics": "array (required)",
  "time_range": "string (required)",
  "sensitivity": "string (required)",
  "algorithm": "string (optional)",
  "options": "object (optional)"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/anomaly-detection \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "metrics": ["temperature", "humidity", "pressure"],
    "time_range": "24h",
    "sensitivity": "medium",
    "algorithm": "isolation_forest",
    "options": {
      "window_size": 60,
      "contamination_rate": 0.1,
      "include_context": true
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "anomaly_id": "anomaly_12345",
    "device_id": 1,
    "analysis_period": "24h",
    "algorithm": "isolation_forest",
    "sensitivity": "medium",
    "anomalies": [
      {
        "id": 1,
        "timestamp": "2024-01-01T14:00:00Z",
        "anomaly_type": "multivariate",
        "severity": "medium",
        "anomaly_score": 0.78,
        "confidence": 0.85,
        "affected_metrics": [
          {
            "metric": "temperature",
            "value": 28.9,
            "expected_range": [18.0, 30.0],
            "deviation": 2.1
          },
          {
            "metric": "humidity",
            "value": 32.1,
            "expected_range": [35.0, 65.0],
            "deviation": -2.9
          }
        ],
        "context": {
          "preceding_values": {
            "temperature": [23.1, 23.3, 23.5, 23.2, 23.4],
            "humidity": [45.2, 45.8, 45.1, 45.6, 45.3]
          },
          "environmental_factors": {
            "time_of_day": "14:00",
            "day_of_week": "Monday",
            "season": "winter"
          }
        },
        "possible_causes": [
          "Sensor calibration drift",
          "Environmental temperature spike",
          "Power supply fluctuation"
        ],
        "recommended_actions": [
          "Verify sensor calibration",
          "Check environmental conditions",
          "Monitor power supply stability"
        ]
      }
    ],
    "statistics": {
      "total_data_points": 1440,
      "anomalies_detected": 1,
      "anomaly_rate": 0.0007,
      "false_positive_rate": 0.02,
      "detection_accuracy": 0.94
    },
    "model_info": {
      "model_version": "v2.1.0",
      "training_data_period": "30d",
      "features_used": 12,
      "model_confidence": 0.91
    }
  },
  "message": "Anomaly detection completed"
}
```

---

### 3. Predictive Maintenance
Generate predictive maintenance recommendations for devices.

**Endpoint**: `POST /api/v1/ai/predictive-maintenance`

**Request Body**:
```json
{
  "device_id": "integer (required)",
  "prediction_horizon": "string (required)",
  "maintenance_type": "string (optional)",
  "include_risk_assessment": "boolean (optional)",
  "options": "object (optional)"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/predictive-maintenance \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "prediction_horizon": "30d",
    "maintenance_type": "preventive",
    "include_risk_assessment": true,
    "options": {
      "failure_probability_threshold": 0.7,
      "include_cost_analysis": true,
      "recommendation_priority": "high"
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "maintenance_id": "maintenance_12345",
    "device_id": 1,
    "prediction_horizon": "30d",
    "generated_at": "2024-01-01T12:00:00Z",
    "maintenance_recommendations": [
      {
        "type": "preventive",
        "priority": "high",
        "title": "Sensor Calibration Maintenance",
        "description": "Calibrate temperature sensor to maintain accuracy",
        "recommended_date": "2024-01-15T00:00:00Z",
        "failure_probability": 0.78,
        "confidence": 0.85,
        "risk_assessment": {
          "risk_level": "medium",
          "potential_impact": "reduced_accuracy",
          "business_impact": "low",
          "safety_impact": "none"
        },
        "cost_analysis": {
          "estimated_cost": 150,
          "cost_if_ignored": 500,
          "cost_savings": 350,
          "roi": 233
        },
        "supporting_data": {
          "accuracy_trend": "declining",
          "current_accuracy": 0.92,
          "expected_accuracy_after_maintenance": 0.98,
          "historical_failures": 0
        },
        "steps": [
          "Schedule maintenance window",
          "Prepare calibration equipment",
          "Perform sensor calibration",
          "Verify accuracy post-maintenance",
          "Update maintenance records"
        ]
      },
      {
        "type": "corrective",
        "priority": "medium",
        "title": "Power Supply Check",
        "description": "Check and potentially replace power supply unit",
        "recommended_date": "2024-01-20T00:00:00Z",
        "failure_probability": 0.45,
        "confidence": 0.72,
        "risk_assessment": {
          "risk_level": "low",
          "potential_impact": "device_failure",
          "business_impact": "medium",
          "safety_impact": "none"
        },
        "cost_analysis": {
          "estimated_cost": 200,
          "cost_if_ignored": 1200,
          "cost_savings": 1000,
          "roi": 500
        }
      }
    ],
    "overall_health_forecast": {
      "current_health_score": 0.91,
      "predicted_health_score": 0.85,
      "health_trend": "declining",
      "confidence": 0.83
    },
    "model_info": {
      "model_version": "v3.1.0",
      "training_data_period": "90d",
      "features_analyzed": 25,
      "prediction_accuracy": 0.87
    }
  },
  "message": "Predictive maintenance analysis completed"
}
```

---

### 4. Device Health Score
Calculate comprehensive health score for a device.

**Endpoint**: `GET /api/v1/ai/health-score/{device_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `device_id` | integer | Device ID |

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `time_range` | string | `24h` | Time range (1h/6h/24h/7d/30d) |
| `include_details` | boolean | false | Include detailed breakdown |
| `include_recommendations` | boolean | false | Include improvement recommendations |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/ai/health-score/1?time_range=24h&include_details=true&include_recommendations=true" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "device_id": 1,
    "health_score": 0.87,
    "calculated_at": "2024-01-01T12:00:00Z",
    "time_range": "24h",
    "score_breakdown": {
      "connectivity": {
        "score": 0.95,
        "weight": 0.25,
        "factors": [
          {
            "factor": "uptime_percentage",
            "value": 99.5,
            "score": 0.98
          },
          {
            "factor": "connection_stability",
            "value": 0.99,
            "score": 0.99
          }
        ]
      },
      "data_quality": {
        "score": 0.92,
        "weight": 0.30,
        "factors": [
          {
            "factor": "completeness",
            "value": 0.99,
            "score": 0.99
          },
          {
            "factor": "accuracy",
            "value": 0.95,
            "score": 0.95
          },
          {
            "factor": "timeliness",
            "value": 0.92,
            "score": 0.92
          }
        ]
      },
      "performance": {
        "score": 0.85,
        "weight": 0.25,
        "factors": [
          {
            "factor": "response_time",
            "value": 45,
            "score": 0.88
          },
          {
            "factor": "throughput",
            "value": 1440,
            "score": 0.82
          }
        ]
      },
      "reliability": {
        "score": 0.78,
        "weight": 0.20,
        "factors": [
          {
            "factor": "error_rate",
            "value": 0.01,
            "score": 0.85
          },
          {
            "factor": "alert_frequency",
            "value": 2,
            "score": 0.70
          }
        ]
      }
    },
    "trend_analysis": {
      "current_score": 0.87,
      "previous_score": 0.89,
      "trend": "declining",
      "trend_change": -0.02,
      "confidence": 0.75
    },
    "recommendations": [
      {
        "category": "reliability",
        "priority": "medium",
        "description": "Reduce alert frequency by adjusting threshold settings",
        "impact": "health_score",
        "estimated_improvement": 0.05
      },
      {
        "category": "performance",
        "priority": "low",
        "description": "Optimize sampling rate to improve throughput",
        "impact": "health_score",
        "estimated_improvement": 0.03
      }
    ],
    "ai_model_version": "v2.3.0"
  }
}
```

---

### 5. Pattern Recognition
Identify patterns in device behavior and telemetry data.

**Endpoint**: `POST /api/v1/ai/pattern-recognition`

**Request Body**:
```json
{
  "device_id": "integer (required)",
  "pattern_type": "string (required)",
  "time_range": "string (required)",
  "metrics": "array (required)",
  "options": "object (optional)"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/pattern-recognition \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "pattern_type": "seasonal",
    "time_range": "7d",
    "metrics": ["temperature", "humidity"],
    "options": {
      "seasonality_period": "daily",
      "confidence_threshold": 0.8,
      "include_visualization": true
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "pattern_id": "pattern_12345",
    "device_id": 1,
    "pattern_type": "seasonal",
    "time_range": "7d",
    "detected_patterns": [
      {
        "pattern_name": "daily_temperature_cycle",
        "pattern_type": "seasonal",
        "confidence": 0.92,
        "period": "24h",
        "amplitude": 5.2,
        "phase": "06:00",
        "description": "Temperature follows daily cycle with peak at 2 PM",
        "metrics": ["temperature"],
        "pattern_data": {
          "peak_time": "14:00",
          "peak_value": 26.8,
          "trough_time": "06:00",
          "trough_value": 21.6,
          "cycle_duration": "24h"
        },
        "visualization": {
          "chart_type": "line",
          "data_points": [
            {"timestamp": "2024-01-01T06:00:00Z", "value": 21.6},
            {"timestamp": "2024-01-01T14:00:00Z", "value": 26.8}
          ]
        },
        "business_implications": [
          "Optimal cooling schedule: 10:00 - 16:00",
          "Energy consumption peaks at 14:00",
          "Maintenance window: 06:00 - 08:00"
        ]
      },
      {
        "pattern_name": "humidity_correlation",
        "pattern_type": "correlation",
        "confidence": 0.87,
        "correlation_coefficient": 0.78,
        "description": "Humidity inversely correlates with temperature",
        "metrics": ["temperature", "humidity"],
        "correlation_data": {
          "correlation_type": "negative",
          "strength": "strong",
          "lag": "0h",
          "significance": 0.001
        }
      }
    ],
    "anomaly_patterns": [
      {
        "pattern_name": "weekend_deviation",
        "pattern_type": "temporal",
        "confidence": 0.75,
        "description": "Temperature patterns deviate on weekends",
        "deviation_magnitude": 2.1,
        "occurrence": "weekends"
      }
    ],
    "model_info": {
      "model_version": "v1.8.0",
      "algorithm": "fft_analysis",
      "confidence_threshold": 0.8
    }
  },
  "message": "Pattern recognition completed"
}
```

---

### 6. Optimization Recommendations
Generate AI-powered optimization recommendations.

**Endpoint**: `POST /api/v1/ai/optimization`

**Request Body**:
```json
{
  "device_ids": "array (optional)",
  "device_type": "string (optional)",
  "optimization_type": "string (required)",
  "objectives": "array (required)",
  "constraints": "object (optional)",
  "options": "object (optional)"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/optimization \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_ids": [1, 2, 3],
    "optimization_type": "energy_efficiency",
    "objectives": ["reduce_energy_consumption", "maintain_accuracy"],
    "constraints": {
      "min_accuracy": 0.90,
      "max_response_time": 100
    },
    "options": {
      "include_cost_analysis": true,
      "implementation_timeline": "30d"
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "optimization_id": "opt_12345",
    "optimization_type": "energy_efficiency",
    "target_devices": [1, 2, 3],
    "generated_at": "2024-01-01T12:00:00Z",
    "recommendations": [
      {
        "id": 1,
        "title": "Adjust Sampling Rates",
        "description": "Optimize sampling rates based on device workload",
        "priority": "high",
        "estimated_impact": {
          "energy_savings": "25%",
          "accuracy_impact": "-2%",
          "response_time_impact": "+10ms"
        },
        "implementation": {
          "steps": [
            "Analyze current sampling patterns",
            "Calculate optimal rates",
            "Update device configurations",
            "Monitor performance"
          ],
          "timeline": "7 days",
          "complexity": "low",
          "cost": 0
        },
        "device_specific": [
          {
            "device_id": 1,
            "current_rate": "1/min",
            "recommended_rate": "2/min",
            "reasoning": "Low variability in readings"
          },
          {
            "device_id": 2,
            "current_rate": "1/min",
            "recommended_rate": "30/sec",
            "reasoning": "High-frequency data needed"
          }
        ]
      },
      {
        "id": 2,
        "title": "Implement Sleep Cycles",
        "description": "Configure sleep cycles during low-activity periods",
        "priority": "medium",
        "estimated_impact": {
          "energy_savings": "15%",
          "accuracy_impact": "0%",
          "response_time_impact": "+50ms"
        },
        "implementation": {
          "steps": [
            "Identify low-activity periods",
            "Configure sleep schedules",
            "Test wake-up reliability",
            "Deploy to production"
          ],
          "timeline": "14 days",
          "complexity": "medium",
          "cost": 500
        }
      }
    ],
    "overall_projection": {
      "current_energy_consumption": "500 kWh/month",
      "projected_energy_consumption": "350 kWh/month",
      "total_savings": "150 kWh/month",
      "cost_savings": "$45/month",
      "roi": "540%",
      "payback_period": "2.2 months"
    },
    "model_info": {
      "model_version": "v2.5.0",
      "optimization_algorithm": "genetic_algorithm",
      "confidence": 0.83
    }
  },
  "message": "Optimization recommendations generated"
}
```

---

### 7. AI Model Training
Train or retrain AI models with new data.

**Endpoint**: `POST /api/v1/ai/train-model`

**Request Body**:
```json
{
  "model_type": "string (required)",
  "training_data_period": "string (required)",
  "features": "array (required)",
  "hyperparameters": "object (optional)",
  "validation_split": "number (optional)",
  "options": "object (optional)"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/train-model \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "anomaly_detection",
    "training_data_period": "30d",
    "features": ["temperature", "humidity", "pressure", "response_time"],
    "hyperparameters": {
      "contamination_rate": 0.1,
      "n_estimators": 100,
      "max_features": "auto"
    },
    "validation_split": 0.2,
    "options": {
      "cross_validation": true,
      "feature_importance": true
    }
  }'
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "training_id": "train_12345",
    "model_type": "anomaly_detection",
    "training_status": "completed",
    "started_at": "2024-01-01T12:00:00Z",
    "completed_at": "2024-01-01T12:15:00Z",
    "training_duration": "15 minutes",
    "model_performance": {
      "accuracy": 0.94,
      "precision": 0.91,
      "recall": 0.89,
      "f1_score": 0.90,
      "auc_roc": 0.96
    },
    "validation_results": {
      "validation_accuracy": 0.92,
      "cross_validation_scores": [0.91, 0.93, 0.92, 0.94, 0.91],
      "mean_cv_score": 0.922,
      "std_cv_score": 0.012
    },
    "feature_importance": [
      {
        "feature": "temperature",
        "importance": 0.35,
        "rank": 1
      },
      {
        "feature": "response_time",
        "importance": 0.28,
        "rank": 2
      },
      {
        "feature": "humidity",
        "importance": 0.22,
        "rank": 3
      },
      {
        "feature": "pressure",
        "importance": 0.15,
        "rank": 4
      }
    ],
    "training_data": {
      "total_samples": 43200,
      "training_samples": 34560,
      "validation_samples": 8640,
      "feature_count": 4,
      "data_quality_score": 0.96
    },
    "model_info": {
      "model_version": "v2.6.0",
      "model_size": "2.5 MB",
      "deployment_ready": true,
      "previous_version": "v2.5.0",
      "performance_improvement": "+3%"
    }
  },
  "message": "Model training completed successfully"
}
```

---

### 8. AI Model Status
Get status and information about AI models.

**Endpoint**: `GET /api/v1/ai/models/status`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_type` | string | null | Filter by model type |
| `include_details` | boolean | false | Include detailed model information |
| `include_performance` | boolean | false | Include performance metrics |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/ai/models/status?include_details=true&include_performance=true" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "models": [
      {
        "model_id": "model_anomaly_001",
        "model_type": "anomaly_detection",
        "version": "v2.6.0",
        "status": "active",
        "deployed_at": "2024-01-01T10:00:00Z",
        "last_trained": "2024-01-01T12:15:00Z",
        "training_data_period": "30d",
        "performance": {
          "accuracy": 0.94,
          "precision": 0.91,
          "recall": 0.89,
          "f1_score": 0.90
        },
        "usage_stats": {
          "total_predictions": 15420,
          "avg_response_time": "125ms",
          "error_rate": 0.001
        },
        "configuration": {
          "algorithm": "isolation_forest",
          "features": ["temperature", "humidity", "pressure", "response_time"],
          "hyperparameters": {
            "contamination_rate": 0.1,
            "n_estimators": 100
          }
        }
      },
      {
        "model_id": "model_health_001",
        "model_type": "health_scoring",
        "version": "v2.3.0",
        "status": "active",
        "deployed_at": "2024-01-01T08:00:00Z",
        "last_trained": "2024-01-01T06:00:00Z",
        "training_data_period": "90d",
        "performance": {
          "r_squared": 0.87,
          "mae": 0.05,
          "rmse": 0.08
        }
      }
    ],
    "summary": {
      "total_models": 2,
      "active_models": 2,
      "models_retraining": 0,
      "avg_model_age": "18 hours",
      "overall_performance": 0.91
    }
  }
}
```

---

### 9. AI Feature Importance
Get feature importance analysis for AI models.

**Endpoint**: `GET /api/v1/ai/feature-importance`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_type` | string | required | Model type |
| `device_id` | integer | null | Filter by device ID |
| `time_range` | string | `24h` | Time range for analysis |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/ai/feature-importance?model_type=anomaly_detection&device_id=1&time_range=24h" \
  -H "Authorization: Bearer <token>"
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "model_type": "anomaly_detection",
    "device_id": 1,
    "time_range": "24h",
    "feature_importance": [
      {
        "feature": "temperature",
        "importance": 0.35,
        "rank": 1,
        "trend": "stable",
        "correlation_with_anomalies": 0.78
      },
      {
        "feature": "response_time",
        "importance": 0.28,
        "rank": 2,
        "trend": "increasing",
        "correlation_with_anomalies": 0.65
      },
      {
        "feature": "humidity",
        "importance": 0.22,
        "rank": 3,
        "trend": "stable",
        "correlation_with_anomalies": 0.42
      },
      {
        "feature": "pressure",
        "importance": 0.15,
        "rank": 4,
        "trend": "decreasing",
        "correlation_with_anomalies": 0.31
      }
    ],
    "analysis_summary": {
      "total_features": 4,
      "dominant_feature": "temperature",
      "feature_diversity": 0.85,
      "model_confidence": 0.91
    },
    "recommendations": [
      {
        "type": "feature_optimization",
        "description": "Focus on temperature monitoring for anomaly detection",
        "impact": "improved_detection_accuracy"
      },
      {
        "type": "feature_engineering",
        "description": "Consider creating composite features from temperature and humidity",
        "impact": "enhanced_pattern_recognition"
      }
    ]
  }
}
```

---

## Data Models

### AI Insight Object
```json
{
  "insight_id": "string",
  "device_id": "integer",
  "analysis_type": "string",
  "time_range": "string",
  "generated_at": "datetime (ISO format)",
  "insights": "array",
  "predictions": "array",
  "overall_health_score": "number",
  "ai_model_version": "string"
}
```

### Anomaly Detection Object
```json
{
  "anomaly_id": "string",
  "device_id": "integer",
  "analysis_period": "string",
  "algorithm": "string",
  "sensitivity": "string",
  "anomalies": "array",
  "statistics": "object",
  "model_info": "object"
}
```

### Predictive Maintenance Object
```json
{
  "maintenance_id": "string",
  "device_id": "integer",
  "prediction_horizon": "string",
  "maintenance_recommendations": "array",
  "overall_health_forecast": "object",
  "model_info": "object"
}
```

---

## AI Model Types

### Available Models
- **anomaly_detection**: Isolation Forest, One-Class SVM
- **health_scoring**: Random Forest, Gradient Boosting
- **predictive_maintenance**: LSTM, Time Series Models
- **pattern_recognition**: FFT Analysis, Clustering
- **optimization**: Genetic Algorithms, Reinforcement Learning

### Model Algorithms
- **isolation_forest**: Unsupervised anomaly detection
- **random_forest**: Ensemble learning for classification/regression
- **lstm**: Long Short-Term Memory for time series
- **genetic_algorithm**: Optimization through evolution
- **kmeans**: Clustering for pattern recognition

---

## Rate Limiting

AI API endpoints have specific rate limits:
- **AI Insights**: 20 requests per minute
- **Anomaly Detection**: 10 requests per minute
- **Predictive Maintenance**: 5 requests per minute
- **Health Score**: 50 requests per minute
- **Model Training**: 2 requests per hour
- **Pattern Recognition**: 15 requests per minute

---

## Performance Considerations

### Model Performance
- Use appropriate model complexity for data size
- Implement model versioning and A/B testing
- Monitor model performance over time
- Retrain models regularly with new data

### Computational Resources
- AI models require significant computational resources
- Implement caching for frequently used predictions
- Use batch processing for large-scale analysis
- Monitor GPU/CPU usage during model training

---

## Best Practices

### AI Model Usage
- Use appropriate models for specific use cases
- Validate model predictions with domain knowledge
- Monitor model performance and drift
- Implement human oversight for critical decisions

### Data Quality
- Ensure high-quality training data
- Preprocess and normalize data appropriately
- Handle missing values and outliers
- Validate data before model training

### Interpretability
- Use explainable AI techniques
- Provide confidence scores for predictions
- Document model limitations and assumptions
- Implement model monitoring and alerting

---

## Examples and Use Cases

### Automated Anomaly Detection
```python
import requests

def detect_anomalies(device_id, metrics, sensitivity="medium"):
    """Detect anomalies in device metrics"""
    response = requests.post(
        "http://localhost:8000/api/v1/ai/anomaly-detection",
        json={
            "device_id": device_id,
            "metrics": metrics,
            "time_range": "24h",
            "sensitivity": sensitivity,
            "algorithm": "isolation_forest"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    result = response.json()["data"]
    
    # Process anomalies
    anomalies = result["anomalies"]
    if anomalies:
        print(f"Detected {len(anomalies)} anomalies:")
        for anomaly in anomalies:
            print(f"  - {anomaly['timestamp']}: {anomaly['description']}")
            print(f"    Severity: {anomaly['severity']}")
            print(f"    Recommended actions: {', '.join(anomaly['recommended_actions'])}")
    
    return result

# Usage example
anomalies = detect_anomalies(1, ["temperature", "humidity", "pressure"])
```

### Predictive Maintenance Scheduling
```python
def schedule_maintenance(device_id, horizon="30d"):
    """Get predictive maintenance recommendations"""
    response = requests.post(
        "http://localhost:8000/api/v1/ai/predictive-maintenance",
        json={
            "device_id": device_id,
            "prediction_horizon": horizon,
            "maintenance_type": "preventive",
            "include_risk_assessment": True,
            "include_cost_analysis": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    result = response.json()["data"]
    
    # Process maintenance recommendations
    recommendations = result["maintenance_recommendations"]
    for rec in recommendations:
        print(f"Maintenance: {rec['title']}")
        print(f"Priority: {rec['priority']}")
        print(f"Recommended date: {rec['recommended_date']}")
        print(f"Failure probability: {rec['failure_probability']}")
        print(f"Cost: ${rec['cost_analysis']['estimated_cost']}")
        print(f"Savings: ${rec['cost_analysis']['cost_savings']}")
        print("---")
    
    return result

# Usage example
maintenance = schedule_maintenance(1, "30d")
```

---

## Support

For AI API support:
- **Documentation**: [API Overview](api-overview.md)
- **Device API**: [Device API](device-api.md)
- **Telemetry API**: [Telemetry API](telemetry-api.md)
- **Analytics API**: [Analytics API](analytics-api.md)
- **Troubleshooting**: [Troubleshooting Guide](../10-reference/troubleshooting.md)
- **Email**: autobotsolution@gmail.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**AI API Documentation v1.0**
