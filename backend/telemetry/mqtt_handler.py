import paho.mqtt.client as mqtt
import json
import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import SessionLocal
from app.services.device_service import DeviceService, TelemetryService
from app.websocket_handler import broadcast_device_update, broadcast_telemetry_data

logger = logging.getLogger(__name__)

class MQTTHandler:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_publish = self.on_publish
        
        # Set authentication if configured
        if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
            self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        
        self.connected = False
        self.db = SessionLocal()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info("Connected to MQTT broker")
            
            # Subscribe to device topics
            self.subscribe_to_topics()
        else:
            logger.error(f"Failed to connect to MQTT broker: {rc}")

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        logger.warning(f"Disconnected from MQTT broker: {rc}")

    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            logger.debug(f"Received message on topic {topic}: {payload}")
            
            # Parse topic to determine message type
            topic_parts = topic.split('/')
            
            if len(topic_parts) >= 2:
                device_id = topic_parts[1]
                message_type = topic_parts[2] if len(topic_parts) > 2 else None
                
                self.handle_device_message(device_id, message_type, payload)
            
        except Exception as e:
            logger.error(f"Error handling MQTT message: {e}")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        logger.info(f"Subscribed to topic with mid {mid}")

    def on_publish(self, client, userdata, mid):
        logger.debug(f"Published message with mid {mid}")

    def subscribe_to_topics(self):
        """Subscribe to relevant MQTT topics"""
        topics = [
            ("valtronics/+/telemetry", 1),  # Device telemetry
            ("valtronics/+/status", 1),     # Device status updates
            ("valtronics/+/heartbeat", 1),  # Device heartbeats
            ("valtronics/+/alert", 1),      # Device alerts
            ("valtronics/+/response", 1),   # Command responses
        ]
        
        for topic, qos in topics:
            self.client.subscribe(topic, qos)
            logger.info(f"Subscribed to topic: {topic}")

    def handle_device_message(self, device_id: str, message_type: str, payload: str):
        """Handle messages from devices"""
        try:
            data = json.loads(payload)
            
            if message_type == "telemetry":
                self.handle_telemetry(device_id, data)
            elif message_type == "status":
                self.handle_status_update(device_id, data)
            elif message_type == "heartbeat":
                self.handle_heartbeat(device_id, data)
            elif message_type == "alert":
                self.handle_alert(device_id, data)
            elif message_type == "response":
                self.handle_command_response(device_id, data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON payload: {payload}")
        except Exception as e:
            logger.error(f"Error processing device message: {e}")

    def handle_telemetry(self, device_id: str, data: Dict[str, Any]):
        """Handle telemetry data from device"""
        try:
            # Find device by device_id
            device = DeviceService.get_device_by_device_id(self.db, device_id)
            if not device:
                logger.warning(f"Telemetry from unknown device: {device_id}")
                return
            
            # Process telemetry data
            timestamp = datetime.fromisoformat(data.get("timestamp", datetime.utcnow().isoformat()))
            
            # Handle single metric or batch metrics
            if "metrics" in data:
                # Batch telemetry
                for metric_data in data["metrics"]:
                    telemetry = TelemetryService.create_telemetry(self.db, {
                        "device_id": device.id,
                        "metric_name": metric_data["name"],
                        "metric_value": metric_data["value"],
                        "unit": metric_data.get("unit"),
                    })
                    
                    # Broadcast to WebSocket clients
                    import asyncio
                    asyncio.create_task(broadcast_telemetry_data(device.id, {
                        "metric_name": metric_data["name"],
                        "metric_value": metric_data["value"],
                        "unit": metric_data.get("unit"),
                        "timestamp": timestamp.isoformat()
                    }))
            else:
                # Single telemetry point
                telemetry = TelemetryService.create_telemetry(self.db, {
                    "device_id": device.id,
                    "metric_name": data["name"],
                    "metric_value": data["value"],
                    "unit": data.get("unit"),
                })
                
                # Broadcast to WebSocket clients
                import asyncio
                asyncio.create_task(broadcast_telemetry_data(device.id, {
                    "metric_name": data["name"],
                    "metric_value": data["value"],
                    "unit": data.get("unit"),
                    "timestamp": timestamp.isoformat()
                }))
            
            # Update device last_seen
            DeviceService.update_device_status(self.db, device.id, device.status)
            
        except Exception as e:
            logger.error(f"Error handling telemetry: {e}")

    def handle_status_update(self, device_id: str, data: Dict[str, Any]):
        """Handle device status updates"""
        try:
            device = DeviceService.get_device_by_device_id(self.db, device_id)
            if not device:
                logger.warning(f"Status update from unknown device: {device_id}")
                return
            
            status = data.get("status")
            if status:
                # Update device status
                updated_device = DeviceService.update_device_status(self.db, device.id, status)
                
                # Broadcast status update
                import asyncio
                asyncio.create_task(broadcast_device_update(device.id, {
                    "status": status,
                    "last_seen": datetime.utcnow().isoformat()
                }))
                
                logger.info(f"Device {device_id} status updated to: {status}")
            
        except Exception as e:
            logger.error(f"Error handling status update: {e}")

    def handle_heartbeat(self, device_id: str, data: Dict[str, Any]):
        """Handle device heartbeat messages"""
        try:
            device = DeviceService.get_device_by_device_id(self.db, device_id)
            if not device:
                logger.warning(f"Heartbeat from unknown device: {device_id}")
                return
            
            # Update last_seen timestamp
            updated_device = DeviceService.update_device_status(self.db, device.id, device.status)
            
            # Broadcast heartbeat
            import asyncio
            asyncio.create_task(broadcast_device_update(device.id, {
                "last_seen": datetime.utcnow().isoformat(),
                "heartbeat": True
            }))
            
        except Exception as e:
            logger.error(f"Error handling heartbeat: {e}")

    def handle_alert(self, device_id: str, data: Dict[str, Any]):
        """Handle device alerts"""
        try:
            device = DeviceService.get_device_by_device_id(self.db, device_id)
            if not device:
                logger.warning(f"Alert from unknown device: {device_id}")
                return
            
            # Process alert data
            alert_data = {
                "device_id": device.id,
                "device_name": device.name,
                "alert_type": data.get("type", "unknown"),
                "severity": data.get("severity", "medium"),
                "message": data.get("message", ""),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Broadcast alert to all clients
            from app.websocket_handler import broadcast_alert
            import asyncio
            asyncio.create_task(broadcast_alert(alert_data))
            
            logger.warning(f"Alert from device {device_id}: {data.get('message', 'No message')}")
            
        except Exception as e:
            logger.error(f"Error handling alert: {e}")

    def handle_command_response(self, device_id: str, data: Dict[str, Any]):
        """Handle responses to device commands"""
        try:
            device = DeviceService.get_device_by_device_id(self.db, device_id)
            if not device:
                logger.warning(f"Command response from unknown device: {device_id}")
                return
            
            command_id = data.get("command_id")
            status = data.get("status", "unknown")
            result = data.get("result", "")
            
            # Update command status in database
            if command_id:
                from app.services.device_service import DeviceCommandService
                updated_command = DeviceCommandService.update_command_status(
                    self.db, command_id, status
                )
                
                if updated_command:
                    # Broadcast command response
                    import asyncio
                    asyncio.create_task(broadcast_device_update(device.id, {
                        "command_response": {
                            "command_id": command_id,
                            "status": status,
                            "result": result
                        }
                    }))
            
            logger.info(f"Command response from device {device_id}: {status}")
            
        except Exception as e:
            logger.error(f"Error handling command response: {e}")

    def send_command(self, device_id: str, command: str, parameters: Dict = None):
        """Send command to device via MQTT"""
        if not self.connected:
            logger.error("Not connected to MQTT broker")
            return False
        
        topic = f"valtronics/{device_id}/command"
        payload = json.dumps({
            "command": command,
            "parameters": parameters or {},
            "timestamp": datetime.utcnow().isoformat()
        })
        
        try:
            result = self.client.publish(topic, payload, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Command sent to device {device_id}: {command}")
                return True
            else:
                logger.error(f"Failed to send command to device {device_id}: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return False

    def start(self):
        """Start MQTT client"""
        try:
            self.client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
            self.client.loop_start()
            logger.info("MQTT client started")
        except Exception as e:
            logger.error(f"Failed to start MQTT client: {e}")

    def stop(self):
        """Stop MQTT client"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT client stopped")
        except Exception as e:
            logger.error(f"Error stopping MQTT client: {e}")
        finally:
            self.db.close()

# Global MQTT handler instance
mqtt_handler = MQTTHandler()

def start_mqtt_client():
    """Start the MQTT client"""
    mqtt_handler.start()

def stop_mqtt_client():
    """Stop the MQTT client"""
    mqtt_handler.stop()

def get_mqtt_handler():
    """Get the global MQTT handler instance"""
    return mqtt_handler
