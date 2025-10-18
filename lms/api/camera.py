"""Camera API endpoints."""
import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, List
from models import RecordingRequest, CameraCommandRequest
from websocket_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/camera", tags=["camera"])


@router.post("/{client_uuid}/initialize")
async def initialize_camera(client_uuid: str):
    """Initialize camera system on client."""
    response = await manager.send_command(
        client_uuid,
        "camera_initialize",
        {}
    )

    if not response.success:
        raise HTTPException(status_code=500, detail=response.error or "Failed to initialize camera")

    return response.data


@router.get("/{client_uuid}/cameras")
async def get_cameras(client_uuid: str):
    """Get list of available cameras on client."""
    response = await manager.send_command(
        client_uuid,
        "camera_get_cameras",
        {}
    )

    if not response.success:
        raise HTTPException(status_code=500, detail=response.error or "Failed to get cameras")

    return response.data


@router.get("/{client_uuid}/encoders")
async def get_encoders(client_uuid: str):
    """Get available video encoders on client."""
    response = await manager.send_command(
        client_uuid,
        "camera_get_encoders",
        {}
    )

    if not response.success:
        raise HTTPException(status_code=500, detail=response.error or "Failed to get encoders")

    return response.data


@router.post("/{client_uuid}/recording/start")
async def start_recording(client_uuid: str, request: RecordingRequest):
    """Start recording on client."""
    params = request.dict(exclude_none=True)

    response = await manager.send_command(
        client_uuid,
        "camera_start_recording",
        params
    )

    if not response.success:
        raise HTTPException(status_code=500, detail=response.error or "Failed to start recording")

    return response.data


@router.post("/{client_uuid}/recording/stop")
async def stop_recording(client_uuid: str, request: CameraCommandRequest):
    """Stop recording on client."""
    response = await manager.send_command(
        client_uuid,
        "camera_stop_recording",
        {"camera_index": request.camera_index}
    )

    if not response.success:
        raise HTTPException(status_code=500, detail=response.error or "Failed to stop recording")

    return response.data


@router.get("/{client_uuid}/status")
async def get_status(client_uuid: str, camera_index: int = None):
    """Get camera status on client."""
    params = {}
    if camera_index is not None:
        params["camera_index"] = camera_index

    response = await manager.send_command(
        client_uuid,
        "camera_get_status",
        params
    )

    if not response.success:
        raise HTTPException(status_code=500, detail=response.error or "Failed to get status")

    return response.data


@router.post("/{client_uuid}/streaming/start")
async def start_streaming(client_uuid: str, request: CameraCommandRequest):
    """Start video streaming on client."""
    response = await manager.send_command(
        client_uuid,
        "camera_start_streaming",
        {"camera_index": request.camera_index}
    )

    if not response.success:
        raise HTTPException(status_code=500, detail=response.error or "Failed to start streaming")

    return response.data


@router.post("/{client_uuid}/streaming/stop")
async def stop_streaming(client_uuid: str, request: CameraCommandRequest):
    """Stop video streaming on client."""
    response = await manager.send_command(
        client_uuid,
        "camera_stop_streaming",
        {"camera_index": request.camera_index}
    )

    if not response.success:
        raise HTTPException(status_code=500, detail=response.error or "Failed to stop streaming")

    return response.data


@router.post("/{client_uuid}/preview/start")
async def start_preview(client_uuid: str, camera_index: int = 0, fps: int = 10):
    """Start camera preview (sends frames via WebSocket)."""
    response = await manager.send_command(
        client_uuid,
        "camera_start_preview",
        {"camera_index": camera_index, "fps": fps}
    )

    if not response.success:
        raise HTTPException(status_code=500, detail=response.error or "Failed to start preview")

    return response.data


@router.post("/{client_uuid}/preview/stop")
async def stop_preview(client_uuid: str, camera_index: int = 0):
    """Stop camera preview."""
    response = await manager.send_command(
        client_uuid,
        "camera_stop_preview",
        {"camera_index": camera_index}
    )

    if not response.success:
        raise HTTPException(status_code=500, detail=response.error or "Failed to stop preview")

    return response.data
