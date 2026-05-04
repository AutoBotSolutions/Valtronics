import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db, Base
from app.core.config import settings

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the database dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def db():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    """Create a test database session"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Create authentication headers for testing"""
    # This would be replaced with actual JWT token generation
    return {"Authorization": "Bearer test-token"}

@pytest.fixture
def sample_device_data():
    """Sample device data for testing"""
    return {
        "name": "Test Device",
        "device_id": "TEST_DEVICE_001",
        "device_type": "sensor",
        "manufacturer": "Test Corp",
        "model": "Test Model",
        "firmware_version": "1.0.0",
        "location": "Test Lab"
    }

@pytest.fixture
def sample_telemetry_data():
    """Sample telemetry data for testing"""
    return {
        "metric_name": "temperature",
        "metric_value": 23.5,
        "unit": "celsius"
    }

@pytest.fixture
def sample_alert_data():
    """Sample alert data for testing"""
    return {
        "title": "Test Alert",
        "description": "This is a test alert",
        "severity": "warning",
        "alert_type": "threshold",
        "threshold_value": 30.0,
        "actual_value": 35.0,
        "metric_name": "temperature"
    }

@pytest.fixture
def sample_alert_rule_data():
    """Sample alert rule data for testing"""
    return {
        "name": "High Temperature Alert",
        "description": "Alert when temperature exceeds threshold",
        "metric_name": "temperature",
        "condition": "gt",
        "threshold_value": 30.0,
        "severity": "warning",
        "is_active": True,
        "notification_enabled": True,
        "cooldown_minutes": 30
    }
