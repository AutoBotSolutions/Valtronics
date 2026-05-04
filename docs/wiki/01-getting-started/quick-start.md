# Valtronics Quick Start Guide

**Get Valtronics running in 5 minutes**

---

## Overview

This quick start guide will get you up and running with Valtronics in just a few minutes. For detailed installation instructions, see the [Installation Guide](installation.md).

---

## Prerequisites

- **Python 3.8+** installed
- **Node.js 16+** installed
- **Git** installed
- **20GB** free disk space

---

## 5-Minute Quick Start

### Step 1: Clone and Setup (1 minute)
```bash
# Clone the repository
git clone https://github.com/valtronics/valtronics.git
cd valtronics

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### Step 2: Configure (1 minute)
```bash
# Copy configuration files
cd ../backend
cp .env.example .env

cd ../frontend
cp .env.example .env

# Use SQLite for quick start (already configured)
```

### Step 3: Initialize Database (1 minute)
```bash
cd ../backend
python init_database.py
python create_sample_data.py
```

### Step 4: Start Services (1 minute)
```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate
python main_sqlite.py

# Terminal 2: Start frontend
cd frontend
npm start
```

### Step 5: Access Valtronics (1 minute)
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## First Steps

### 1. Explore the Dashboard
Open http://localhost:3000 to see the main dashboard with:
- Device overview and statistics
- Real-time telemetry data
- Alert management
- System analytics

### 2. Test the API
```bash
# Check system health
curl http://localhost:8000/api/v1/health/

# List devices
curl http://localhost:8000/api/v1/devices/

# View analytics
curl http://localhost:8000/api/v1/analytics/system
```

### 3. Add Your First Device
```bash
# Create a new device
curl -X POST http://localhost:8000/api/v1/devices/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Device",
    "device_id": "DEV-001",
    "device_type": "sensor",
    "manufacturer": "Test Corp",
    "model": "TC-1000",
    "firmware_version": "1.0.0",
    "location": "Office",
    "status": "online"
  }'
```

### 4. Send Telemetry Data
```bash
# Send telemetry data
curl -X POST http://localhost:8000/api/v1/telemetry/ \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "metric_name": "temperature",
    "metric_value": 23.5,
    "unit": "°C"
  }'
```

### 5. Create an Alert
```bash
# Create an alert rule
curl -X POST http://localhost:8000/api/v1/alerts/ \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "title": "High Temperature Alert",
    "description": "Temperature exceeds threshold",
    "severity": "warning",
    "alert_type": "threshold",
    "threshold_value": 25.0,
    "metric_name": "temperature"
  }'
```

---

## Sample Data

The quick start includes sample data with:

### Devices (5 devices)
- **Temperature Sensor Alpha** - Online, Zone A
- **Pressure Monitor Beta** - Online, Zone B  
- **Flow Controller Gamma** - Warning, Zone C
- **Voltage Sensor Delta** - Offline, Zone D
- **Humidity Monitor Epsilon** - Online, Zone E

### Telemetry Data
- **480 data points** across 24 hours
- **Multiple metrics**: temperature, humidity, pressure, voltage
- **Real-time updates** via WebSocket

### Alerts
- **3 active alerts** with different severity levels
- **Alert rules** for automated monitoring

---

## Key Features to Try

### 1. Real-time Dashboard
- Live device status updates
- Interactive charts and graphs
- Real-time telemetry streaming

### 2. Device Management
- Add, edit, and delete devices
- Monitor device health
- Track device locations

### 3. Alert System
- Create custom alert rules
- Set severity levels
- Configure notifications

### 4. Analytics
- System performance metrics
- Device efficiency tracking
- Historical data analysis

### 5. WebSocket Real-time
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// Send message
ws.send(JSON.stringify({
  type: 'ping',
  timestamp: new Date().toISOString()
}));

// Receive messages
ws.onmessage = function(event) {
  console.log('Received:', JSON.parse(event.data));
};
```

---

## Configuration Basics

### Environment Variables
Key configuration options in `.env` files:

**Backend (.env)**
```bash
DATABASE_URL=sqlite:///./valtronics.db
SECRET_KEY=your-secret-key
API_V1_STR=/api/v1
```

**Frontend (.env)**
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
```

### Database
- **Development**: SQLite (file-based)
- **Production**: PostgreSQL (recommended)
- **Caching**: Redis (optional)

---

## Common Commands

### Backend Commands
```bash
# Start development server
python main_sqlite.py

# Initialize database
python init_database.py

# Create sample data
python create_sample_data.py

# Run tests
python -m pytest tests/

# Check dependencies
pip list
```

### Frontend Commands
```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Check dependencies
npm list
```

### API Commands
```bash
# Health check
curl http://localhost:8000/api/v1/health/

# List all endpoints
curl http://localhost:8000/docs

# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

---

## Troubleshooting Quick Fixes

### Backend Issues
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check database
ls -la valtronics.db
```

### Frontend Issues
```bash
# Clear cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000

# Kill processes
sudo kill -9 <PID>
```

---

## Next Steps

After the quick start:

1. **Read the Full Documentation**: Explore the complete [wiki documentation](../README.md)
2. **Configure Production**: Set up PostgreSQL and Redis for production use
3. **Deploy to Cloud**: Learn about cloud deployment options
4. **Customize**: Modify themes and components
5. **Integrate**: Connect your own devices and systems

---

## Support

- **Documentation**: [Full Wiki](../README.md)
- **Installation Guide**: [Detailed Installation](installation.md)
- **API Reference**: [API Documentation](../03-api/api-overview.md)
- **Troubleshooting**: [Troubleshooting Guide](../10-reference/troubleshooting.md)

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Valtronics Quick Start Guide v1.0**
