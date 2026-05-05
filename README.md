# Valtronics - AI-Powered Intelligent Electronics Ecosystem

Valtronics is a cutting-edge, enterprise-grade IoT platform that delivers real-time monitoring, advanced analytics, and AI-powered insights for electronic devices and sensors. Built with a modern microservices architecture, it provides businesses with the tools to monitor, analyze, and control their IoT infrastructure through an intuitive web-based dashboard and robust API ecosystem.

[Live Demo](https://autobotsolutions.github.io/Valtronics/) • [Documentation](https://github.com/AutoBotSolutions/Valtronics/wiki) • [API Reference](https://autobotsolutions.github.io/Valtronics/api.html)

---

## Key Features

### Core Capabilities
- **Real-time Device Monitoring** - Track IoT devices via MQTT and WebSocket connections
- **Advanced Analytics** - Comprehensive data analysis with trend detection and anomaly identification  
- **AI-Powered Insights** - Intelligent device analysis using OpenAI GPT integration
- **Smart Alert System** - Configurable alert rules with multi-channel notifications
- **Interactive Dashboard** - Modern React-based UI with real-time updates
- **Multi-tenant Architecture** - Scalable design supporting multiple organizations
- **RESTful API** - Complete API documentation with FastAPI
- **WebSocket Support** - Real-time bidirectional communication
- **MQTT Integration** - Standard IoT protocol support
- **Containerized Deployment** - Docker and Kubernetes ready

### Technology Stack
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Redis, Celery
- **Frontend**: React 18, TailwindCSS, Recharts, WebSocket Client
- **Messaging**: MQTT (Mosquitto), WebSocket, Redis Pub/Sub
- **AI/ML**: OpenAI GPT, Scikit-learn, Pandas, NumPy
- **Infrastructure**: Docker, Kubernetes, Terraform
- **Monitoring**: Grafana, Prometheus, Custom Health Checks

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- PostgreSQL 15+ (if not using Docker)
- Redis 7+ (if not using Docker)
- MQTT broker (Mosquitto recommended)

### Using Docker Compose (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/AutoBotSolutions/Valtronics.git
cd valtronics

# 2. Set environment variables
cp .env.example .env
# Edit .env with your configuration

# 3. Start all services
docker-compose up -d

# 4. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
# MQTT Broker: localhost:1883
```

### Local Development

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
# Access: http://localhost:3000
```

---

## Project Structure

```
valtronics/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── api/v1/endpoints/    # API endpoints
│   │   ├── core/                # Core configuration
│   │   ├── db/                  # Database session management
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   └── services/            # Business logic services
│   ├── telemetry/               # MQTT and telemetry handling
│   ├── tests/                   # Backend tests
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile              # Backend Docker configuration
├── frontend/                   # React frontend application
│   ├── public/                  # Static assets
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API and WebSocket services
│   │   └── utils/              # Utility functions
│   ├── package.json            # Node.js dependencies
│   ├── tailwind.config.js      # TailwindCSS configuration
│   └── Dockerfile             # Frontend Docker configuration
├── cloud/                      # Cloud deployment configurations
│   ├── kubernetes/             # K8s deployment manifests
│   └── terraform/              # Terraform infrastructure
├── firmware/                   # Embedded firmware development
├── mock-devices/               # Device simulation framework
├── scripts/                    # Utility scripts
├── docs/                       # Documentation
├── site/                       # Static website (GitHub Pages)
├── config/                     # Configuration files
├── docker-compose.yml          # Local development setup
└── README.md                  # This file
```

---

## API Documentation

### Authentication
The API uses JWT tokens for authentication:
```http
Authorization: Bearer <your-jwt-token>
```

### Key Endpoints

#### Devices
- `GET /api/v1/devices` - List all devices
- `POST /api/v1/devices` - Create new device
- `GET /api/v1/devices/{id}` - Get device details
- `PUT /api/v1/devices/{id}` - Update device
- `DELETE /api/v1/devices/{id}` - Delete device
- `GET /api/v1/devices/{id}/telemetry` - Get device telemetry
- `POST /api/v1/devices/{id}/telemetry` - Add telemetry data

#### Analytics
- `GET /api/v1/analytics/device/{id}` - Get device analytics
- `GET /api/v1/analytics/system` - Get system analytics
- `GET /api/v1/analytics/device/{id}/timeseries` - Get time series data
- `POST /api/v1/analytics/comparison` - Compare devices

#### AI Insights
- `POST /api/v1/ai/insights` - Get AI-powered insights
- `POST /api/v1/ai/anomaly-detection` - Detect anomalies
- `POST /api/v1/ai/predictive-maintenance` - Get maintenance predictions

#### Alerts
- `GET /api/v1/alerts` - List alerts
- `POST /api/v1/alerts` - Create alert
- `PATCH /api/v1/alerts/{id}/acknowledge` - Acknowledge alert
- `PATCH /api/v1/alerts/{id}/resolve` - Resolve alert

#### WebSocket Connections
- `ws://localhost:8000/ws` - General WebSocket connection
- `ws://localhost:8000/ws/{device_id}` - Device-specific connection

---

## Configuration

### Environment Variables

#### Backend Configuration
```bash
# Database
DATABASE_URL=postgresql://valtronics:password@localhost:5432/valtronics_db

# Redis
REDIS_URL=redis://localhost:6379

# MQTT
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# AI Integration
OPENAI_API_KEY=your-openai-api-key

# Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_HOSTS=["http://localhost:3000"]
```

#### Frontend Configuration
```bash
# API URL
REACT_APP_API_URL=http://localhost:8000/api/v1
```

---

## Deployment

### Docker Deployment

1. **Build images**
   ```bash
   docker build -t valtronics/backend ./backend
   docker build -t valtronics/frontend ./frontend
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Kubernetes Deployment

1. **Create namespace**
   ```bash
   kubectl create namespace valtronics
   ```

2. **Apply secrets**
   ```bash
   kubectl apply -f cloud/kubernetes/secrets.yaml
   ```

3. **Deploy database**
   ```bash
   kubectl apply -f cloud/kubernetes/postgres-deployment.yaml
   ```

4. **Deploy applications**
   ```bash
   kubectl apply -f cloud/kubernetes/backend-deployment.yaml
   kubectl apply -f cloud/kubernetes/frontend-deployment.yaml
   ```

5. **Setup ingress**
   ```bash
   kubectl apply -f cloud/kubernetes/ingress.yaml
   ```

---

## MQTT Integration

### Device Message Format

#### Telemetry Data
```json
{
  "device_id": "TEMP_SENSOR_001",
  "timestamp": "2024-01-01T12:00:00Z",
  "metrics": [
    {
      "name": "temperature",
      "value": 23.5,
      "unit": "celsius"
    },
    {
      "name": "humidity",
      "value": 45.2,
      "unit": "percent"
    }
  ]
}
```

#### Status Updates
```json
{
  "device_id": "TEMP_SENSOR_001",
  "status": "online",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Alerts
```json
{
  "device_id": "TEMP_SENSOR_001",
  "type": "threshold",
  "severity": "warning",
  "message": "Temperature exceeds threshold",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### MQTT Topics
- `valtronics/{device_id}/telemetry` - Device telemetry data
- `valtronics/{device_id}/status` - Device status updates
- `valtronics/{device_id}/heartbeat` - Device heartbeat
- `valtronics/{device_id}/alert` - Device alerts
- `valtronics/{device_id}/command` - Commands to device
- `valtronics/{device_id}/response` - Command responses

---

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# Run with Docker Compose
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

---

## Monitoring and Logging

### Application Logs
- Backend logs: Available in container logs or `/app/logs/`
- Frontend logs: Browser console and Nginx logs
- Database logs: PostgreSQL logs

### Health Checks
- Backend: `GET /api/v1/health/`
- Database: PostgreSQL health check
- Redis: Redis ping command
- MQTT: MQTT connection status

### Metrics
- Application performance metrics
- Database query performance
- API response times
- WebSocket connection counts
- MQTT message throughput

---

## Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes**
4. **Commit your changes**: `git commit -m 'Add feature'`
5. **Push to branch**: `git push origin feature-name`
6. **Create a Pull Request**

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation in `/docs`
- Review the API documentation at `/docs`

---

## GitHub & Deployment

### Repository Structure
This repository is organized for both development and deployment:

- **Main Project**: Complete IoT platform with backend, frontend, and infrastructure
- **Static Website**: `site/` directory contains the GitHub Pages website
- **Documentation**: Comprehensive docs in `docs/` directory
- **Firmware**: Embedded firmware development in `firmware/` directory

### GitHub Pages
The project includes a static website deployed via GitHub Pages:

- **Website URL**: `https://autobotsolutions.github.io/Valtronics/`
- **Source**: `site/` directory
- **Auto-deployment**: Automatic deployment on push to main branch
- **Build Process**: GitHub Actions workflow handles deployment

### Quick GitHub Setup

1. **Create GitHub Repository**
   ```bash
   # Create a new repository on GitHub named "valtronics"
   # Then add the remote:
   git remote add origin https://github.com/your-username/valtronics.git
   ```

2. **Push to GitHub**
   ```bash
   git push -u origin main
   ```

3. **Enable GitHub Pages**
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: main
   - Folder: /(root)
   - Save settings

4. **Enable GitHub Actions**
   - Go to repository Settings → Actions → General
   - Allow all actions and reusable workflows
   - Save settings

### Development Workflow

```bash
# Clone the repository
git clone https://github.com/your-username/valtronics.git
cd valtronics

# Start development environment
./start-dev.sh

# Make changes and commit
git add .
git commit -m "Your changes"
git push origin main
```

### CI/CD Pipeline

The project includes automated workflows:

- **GitHub Pages Deployment**: Automatic website deployment
- **Testing**: Automated backend and frontend tests
- **Code Quality**: Linting and formatting checks
- **Security**: Dependency vulnerability scanning

---

## Built with ❤️ by Valtronics Team

[Live Demo](https://autobotsolutions.github.io/Valtronics/) • [Wiki](https://github.com/AutoBotSolutions/Valtronics/wiki) • [API Docs](https://autobotsolutions.github.io/Valtronics/api.html)

[![GitHub stars](https://img.shields.io/github/stars/AutoBotSolutions/Valtronics?style=social&logo=github)](https://github.com/AutoBotSolutions/Valtronics/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/AutoBotSolutions/Valtronics?style=social&logo=github)](https://github.com/AutoBotSolutions/Valtronics/network)
[![GitHub license](https://img.shields.io/github/license/AutoBotSolutions/Valtronics?logo=github)](https://github.com/AutoBotSolutions/Valtronics/blob/main/LICENSE)

---

**Valtronics** - Building the future of intelligent electronics monitoring and control.
5. Push to branch: `git push origin feature-name`
6. Create a Pull Request

---

**Valtronics** - Building the future of intelligent electronics monitoring and control. 
