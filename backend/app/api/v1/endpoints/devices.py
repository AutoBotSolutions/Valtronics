from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.session_sqlite import get_db  # Use SQLite session for local development
from app.schemas.device import (
    Device, DeviceCreate, DeviceUpdate, DeviceWithTelemetry,
    TelemetryData, TelemetryDataCreate,
    DeviceCommand, DeviceCommandCreate, DeviceStats
)
from app.services.device_service import DeviceService, TelemetryService, DeviceCommandService

router = APIRouter()

# Device Endpoints
@router.get("/", response_model=List[Device])
async def get_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all devices with pagination"""
    return DeviceService.get_devices(db, skip=skip, limit=limit)

@router.get("/stats", response_model=DeviceStats)
async def get_device_stats(db: Session = Depends(get_db)):
    """Get device statistics"""
    return DeviceService.get_device_stats(db)

@router.get("/status/{status}", response_model=List[Device])
async def get_devices_by_status(status: str, db: Session = Depends(get_db)):
    """Get devices filtered by status"""
    if status not in ["online", "offline", "error"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be: online, offline, or error")
    return DeviceService.get_devices_by_status(db, status)

@router.get("/{device_id}", response_model=DeviceWithTelemetry)
async def get_device(device_id: int, db: Session = Depends(get_db)):
    """Get a specific device with its latest telemetry and pending commands"""
    device = DeviceService.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Get latest telemetry
    latest_telemetry = TelemetryService.get_latest_telemetry(db, device_id)
    
    # Get pending commands
    pending_commands = DeviceCommandService.get_pending_commands(db, device_id)
    
    return DeviceWithTelemetry(
        **device.__dict__,
        latest_telemetry=latest_telemetry,
        pending_commands=pending_commands
    )

@router.post("/", response_model=Device, status_code=201)
async def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    """Create a new device"""
    # Check if device_id already exists
    existing_device = DeviceService.get_device_by_device_id(db, device.device_id)
    if existing_device:
        raise HTTPException(status_code=400, detail="Device ID already exists")
    
    return DeviceService.create_device(db, device)

@router.put("/{device_id}", response_model=Device)
async def update_device(device_id: int, device: DeviceUpdate, db: Session = Depends(get_db)):
    """Update a device"""
    updated_device = DeviceService.update_device(db, device_id, device)
    if not updated_device:
        raise HTTPException(status_code=404, detail="Device not found")
    return updated_device

@router.delete("/{device_id}", status_code=204)
async def delete_device(device_id: int, db: Session = Depends(get_db)):
    """Delete a device (soft delete)"""
    success = DeviceService.delete_device(db, device_id)
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")

@router.patch("/{device_id}/status", response_model=Device)
async def update_device_status(device_id: int, status: str, db: Session = Depends(get_db)):
    """Update device status"""
    if status not in ["online", "offline", "error"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be: online, offline, or error")
    
    updated_device = DeviceService.update_device_status(db, device_id, status)
    if not updated_device:
        raise HTTPException(status_code=404, detail="Device not found")
    return updated_device

# Telemetry Endpoints
@router.get("/{device_id}/telemetry", response_model=List[TelemetryData])
async def get_device_telemetry(
    device_id: int,
    limit: int = Query(100, ge=1, le=1000),
    hours: int = Query(24, ge=1, le=168),  # Max 7 days
    db: Session = Depends(get_db)
):
    """Get telemetry data for a device"""
    device = DeviceService.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return TelemetryService.get_device_telemetry(db, device_id, limit, hours)

@router.post("/{device_id}/telemetry", response_model=TelemetryData, status_code=201)
async def create_telemetry(
    device_id: int,
    telemetry: TelemetryDataCreate,
    db: Session = Depends(get_db)
):
    """Create telemetry data for a device"""
    device = DeviceService.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    telemetry.device_id = device_id
    return TelemetryService.create_telemetry(db, telemetry)

@router.post("/{device_id}/telemetry/batch", response_model=List[TelemetryData], status_code=201)
async def create_batch_telemetry(
    device_id: int,
    telemetry_data: List[TelemetryDataCreate],
    db: Session = Depends(get_db)
):
    """Create multiple telemetry data points for a device"""
    device = DeviceService.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    created_telemetry = []
    for telemetry in telemetry_data:
        telemetry.device_id = device_id
        created_telemetry.append(TelemetryService.create_telemetry(db, telemetry))
    
    return created_telemetry

# Command Endpoints
@router.post("/{device_id}/commands", response_model=DeviceCommand, status_code=201)
async def create_device_command(
    device_id: int,
    command: DeviceCommandCreate,
    db: Session = Depends(get_db)
):
    """Create a command for a device"""
    device = DeviceService.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    command.device_id = device_id
    return DeviceCommandService.create_command(db, command)

@router.get("/{device_id}/commands", response_model=List[DeviceCommand])
async def get_device_commands(device_id: int, db: Session = Depends(get_db)):
    """Get pending commands for a device"""
    device = DeviceService.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return DeviceCommandService.get_pending_commands(db, device_id)

@router.patch("/commands/{command_id}/status", response_model=DeviceCommand)
async def update_command_status(
    command_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update command status"""
    if status not in ["pending", "sent", "executed", "failed"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid status. Must be: pending, sent, executed, or failed"
        )
    
    updated_command = DeviceCommandService.update_command_status(db, command_id, status)
    if not updated_command:
        raise HTTPException(status_code=404, detail="Command not found")
    
    return updated_command
