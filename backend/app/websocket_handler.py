from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import asyncio
import logging
from datetime import datetime
from app.core.config import settings
from app.db.session import SessionLocal
from app.services.device_service import DeviceService

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.device_subscribers: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, device_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if device_id:
            if device_id not in self.device_subscribers:
                self.device_subscribers[device_id] = []
            self.device_subscribers[device_id].append(websocket)
            
            logger.info(f"WebSocket connected for device {device_id}")
        else:
            logger.info("General WebSocket connected")

    def disconnect(self, websocket: WebSocket, device_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if device_id and device_id in self.device_subscribers:
            if websocket in self.device_subscribers[device_id]:
                self.device_subscribers[device_id].remove(websocket)
            if not self.device_subscribers[device_id]:
                del self.device_subscribers[device_id]
        
        logger.info(f"WebSocket disconnected for device {device_id or 'general'}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast(self, message: Dict):
        if not self.active_connections:
            return
            
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_to_device_subscribers(self, device_id: str, message: Dict):
        if device_id not in self.device_subscribers:
            return
            
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.device_subscribers[device_id]:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending to device subscriber: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection, device_id)

    async def send_heartbeat(self):
        """Send periodic heartbeat to all connected clients"""
        heartbeat = {
            "type": "heartbeat",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "alive"
        }
        await self.broadcast(heartbeat)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, device_id: str = None):
    await manager.connect(websocket, device_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_websocket_message(message, websocket, device_id)
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    json.dumps({"error": "Invalid JSON format"}), 
                    websocket
                )
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await manager.send_personal_message(
                    json.dumps({"error": "Internal server error"}), 
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, device_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, device_id)

async def handle_websocket_message(message: Dict, websocket: WebSocket, device_id: str = None):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")
    
    if message_type == "ping":
        response = {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.send_personal_message(json.dumps(response), websocket)
    
    elif message_type == "subscribe_device":
        # Subscribe to specific device updates
        target_device_id = message.get("device_id")
        if target_device_id:
            # Add connection to device subscribers
            if target_device_id not in manager.device_subscribers:
                manager.device_subscribers[target_device_id] = []
            if websocket not in manager.device_subscribers[target_device_id]:
                manager.device_subscribers[target_device_id].append(websocket)
            
            await manager.send_personal_message(
                json.dumps({
                    "type": "subscription_confirmed",
                    "device_id": target_device_id
                }), 
                websocket
            )
    
    elif message_type == "unsubscribe_device":
        # Unsubscribe from specific device updates
        target_device_id = message.get("device_id")
        if target_device_id and target_device_id in manager.device_subscribers:
            if websocket in manager.device_subscribers[target_device_id]:
                manager.device_subscribers[target_device_id].remove(websocket)
            
            await manager.send_personal_message(
                json.dumps({
                    "type": "unsubscription_confirmed",
                    "device_id": target_device_id
                }), 
                websocket
            )
    
    elif message_type == "get_device_status":
        # Get current device status
        target_device_id = message.get("device_id")
        if target_device_id:
            db = SessionLocal()
            try:
                device = DeviceService.get_device(db, target_device_id)
                if device:
                    status_message = {
                        "type": "device_status",
                        "device_id": target_device_id,
                        "status": device.status,
                        "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await manager.send_personal_message(json.dumps(status_message), websocket)
                else:
                    await manager.send_personal_message(
                        json.dumps({"error": "Device not found"}), 
                        websocket
                    )
            finally:
                db.close()
    
    else:
        await manager.send_personal_message(
            json.dumps({"error": f"Unknown message type: {message_type}"}), 
            websocket
        )

async def broadcast_device_update(device_id: int, updates: Dict):
    """Broadcast device updates to all subscribers"""
    message = {
        "type": "device_update",
        "device_id": device_id,
        "updates": updates,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast_to_device_subscribers(str(device_id), message)
    await manager.broadcast(message)

async def broadcast_telemetry_data(device_id: int, telemetry_data: Dict):
    """Broadcast new telemetry data to subscribers"""
    message = {
        "type": "telemetry_update",
        "device_id": device_id,
        "data": telemetry_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast_to_device_subscribers(str(device_id), message)

async def broadcast_alert(alert_data: Dict):
    """Broadcast alert to all connected clients"""
    message = {
        "type": "alert",
        "alert": alert_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast(message)

async def broadcast_system_notification(notification: Dict):
    """Broadcast system-wide notification"""
    message = {
        "type": "system_notification",
        "notification": notification,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.broadcast(message)

# Background task for heartbeat
async def heartbeat_task():
    """Send periodic heartbeat to maintain connections"""
    while True:
        await asyncio.sleep(settings.WS_HEARTBEAT_INTERVAL)
        await manager.send_heartbeat()

# Start heartbeat task when the module is imported
def start_heartbeat_task():
    """Start the heartbeat background task"""
    import asyncio
    asyncio.create_task(heartbeat_task())
