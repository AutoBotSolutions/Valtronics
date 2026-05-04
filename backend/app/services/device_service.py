from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.device import Device, TelemetryData, DeviceCommand
from app.schemas.device import DeviceCreate, DeviceUpdate, TelemetryDataCreate, DeviceCommandCreate

class DeviceService:
    
    @staticmethod
    def get_device(db: Session, device_id: int) -> Optional[Device]:
        """Get a single device by ID"""
        return db.query(Device).filter(Device.id == device_id, Device.is_active == True).first()
    
    @staticmethod
    def get_device_by_device_id(db: Session, device_identifier: str) -> Optional[Device]:
        """Get a device by its unique device_id"""
        return db.query(Device).filter(
            Device.device_id == device_identifier, 
            Device.is_active == True
        ).first()
    
    @staticmethod
    def get_devices(db: Session, skip: int = 0, limit: int = 100) -> List[Device]:
        """Get all active devices with pagination"""
        return db.query(Device).filter(Device.is_active == True).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_device(db: Session, device: DeviceCreate) -> Device:
        """Create a new device"""
        db_device = Device(**device.dict())
        db.add(db_device)
        db.commit()
        db.refresh(db_device)
        return db_device
    
    @staticmethod
    def update_device(db: Session, device_id: int, device: DeviceUpdate) -> Optional[Device]:
        """Update an existing device"""
        db_device = db.query(Device).filter(Device.id == device_id, Device.is_active == True).first()
        if not db_device:
            return None
        
        update_data = device.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_device, field, value)
        
        db_device.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_device)
        return db_device
    
    @staticmethod
    def delete_device(db: Session, device_id: int) -> bool:
        """Soft delete a device"""
        db_device = db.query(Device).filter(Device.id == device_id, Device.is_active == True).first()
        if not db_device:
            return False
        
        db_device.is_active = False
        db_device.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def update_device_status(db: Session, device_id: int, status: str) -> Optional[Device]:
        """Update device status and last_seen timestamp"""
        db_device = db.query(Device).filter(Device.id == device_id, Device.is_active == True).first()
        if not db_device:
            return None
        
        db_device.status = status
        db_device.last_seen = datetime.utcnow()
        db_device.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_device)
        return db_device
    
    @staticmethod
    def get_devices_by_status(db: Session, status: str) -> List[Device]:
        """Get devices filtered by status"""
        return db.query(Device).filter(
            Device.status == status, 
            Device.is_active == True
        ).all()
    
    @staticmethod
    def get_device_stats(db: Session) -> Dict[str, Any]:
        """Get device statistics"""
        total = db.query(Device).filter(Device.is_active == True).count()
        online = db.query(Device).filter(Device.status == "online", Device.is_active == True).count()
        offline = db.query(Device).filter(Device.status == "offline", Device.is_active == True).count()
        error = db.query(Device).filter(Device.status == "error", Device.is_active == True).count()
        
        # Devices by type
        devices_by_type = db.query(
            Device.device_type, 
            func.count(Device.id)
        ).filter(Device.is_active == True).group_by(Device.device_type).all()
        
        return {
            "total_devices": total,
            "online_devices": online,
            "offline_devices": offline,
            "error_devices": error,
            "devices_by_type": dict(devices_by_type)
        }

class TelemetryService:
    
    @staticmethod
    def create_telemetry(db: Session, telemetry: TelemetryDataCreate) -> TelemetryData:
        """Create new telemetry data"""
        db_telemetry = TelemetryData(**telemetry.dict())
        db.add(db_telemetry)
        db.commit()
        db.refresh(db_telemetry)
        return db_telemetry
    
    @staticmethod
    def get_device_telemetry(
        db: Session, 
        device_id: int, 
        limit: int = 100,
        hours: int = 24
    ) -> List[TelemetryData]:
        """Get telemetry data for a device"""
        since = datetime.utcnow() - timedelta(hours=hours)
        return db.query(TelemetryData).filter(
            TelemetryData.device_id == device_id,
            TelemetryData.timestamp >= since
        ).order_by(desc(TelemetryData.timestamp)).limit(limit).all()
    
    @staticmethod
    def get_latest_telemetry(db: Session, device_id: int) -> List[TelemetryData]:
        """Get latest telemetry data for each metric of a device"""
        # Subquery to get the latest timestamp for each metric
        latest_metrics = db.query(
            TelemetryData.metric_name,
            func.max(TelemetryData.timestamp).label('latest_timestamp')
        ).filter(TelemetryData.device_id == device_id).group_by(TelemetryData.metric_name).subquery()
        
        return db.query(TelemetryData).join(
            latest_metrics,
            (TelemetryData.metric_name == latest_metrics.c.metric_name) &
            (TelemetryData.timestamp == latest_metrics.c.latest_timestamp)
        ).filter(TelemetryData.device_id == device_id).all()

class DeviceCommandService:
    
    @staticmethod
    def create_command(db: Session, command: DeviceCommandCreate) -> DeviceCommand:
        """Create a new device command"""
        db_command = DeviceCommand(**command.dict())
        db.add(db_command)
        db.commit()
        db.refresh(db_command)
        return db_command
    
    @staticmethod
    def get_pending_commands(db: Session, device_id: int) -> List[DeviceCommand]:
        """Get pending commands for a device"""
        return db.query(DeviceCommand).filter(
            DeviceCommand.device_id == device_id,
            DeviceCommand.status == "pending"
        ).order_by(DeviceCommand.created_at).all()
    
    @staticmethod
    def update_command_status(
        db: Session, 
        command_id: int, 
        status: str
    ) -> Optional[DeviceCommand]:
        """Update command status"""
        db_command = db.query(DeviceCommand).filter(DeviceCommand.id == command_id).first()
        if not db_command:
            return None
        
        db_command.status = status
        if status in ["executed", "failed"]:
            db_command.executed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_command)
        return db_command
