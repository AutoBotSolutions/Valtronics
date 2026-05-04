import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.services.alert_service import AlertService, NotificationService
from app.services.device_service import DeviceService, TelemetryService
from app.models.alert import Alert, AlertRule, AlertNotification

class TestAlertService:
    """Test alert service"""
    
    def test_create_alert(self, db_session: Session, sample_device_data, sample_alert_data):
        """Test creating an alert"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        alert_data = {**sample_alert_data, "device_id": device.id}
        alert = AlertService.create_alert(db_session, alert_data)
        
        assert alert.device_id == device.id
        assert alert.title == sample_alert_data["title"]
        assert alert.severity == sample_alert_data["severity"]
        assert alert.status == "active"
        assert alert.created_at is not None
    
    def test_get_alerts(self, db_session: Session, sample_device_data, sample_alert_data):
        """Test getting alerts"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create multiple alerts
        for i in range(3):
            alert_data = {**sample_alert_data, "device_id": device.id, "title": f"Alert {i}"}
            AlertService.create_alert(db_session, alert_data)
        
        alerts = AlertService.get_alerts(db_session)
        assert len(alerts) >= 3
        assert all(alert.device_id == device.id for alert in alerts)
    
    def test_get_alert_by_id(self, db_session: Session, sample_device_data, sample_alert_data):
        """Test getting a specific alert"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        alert_data = {**sample_alert_data, "device_id": device.id}
        created_alert = AlertService.create_alert(db_session, alert_data)
        
        retrieved_alert = AlertService.get_alert(db_session, created_alert.id)
        
        assert retrieved_alert is not None
        assert retrieved_alert.id == created_alert.id
        assert retrieved_alert.title == sample_alert_data["title"]
    
    def test_get_device_alerts(self, db_session: Session, sample_device_data, sample_alert_data):
        """Test getting alerts for a specific device"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create alerts for this device
        for i in range(2):
            alert_data = {**sample_alert_data, "device_id": device.id, "title": f"Device Alert {i}"}
            AlertService.create_alert(db_session, alert_data)
        
        # Create alert for another device
        device2_data = {**sample_device_data, "device_id": "TEST_002"}
        device2 = DeviceService.create_device(db_session, device2_data)
        alert_data = {**sample_alert_data, "device_id": device2.id, "title": "Other Device Alert"}
        AlertService.create_alert(db_session, alert_data)
        
        device_alerts = AlertService.get_device_alerts(db_session, device.id)
        
        assert len(device_alerts) == 2
        assert all(alert.device_id == device.id for alert in device_alerts)
    
    def test_acknowledge_alert(self, db_session: Session, sample_device_data, sample_alert_data):
        """Test acknowledging an alert"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        alert_data = {**sample_alert_data, "device_id": device.id}
        alert = AlertService.create_alert(db_session, alert_data)
        
        acknowledged_alert = AlertService.acknowledge_alert(db_session, alert.id)
        
        assert acknowledged_alert is not None
        assert acknowledged_alert.status == "acknowledged"
        assert acknowledged_alert.acknowledged_at is not None
    
    def test_resolve_alert(self, db_session: Session, sample_device_data, sample_alert_data):
        """Test resolving an alert"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        alert_data = {**sample_alert_data, "device_id": device.id}
        alert = AlertService.create_alert(db_session, alert_data)
        
        resolved_alert = AlertService.resolve_alert(db_session, alert.id, "Issue fixed")
        
        assert resolved_alert is not None
        assert resolved_alert.status == "resolved"
        assert resolved_alert.resolved_at is not None
    
    def test_get_active_alerts_count(self, db_session: Session, sample_device_data, sample_alert_data):
        """Test getting active alerts count"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create alerts with different severities
        severities = ["critical", "warning", "info"]
        for severity in severities:
            alert_data = {**sample_alert_data, "device_id": device.id, "severity": severity, "title": f"{severity.title()} Alert"}
            AlertService.create_alert(db_session, alert_data)
        
        # Create a resolved alert
        alert_data = {**sample_alert_data, "device_id": device.id, "title": "Resolved Alert"}
        alert = AlertService.create_alert(db_session, alert_data)
        AlertService.resolve_alert(db_session, alert.id)
        
        counts = AlertService.get_active_alerts_count(db_session)
        
        assert counts["total"] == 3
        assert counts["critical"] == 1
        assert counts["warning"] == 1
        assert counts["info"] == 1
    
    def test_create_alert_rule(self, db_session: Session, sample_device_data, sample_alert_rule_data):
        """Test creating an alert rule"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        rule_data = {**sample_alert_rule_data, "device_id": device.id}
        rule = AlertService.create_alert_rule(db_session, rule_data)
        
        assert rule.device_id == device.id
        assert rule.name == sample_alert_rule_data["name"]
        assert rule.metric_name == sample_alert_rule_data["metric_name"]
        assert rule.condition == sample_alert_rule_data["condition"]
        assert rule.is_active is True
    
    def test_get_alert_rules(self, db_session: Session, sample_device_data, sample_alert_rule_data):
        """Test getting alert rules"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create device-specific rule
        device_rule_data = {**sample_alert_rule_data, "device_id": device.id, "name": "Device Rule"}
        AlertService.create_alert_rule(db_session, device_rule_data)
        
        # Create global rule
        global_rule_data = {**sample_alert_rule_data, "device_id": None, "device_type": sample_device_data["device_type"], "name": "Global Rule"}
        AlertService.create_alert_rule(db_session, global_rule_data)
        
        # Get device-specific rules
        device_rules = AlertService.get_alert_rules(db_session, device.id)
        assert len(device_rules) >= 2  # Should include both device-specific and global rules
        
        # Get all active rules
        all_rules = AlertService.get_alert_rules(db_session, is_active=True)
        assert len(all_rules) >= 2
    
    def test_check_alert_rules(self, db_session: Session, sample_device_data, sample_telemetry_data, sample_alert_rule_data):
        """Test checking alert rules against telemetry"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create alert rule
        rule_data = {**sample_alert_rule_data, "device_id": device.id, "metric_name": sample_telemetry_data["metric_name"]}
        rule = AlertService.create_alert_rule(db_session, rule_data)
        
        # Create telemetry that should trigger the alert
        telemetry_list = []
        for i in range(3):
            telemetry = TelemetryService.create_telemetry(db_session, {
                **sample_telemetry_data,
                "device_id": device.id,
                "metric_value": rule.threshold_value + 10  # Above threshold
            })
            telemetry_list.append(telemetry)
        
        # Check alert rules
        new_alerts = AlertService.check_alert_rules(db_session, device.id, telemetry_list)
        
        assert len(new_alerts) > 0
        assert all(alert.device_id == device.id for alert in new_alerts)
        assert all(alert.metric_name == rule.metric_name for alert in new_alerts)
    
    def test_evaluate_condition(self):
        """Test condition evaluation logic"""
        # Greater than
        assert AlertService._evaluate_condition(25.0, "gt", 20.0) is True
        assert AlertService._evaluate_condition(20.0, "gt", 20.0) is False
        assert AlertService._evaluate_condition(15.0, "gt", 20.0) is False
        
        # Less than
        assert AlertService._evaluate_condition(15.0, "lt", 20.0) is True
        assert AlertService._evaluate_condition(20.0, "lt", 20.0) is False
        assert AlertService._evaluate_condition(25.0, "lt", 20.0) is False
        
        # Greater than or equal
        assert AlertService._evaluate_condition(25.0, "gte", 20.0) is True
        assert AlertService._evaluate_condition(20.0, "gte", 20.0) is True
        assert AlertService._evaluate_condition(15.0, "gte", 20.0) is False
        
        # Less than or equal
        assert AlertService._evaluate_condition(15.0, "lte", 20.0) is True
        assert AlertService._evaluate_condition(20.0, "lte", 20.0) is True
        assert AlertService._evaluate_condition(25.0, "lte", 20.0) is False
        
        # Equal
        assert AlertService._evaluate_condition(20.0, "eq", 20.0) is True
        assert AlertService._evaluate_condition(25.0, "eq", 20.0) is False
    
    def test_is_in_cooldown(self, db_session: Session, sample_device_data, sample_alert_data, sample_alert_rule_data):
        """Test cooldown period logic"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create alert rule with short cooldown
        rule_data = {**sample_alert_rule_data, "device_id": device.id, "cooldown_minutes": 5}
        rule = AlertService.create_alert_rule(db_session, rule_data)
        
        # Create recent alert
        alert_data = {**sample_alert_data, "device_id": device.id, "metric_name": rule.metric_name}
        alert = AlertService.create_alert(db_session, alert_data)
        
        # Should be in cooldown
        is_in_cooldown = AlertService._is_in_cooldown(db_session, device.id, rule)
        assert is_in_cooldown is True
        
        # Simulate time passing
        alert.created_at = datetime.utcnow() - timedelta(minutes=10)
        db_session.commit()
        
        # Should not be in cooldown anymore
        is_in_cooldown = AlertService._is_in_cooldown(db_session, device.id, rule)
        assert is_in_cooldown is False
    
    def test_get_alert_statistics(self, db_session: Session, sample_device_data, sample_alert_data):
        """Test getting alert statistics"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create alerts with different severities and types
        severities = ["critical", "warning", "info"]
        alert_types = ["threshold", "anomaly", "system"]
        
        for severity in severities:
            for alert_type in alert_types:
                alert_data = {
                    **sample_alert_data,
                    "device_id": device.id,
                    "severity": severity,
                    "alert_type": alert_type,
                    "title": f"{severity} {alert_type} alert"
                }
                AlertService.create_alert(db_session, alert_data)
        
        stats = AlertService.get_alert_statistics(db_session, hours=24)
        
        assert "total_alerts" in stats
        assert "by_severity" in stats
        assert "by_status" in stats
        assert "by_type" in stats
        
        assert stats["total_alerts"] == 9  # 3 severities * 3 types
        assert stats["by_severity"]["critical"] == 3
        assert stats["by_severity"]["warning"] == 3
        assert stats["by_severity"]["info"] == 3
        assert stats["by_type"]["threshold"] == 3
        assert stats["by_type"]["anomaly"] == 3
        assert stats["by_type"]["system"] == 3

class TestNotificationService:
    """Test notification service"""
    
    def test_send_notifications(self, db_session: Session, sample_device_data, sample_alert_data):
        """Test sending notifications for an alert"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        alert_data = {**sample_alert_data, "device_id": device.id}
        alert = AlertService.create_alert(db_session, alert_data)
        
        # Send notifications
        success = NotificationService.send_notifications(db_session, alert.id)
        
        assert success is True  # Should succeed even with mock implementation
        
        # Check that notifications were created
        notifications = db_session.query(AlertNotification).filter(
            AlertNotification.alert_id == alert.id
        ).all()
        
        assert len(notifications) > 0
        assert all(notification.alert_id == alert.id for notification in notifications)
    
    def test_send_email_notification(self, db_session: Session, sample_device_data, sample_alert_data):
        """Test email notification sending (mock)"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        alert_data = {**sample_alert_data, "device_id": device.id}
        alert = AlertService.create_alert(db_session, alert_data)
        
        # Create notification
        notification = AlertNotification(
            alert_id=alert.id,
            notification_type="email",
            recipient="test@example.com"
        )
        db_session.add(notification)
        db_session.commit()
        
        # This should not raise an exception (mock implementation)
        try:
            NotificationService._send_email_notification(alert, notification)
        except Exception as e:
            pytest.fail(f"Email notification failed: {e}")
    
    def test_send_webhook_notification(self, db_session: Session, sample_device_data, sample_alert_data):
        """Test webhook notification sending (mock)"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        alert_data = {**sample_alert_data, "device_id": device.id}
        alert = AlertService.create_alert(db_session, alert_data)
        
        # Create notification
        notification = AlertNotification(
            alert_id=alert.id,
            notification_type="webhook",
            recipient="https://hooks.slack.com/test"
        )
        db_session.add(notification)
        db_session.commit()
        
        # This should not raise an exception (mock implementation)
        try:
            NotificationService._send_webhook_notification(alert, notification)
        except Exception as e:
            pytest.fail(f"Webhook notification failed: {e}")
