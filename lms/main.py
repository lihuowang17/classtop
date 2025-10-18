"""LMS (Light Management Service) - FastAPI application for managing ClassTop clients."""
import logging
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from websocket_manager import manager
from api import clients, settings, camera
from db import LMSDatabase
from management_client import ManagementClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database
lms_db = LMSDatabase()

# Initialize Management-Server client (optional)
management_url = os.getenv("MANAGEMENT_SERVER_URL")
management_client = None
if management_url:
    logger.info(f"Management-Server URL configured: {management_url}")
    management_client = ManagementClient(management_url, lms_db)
else:
    logger.info("No Management-Server URL configured, running in standalone mode")

# Create FastAPI app
app = FastAPI(
    title="ClassTop LMS",
    description="Light Management Service for ClassTop clients",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(clients.router)
app.include_router(settings.router)
app.include_router(camera.router)


@app.on_event("startup")
async def startup():
    """Startup event: register to Management-Server"""
    if management_client:
        logger.info("Attempting to register with Management-Server...")
        if management_client.register():
            management_client.start_heartbeat()
        else:
            logger.warning("Failed to register with Management-Server, continuing in standalone mode")


@app.on_event("shutdown")
async def shutdown():
    """Shutdown event: stop heartbeat and close database"""
    if management_client:
        management_client.stop_heartbeat()
    lms_db.close()
    logger.info("LMS shutdown complete")


@app.get("/")
async def root():
    """Serve admin interface."""
    return FileResponse("static/index.html")


@app.websocket("/ws/{client_uuid}")
async def websocket_endpoint(websocket: WebSocket, client_uuid: str):
    """WebSocket endpoint for client connections."""
    client_ip = websocket.client.host if websocket.client else "unknown"

    logger.info(f"WebSocket connection request from client {client_uuid} at {client_ip}")

    # Register client in database
    lms_db.register_client(client_uuid, f"Client-{client_uuid[:8]}", client_ip)
    lms_db.log_connection(client_uuid, "connected", client_ip)

    await manager.connect(websocket, client_uuid, client_ip)

    try:
        await manager.listen_to_client(client_uuid)
    except WebSocketDisconnect:
        logger.info(f"Client {client_uuid} disconnected")
        lms_db.update_client_status(client_uuid, "offline")
        lms_db.log_connection(client_uuid, "disconnected", client_ip)
        manager.disconnect(client_uuid)
    except Exception as e:
        logger.error(f"Error in WebSocket connection for {client_uuid}: {e}")
        lms_db.update_client_status(client_uuid, "error")
        manager.disconnect(client_uuid)


@app.websocket("/ws/viewer/{client_uuid}/{viewer_id}")
async def viewer_websocket_endpoint(websocket: WebSocket, client_uuid: str, viewer_id: str):
    """WebSocket endpoint for viewing client camera preview."""
    logger.info(f"Viewer {viewer_id} connecting to watch client {client_uuid}")

    await manager.add_viewer(websocket, viewer_id, client_uuid)

    try:
        # Keep connection alive
        while True:
            # Just receive pings/close messages
            try:
                message = await websocket.receive_json()
                # Handle viewer commands if needed
            except Exception:
                break
    except WebSocketDisconnect:
        logger.info(f"Viewer {viewer_id} disconnected")
        manager.remove_viewer(viewer_id)
    except Exception as e:
        logger.error(f"Error in viewer WebSocket for {viewer_id}: {e}")
        manager.remove_viewer(viewer_id)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    online_clients = len(manager.get_online_clients())
    total_clients = len(manager.get_all_clients())

    return {
        "status": "healthy",
        "lms_uuid": lms_db.get_config("lms_uuid"),
        "clients_online": online_clients,
        "clients_total": total_clients,
        "management_server_connected": management_client is not None and management_client.api_key is not None
    }


@app.get("/api/stats")
async def get_stats():
    """Get LMS statistics."""
    return {
        "online_clients": lms_db.get_online_clients(),
        "total_clients": len(lms_db.get_all_clients()),
        "lms_uuid": lms_db.get_config("lms_uuid")
    }


# Mount static files last
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    logger.info("Starting ClassTop LMS (Light Management Service)...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
