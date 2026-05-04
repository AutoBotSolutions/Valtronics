# 🚀 Valtronics Quick Start Guide

## System Status
- ✅ Python 3.13.5 available
- ✅ Node.js v20.19.2 available
- ❌ Docker not installed (optional)

## Quick Start (Local Development)

### Option 1: Using the Local Setup Script (Recommended)

```bash
# Navigate to project directory
cd /home/robbie/Desktop/Valtronics/valtronics

# Run the setup script (one-time setup)
sudo ./scripts/start-local.sh setup

# Start all services
./scripts/start-local.sh start

# Check status
./scripts/start-local.sh status
```

### Option 2: Manual Setup

#### 1. Install Dependencies
```bash
# Install PostgreSQL (if not installed)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Install Redis (if not installed)
sudo apt install redis-server

# Start services
sudo systemctl start postgresql redis-server
```

#### 2. Setup Database
```bash
# Create database and user
sudo -u postgres createdb valtronics_db
sudo -u postgres createuser valtronics
sudo -u postgres psql -c "ALTER USER valtronics PASSWORD 'password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE valtronics_db TO valtronics;"

# Initialize database
psql -h localhost -U valtronics -d valtronics_db -f scripts/init-db.sql
```

#### 3. Start Backend
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 4. Start Frontend (in another terminal)
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Access Points

Once running, you can access:
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health/ping

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL if needed
sudo systemctl restart postgresql

# Test connection
psql -h localhost -U valtronics -d valtronics_db
```

### Port Already in Use
```bash
# Check what's using port 8000
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

### Redis Connection Issues
```bash
# Check Redis status
sudo systemctl status redis-server

# Restart Redis if needed
sudo systemctl restart redis-server

# Test connection
redis-cli ping
```

## Device Simulator (Optional)

To simulate IoT devices for testing:
```bash
# Install Python MQTT client
pip install paho-mqtt

# Run device simulator
python3 scripts/device-simulator.py --broker-host localhost --devices 5
```

## Docker Installation (Optional)

If you prefer using Docker:
```bash
# Install Docker and Docker Compose
sudo ./scripts/install-docker.sh

# Log out and log back in (or run: newgrp docker)

# Start with Docker Compose
docker compose up -d
```

## Next Steps

1. **Access the frontend** at http://localhost:3000
2. **Add devices** using the "Add Device" page
3. **View real-time data** on the dashboard
4. **Check API documentation** at http://localhost:8000/docs
5. **Run device simulator** to generate test data

## Support

If you encounter issues:
1. Check the service status: `./scripts/start-local.sh status`
2. View logs: `./scripts/start-local.sh logs backend`
3. Restart services: `./scripts/start-local.sh restart`
4. Check the troubleshooting section above

## System Requirements

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- 2GB+ RAM
- 5GB+ disk space

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│   :3000         │    │   :8000         │    │   :5432         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Redis Cache   │
                       │   :6379         │
                       └─────────────────┘
```

The system is designed to be modular and can run with or without Docker. Choose the setup method that works best for your environment.
