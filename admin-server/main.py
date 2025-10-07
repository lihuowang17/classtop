"""Admin Server - FastAPI application for managing ClassTop clients."""
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from websocket_manager import manager
from api import clients, settings, camera

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ClassTop Admin Server",
    description="Remote management server for ClassTop clients",
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


@app.get("/")
async def root():
    """Serve admin interface."""
    return FileResponse("static/index.html")


@app.websocket("/ws/{client_uuid}")
async def websocket_endpoint(websocket: WebSocket, client_uuid: str):
    """WebSocket endpoint for client connections."""
    client_ip = websocket.client.host if websocket.client else "unknown"

    logger.info(f"WebSocket connection request from client {client_uuid} at {client_ip}")

    await manager.connect(websocket, client_uuid, client_ip)

    try:
        await manager.listen_to_client(client_uuid)
    except WebSocketDisconnect:
        logger.info(f"Client {client_uuid} disconnected")
        manager.disconnect(client_uuid)
    except Exception as e:
        logger.error(f"Error in WebSocket connection for {client_uuid}: {e}")
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
    return {
        "status": "healthy",
        "clients_online": len(manager.get_online_clients()),
        "clients_total": len(manager.get_all_clients())
    }


# Mount static files last
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    logger.info("Starting ClassTop Admin Server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
