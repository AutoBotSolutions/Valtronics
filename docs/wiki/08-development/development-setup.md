# Development Setup Guide

**Complete guide for setting up the Valtronics development environment**

---

## Overview

This guide provides comprehensive instructions for setting up a complete development environment for the Valtronics system, including backend, frontend, database, and supporting services.

---

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10+ with WSL2
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB free space minimum
- **Processor**: 4-core CPU minimum, 8-core recommended

### Software Requirements
- **Python**: 3.8+ (3.10+ recommended)
- **Node.js**: 16.0+ (18.0+ recommended)
- **npm**: 7.0+ or yarn 1.22+
- **Git**: 2.0+
- **Docker**: 20.0+ (for containerized development)
- **Docker Compose**: 1.29+ (for multi-container development)
- **VS Code**: Recommended IDE (or any preferred IDE)

### Optional Tools
- **PostgreSQL**: 12+ (for production-like development)
- **Redis**: 6+ (for caching and session management)
- **Postman**: For API testing
- **DBeaver**: Database management tool
- **Redis Desktop Manager**: Redis GUI tool

---

## Environment Setup

### 1. Clone the Repository
```bash
# Clone the Valtronics repository
git clone https://github.com/valtronics/valtronics.git
cd valtronics

# Verify repository structure
ls -la
```

### 2. Backend Development Setup

#### Python Environment Setup
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

# Upgrade pip
pip install --upgrade pip

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verify installation
python -c "import fastapi; print('FastAPI installed successfully')"
python -c "import sqlalchemy; print('SQLAlchemy installed successfully')"
```

#### Development Dependencies
Create `requirements-dev.txt` if it doesn't exist:
```txt
# Testing
pytest==7.4.0
pytest-asyncio==0.21.0
pytest-cov==4.1.0
pytest-mock==3.11.1
httpx==0.24.1

# Code Quality
black==23.7.0
isort==5.12.0
flake8==6.0.0
mypy==1.5.1
pre-commit==3.3.3

# Development Tools
python-dotenv==1.0.0
watchdog==3.0.0
ipython==8.14.0
jupyter==1.0.0

# Documentation
mkdocs==1.5.3
mkdocs-material==9.1.21
mkdocs-mermaid2-plugin==1.1.1
```

#### Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment file for development
nano .env
```

Development `.env` configuration:
```bash
# Development Settings
DEBUG=true
ENVIRONMENT=development

# Database
DATABASE_URL=sqlite:///./valtronics_dev.db

# Security (use development keys only!)
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS (allow all origins in development)
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Redis (optional for development)
REDIS_URL=redis://localhost:6379/0

# OpenAI (optional)
OPENAI_API_KEY=your-openai-api-key

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=json
```

### 3. Frontend Development Setup

#### Node.js Environment Setup
```bash
# Navigate to frontend directory
cd ../frontend

# Install Node.js dependencies
npm install

# Verify installation
node --version
npm --version

# Install additional development tools
npm install --save-dev @typescript-eslint/eslint-plugin
npm install --save-dev @typescript-eslint/parser
npm install --save-dev eslint-plugin-react-hooks
npm install --save-dev prettier
```

#### Frontend Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment file for development
nano .env
```

Development `.env` configuration:
```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws

# Application
REACT_APP_NAME=Valtronics
REACT_APP_VERSION=1.0.0

# Feature Flags
REACT_APP_ENABLE_AI_FEATURES=true
REACT_APP_ENABLE_REAL_TIME=true
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_DARK_MODE=true

# Development Settings
REACT_APP_DEV_SERVER_PORT=3000
REACT_APP_FAST_REFRESH=true
REACT_APP_DISABLE_ESLINT=false
```

### 4. Database Setup

#### SQLite (Default Development)
```bash
# Navigate to backend directory
cd ../backend

# Initialize database
python init_database.py

# Create sample data
python create_sample_data.py

# Verify database
ls -la valtronics_dev.db
```

#### PostgreSQL (Production-like Development)
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
```

SQL commands:
```sql
CREATE DATABASE valtronics_dev;
CREATE USER valtronics_dev WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE valtronics_dev TO valtronics_dev;
ALTER USER valtronics_dev CREATEDB;
\q
```

Update `.env` for PostgreSQL:
```bash
DATABASE_URL=postgresql://valtronics_dev:dev_password@localhost:5432/valtronics_dev
```

### 5. Redis Setup (Optional)
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping
```

---

## IDE Configuration

### VS Code Setup

#### Recommended Extensions
```json
{
  "recommendations": [
    "ms-python.python",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "ms-vscode.vscode-json",
    "redhat.vscode-yaml",
    "ms-vscode-remote.remote-containers",
    "ms-vscode.vscode-docker",
    "ms-vscode.vscode-git",
    "ms-vscode.vscode-jupyter",
    "ms-vscode.vscode-tslint",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense",
    "ms-vscode.vscode-live-server"
  ]
}
```

#### Workspace Settings
Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],
  "python.sortImports.args": ["--profile", "black"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "typescript.preferences.importModuleSpecifier": "relative",
  "typescript.suggest.autoImports": true,
  "eslint.workingDirectories": ["frontend"],
  "prettier.configPath": "frontend/.prettierrc",
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/node_modules": true,
    "**/venv": true,
    "**/.pytest_cache": true
  }
}
```

#### Debug Configuration
Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/backend/main_sqlite.py",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      },
      "args": ["--reload"]
    },
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["${workspaceFolder}/backend/tests", "-v"],
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}/backend"
    },
    {
      "name": "Node: React App",
      "type": "node",
      "request": "launch",
      "cwd": "${workspaceFolder}/frontend",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["start"]
    }
  ]
}
```

---

## Development Workflow

### 1. Start Development Servers

#### Backend Server
```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate
python main_sqlite.py --reload
```

#### Frontend Server
```bash
# Terminal 2: Start frontend
cd frontend
npm start
```

#### Optional Services
```bash
# Terminal 3: Redis (if using)
redis-server

# Terminal 4: PostgreSQL (if using)
sudo systemctl start postgresql
```

### 2. Development Tasks

#### Code Quality Tools
```bash
# Backend code formatting
cd backend
black app/
isort app/

# Frontend code formatting
cd frontend
npm run format
npm run lint:fix
```

#### Testing
```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
npm run test:coverage
```

#### Database Operations
```bash
# Reset database
cd backend
rm valtronics_dev.db
python init_database.py
python create_sample_data.py

# Run migrations
alembic upgrade head
```

---

## Development Tools Configuration

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Create pre-commit configuration
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.44.0
    hooks:
      - id: eslint
        files: \.(js|ts|tsx)$
        types: [file]
EOF

# Install pre-commit hooks
pre-commit install
```

### Docker Development Setup

#### Development Dockerfile
```dockerfile
# backend/Dockerfile.dev
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main_sqlite.py", "--reload"]
```

#### Docker Compose Development
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - /app/venv
    environment:
      - DATABASE_URL=sqlite:///./valtronics_dev.db
      - DEBUG=true
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      - REACT_APP_WS_URL=ws://localhost:8000/ws
    depends_on:
      - backend

  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: valtronics_dev
      POSTGRES_USER: valtronics_dev
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### Docker Development Commands
```bash
# Build and start development containers
docker-compose -f docker-compose.dev.yml up --build

# Run in detached mode
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f backend

# Stop containers
docker-compose -f docker-compose.dev.yml down
```

---

## Testing Setup

### Backend Testing Configuration

#### pytest Configuration
Create `backend/pytest.ini`:
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    --strict-markers
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
    api: API tests
    database: Database tests
```

#### Test Structure
```
backend/tests/
├── conftest.py              # Pytest configuration
├── unit/                    # Unit tests
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/             # Integration tests
│   ├── test_api.py
│   ├── test_database.py
│   └── test_websocket.py
├── fixtures/                # Test fixtures
│   ├── __init__.py
│   ├── devices.py
│   ├── telemetry.py
│   └── alerts.py
└── utils/                   # Test utilities
    ├── __init__.py
    ├── test_client.py
    └── database.py
```

#### Test Fixtures Example
```python
# tests/conftest.py
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from app.core.config import settings

@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    
    Base.metadata.create_all(engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield TestingSessionLocal
    
    Base.metadata.drop_all(engine)

@pytest.fixture
def test_client(test_db):
    """Create test client"""
    from app.main_sqlite import app
    
    app.dependency_overrides[get_db] = lambda: test_db
    
    with TestClient(app) as client:
        yield client

@pytest.fixture
def sample_device(test_db):
    """Create sample device for testing"""
    from app.models.device import Device
    
    device = Device(
        name="Test Device",
        device_id="TEST-001",
        device_type="sensor",
        manufacturer="Test Corp",
        model="TC-1000",
        firmware_version="1.0.0",
        location="Test Lab",
        status="online"
    )
    
    test_db.add(device)
    test_db.commit()
    test_db.refresh(device)
    
    return device
```

### Frontend Testing Configuration

#### Jest Configuration
Update `frontend/package.json`:
```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:ci": "jest --ci --coverage --watchAll=false"
  },
  "jest": {
    "testEnvironment": "jsdom",
    "setupFilesAfterEnv": ["<rootDir>/src/setupTests.js"],
    "moduleNameMapping": {
      "^@/(.*)$": "<rootDir>/src/$1"
    },
    "collectCoverageFrom": [
      "src/**/*.{js,jsx,ts,tsx}",
      "!src/**/*.d.ts",
      "!src/index.js",
      "!src/reportWebVitals.js"
    ],
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

#### Test Setup File
Create `frontend/src/setupTests.js`:
```javascript
import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';

// Configure testing library
configure({ testIdAttribute: 'data-testid' });

// Mock WebSocket
global.WebSocket = jest.fn(() => ({
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  send: jest.fn(),
  close: jest.fn(),
  readyState: WebSocket.OPEN,
}));

// Mock Intersection Observer
global.IntersectionObserver = jest.fn(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock ResizeObserver
global.ResizeObserver = jest.fn(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));
```

---

## Debugging Setup

### Backend Debugging

#### Python Debugger Configuration
```python
# Add to your code for debugging
import pdb; pdb.set_trace()

# Or use ipdb for better debugging
import ipdb; ipdb.set_trace()
```

#### VS Code Debugging
Use the debug configuration provided in the IDE setup section.

### Frontend Debugging

#### Chrome DevTools Setup
```javascript
// Add to your code for debugging
console.log('Debug point:', data);
debugger; // Breakpoint in browser

// React DevTools
if (process.env.NODE_ENV === 'development') {
  const { ReactDevTools } = require('react-devtools');
  ReactDevTools.instrument();
}
```

---

## Performance Monitoring

### Development Performance Tools

#### Backend Profiling
```python
# Add to main_sqlite.py
import cProfile
import pstats

@app.middleware("http")
async def profile_middleware(request: Request, call_next):
    if request.query.get("profile"):
        profiler = cProfile.Profile()
        profiler.enable()
        
        response = await call_next(request)
        
        profiler.disable()
        
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        
        # Save profiling results
        stats.dump_stats('profile_stats.prof')
        
        return response
    
    return await call_next(request)
```

#### Frontend Performance Monitoring
```javascript
// Add to App.js
import React, { useEffect } from 'react';
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  // Send to analytics service
  console.log('Performance metric:', metric);
}

export default function App() {
  useEffect(() => {
    getCLS(sendToAnalytics);
    getFID(sendToAnalytics);
    getFCP(sendToAnalytics);
    getLCP(sendToAnalytics);
    getTTFB(sendToAnalytics);
  }, []);

  return (
    // Your app content
    <div>Valtronics App</div>
  );
}
```

---

## Common Development Issues

### Backend Issues

#### Database Connection Errors
```bash
# Check database file permissions
ls -la valtronics_dev.db

# Recreate database
rm valtronics_dev.db
python init_database.py
```

#### Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8000
lsof -i :8000

# Kill process using port
sudo kill -9 <PID>
```

### Frontend Issues

#### Module Resolution Errors
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

#### Build Errors
```bash
# Check for syntax errors
npm run build

# Fix ESLint errors
npm run lint:fix

# Fix TypeScript errors
npx tsc --noEmit
```

---

## Development Best Practices

### Code Organization
- Follow the established directory structure
- Use meaningful variable and function names
- Write modular, reusable code
- Add appropriate comments and documentation

### Git Workflow
- Use feature branches for new development
- Commit frequently with descriptive messages
- Use pull requests for code review
- Keep main branch stable

### Testing
- Write tests for new features
- Maintain high test coverage
- Test edge cases and error conditions
- Use descriptive test names

### Documentation
- Document API endpoints with OpenAPI
- Add inline code comments
- Update README files
- Maintain up-to-date documentation

---

## Support

For development support:
- **Documentation**: [Code Structure](code-structure.md)
- **Contributing**: [Contributing Guidelines](contributing.md)
- **Testing**: [Testing Guide](testing.md)
- **Troubleshooting**: [Troubleshooting Guide](../10-reference/troubleshooting.md)
- **Email**: autobotsolution@gmail.com

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Development Setup Guide v1.0**
