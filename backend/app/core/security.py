from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.device import Device

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token handling
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def authenticate_device(db: Session, device_id: str, password: str) -> Optional[Device]:
    """Authenticate a device"""
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        return None
    
    # For demo purposes, we'll use a simple authentication
    # In production, you'd have proper device credentials stored
    if device.device_type == "sensor" and password == "sensor_secret":
        return device
    elif device.device_type == "actuator" and password == "actuator_secret":
        return device
    elif device.device_type == "gateway" and password == "gateway_secret":
        return device
    
    return None

async def get_current_device(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Device:
    """Get current authenticated device from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        device_id: str = payload.get("sub")
        if device_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if device is None:
        raise credentials_exception
    
    return device

async def get_current_active_device(
    current_device: Device = Depends(get_current_device)
) -> Device:
    """Get current active device"""
    if not current_device.is_active:
        raise HTTPException(status_code=400, detail="Inactive device")
    return current_device

def create_device_token(device: Device) -> str:
    """Create JWT token for device authentication"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": device.device_id, "type": "device"}, 
        expires_delta=access_token_expires
    )
    return access_token

class SecurityMiddleware:
    """Security middleware for FastAPI"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        # Add security headers
        if scope["type"] == "http":
            # Add custom security logic here
            pass
        
        await self.app(scope, receive, send)

def add_security_headers(response):
    """Add security headers to HTTP response"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

def validate_input_data(data: dict, required_fields: list) -> bool:
    """Validate input data against required fields"""
    for field in required_fields:
        if field not in data or data[field] is None:
            return False
    return True

def sanitize_input(input_str: str) -> str:
    """Sanitize user input to prevent XSS"""
    # Basic XSS prevention
    dangerous_chars = ["<", ">", "&", "\"", "'", "/"]
    for char in dangerous_chars:
        input_str = input_str.replace(char, "")
    return input_str

class RateLimiter:
    """Simple rate limiter for API endpoints"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed based on rate limit"""
        now = datetime.utcnow()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if (now - req_time).total_seconds() < window
        ]
        
        # Check if under limit
        if len(self.requests[key]) < limit:
            self.requests[key].append(now)
            return True
        
        return False

# Global rate limiter instance
rate_limiter = RateLimiter()
