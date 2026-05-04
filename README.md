# 🚀 Valtronics - AI-Powered Intelligent Electronics Ecosystem

Valtronics is a comprehensive IoT platform that provides real-time monitoring, analytics, and AI-powered insights for electronic devices and sensors. Built with modern technologies including FastAPI, React, WebSocket, MQTT, and machine learning integration.

## 🌟 Features

### Core Capabilities
- **Real-time Device Monitoring**: Track IoT devices via MQTT and WebSocket connections
- **Advanced Analytics**: Comprehensive data analysis with trend detection and anomaly identification
- **AI-Powered Insights**: Intelligent device analysis using OpenAI GPT integration
- **Alert System**: Configurable alert rules with multi-channel notifications
- **Interactive Dashboard**: Modern React-based UI with real-time updates
- **Multi-tenant Architecture**: Scalable design supporting multiple organizations
- **RESTful API**: Complete API documentation with FastAPI
- **WebSocket Support**: Real-time bidirectional communication
- **MQTT Integration**: Standard IoT protocol support
- **Containerized Deployment**: Docker and Kubernetes ready

### Key Components
- **Backend**: FastAPI with SQLAlchemy, PostgreSQL, Redis
- **Frontend**: React with TailwindCSS, Recharts, WebSocket client
- **Message Queue**: MQTT broker for IoT communication
- **Database**: PostgreSQL with time-series optimization
- **Cache**: Redis for session management and caching
- **AI Integration**: OpenAI API for intelligent analysis

## 📁 Project Structure

```
valtronics/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── api/v1/endpoints/  # API endpoints
│   │   ├── core/              # Core configuration
│   │   ├── db/                # Database session management
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic services
│   ├── telemetry/             # MQTT and telemetry handling
│   ├── tests/                 # Backend tests
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Backend Docker configuration
├── frontend/                  # React frontend application
│   ├── public/               # Static assets
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API and WebSocket services
│   │   └── utils/           # Utility functions
│   ├── package.json         # Node.js dependencies
│   ├── tailwind.config.js   # TailwindCSS configuration
│   └── Dockerfile          # Frontend Docker configuration
├── cloud/                    # Cloud deployment configurations
│   ├── kubernetes/          # K8s deployment manifests
│   └── terraform/           # Terraform infrastructure
├── scripts/                 # Utility scripts
├── docs/                   # Documentation
├── config/                 # Configuration files
├── docker-compose.yml      # Local development setup
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- PostgreSQL 15+ (if not using Docker)
- Redis 7+ (if not using Docker)
- MQTT broker (Mosquitto recommended)

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd valtronics
   ```

2. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - MQTT Broker: localhost:1883

### Local Development

#### Backend Setup

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up database**
   ```bash
   # Ensure PostgreSQL is running
   # Create database and user
   createdb valtronics_db
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

3. **Access the application**
   - Frontend: http://localhost:3000

## 📊 API Documentation

### Authentication
The API uses JWT tokens for authentication. Include the token in the Authorization header:
```
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

#### Health
- `GET /api/v1/health/` - System health check
- `GET /api/v1/health/ping` - Simple ping

### WebSocket Connections
- `ws://localhost:8000/ws` - General WebSocket connection
- `ws://localhost:8000/ws/{device_id}` - Device-specific connection

## 🔧 Configuration

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

## 🏗️ Deployment

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

### Production Considerations

- **Security**: Enable HTTPS, use proper secrets management
- **Scaling**: Configure HPA based on CPU/memory usage
- **Monitoring**: Implement logging and monitoring (Prometheus, Grafana)
- **Backup**: Regular database backups
- **Updates**: Implement CI/CD pipeline for automated deployments

## 📱 MQTT Integration

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

## 🧪 Testing

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

## 🔍 Monitoring and Logging

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

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in `/docs`
- Review the API documentation at `/docs`

## 🗺️ Roadmap

### Upcoming Features
- [ ] Advanced user management and RBAC
- [ ] Mobile application (React Native)
- [ ] Edge computing support
- [ ] Advanced machine learning models
- [ ] Multi-region deployment
- [ ] Plugin system for custom integrations
- [ ] Real-time collaboration features
- [ ] Advanced reporting and export capabilities

### Performance Improvements
- [ ] Database optimization and indexing
- [ ] Caching strategy improvements
- [ ] WebSocket connection pooling
- [ ] API response optimization
- [ ] Frontend bundle optimization

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   IoT Devices   │    │   MQTT Broker   │    │   Backend API   │
│                 │◄──►│                 │◄──►│                 │
│ - Sensors       │    │ - Mosquitto     │    │ - FastAPI       │
│ - Actuators     │    │ - Message Queue │    │ - PostgreSQL    │
│ - Gateways      │    │ - Pub/Sub       │    │ - Redis         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   WebSocket     │    │   AI Services   │
│                 │◄──►│                 │◄──►│                 │
│ - React App     │    │ - Real-time     │    │ - OpenAI GPT    │
│ - Dashboard     │    │ - Notifications │    │ - Analytics     │
│ - Analytics     │    │ - Live Updates  │    │ - ML Models     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/)
- [MQTT Protocol](https://mqtt.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

---

**Valtronics** - Building the future of intelligent electronics monitoring and control. 🚀
