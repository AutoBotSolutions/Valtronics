from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Device Schemas
class DeviceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    device_id: str = Field(..., min_length=1, max_length=100)
    device_type: str = Field(..., min_length=1, max_length=50)
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    firmware_version: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=200)

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    device_type: Optional[str] = Field(None, min_length=1, max_length=50)
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    firmware_version: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=200)
    status: Optional[str] = Field(None, pattern="^(online|offline|error)$")

class Device(DeviceBase):
    id: int
    status: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_seen: Optional[datetime]
    
    class Config:
        from_attributes = True

# Telemetry Schemas
class TelemetryDataBase(BaseModel):
    metric_name: str = Field(..., min_length=1, max_length=100)
    metric_value: float
    unit: Optional[str] = Field(None, max_length=20)

class TelemetryDataCreate(TelemetryDataBase):
    device_id: int

class TelemetryData(TelemetryDataBase):
    id: int
    device_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Device Command Schemas
class DeviceCommandBase(BaseModel):
    command: str = Field(..., min_length=1, max_length=200)
    parameters: Optional[Dict[str, Any]] = None

class DeviceCommandCreate(DeviceCommandBase):
    device_id: int

class DeviceCommand(DeviceCommandBase):
    id: int
    device_id: int
    status: str
    created_at: datetime
    executed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Device Statistics
class DeviceStats(BaseModel):
    total_devices: int
    online_devices: int
    offline_devices: int
    error_devices: int
    devices_by_type: Dict[str, int]

# Device with Telemetry
class DeviceWithTelemetry(Device):
    latest_telemetry: List[TelemetryData] = []
    pending_commands: List[DeviceCommand] = []
