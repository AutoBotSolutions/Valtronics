from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from app.db.session_sqlite import get_db  # Use SQLite session for local development
from app.services.device_service import DeviceService, TelemetryService
from app.core.config import settings
import openai
import json

router = APIRouter()

# AI Request/Response Models
class AIInsightRequest(BaseModel):
    device_id: int
    query: str
    time_range_hours: int = 24

class AIInsightResponse(BaseModel):
    insight: str
    recommendations: List[str]
    confidence_score: float
    data_points_analyzed: int

class DeviceAnomalyRequest(BaseModel):
    device_id: int
    metrics: List[str] = ["temperature", "vibration", "power_consumption"]

class DeviceAnomalyResponse(BaseModel):
    anomalies_detected: List[Dict[str, Any]]
    severity: str
    confidence: float

class PredictiveMaintenanceRequest(BaseModel):
    device_id: int
    prediction_days: int = 7

class PredictiveMaintenanceResponse(BaseModel):
    maintenance_score: float
    risk_factors: List[str]
    recommended_actions: List[str]
    next_maintenance_date: str

# Initialize OpenAI client
if settings.OPENAI_API_KEY:
    openai.api_key = settings.OPENAI_API_KEY

@router.post("/insights", response_model=AIInsightResponse)
async def get_device_insights(
    request: AIInsightRequest,
    db: Session = Depends(get_db)
):
    """Get AI-powered insights for a device"""
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=503, 
            detail="OpenAI API key not configured"
        )
    
    device = DeviceService.get_device(db, request.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Get telemetry data
    telemetry_data = TelemetryService.get_device_telemetry(
        db, request.device_id, limit=500, hours=request.time_range_hours
    )
    
    if not telemetry_data:
        raise HTTPException(
            status_code=404, 
            detail="No telemetry data available for analysis"
        )
    
    # Prepare data for AI analysis
    data_summary = _prepare_telemetry_summary(telemetry_data)
    
    # Create AI prompt
    prompt = f"""
    Analyze the following device telemetry data and provide insights:
    
    Device: {device.name} ({device.device_type})
    Location: {device.location}
    Data Summary: {json.dumps(data_summary, indent=2)}
    User Query: {request.query}
    
    Provide:
    1. A detailed insight about the device performance
    2. Specific recommendations for optimization
    3. A confidence score (0-1) for your analysis
    """
    
    try:
        response = openai.ChatCompletion.create(
            model=settings.AI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert IoT and device analytics AI assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        ai_response = response.choices[0].message.content
        
        # Parse AI response (simplified - in production, use structured output)
        return AIInsightResponse(
            insight=ai_response,
            recommendations=["Optimize power consumption", "Schedule maintenance check"],
            confidence_score=0.85,
            data_points_analyzed=len(telemetry_data)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"AI analysis failed: {str(e)}"
        )

@router.post("/anomaly-detection", response_model=DeviceAnomalyResponse)
async def detect_anomalies(
    request: DeviceAnomalyRequest,
    db: Session = Depends(get_db)
):
    """Detect anomalies in device telemetry data"""
    device = DeviceService.get_device(db, request.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Get recent telemetry data
    telemetry_data = TelemetryService.get_device_telemetry(
        db, request.device_id, limit=1000, hours=48
    )
    
    # Simple anomaly detection (in production, use ML models)
    anomalies = _detect_simple_anomalies(telemetry_data, request.metrics)
    
    severity = "high" if len(anomalies) > 5 else "medium" if len(anomalies) > 2 else "low"
    confidence = min(0.9, len(anomalies) / 10.0)
    
    return DeviceAnomalyResponse(
        anomalies_detected=anomalies,
        severity=severity,
        confidence=confidence
    )

@router.post("/predictive-maintenance", response_model=PredictiveMaintenanceResponse)
async def predictive_maintenance(
    request: PredictiveMaintenanceRequest,
    db: Session = Depends(get_db)
):
    """Get predictive maintenance recommendations"""
    device = DeviceService.get_device(db, request.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Get historical telemetry data
    telemetry_data = TelemetryService.get_device_telemetry(
        db, request.device_id, limit=2000, hours=168  # 7 days
    )
    
    # Simple predictive analysis (in production, use ML models)
    maintenance_score = _calculate_maintenance_score(telemetry_data)
    risk_factors = _identify_risk_factors(telemetry_data, device)
    recommended_actions = _get_maintenance_recommendations(maintenance_score)
    
    from datetime import datetime, timedelta
    next_maintenance = datetime.now() + timedelta(days=request.prediction_days)
    
    return PredictiveMaintenanceResponse(
        maintenance_score=maintenance_score,
        risk_factors=risk_factors,
        recommended_actions=recommended_actions,
        next_maintenance_date=next_maintenance.isoformat()
    )

@router.get("/device/{device_id}/health-score")
async def get_device_health_score(device_id: int, db: Session = Depends(get_db)):
    """Get overall health score for a device"""
    device = DeviceService.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Get recent telemetry
    telemetry_data = TelemetryService.get_device_telemetry(
        db, device_id, limit=100, hours=24
    )
    
    # Calculate health score based on various factors
    health_score = _calculate_health_score(telemetry_data, device)
    
    return {
        "device_id": device_id,
        "health_score": health_score,
        "status": device.status,
        "last_analyzed": telemetry_data[-1].timestamp.isoformat() if telemetry_data else None
    }

# Helper functions
def _prepare_telemetry_summary(telemetry_data: List) -> Dict[str, Any]:
    """Prepare telemetry data summary for AI analysis"""
    summary = {}
    
    for data_point in telemetry_data:
        metric = data_point.metric_name
        if metric not in summary:
            summary[metric] = {
                "values": [],
                "unit": data_point.unit,
                "count": 0
            }
        
        summary[metric]["values"].append(data_point.metric_value)
        summary[metric]["count"] += 1
    
    # Calculate statistics
    for metric in summary:
        values = summary[metric]["values"]
        if values:
            summary[metric]["min"] = min(values)
            summary[metric]["max"] = max(values)
            summary[metric]["avg"] = sum(values) / len(values)
            summary[metric]["latest"] = values[-1]
    
    return summary

def _detect_simple_anomalies(telemetry_data: List, metrics: List[str]) -> List[Dict[str, Any]]:
    """Simple anomaly detection using statistical methods"""
    anomalies = []
    
    for metric in metrics:
        metric_data = [d for d in telemetry_data if d.metric_name == metric]
        if len(metric_data) < 10:
            continue
        
        values = [d.metric_value for d in metric_data]
        mean = sum(values) / len(values)
        std = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
        
        # Detect outliers (2 standard deviations from mean)
        for data_point in metric_data:
            if abs(data_point.metric_value - mean) > 2 * std:
                anomalies.append({
                    "metric": metric,
                    "value": data_point.metric_value,
                    "expected_range": [mean - 2 * std, mean + 2 * std],
                    "timestamp": data_point.timestamp.isoformat(),
                    "severity": "high" if abs(data_point.metric_value - mean) > 3 * std else "medium"
                })
    
    return anomalies

def _calculate_maintenance_score(telemetry_data: List) -> float:
    """Calculate maintenance need score (0-1)"""
    if not telemetry_data:
        return 0.5
    
    # Simple scoring based on data recency and variability
    recent_data = [d for d in telemetry_data if (d.timestamp - telemetry_data[-1].timestamp).total_seconds() < 86400]  # Last 24h
    
    if not recent_data:
        return 0.8  # No recent data is concerning
    
    # Score based on metric variability
    scores = []
    for metric in set(d.metric_name for d in recent_data):
        metric_values = [d.metric_value for d in recent_data if d.metric_name == metric]
        if len(metric_values) > 1:
            mean = sum(metric_values) / len(metric_values)
            std = (sum((x - mean) ** 2 for x in metric_values) / len(metric_values)) ** 0.5
            cv = std / mean if mean != 0 else 0
            scores.append(min(cv * 2, 1.0))  # Coefficient of variation
    
    return sum(scores) / len(scores) if scores else 0.3

def _identify_risk_factors(telemetry_data: List, device) -> List[str]:
    """Identify potential risk factors"""
    risk_factors = []
    
    if device.status == "offline":
        risk_factors.append("Device currently offline")
    
    if not telemetry_data:
        risk_factors.append("No recent telemetry data")
        return risk_factors
    
    # Check for unusual patterns
    for metric in set(d.metric_name for d in telemetry_data):
        metric_data = [d for d in telemetry_data if d.metric_name == metric]
        if len(metric_data) < 5:
            continue
        
        values = [d.metric_value for d in metric_data]
        latest = values[-1]
        avg = sum(values) / len(values)
        
        if latest > avg * 1.5:
            risk_factors.append(f"{metric} significantly above average")
        elif latest < avg * 0.5:
            risk_factors.append(f"{metric} significantly below average")
    
    return risk_factors

def _get_maintenance_recommendations(score: float) -> List[str]:
    """Get maintenance recommendations based on score"""
    if score > 0.8:
        return ["Schedule immediate maintenance", "Perform comprehensive diagnostics"]
    elif score > 0.6:
        return ["Schedule maintenance within 48 hours", "Monitor closely"]
    elif score > 0.4:
        return ["Routine maintenance check recommended", "Continue monitoring"]
    else:
        return ["No immediate maintenance needed", "Continue normal operation"]

def _calculate_health_score(telemetry_data: List, device) -> float:
    """Calculate overall device health score"""
    if not telemetry_data:
        return 0.3 if device.status == "online" else 0.1
    
    # Base score from status
    status_scores = {"online": 0.8, "offline": 0.3, "error": 0.1}
    base_score = status_scores.get(device.status, 0.5)
    
    # Adjust based on data recency and quality
    recent_data = [d for d in telemetry_data if (d.timestamp - telemetry_data[-1].timestamp).total_seconds() < 3600]  # Last hour
    
    if recent_data:
        data_quality = len(recent_data) / 60.0  # Expecting ~1 data point per minute
        data_quality = min(data_quality, 1.0)
    else:
        data_quality = 0.3
    
    return (base_score + data_quality) / 2
