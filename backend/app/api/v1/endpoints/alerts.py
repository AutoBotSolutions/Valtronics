from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.db.session_sqlite import get_db  # Use SQLite session for local development
from app.services.alert_service import AlertService, NotificationService

router = APIRouter()

# Alert schemas
class AlertCreate(BaseModel):
    device_id: int
    title: str
    description: Optional[str] = None
    severity: str  # critical, warning, info
    alert_type: str  # threshold, anomaly, system, device
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    metric_name: Optional[str] = None

class AlertRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    device_id: Optional[int] = None
    device_type: Optional[str] = None
    metric_name: str
    condition: str  # gt, lt, eq, gte, lte
    threshold_value: float
    severity: str = "warning"
    is_active: bool = True
    notification_enabled: bool = True
    cooldown_minutes: int = 30

# Alert endpoints
@router.get("/")
async def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get alerts with optional filtering"""
    return AlertService.get_alerts(db, skip=skip, limit=limit, status=status)

@router.get("/{alert_id}")
async def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get a specific alert by ID"""
    alert = AlertService.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.get("/device/{device_id}")
async def get_device_alerts(
    device_id: int,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get alerts for a specific device"""
    return AlertService.get_device_alerts(db, device_id, status)

@router.post("/", status_code=201)
async def create_alert(alert: AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert"""
    return AlertService.create_alert(db, alert.dict())

@router.patch("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    """Acknowledge an alert"""
    alert = AlertService.acknowledge_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.patch("/{alert_id}/resolve")
async def resolve_alert(alert_id: int, resolution_note: str = "", db: Session = Depends(get_db)):
    """Resolve an alert"""
    alert = AlertService.resolve_alert(db, alert_id, resolution_note)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.get("/stats/active")
async def get_active_alerts_count(db: Session = Depends(get_db)):
    """Get count of active alerts by severity"""
    return AlertService.get_active_alerts_count(db)

@router.get("/stats/summary")
async def get_alert_statistics(
    hours: int = Query(24, ge=1, le=168),  # Max 7 days
    db: Session = Depends(get_db)
):
    """Get alert statistics for a time period"""
    return AlertService.get_alert_statistics(db, hours)

# Alert Rule endpoints
@router.get("/rules/")
async def get_alert_rules(
    device_id: Optional[int] = Query(None),
    is_active: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get alert rules"""
    return AlertService.get_alert_rules(db, device_id, is_active)

@router.post("/rules/", status_code=201)
async def create_alert_rule(rule: AlertRuleCreate, db: Session = Depends(get_db)):
    """Create a new alert rule"""
    return AlertService.create_alert_rule(db, rule.dict())

@router.post("/check/{device_id}")
async def check_alert_rules(device_id: int, db: Session = Depends(get_db)):
    """Check alert rules for a device (triggered by new telemetry)"""
    # Get recent telemetry data
    from app.services.device_service import TelemetryService
    telemetry_data = TelemetryService.get_device_telemetry(db, device_id, limit=100, hours=1)
    
    new_alerts = AlertService.check_alert_rules(db, device_id, telemetry_data)
    
    return {
        "device_id": device_id,
        "telemetry_points_checked": len(telemetry_data),
        "new_alerts_created": len(new_alerts),
        "alerts": new_alerts
    }

# Notification endpoints
@router.post("/{alert_id}/notify")
async def send_alert_notifications(alert_id: int, db: Session = Depends(get_db)):
    """Send notifications for an alert"""
    success = NotificationService.send_notifications(db, alert_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Some notifications failed to send")
    
    return {"message": "Notifications sent successfully"}

@router.get("/notifications/pending")
async def get_pending_notifications(db: Session = Depends(get_db)):
    """Get pending notifications (for admin monitoring)"""
    from app.models.alert import AlertNotification
    
    notifications = db.query(AlertNotification).filter(
        AlertNotification.status == "pending"
    ).order_by(AlertNotification.created_at).limit(100).all()
    
    return notifications
