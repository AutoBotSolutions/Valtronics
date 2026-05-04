# WebSocket API Documentation

**Complete API reference for real-time WebSocket communication**

---

## Overview

The WebSocket API provides real-time bidirectional communication between clients and the Valtronics server. This API enables live data streaming, instant notifications, and real-time updates for devices, telemetry, alerts, and system events.

---

## WebSocket Endpoints

### Primary WebSocket Endpoint
```
ws://localhost:8000/ws
```

### Specialized Endpoints
- **Telemetry Stream**: `ws://localhost:8000/ws/telemetry`
- **Alert Notifications**: `ws://localhost:8000/ws/alerts`
- **System Status**: `ws://localhost:8000/ws/system`
- **Device Status**: `ws://localhost:8000/ws/devices`

---

## Connection Process

### 1. Establish Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function(event) {
    console.log('WebSocket connected');
};
```

### 2. Authentication
After connection, authenticate with JWT token:
```javascript
ws.send(JSON.stringify({
    type: 'auth',
    token: 'your-jwt-token'
}));
```

### 3. Subscribe to Channels
Subscribe to specific data channels:
```javascript
ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'telemetry',
    device_id: 1
}));
```

---

## Message Formats

### Authentication Message
```json
{
  "type": "auth",
  "token": "jwt-token-string"
}
```

### Subscription Message
```json
{
  "type": "subscribe",
  "channel": "channel-name",
  "device_id": 1,
  "filters": {
    "metrics": ["temperature", "humidity"]
  }
}
```

### Unsubscription Message
```json
{
  "type": "unsubscribe",
  "channel": "channel-name",
  "device_id": 1
}
```

### Ping Message (Keep-alive)
```json
{
  "type": "ping",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## Available Channels

### 1. Telemetry Channel
Receive real-time telemetry data updates.

**Channel**: `telemetry`

**Subscription Options**:
- `device_id`: Specific device ID (optional)
- `metrics`: Array of metric names (optional)
- `frequency`: Update frequency (optional)

**Message Format**:
```json
{
  "type": "telemetry_update",
  "channel": "telemetry",
  "device_id": 1,
  "telemetry": {
    "temperature": {
      "value": 23.5,
      "unit": "°C",
      "timestamp": "2024-01-01T12:00:00Z"
    },
    "humidity": {
      "value": 45.2,
      "unit": "%",
      "timestamp": "2024-01-01T12:00:00Z"
    }
  }
}
```

**Example Subscription**:
```javascript
ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'telemetry',
    device_id: 1,
    filters: {
        metrics: ['temperature', 'humidity'],
        frequency: 'real-time'
    }
}));
```

### 2. Alerts Channel
Receive real-time alert notifications.

**Channel**: `alerts`

**Subscription Options**:
- `severity`: Alert severity filter (optional)
- `device_id`: Specific device ID (optional)
- `alert_type`: Alert type filter (optional)

**Message Format**:
```json
{
  "type": "alert",
  "channel": "alerts",
  "alert_id": 123,
  "device_id": 1,
  "severity": "critical",
  "title": "High Temperature Alert",
  "message": "Temperature exceeds safe threshold",
  "timestamp": "2024-01-01T12:00:00Z",
  "metadata": {
    "threshold_value": 30.0,
    "actual_value": 32.5
  }
}
```

**Example Subscription**:
```javascript
ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'alerts',
    filters: {
        severity: ['critical', 'warning'],
        device_id: 1
    }
}));
```

### 3. Device Status Channel
Receive real-time device status updates.

**Channel**: `devices`

**Subscription Options**:
- `device_id`: Specific device ID (optional)
- `status_types`: Array of status types to monitor

**Message Format**:
```json
{
  "type": "device_status_update",
  "channel": "devices",
  "device_id": 1,
  "old_status": "online",
  "new_status": "offline",
  "timestamp": "2024-01-01T12:00:00Z",
  "reason": "Connection lost",
  "metadata": {
    "last_seen": "2024-01-01T11:45:00Z"
  }
}
```

**Example Subscription**:
```javascript
ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'devices',
    filters: {
        device_id: [1, 2, 3],
        status_types: ['online', 'offline', 'warning']
    }
}));
```

### 4. System Status Channel
Receive real-time system status updates.

**Channel**: `system`

**Subscription Options**:
- `metrics`: System metrics to monitor
- `frequency`: Update frequency

**Message Format**:
```json
{
  "type": "system_status_update",
  "channel": "system",
  "metrics": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 23.1,
    "active_connections": 15
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Example Subscription**:
```javascript
ws.send(JSON.stringify({
    type: 'subscribe',
    channel: 'system',
    filters: {
        metrics: ['cpu_usage', 'memory_usage', 'active_connections'],
        frequency: '30s'
    }
}));
```

---

## Client Implementation Examples

### JavaScript Client
```javascript
class ValtronicsWebSocket {
    constructor(url, token) {
        this.url = url;
        this.token = token;
        this.ws = null;
        this.subscriptions = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 1000;
    }

    connect() {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.authenticate();
            this.reconnectAttempts = 0;
        };

        this.ws.onmessage = (event) => {
            this.handleMessage(JSON.parse(event.data));
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.reconnect();
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    authenticate() {
        this.send({
            type: 'auth',
            token: this.token
        });
    }

    subscribe(channel, filters = {}) {
        const subscription = {
            type: 'subscribe',
            channel: channel,
            ...filters
        };
        
        this.send(subscription);
        this.subscriptions.set(channel, filters);
    }

    unsubscribe(channel) {
        const subscription = {
            type: 'unsubscribe',
            channel: channel
        };
        
        this.send(subscription);
        this.subscriptions.delete(channel);
    }

    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        }
    }

    handleMessage(data) {
        switch (data.type) {
            case 'auth_response':
                this.handleAuthResponse(data);
                break;
            case 'telemetry_update':
                this.handleTelemetryUpdate(data);
                break;
            case 'alert':
                this.handleAlert(data);
                break;
            case 'device_status_update':
                this.handleDeviceStatusUpdate(data);
                break;
            case 'system_status_update':
                this.handleSystemStatusUpdate(data);
                break;
            case 'pong':
                // Handle keep-alive response
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    handleTelemetryUpdate(data) {
        // Handle telemetry updates
        console.log('Telemetry update:', data);
        if (this.onTelemetryUpdate) {
            this.onTelemetryUpdate(data);
        }
    }

    handleAlert(data) {
        // Handle alert notifications
        console.log('Alert received:', data);
        if (this.onAlert) {
            this.onAlert(data);
        }
    }

    handleDeviceStatusUpdate(data) {
        // Handle device status updates
        console.log('Device status update:', data);
        if (this.onDeviceStatusUpdate) {
            this.onDeviceStatusUpdate(data);
        }
    }

    handleSystemStatusUpdate(data) {
        // Handle system status updates
        console.log('System status update:', data);
        if (this.onSystemStatusUpdate) {
            this.onSystemStatusUpdate(data);
        }
    }

    reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
                console.log(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                this.connect();
            }, this.reconnectInterval * this.reconnectAttempts);
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}

// Usage example
const wsClient = new ValtronicsWebSocket('ws://localhost:8000/ws', 'jwt-token');

wsClient.onTelemetryUpdate = (data) => {
    console.log('New telemetry data:', data.telemetry);
};

wsClient.onAlert = (data) => {
    console.log('New alert:', data.title);
    showNotification(data);
};

wsClient.connect();
wsClient.subscribe('telemetry', { device_id: 1 });
wsClient.subscribe('alerts', { severity: ['critical', 'warning'] });
```

### Python Client
```python
import asyncio
import json
import websockets
from datetime import datetime

class ValtronicsWebSocketClient:
    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.websocket = None
        self.subscriptions = {}
        self.running = False

    async def connect(self):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.url)
            await self.authenticate()
            self.running = True
            print("WebSocket connected successfully")
        except Exception as e:
            print(f"Failed to connect: {e}")
            raise

    async def authenticate(self):
        """Authenticate with JWT token"""
        auth_message = {
            "type": "auth",
            "token": self.token
        }
        await self.send_message(auth_message)
        
        # Wait for authentication response
        response = await self.websocket.recv()
        data = json.loads(response)
        
        if data.get("type") == "auth_response" and data.get("success"):
            print("Authentication successful")
        else:
            raise Exception("Authentication failed")

    async def subscribe(self, channel, filters=None):
        """Subscribe to a channel"""
        subscription = {
            "type": "subscribe",
            "channel": channel
        }
        if filters:
            subscription["filters"] = filters
        
        await self.send_message(subscription)
        self.subscriptions[channel] = filters
        print(f"Subscribed to {channel}")

    async def unsubscribe(self, channel):
        """Unsubscribe from a channel"""
        unsubscription = {
            "type": "unsubscribe",
            "channel": channel
        }
        await self.send_message(unsubscription)
        self.subscriptions.pop(channel, None)
        print(f"Unsubscribed from {channel}")

    async def send_message(self, message):
        """Send message to WebSocket"""
        if self.websocket:
            await self.websocket.send(json.dumps(message))

    async def listen(self):
        """Listen for incoming messages"""
        try:
            while self.running:
                message = await self.websocket.recv()
                data = json.loads(message)
                await self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
        except Exception as e:
            print(f"Error listening for messages: {e}")

    async def handle_message(self, data):
        """Handle incoming messages"""
        message_type = data.get("type")
        
        if message_type == "telemetry_update":
            await self.handle_telemetry_update(data)
        elif message_type == "alert":
            await self.handle_alert(data)
        elif message_type == "device_status_update":
            await self.handle_device_status_update(data)
        elif message_type == "system_status_update":
            await self.handle_system_status_update(data)
        elif message_type == "pong":
            # Handle keep-alive response
            pass
        else:
            print(f"Unknown message type: {message_type}")

    async def handle_telemetry_update(self, data):
        """Handle telemetry updates"""
        device_id = data.get("device_id")
        telemetry = data.get("telemetry")
        print(f"Telemetry update for device {device_id}: {telemetry}")

    async def handle_alert(self, data):
        """Handle alert notifications"""
        alert_id = data.get("alert_id")
        severity = data.get("severity")
        title = data.get("title")
        print(f"Alert [{severity}]: {title} (ID: {alert_id})")

    async def handle_device_status_update(self, data):
        """Handle device status updates"""
        device_id = data.get("device_id")
        old_status = data.get("old_status")
        new_status = data.get("new_status")
        print(f"Device {device_id} status changed: {old_status} -> {new_status}")

    async def handle_system_status_update(self, data):
        """Handle system status updates"""
        metrics = data.get("metrics")
        print(f"System status update: {metrics}")

    async def ping(self):
        """Send ping message (keep-alive)"""
        ping_message = {
            "type": "ping",
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message(ping_message)

    async def disconnect(self):
        """Disconnect from WebSocket"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            print("WebSocket disconnected")

# Usage example
async def main():
    client = ValtronicsWebSocket("ws://localhost:8000/ws", "jwt-token")
    
    try:
        await client.connect()
        
        # Subscribe to channels
        await client.subscribe("telemetry", {"device_id": 1})
        await client.subscribe("alerts", {"severity": ["critical", "warning"]})
        await client.subscribe("devices")
        
        # Listen for messages
        await client.listen()
        
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Error Handling

### Connection Errors
```javascript
ws.onerror = function(error) {
    console.error('WebSocket error:', error);
    // Implement error handling logic
    switch (error.code) {
        case 1006:
            console.log('Connection lost - attempting to reconnect');
            break;
        case 1000:
            console.log('Normal closure');
            break;
        default:
            console.log('Unknown error code:', error.code);
    }
};
```

### Authentication Errors
```javascript
function handleAuthResponse(data) {
    if (!data.success) {
        console.error('Authentication failed:', data.message);
        // Handle authentication failure
        if (data.error === 'invalid_token') {
            // Refresh token or redirect to login
            refreshToken();
        }
    }
}
```

### Message Processing Errors
```javascript
function handleMessage(data) {
    try {
        // Validate message structure
        if (!data.type) {
            throw new Error('Missing message type');
        }
        
        // Process message
        processMessage(data);
        
    } catch (error) {
        console.error('Error processing message:', error);
        // Send error report to server
        sendErrorReport(error, data);
    }
}
```

---

## Performance Optimization

### Connection Pooling
```javascript
class WebSocketPool {
    constructor(maxConnections = 5) {
        this.connections = [];
        this.maxConnections = maxConnections;
        this.currentIndex = 0;
    }

    getConnection() {
        if (this.connections.length < this.maxConnections) {
            const ws = new WebSocket('ws://localhost:8000/ws');
            this.connections.push(ws);
            return ws;
        }
        
        // Round-robin selection
        const ws = this.connections[this.currentIndex];
        this.currentIndex = (this.currentIndex + 1) % this.connections.length;
        return ws;
    }
}
```

### Message Batching
```javascript
class MessageBatcher {
    constructor(ws, batchSize = 10, batchTimeout = 100) {
        this.ws = ws;
        this.batchSize = batchSize;
        this.batchTimeout = batchTimeout;
        this.messageQueue = [];
        this.batchTimer = null;
    }

    send(message) {
        this.messageQueue.push(message);
        
        if (this.messageQueue.length >= this.batchSize) {
            this.flushBatch();
        } else if (!this.batchTimer) {
            this.batchTimer = setTimeout(() => this.flushBatch(), this.batchTimeout);
        }
    }

    flushBatch() {
        if (this.messageQueue.length > 0) {
            const batch = {
                type: 'batch',
                messages: [...this.messageQueue]
            };
            
            this.ws.send(JSON.stringify(batch));
            this.messageQueue = [];
        }
        
        if (this.batchTimer) {
            clearTimeout(this.batchTimer);
            this.batchTimer = null;
        }
    }
}
```

---

## Security Considerations

### Token Validation
- Always validate JWT tokens before allowing connections
- Implement token refresh mechanisms
- Monitor for suspicious connection patterns

### Message Validation
- Validate all incoming message structures
- Implement rate limiting per connection
- Sanitize message content

### Connection Security
- Use WSS (WebSocket Secure) in production
- Implement origin validation
- Monitor connection attempts

---

## Rate Limiting

### Connection Limits
- Maximum 100 concurrent connections per user
- Maximum 1000 total concurrent connections
- Connection rate limited to 10 per minute

### Message Limits
- Maximum 100 messages per second per connection
- Maximum 1KB message size
- Batch messages limited to 50 items

---

## Monitoring and Logging

### Connection Monitoring
```javascript
class ConnectionMonitor {
    constructor() {
        this.connections = new Map();
        this.stats = {
            totalConnections: 0,
            activeConnections: 0,
            messagesReceived: 0,
            messagesSent: 0
        };
    }

    addConnection(connectionId, ws) {
        this.connections.set(connectionId, {
            ws: ws,
            connectedAt: new Date(),
            messagesReceived: 0,
            messagesSent: 0
        });
        
        this.stats.totalConnections++;
        this.stats.activeConnections++;
    }

    removeConnection(connectionId) {
        this.connections.delete(connectionId);
        this.stats.activeConnections--;
    }

    getStats() {
        return {
            ...this.stats,
            averageConnectionDuration: this.calculateAverageDuration(),
            messagesPerConnection: this.calculateMessagesPerConnection()
        };
    }
}
```

### Message Logging
```javascript
function logMessage(direction, message) {
    const logEntry = {
        timestamp: new Date().toISOString(),
        direction: direction, // 'sent' or 'received'
        type: message.type,
        size: JSON.stringify(message).length,
        channel: message.channel
    };
    
    console.log('WebSocket message:', logEntry);
    
    // Send to logging service
    sendToLoggingService(logEntry);
}
```

---

## Best Practices

### Connection Management
- Implement proper connection lifecycle management
- Handle reconnection logic gracefully
- Monitor connection health and performance
- Implement connection pooling for high-load scenarios

### Message Handling
- Validate all message structures
- Implement proper error handling
- Use message batching for high-frequency updates
- Implement message deduplication when necessary

### Performance Optimization
- Use binary message formats for large data
- Implement message compression
- Optimize message size and frequency
- Use connection pooling and load balancing

### Security
- Always use WSS in production
- Implement proper authentication and authorization
- Validate and sanitize all messages
- Monitor for suspicious activity

---

## Troubleshooting

### Common Issues

#### Connection Failures
- Check WebSocket server status
- Verify JWT token validity
- Check network connectivity
- Verify WebSocket URL and port

#### Authentication Issues
- Ensure JWT token is not expired
- Check token format and structure
- Verify token permissions
- Check server authentication logs

#### Message Issues
- Validate message JSON format
- Check message size limits
- Verify channel subscriptions
- Check server message processing logs

### Debugging Tools
```javascript
// WebSocket debugging utility
class WebSocketDebugger {
    constructor(ws) {
        this.ws = ws;
        this.enabled = true;
        this.logLevel = 'info'; // debug, info, warn, error
    }

    log(level, message, data = null) {
        if (!this.enabled || !this.shouldLog(level)) return;
        
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level: level.toUpperCase(),
            message,
            data
        };
        
        console.log(`[WebSocket] ${timestamp} ${logEntry.level}: ${message}`, data);
    }

    shouldLog(level) {
        const levels = ['debug', 'info', 'warn', 'error'];
        return levels.indexOf(level) >= levels.indexOf(this.logLevel);
    }

    enable() {
        this.enabled = true;
    }

    disable() {
        this.enabled = false;
    }

    setLogLevel(level) {
        this.logLevel = level;
    }
}
```

---

## Support

For WebSocket API support:
- **Documentation**: [API Overview](api-overview.md)
- **Device API**: [Device API](device-api.md)
- **Telemetry API**: [Telemetry API](telemetry-api.md)
- **Alerts API**: [Alerts API](alerts-api.md)
- **Troubleshooting**: [Troubleshooting Guide](../10-reference/troubleshooting.md)
- **Email**: autobotsolution@gmail.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**WebSocket API Documentation v1.0**
