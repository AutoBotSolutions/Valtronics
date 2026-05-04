from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session_sqlite import get_db  # Use SQLite session for local development
from app.services.analytics_service import AnalyticsService
from app.schemas.device import Device

router = APIRouter()

@router.get("/device/{device_id}")
async def get_device_analytics(
    device_id: int,
    hours: int = Query(24, ge=1, le=168),  # Max 7 days
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics for a specific device"""
    analytics = AnalyticsService.get_device_analytics(db, device_id, hours)
    
    if not analytics:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return analytics

@router.get("/system")
async def get_system_analytics(
    hours: int = Query(24, ge=1, le=168),  # Max 7 days
    db: Session = Depends(get_db)
):
    """Get system-wide analytics"""
    return AnalyticsService.get_system_analytics(db, hours)

@router.get("/device/{device_id}/timeseries")
async def get_time_series_data(
    device_id: int,
    metric: str = Query(..., description="Metric name to retrieve"),
    hours: int = Query(24, ge=1, le=168),  # Max 7 days
    db: Session = Depends(get_db)
):
    """Get time series data for a specific device metric"""
    time_series = AnalyticsService.get_time_series_data(db, device_id, metric, hours)
    
    if not time_series:
        raise HTTPException(
            status_code=404, 
            detail=f"No data found for metric '{metric}' on device {device_id}"
        )
    
    return {
        "device_id": device_id,
        "metric": metric,
        "time_range_hours": hours,
        "data_points": len(time_series),
        "data": time_series
    }

@router.post("/comparison")
async def compare_devices(
    device_ids: List[int],
    metric: str = Query(..., description="Metric name to compare"),
    hours: int = Query(24, ge=1, le=168),  # Max 7 days
    db: Session = Depends(get_db)
):
    """Compare metrics across multiple devices"""
    if len(device_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 devices required for comparison")
    
    if len(device_ids) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 devices can be compared at once")
    
    comparison = AnalyticsService.get_comparison_data(db, device_ids, metric, hours)
    
    return {
        "metric": metric,
        "time_range_hours": hours,
        "devices_compared": len(device_ids),
        "comparison_data": comparison
    }

@router.get("/metrics")
async def get_available_metrics(
    device_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get available metrics for analytics"""
    if device_id:
        # Get metrics for specific device
        from app.services.device_service import TelemetryService
        telemetry = TelemetryService.get_device_telemetry(db, device_id, limit=1000, hours=24)
        metrics = list(set(t.metric_name for t in telemetry))
    else:
        # Get all system metrics
        from app.services.device_service import DeviceService
        devices = DeviceService.get_devices(db, limit=100)
        all_metrics = set()
        
        for device in devices:
            telemetry = TelemetryService.get_device_telemetry(db, device.id, limit=100, hours=24)
            all_metrics.update(t.metric_name for t in telemetry)
        
        metrics = list(all_metrics)
    
    return {
        "metrics": sorted(metrics),
        "count": len(metrics)
    }

@router.get("/device/{device_id}/performance")
async def get_device_performance(
    device_id: int,
    hours: int = Query(24, ge=1, le=168),  # Max 7 days
    db: Session = Depends(get_db)
):
    """Get detailed performance metrics for a device"""
    analytics = AnalyticsService.get_device_analytics(db, device_id, hours)
    
    if not analytics:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {
        "device_id": device_id,
        "time_range_hours": hours,
        "performance_metrics": analytics["performance_metrics"],
        "data_quality": analytics["data_quality"],
        "anomalies": analytics["anomalies"],
        "trends": analytics["trends"]
    }

@router.get("/system/health")
async def get_system_health(
    hours: int = Query(24, ge=1, le=168),  # Max 7 days
    db: Session = Depends(get_db)
):
    """Get overall system health metrics"""
    analytics = AnalyticsService.get_system_analytics(db, hours)
    
    return {
        "system_health": analytics["system_health"],
        "system_stats": analytics["system_stats"],
        "utilization_trends": analytics["utilization_trends"],
        "alert_summary": analytics["alert_summary"]
    }

@router.get("/device/{device_id}/summary")
async def get_device_summary(
    device_id: int,
    hours: int = Query(24, ge=1, le=168),  # Max 7 days
    db: Session = Depends(get_db)
):
    """Get a quick summary of device status and recent activity"""
    analytics = AnalyticsService.get_device_analytics(db, device_id, hours)
    
    if not analytics:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return {
        "device_info": analytics["device_info"],
        "telemetry_summary": analytics["telemetry_summary"],
        "performance_score": analytics["performance_metrics"]["score"],
        "anomaly_count": len(analytics["anomalies"]),
        "data_quality_score": analytics["data_quality"]["score"],
        "last_updated": analytics["telemetry_summary"]["metrics"].get("latest", {})
    }
