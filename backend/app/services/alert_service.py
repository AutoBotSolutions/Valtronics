from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.alert import Alert, AlertRule, AlertNotification
from app.models.device import Device
from app.services.device_service import DeviceService, TelemetryService

class AlertService:
    
    @staticmethod
    def create_alert(db: Session, alert_data: Dict[str, Any]) -> Alert:
        """Create a new alert"""
        alert = Alert(**alert_data)
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        # Create notifications if enabled
        AlertService._create_notifications(db, alert)
        
        return alert
    
    @staticmethod
    def get_alerts(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Alert]:
        """Get alerts with optional filtering"""
        query = db.query(Alert)
        
        if status:
            query = query.filter(Alert.status == status)
        
        return query.order_by(desc(Alert.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_alert(db: Session, alert_id: int) -> Optional[Alert]:
        """Get a specific alert by ID"""
        return db.query(Alert).filter(Alert.id == alert_id).first()
    
    @staticmethod
    def get_device_alerts(db: Session, device_id: int, status: Optional[str] = None) -> List[Alert]:
        """Get alerts for a specific device"""
        query = db.query(Alert).filter(Alert.device_id == device_id)
        
        if status:
            query = query.filter(Alert.status == status)
        
        return query.order_by(desc(Alert.created_at)).all()
    
    @staticmethod
    def acknowledge_alert(db: Session, alert_id: int, acknowledged_by: str = "system") -> Optional[Alert]:
        """Acknowledge an alert"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        
        alert.status = "acknowledged"
        alert.acknowledged_at = datetime.utcnow()
        db.commit()
        db.refresh(alert)
        
        return alert
    
    @staticmethod
    def resolve_alert(db: Session, alert_id: int, resolution_note: str = "") -> Optional[Alert]:
        """Resolve an alert"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        
        alert.status = "resolved"
        alert.resolved_at = datetime.utcnow()
        db.commit()
        db.refresh(alert)
        
        return alert
    
    @staticmethod
    def get_active_alerts_count(db: Session) -> Dict[str, int]:
        """Get count of active alerts by severity"""
        counts = {
            "critical": 0,
            "warning": 0,
            "info": 0,
            "total": 0
        }
        
        alerts = db.query(Alert).filter(Alert.status == "active").all()
        
        for alert in alerts:
            counts[alert.severity] = counts.get(alert.severity, 0) + 1
            counts["total"] += 1
        
        return counts
    
    @staticmethod
    def create_alert_rule(db: Session, rule_data: Dict[str, Any]) -> AlertRule:
        """Create a new alert rule"""
        rule = AlertRule(**rule_data)
        db.add(rule)
        db.commit()
        db.refresh(rule)
        
        return rule
    
    @staticmethod
    def get_alert_rules(db: Session, device_id: Optional[int] = None, is_active: bool = True) -> List[AlertRule]:
        """Get alert rules"""
        query = db.query(AlertRule).filter(AlertRule.is_active == is_active)
        
        if device_id:
            # Get rules for specific device and global rules
            query = query.filter(
                or_(
                    AlertRule.device_id == device_id,
                    and_(
                        AlertRule.device_id.is_(None),
                        AlertRule.device_type.in_(
                            db.query(Device.device_type).filter(Device.id == device_id).subquery()
                        )
                    )
                )
            )
        
        return query.all()
    
    @staticmethod
    def check_alert_rules(db: Session, device_id: int, telemetry_data: List) -> List[Alert]:
        """Check telemetry data against alert rules and create alerts if needed"""
        device = DeviceService.get_device(db, device_id)
        if not device:
            return []
        
        # Get applicable alert rules
        rules = AlertService.get_alert_rules(db, device_id)
        new_alerts = []
        
        for rule in rules:
            # Check if we're in cooldown period
            if AlertService._is_in_cooldown(db, device_id, rule):
                continue
            
            # Find matching telemetry data
            matching_data = [t for t in telemetry_data if t.metric_name == rule.metric_name]
            
            for data_point in matching_data:
                if AlertService._evaluate_condition(data_point.metric_value, rule.condition, rule.threshold_value):
                    # Check if similar alert already exists and is active
                    existing_alert = db.query(Alert).filter(
                        and_(
                            Alert.device_id == device_id,
                            Alert.metric_name == rule.metric_name,
                            Alert.severity == rule.severity,
                            Alert.status == "active"
                        )
                    ).first()
                    
                    if not existing_alert:
                        # Create new alert
                        alert_data = {
                            "device_id": device_id,
                            "title": f"{rule.severity.title()}: {rule.metric_name} {rule.condition} {rule.threshold_value}",
                            "description": f"Device {device.name} has {rule.metric_name} of {data_point.metric_value} which {rule.condition} the threshold of {rule.threshold_value}",
                            "severity": rule.severity,
                            "alert_type": "threshold",
                            "threshold_value": rule.threshold_value,
                            "actual_value": data_point.metric_value,
                            "metric_name": rule.metric_name
                        }
                        
                        alert = AlertService.create_alert(db, alert_data)
                        new_alerts.append(alert)
        
        return new_alerts
    
    @staticmethod
    def _evaluate_condition(value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition"""
        if condition == "gt":
            return value > threshold
        elif condition == "lt":
            return value < threshold
        elif condition == "gte":
            return value >= threshold
        elif condition == "lte":
            return value <= threshold
        elif condition == "eq":
            return value == threshold
        else:
            return False
    
    @staticmethod
    def _is_in_cooldown(db: Session, device_id: int, rule: AlertRule) -> bool:
        """Check if alert rule is in cooldown period"""
        cooldown_time = datetime.utcnow() - timedelta(minutes=rule.cooldown_minutes)
        
        recent_alert = db.query(Alert).filter(
            and_(
                Alert.device_id == device_id,
                Alert.metric_name == rule.metric_name,
                Alert.severity == rule.severity,
                Alert.created_at > cooldown_time
            )
        ).first()
        
        return recent_alert is not None
    
    @staticmethod
    def _create_notifications(db: Session, alert: Alert) -> List[AlertNotification]:
        """Create notifications for an alert"""
        notifications = []
        
        # Get notification settings (simplified - would come from user preferences)
        notification_types = ["email"]  # Default to email notifications
        
        for notification_type in notification_types:
            notification = AlertNotification(
                alert_id=alert.id,
                notification_type=notification_type,
                recipient="admin@valtronics.com",  # Would get from user settings
                status="pending"
            )
            db.add(notification)
            notifications.append(notification)
        
        db.commit()
        return notifications
    
    @staticmethod
    def get_alert_statistics(db: Session, hours: int = 24) -> Dict[str, Any]:
        """Get alert statistics for a time period"""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        alerts = db.query(Alert).filter(Alert.created_at >= since).all()
        
        stats = {
            "total_alerts": len(alerts),
            "by_severity": {"critical": 0, "warning": 0, "info": 0},
            "by_status": {"active": 0, "acknowledged": 0, "resolved": 0},
            "by_type": {},
            "alerts_per_hour": {},
            "top_devices": {}
        }
        
        # Categorize alerts
        for alert in alerts:
            # By severity
            stats["by_severity"][alert.severity] = stats["by_severity"].get(alert.severity, 0) + 1
            
            # By status
            stats["by_status"][alert.status] = stats["by_status"].get(alert.status, 0) + 1
            
            # By type
            stats["by_type"][alert.alert_type] = stats["by_type"].get(alert.alert_type, 0) + 1
            
            # By hour
            hour = alert.created_at.hour
            stats["alerts_per_hour"][hour] = stats["alerts_per_hour"].get(hour, 0) + 1
            
            # By device
            stats["top_devices"][alert.device_id] = stats["top_devices"].get(alert.device_id, 0) + 1
        
        # Sort top devices
        stats["top_devices"] = dict(sorted(stats["top_devices"].items(), key=lambda x: x[1], reverse=True)[:10])
        
        return stats

class NotificationService:
    
    @staticmethod
    def send_notifications(db: Session, alert_id: int) -> bool:
        """Send all pending notifications for an alert"""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return False
        
        pending_notifications = db.query(AlertNotification).filter(
            and_(
                AlertNotification.alert_id == alert_id,
                AlertNotification.status == "pending"
            )
        ).all()
        
        success = True
        
        for notification in pending_notifications:
            try:
                # Send notification based on type
                if notification.notification_type == "email":
                    NotificationService._send_email_notification(alert, notification)
                elif notification.notification_type == "webhook":
                    NotificationService._send_webhook_notification(alert, notification)
                # Add other notification types as needed
                
                notification.status = "sent"
                notification.sent_at = datetime.utcnow()
                
            except Exception as e:
                notification.status = "failed"
                notification.error_message = str(e)
                success = False
            
            db.commit()
        
        return success
    
    @staticmethod
    def _send_email_notification(alert: Alert, notification: AlertNotification):
        """Send email notification (placeholder implementation)"""
        # In a real implementation, this would use an email service
        print(f"Sending email to {notification.recipient}: {alert.title}")
        # Simulate email sending
        import time
        time.sleep(0.1)
    
    @staticmethod
    def _send_webhook_notification(alert: Alert, notification: AlertNotification):
        """Send webhook notification (placeholder implementation)"""
        # In a real implementation, this would make HTTP request to webhook URL
        print(f"Sending webhook to {notification.recipient}: {alert.title}")
        # Simulate webhook call
        import time
        time.sleep(0.1)
