from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session_sqlite import Base

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    severity = Column(String(20), nullable=False)  # critical, warning, info
    alert_type = Column(String(50), nullable=False)  # threshold, anomaly, system, device
    status = Column(String(20), default="active")  # active, acknowledged, resolved
    threshold_value = Column(Float)
    actual_value = Column(Float)
    metric_name = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    
    # Relationships
    device = relationship("Device", back_populates="alerts")
    
    def __repr__(self):
        return f"<Alert(id={self.id}, device_id={self.device_id}, severity={self.severity})>"

class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    device_id = Column(Integer, ForeignKey("devices.id"))  # Null for global rules
    device_type = Column(String(50))  # Apply to all devices of this type
    
    # Rule configuration
    metric_name = Column(String(100), nullable=False)
    condition = Column(String(20), nullable=False)  # gt, lt, eq, gte, lte
    threshold_value = Column(Float, nullable=False)
    severity = Column(String(20), default="warning")  # critical, warning, info
    
    # Rule settings
    is_active = Column(Boolean, default=True)
    notification_enabled = Column(Boolean, default=True)
    cooldown_minutes = Column(Integer, default=30)  # Minimum time between alerts
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    device = relationship("Device")
    
    def __repr__(self):
        return f"<AlertRule(id={self.id}, name={self.name}, metric={self.metric_name})>"

class AlertNotification(Base):
    __tablename__ = "alert_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    notification_type = Column(String(50), nullable=False)  # email, sms, webhook, push
    recipient = Column(String(200), nullable=False)  # Email, phone number, webhook URL
    status = Column(String(20), default="pending")  # pending, sent, failed
    sent_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    alert = relationship("Alert")
    
    def __repr__(self):
        return f"<AlertNotification(id={self.id}, type={self.notification_type}, status={self.status})>"
