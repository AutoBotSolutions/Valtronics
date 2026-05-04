"""
FastAPI application with SQLite for local development
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import health, devices, ai, analytics, alerts
from app.db.session_sqlite import engine, Base
from app.websocket_handler import websocket_endpoint, start_heartbeat_task
from telemetry.mqtt_handler import start_mqtt_client, stop_mqtt_client
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Valtronics API (SQLite)",
    description="AI-powered intelligent electronics ecosystem - Local Development",
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
    return {"message": "Valtronics API (SQLite)", "version": "1.0.0"}

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Valtronics API (SQLite)...")
    
    # Note: MQTT and Redis may not be available in local setup
    try:
        start_mqtt_client()
        logger.info("MQTT client started")
    except Exception as e:
        logger.warning(f"MQTT client not available: {e}")
    
    try:
        start_heartbeat_task()
        logger.info("WebSocket heartbeat task started")
    except Exception as e:
        logger.warning(f"Heartbeat task not available: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Valtronics API...")
    
    try:
        stop_mqtt_client()
        logger.info("MQTT client stopped")
    except Exception as e:
        logger.warning(f"Error stopping MQTT client: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_sqlite:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
