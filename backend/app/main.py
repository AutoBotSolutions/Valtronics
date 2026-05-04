from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import health, devices, ai, analytics, alerts
from app.db.session import engine
from app.models import device
from app.websocket_handler import websocket_endpoint, start_heartbeat_task
from telemetry.mqtt_handler import start_mqtt_client, stop_mqtt_client
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
device.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Valtronics API",
    description="AI-powered intelligent electronics ecosystem",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    health.router,
    prefix=f"{settings.API_V1_STR}/health",
    tags=["health"]
)
app.include_router(
    devices.router,
    prefix=f"{settings.API_V1_STR}/devices",
    tags=["devices"]
)
app.include_router(
    ai.router,
    prefix=f"{settings.API_V1_STR}/ai",
    tags=["ai"]
)
app.include_router(
    analytics.router,
    prefix=f"{settings.API_V1_STR}/analytics",
    tags=["analytics"]
)
app.include_router(
    alerts.router,
    prefix=f"{settings.API_V1_STR}/alerts",
    tags=["alerts"]
)

# WebSocket endpoint
@app.websocket("/ws")
async def websocket(websocket: WebSocket):
    await websocket_endpoint(websocket)

@app.websocket("/ws/{device_id}")
async def websocket_device(websocket: WebSocket, device_id: str):
    await websocket_endpoint(websocket, device_id)

@app.get("/")
async def root():
    return {"message": "Valtronics API", "version": "1.0.0"}

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Valtronics API...")
    
    # Start MQTT client
    try:
        start_mqtt_client()
        logger.info("MQTT client started")
    except Exception as e:
        logger.error(f"Failed to start MQTT client: {e}")
    
    # Start WebSocket heartbeat task
    try:
        start_heartbeat_task()
        logger.info("WebSocket heartbeat task started")
    except Exception as e:
        logger.error(f"Failed to start heartbeat task: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Valtronics API...")
    
    # Stop MQTT client
    try:
        stop_mqtt_client()
        logger.info("MQTT client stopped")
    except Exception as e:
        logger.error(f"Error stopping MQTT client: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
