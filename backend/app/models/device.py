from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session_sqlite import Base

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    device_id = Column(String(100), unique=True, index=True, nullable=False)
    device_type = Column(String(50), nullable=False)
    manufacturer = Column(String(100))
    model = Column(String(100))
    firmware_version = Column(String(50))
    location = Column(String(200))
    status = Column(String(20), default="offline")  # online, offline, error
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_seen = Column(DateTime(timezone=True))
    
    # Relationships
    telemetry_data = relationship("TelemetryData", back_populates="device", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="device", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Device(id={self.id}, device_id={self.device_id}, status={self.status})>"

class TelemetryData(Base):
    __tablename__ = "telemetry_data"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    unit = Column(String(20))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    device = relationship("Device", back_populates="telemetry_data")
    
    def __repr__(self):
        return f"<TelemetryData(device_id={self.device_id}, metric={self.metric_name}, value={self.metric_value})>"

class DeviceCommand(Base):
    __tablename__ = "device_commands"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    command = Column(String(200), nullable=False)
    parameters = Column(Text)  # JSON string
    status = Column(String(20), default="pending")  # pending, sent, executed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    executed_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<DeviceCommand(device_id={self.device_id}, command={self.command}, status={self.status})>"
