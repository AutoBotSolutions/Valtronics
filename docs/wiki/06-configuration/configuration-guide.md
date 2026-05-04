# Configuration Guide

**Complete configuration guide for the Valtronics system**

---

## Overview

This guide covers all aspects of configuring the Valtronics system, from basic setup to advanced production configurations. Proper configuration is essential for optimal performance, security, and reliability.

---

## Configuration Files

### Backend Configuration
```
backend/
├── .env                    # Environment variables
├── .env.example           # Environment template
├── app/core/config.py      # Configuration settings
├── app/db/session.py       # Database configuration
└── app/main.py            # Application entry point
```

### Frontend Configuration
```
frontend/
├── .env                    # Environment variables
├── .env.example           # Environment template
├── src/config/            # Configuration files
├── vite.config.js         # Build configuration
└── package.json           # Dependencies and scripts
```

---

## Environment Variables

### Backend Environment Variables (.env)

#### Core Settings
```bash
# Application Settings
PROJECT_NAME=Valtronics
API_V1_STR=/api/v1
VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production

# Database Configuration
DATABASE_URL=postgresql://valtronics_user:password@localhost:5432/valtronics
# For development: DATABASE_URL=sqlite:///./valtronics.db

# Security Settings
SECRET_KEY=your-super-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
BCRYPT_ROUNDS=12

# CORS Settings
BACKEND_CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
BACKEND_CORS_ALLOW_CREDENTIALS=true
```

#### External Services
```bash
# Redis Configuration (Optional)
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=
REDIS_DB=0

# MQTT Configuration
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_CLIENT_ID=valtronics_backend
MQTT_KEEPALIVE=60

# OpenAI Configuration (Optional)
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
```

#### WebSocket Configuration
```bash
# WebSocket Settings
WEBSOCKET_HEARTBEAT_INTERVAL=30
WEBSOCKET_MAX_CONNECTIONS=1000
WEBSOCKET_MESSAGE_QUEUE_SIZE=10000
```

#### Monitoring and Logging
```bash
# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/valtronics.log
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=5

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=60
```

### Frontend Environment Variables (.env)

#### API Configuration
```bash
# API Settings
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
REACT_APP_API_TIMEOUT=30000
```

#### Application Settings
```bash
# Application
REACT_APP_NAME=Valtronics
REACT_APP_VERSION=1.0.0
REACT_APP_DESCRIPTION=AI-powered intelligent electronics ecosystem
```

#### Feature Flags
```bash
# Feature Toggles
REACT_APP_ENABLE_AI_FEATURES=true
REACT_APP_ENABLE_REAL_TIME=true
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_DARK_MODE=true
```

#### UI Configuration
```bash
# UI Settings
REACT_APP_DEFAULT_LANGUAGE=en
REACT_APP_THEME=dark
REACT_APP_PAGE_SIZE=20
REACT_APP_REFRESH_INTERVAL=5000
```

---

## Configuration Classes

### Backend Configuration (app/core/config.py)
```python
from pydantic import BaseSettings, validator
from typing import List, Optional
import secrets

class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Core Settings
    PROJECT_NAME: str = "Valtronics"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    BCRYPT_ROUNDS: int = 12
    
    # Database
    DATABASE_URL: str = "sqlite:///./valtronics.db"
    
    # Redis
    REDIS_URL: Optional[str] = None
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # MQTT
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    MQTT_CLIENT_ID: str = "valtronics_backend"
    MQTT_KEEPALIVE: int = 60
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 1000
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    BACKEND_CORS_ALLOW_CREDENTIALS: bool = True
    
    # WebSocket
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    WEBSOCKET_MAX_CONNECTIONS: int = 1000
    WEBSOCKET_MESSAGE_QUEUE_SIZE: int = 10000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/valtronics.log"
    LOG_MAX_SIZE: str = "10MB"
    LOG_BACKUP_COUNT: int = 5
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    HEALTH_CHECK_INTERVAL: int = 60
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### Database Configuration (app/db/session.py)
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Database engine configuration
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Configuration Scenarios

### Development Configuration
```bash
# .env.development
DEBUG=true
ENVIRONMENT=development
DATABASE_URL=sqlite:///./valtronics.db
LOG_LEVEL=DEBUG
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

### Staging Configuration
```bash
# .env.staging
DEBUG=false
ENVIRONMENT=staging
DATABASE_URL=postgresql://staging_user:password@staging-db:5432/valtronics_staging
REDIS_URL=redis://staging-redis:6379/0
LOG_LEVEL=INFO
CORS_ORIGINS=["https://staging.valtronics.com"]
```

### Production Configuration
```bash
# .env.production
DEBUG=false
ENVIRONMENT=production
DATABASE_URL=postgresql://prod_user:secure_password@prod-db:5432/valtronics
REDIS_URL=redis://prod-redis:6379/0
SECRET_KEY=your-production-secret-key
LOG_LEVEL=WARNING
CORS_ORIGINS=["https://valtronics.com"]
```

---

## Advanced Configuration

### Database Configuration

#### PostgreSQL Production Setup
```python
# app/db/session_postgres.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)
```

#### Connection Pooling
```python
# Connection pool configuration
POOL_SIZE = 20
MAX_OVERFLOW = 30
POOL_TIMEOUT = 30
POOL_RECYCLE = 3600
POOL_PRE_PING = True
```

### Redis Configuration

#### Redis Client Setup
```python
# app/cache/redis_client.py
import redis
from app.core.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30
)
```

#### Redis Configuration Options
```bash
# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_MAX_CONNECTIONS=100
REDIS_SOCKET_TIMEOUT=5
```

### MQTT Configuration

#### MQTT Client Setup
```python
# app/mqtt/mqtt_client.py
import paho.mqtt.client as mqtt
from app.core.config import settings

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        self.client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
```

#### MQTT Topics Configuration
```python
# MQTT topic structure
MQTT_TOPICS = {
    "telemetry": "valtronics/+/telemetry",
    "commands": "valtronics/+/commands",
    "alerts": "valtronics/+/alerts",
    "status": "valtronics/+/status"
}
```

---

## Security Configuration

### JWT Configuration
```python
# app/core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.core.config import settings

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
```

### Password Hashing
```python
# app/core/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)
```

### API Key Configuration
```python
# app/core/api_keys.py
from cryptography.fernet import Fernet
import base64

def generate_api_key():
    key = Fernet.generate_key()
    return base64.urlsafe_b64encode(key).decode()

def encrypt_api_key(api_key: str):
    key = Fernet.generate_key()
    f = Fernet(key)
    encrypted_key = f.encrypt(api_key.encode())
    return encrypted_key.decode()
```

---

## Performance Configuration

### Application Performance
```python
# app/core/performance.py
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Thread pool for CPU-intensive tasks
thread_pool = ThreadPoolExecutor(max_workers=4)

# Async settings
ASYNCIO_POOL_SIZE = 100
CONCURRENT_REQUESTS = 1000
REQUEST_TIMEOUT = 30
```

### Database Performance
```sql
-- PostgreSQL performance settings
-- postgresql.conf

# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Connection settings
max_connections = 200
listen_addresses = '*'
port = 5432

# Logging settings
log_destination = 'stderr'
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
```

### Caching Configuration
```python
# app/cache/cache_config.py
from app.core.config import settings

CACHE_CONFIG = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": settings.REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 50}
        },
        "KEY_PREFIX": "valtronics",
        "TIMEOUT": 300,
        "VERSION": 1
    },
    "telemetry": {
        "TIMEOUT": 60,
        "KEY_PREFIX": "telemetry"
    },
    "analytics": {
        "TIMEOUT": 3600,
        "KEY_PREFIX": "analytics"
    }
}
```

---

## Monitoring Configuration

### Health Check Configuration
```python
# app/api/v1/endpoints/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "services": {}
    }
    
    # Database health
    try:
        db.execute("SELECT 1")
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Redis health (if configured)
    if settings.REDIS_URL:
        try:
            redis_client.ping()
            health_status["services"]["redis"] = "healthy"
        except Exception as e:
            health_status["services"]["redis"] = f"unhealthy: {str(e)}"
    
    return health_status
```

### Metrics Configuration
```python
# app/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics definitions
REQUEST_COUNT = Counter(
    'valtronics_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'valtronics_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'valtronics_active_connections',
    'Number of active connections'
)

# Middleware for metrics collection
async def metrics_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response
```

---

## Logging Configuration

### Logging Setup
```python
# app/core/logging.py
import logging
import logging.config
from pathlib import Path
from app.core.config import settings

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "json": {
            "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "json" if settings.LOG_FORMAT == "json" else "default",
            "filename": settings.LOG_FILE,
            "maxBytes": int(settings.LOG_MAX_SIZE.replace("MB", "")) * 1024 * 1024,
            "backupCount": settings.LOG_BACKUP_COUNT,
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": settings.LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "sqlalchemy": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# Configure logging
logging.config.dictConfig(LOGGING_CONFIG)
```

### Structured Logging
```python
# app/core/structured_logging.py
import json
import logging
from datetime import datetime

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
    
    def log_event(self, event_type: str, **kwargs):
        log_data = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        self.logger.info(json.dumps(log_data))
    
    def log_error(self, error_type: str, **kwargs):
        log_data = {
            "event_type": "error",
            "error_type": error_type,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        self.logger.error(json.dumps(log_data))
```

---

## Configuration Validation

### Environment Validation
```python
# app/core/validation.py
from pydantic import BaseModel, validator
from typing import List
import os

class EnvironmentConfig(BaseModel):
    """Environment configuration validation"""
    
    PROJECT_NAME: str
    DATABASE_URL: str
    SECRET_KEY: str
    
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        return v
    
    @validator('DATABASE_URL')
    def validate_database_url(cls, v):
        if not v.startswith(('sqlite:///', 'postgresql://')):
            raise ValueError('DATABASE_URL must be SQLite or PostgreSQL')
        return v

def validate_environment():
    """Validate current environment configuration"""
    try:
        config = EnvironmentConfig(
            PROJECT_NAME=os.getenv('PROJECT_NAME'),
            DATABASE_URL=os.getenv('DATABASE_URL'),
            SECRET_KEY=os.getenv('SECRET_KEY')
        )
        return True, "Environment validation passed"
    except Exception as e:
        return False, f"Environment validation failed: {str(e)}"
```

### Configuration Health Check
```python
# app/core/config_health.py
from app.core.config import settings
from app.core.validation import validate_environment

def check_configuration_health():
    """Check overall configuration health"""
    health_status = {
        "status": "healthy",
        "checks": {},
        "issues": []
    }
    
    # Validate environment
    env_valid, env_message = validate_environment()
    health_status["checks"]["environment"] = env_valid
    if not env_valid:
        health_status["issues"].append(env_message)
        health_status["status"] = "unhealthy"
    
    # Check database connectivity
    try:
        from app.db.session import engine
        engine.execute("SELECT 1")
        health_status["checks"]["database"] = True
    except Exception as e:
        health_status["checks"]["database"] = False
        health_status["issues"].append(f"Database connection failed: {str(e)}")
        health_status["status"] = "unhealthy"
    
    # Check Redis (if configured)
    if settings.REDIS_URL:
        try:
            from app.cache.redis_client import redis_client
            redis_client.ping()
            health_status["checks"]["redis"] = True
        except Exception as e:
            health_status["checks"]["redis"] = False
            health_status["issues"].append(f"Redis connection failed: {str(e)}")
    
    return health_status
```

---

## Configuration Management

### Configuration Loading
```python
# app/core/config_loader.py
import os
from pathlib import Path
from typing import Dict, Any

class ConfigLoader:
    """Load and manage configuration from multiple sources"""
    
    def __init__(self):
        self.config = {}
        self.load_default_config()
        self.load_env_file()
        self.load_environment_variables()
    
    def load_default_config(self):
        """Load default configuration"""
        self.config.update({
            "PROJECT_NAME": "Valtronics",
            "VERSION": "1.0.0",
            "DEBUG": False,
            "LOG_LEVEL": "INFO"
        })
    
    def load_env_file(self):
        """Load configuration from .env file"""
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        self.config[key] = value
    
    def load_environment_variables(self):
        """Load configuration from environment variables"""
        env_vars = [
            "PROJECT_NAME", "VERSION", "DEBUG", "DATABASE_URL",
            "SECRET_KEY", "REDIS_URL", "MQTT_BROKER_HOST"
        ]
        
        for var in env_vars:
            if os.getenv(var):
                self.config[var] = os.getenv(var)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
```

### Dynamic Configuration Updates
```python
# app/core/dynamic_config.py
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigWatcher(FileSystemEventHandler):
    """Watch for configuration file changes"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    def on_modified(self, event):
        if event.src_path.endswith('.env'):
            asyncio.create_task(self.config_manager.reload_config())

class DynamicConfigManager:
    """Manage dynamic configuration updates"""
    
    def __init__(self):
        self.config = {}
        self.observers = []
    
    async def reload_config(self):
        """Reload configuration from files"""
        # Reload logic here
        pass
    
    def start_watching(self):
        """Start watching configuration files"""
        event_handler = ConfigWatcher(self)
        observer = Observer()
        observer.schedule(event_handler, path='.', recursive=False)
        observer.start()
        self.observers.append(observer)
    
    def stop_watching(self):
        """Stop watching configuration files"""
        for observer in self.observers:
            observer.stop()
            observer.join()
```

---

## Best Practices

### Security Best Practices
- Use strong, randomly generated SECRET_KEY
- Store sensitive configuration in environment variables
- Rotate secrets regularly
- Use HTTPS in production
- Implement proper CORS policies
- Validate all configuration values

### Performance Best Practices
- Use connection pooling for databases
- Configure appropriate cache settings
- Optimize database queries
- Monitor resource usage
- Use structured logging for better debugging

### Maintenance Best Practices
- Document all configuration options
- Use version control for configuration templates
- Implement configuration validation
- Regularly review and update configurations
- Backup configuration files

---

## Troubleshooting Configuration

### Common Issues

#### Database Connection Issues
```bash
# Check database URL format
echo $DATABASE_URL

# Test database connection
python -c "from app.db.session import engine; print(engine.execute('SELECT 1').scalar())"
```

#### Environment Variable Issues
```bash
# List all environment variables
env | grep -E "(DATABASE_URL|SECRET_KEY|REDIS_URL)"

# Check .env file permissions
ls -la .env

# Reload environment variables
source .env
```

#### CORS Issues
```bash
# Check CORS origins
echo $BACKEND_CORS_ORIGINS

# Test CORS preflight
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS http://localhost:8000/api/v1/devices/
```

---

## Support

For configuration support:
- **Documentation**: [Environment Variables](environment-variables.md)
- **Deployment**: [Deployment Guide](deployment-guide.md)
- **Troubleshooting**: [Troubleshooting Guide](../10-reference/troubleshooting.md)
- **Email**: autobotsolution@gmail.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Configuration Guide v1.0**
