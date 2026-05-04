# Valtronics Installation Guide

**Complete installation instructions for the Valtronics system**

---

## Overview

This guide provides step-by-step instructions for installing and configuring the Valtronics intelligent electronics ecosystem on your system.

---

## System Requirements

### Hardware Requirements

#### Minimum Requirements
- **CPU**: 2 cores, 2.4 GHz or faster
- **RAM**: 4 GB RAM
- **Storage**: 20 GB available disk space
- **Network**: Internet connection for API access

#### Recommended Requirements
- **CPU**: 4 cores, 3.0 GHz or faster
- **RAM**: 8 GB RAM or more
- **Storage**: 50 GB available disk space
- **Network**: High-speed internet connection

#### Enterprise Requirements
- **CPU**: 8 cores, 3.5 GHz or faster
- **RAM**: 16 GB RAM or more
- **Storage**: 100 GB available disk space (SSD recommended)
- **Network**: Dedicated network connection

### Software Requirements

#### Operating Systems
- **Linux**: Ubuntu 20.04+, CentOS 8+, RHEL 8+
- **macOS**: 10.15+ (Catalina or newer)
- **Windows**: Windows 10/11 (with WSL2 recommended)

#### Required Software
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **npm**: 7.0 or higher
- **Git**: 2.0 or higher

#### Optional Dependencies
- **PostgreSQL**: 12.0 or higher (production)
- **Redis**: 6.0 or higher (caching)
- **Docker**: 20.0 or higher (containerization)
- **Docker Compose**: 1.29 or higher

---

## Installation Methods

### Method 1: Local Development Setup

#### Step 1: Clone the Repository
```bash
# Clone the Valtronics repository
git clone https://github.com/valtronics/valtronics.git
cd valtronics

# Verify the repository structure
ls -la
```

#### Step 2: Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print('FastAPI installed successfully')"
```

#### Step 3: Frontend Setup
```bash
# Navigate to frontend directory
cd ../frontend

# Install Node.js dependencies
npm install

# Verify installation
npm --version
node --version
```

#### Step 4: Configuration Setup
```bash
# Copy environment configuration files
cd ../backend
cp .env.example .env

cd ../frontend
cp .env.example .env

# Edit configuration files
nano backend/.env
nano frontend/.env
```

#### Step 5: Database Setup
```bash
# Navigate to backend directory
cd ../backend

# Initialize database (SQLite for development)
python init_database.py

# Create sample data (optional)
python create_sample_data.py
```

#### Step 6: Start the Development Servers
```bash
# Terminal 1: Start backend server
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main_sqlite.py

# Terminal 2: Start frontend server
cd frontend
npm start
```

#### Step 7: Verify Installation
- **Frontend**: Open http://localhost:3000
- **Backend API**: Open http://localhost:8000
- **API Documentation**: Open http://localhost:8000/docs

### Method 2: Docker Installation

#### Step 1: Install Docker
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# CentOS/RHEL
sudo yum install docker docker-compose

# macOS
# Download Docker Desktop from https://www.docker.com/products/docker-desktop

# Windows
# Download Docker Desktop from https://www.docker.com/products/docker-desktop
```

#### Step 2: Build Docker Images
```bash
# Navigate to project root
cd valtronics

# Build backend image
cd backend
docker build -t valtronics-backend .

# Build frontend image
cd ../frontend
docker build -t valtronics-frontend .
```

#### Step 3: Run with Docker Compose
```bash
# Navigate to project root
cd valtronics

# Create docker-compose.yml file
cat > docker-compose.yml << EOF
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./valtronics.db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./backend:/app
      - ./valtronics.db:/app/valtronics.db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
EOF

# Start the services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Method 3: Production Deployment

#### Step 1: Server Preparation
```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Install required software
sudo apt-get install -y python3 python3-pip nodejs npm postgresql redis-server nginx

# Create valtronics user
sudo useradd -m -s /bin/bash valtronics
sudo usermod -aG sudo valtronics
```

#### Step 2: Database Setup
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE valtronics;
CREATE USER valtronics_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE valtronics TO valtronics_user;
\q

# Test connection
psql -h localhost -U valtronics_user -d valtronics
```

#### Step 3: Application Deployment
```bash
# Create application directory
sudo mkdir -p /opt/valtronics
sudo chown valtronics:valtronics /opt/valtronics

# Deploy application (as valtronics user)
sudo su - valtronics
cd /opt/valtronics
git clone https://github.com/valtronics/valtronics.git .

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend build
cd ../frontend
npm install
npm run build

# Configure production settings
cd ../backend
cp .env.example .env
# Edit .env with production settings
nano .env
```

#### Step 4: System Service Setup
```bash
# Create systemd service for backend
sudo tee /etc/systemd/system/valtronics-backend.service > /dev/null << EOF
[Unit]
Description=Valtronics Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=valtronics
WorkingDirectory=/opt/valtronics/backend
Environment=PATH=/opt/valtronics/backend/venv/bin
ExecStart=/opt/valtronics/backend/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable valtronics-backend
sudo systemctl start valtronics-backend

# Check status
sudo systemctl status valtronics-backend
```

#### Step 5: Web Server Configuration
```bash
# Configure Nginx
sudo tee /etc/nginx/sites-available/valtronics > /dev/null << EOF
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /opt/valtronics/frontend/build;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/valtronics /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Configuration

### Backend Configuration (.env)
```bash
# Database Configuration
DATABASE_URL=postgresql://valtronics_user:password@localhost/valtronics
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Valtronics

# MQTT Configuration
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# OpenAI Configuration (optional)
OPENAI_API_KEY=your-openai-api-key

# WebSocket Configuration
WEBSOCKET_HEARTBEAT_INTERVAL=30

# CORS Configuration
BACKEND_CORS_ORIGINS=["http://localhost:3000", "https://your-domain.com"]
```

### Frontend Configuration (.env)
```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws

# Application Configuration
REACT_APP_NAME=Valtronics
REACT_APP_VERSION=1.0.0

# Feature Flags
REACT_APP_ENABLE_AI_FEATURES=true
REACT_APP_ENABLE_REAL_TIME=true
REACT_APP_ENABLE_ANALYTICS=true
```

---

## Verification and Testing

### Health Check
```bash
# Test backend health
curl http://localhost:8000/api/v1/health/

# Expected response
{
    "status": "healthy",
    "services": {
        "database": "healthy",
        "redis": "healthy",
        "api": "healthy"
    }
}
```

### API Test
```bash
# Test device API
curl http://localhost:8000/api/v1/devices/

# Test WebSocket connection
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
     -H "Sec-WebSocket-Version: 13" \
     http://localhost:8000/ws
```

### Frontend Test
```bash
# Test frontend accessibility
curl -I http://localhost:3000

# Expected response
HTTP/1.1 200 OK
Content-Type: text/html
```

---

## Troubleshooting

### Common Issues

#### Backend Issues
**Problem**: Backend fails to start
```bash
# Check Python version
python --version

# Check dependencies
pip list

# Check logs
python main_sqlite.py
```

**Problem**: Database connection error
```bash
# Check database status
sudo systemctl status postgresql

# Test connection
psql -h localhost -U valtronics_user -d valtronics
```

#### Frontend Issues
**Problem**: Frontend build fails
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules
rm -rf node_modules package-lock.json

# Reinstall dependencies
npm install
```

**Problem**: API connection errors
```bash
# Check backend status
curl http://localhost:8000/api/v1/health/

# Check CORS configuration
grep CORS backend/.env
```

#### Docker Issues
**Problem**: Container fails to start
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild images
docker-compose build --no-cache
```

### Log Locations
- **Backend Logs**: `/opt/valtronics/logs/`
- **Nginx Logs**: `/var/log/nginx/`
- **System Logs**: `journalctl -u valtronics-backend`

---

## Next Steps

After successful installation:

1. **Review Configuration**: Verify all configuration settings
2. **Create Admin User**: Set up administrative accounts
3. **Configure Devices**: Add your first devices
4. **Set Up Monitoring**: Configure system monitoring
5. **Review Security**: Implement security best practices

For detailed configuration and usage instructions, see the [Configuration Guide](../06-configuration/configuration-guide.md).

---

## Support

For installation support:
- **Email**: autobotsolution@gmail.com
- **Documentation**: [Troubleshooting Guide](../10-reference/troubleshooting.md)
- **Community**: [Support Forums] (coming soon)

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Valtronics Installation Guide v1.0**
