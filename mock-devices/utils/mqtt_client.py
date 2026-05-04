"""
MQTT Client Utilities for Mock Devices

This module provides enhanced MQTT client functionality for mock devices.
"""

import asyncio
import json
import logging
import paho.mqtt.client as mqtt
from typing import Dict, Any, Callable, Optional
from datetime import datetime
import time


class EnhancedMQTTClient:
    """Enhanced MQTT client with reconnection and error handling"""
    
    def __init__(self, broker_host: str, broker_port: int = 1883, 
                 username: str = None, password: str = None,
                 keepalive: int = 60, qos: int = 1):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.keepalive = keepalive
        self.qos = qos
        
        self.client = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 5
        
        self.message_callbacks = {}
        self.logger = logging.getLogger("mqtt_client")
        
        # Statistics
        self.messages_sent = 0
        self.messages_received = 0
        self.errors = 0
        self.last_activity = None
    
    async def connect(self) -> bool:
        """Connect to MQTT broker with retry logic"""
        try:
            self.client = mqtt.Client()
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_publish = self._on_publish
            self.client.on_message = self._on_message
            self.client.on_subscribe = self._on_subscribe
            
            # Set credentials if provided
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            # Connect
            result = self.client.connect(
                self.broker_host,
                self.broker_port,
                self.keepalive
            )
            
            # Start loop
            self.client.loop_start()
            
            # Wait for connection
            for i in range(10):
                if self.connected:
                    self.logger.info(f"Connected to MQTT broker {self.broker_host}:{self.broker_port}")
                    return True
                await asyncio.sleep(0.5)
            
            raise Exception("Connection timeout")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")
            self.errors += 1
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.disconnect()
            self.connected = False
            self.logger.info("Disconnected from MQTT broker")
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.connected = True
            self.reconnect_attempts = 0
            self.logger.info("MQTT connected successfully")
        else:
            self.connected = False
            self.logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.connected = False
        self.logger.warning(f"MQTT disconnected with code {rc}")
        
        # Attempt reconnection
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            self.logger.info(f"Attempting reconnection {self.reconnect_attempts}/{self.max_reconnect_attempts}")
            time.sleep(self.reconnect_delay)
            asyncio.create_task(self._reconnect())
    
    async def _reconnect(self):
        """Attempt to reconnect to MQTT broker"""
        try:
            await self.connect()
        except Exception as e:
            self.logger.error(f"Reconnection failed: {e}")
    
    def _on_publish(self, client, userdata, mid):
        """MQTT publish callback"""
        self.messages_sent += 1
        self.last_activity = datetime.utcnow()
    
    def _on_message(self, client, userdata, msg):
        """MQTT message callback"""
        self.messages_received += 1
        self.last_activity = datetime.utcnow()
        
        # Call registered callback if exists
        topic = msg.topic
        if topic in self.message_callbacks:
            try:
                payload = json.loads(msg.payload.decode())
                self.message_callbacks[topic](topic, payload)
            except Exception as e:
                self.logger.error(f"Error processing message for topic {topic}: {e}")
    
    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """MQTT subscribe callback"""
        self.logger.info(f"Subscribed with mid {mid}, QoS {granted_qos}")
    
    def publish(self, topic: str, payload: Dict[str, Any], retain: bool = False) -> bool:
        """Publish message to MQTT topic"""
        if not self.connected:
            self.logger.warning(f"Cannot publish - not connected to MQTT broker")
            return False
        
        try:
            result = self.client.publish(
                topic,
                json.dumps(payload),
                qos=self.qos,
                retain=retain
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.error(f"Failed to publish to topic {topic}")
                self.errors += 1
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error publishing to topic {topic}: {e}")
            self.errors += 1
            return False
    
    def subscribe(self, topic: str, callback: Callable) -> bool:
        """Subscribe to MQTT topic"""
        if not self.connected:
            self.logger.warning(f"Cannot subscribe - not connected to MQTT broker")
            return False
        
        try:
            result, mid = self.client.subscribe(topic, self.qos)
            
            if result == mqtt.MQTT_ERR_SUCCESS:
                self.logger.error(f"Failed to subscribe to topic {topic}")
                self.errors += 1
                return False
            
            # Register callback
            self.message_callbacks[topic] = callback
            
            self.logger.info(f"Subscribed to topic {topic}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error subscribing to topic {topic}: {e}")
            self.errors += 1
            return False
    
    def unsubscribe(self, topic: str) -> bool:
        """Unsubscribe from MQTT topic"""
        if not self.connected:
            return False
        
        try:
            result, mid = self.client.unsubscribe(topic)
            
            if result == mqtt.MQTT_ERR_SUCCESS:
                self.logger.error(f"Failed to unsubscribe from topic {topic}")
                self.errors += 1
                return False
            
            # Remove callback
            if topic in self.message_callbacks:
                del self.message_callbacks[topic]
            
            self.logger.info(f"Unsubscribed from topic {topic}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unsubscribing from topic {topic}: {e}")
            self.errors += 1
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get MQTT client statistics"""
        return {
            "connected": self.connected,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "errors": self.errors,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "reconnect_attempts": self.reconnect_attempts,
            "subscribed_topics": list(self.message_callbacks.keys())
        }
