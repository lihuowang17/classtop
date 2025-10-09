"""Client management API endpoints."""
from fastapi import APIRouter, HTTPException
from typing import Dict, List
from models import ClientInfo, CommandRequest, CommandResponse
from websocket_manager import manager

router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("/", response_model=Dict[str, ClientInfo])
async def get_all_clients():
    """Get all registered clients."""
    return manager.get_all_clients()


@router.get("/online", response_model=Dict[str, ClientInfo])
async def get_online_clients():
    """Get all online clients."""
    return manager.get_online_clients()


@router.get("/{client_uuid}", response_model=ClientInfo)
async def get_client(client_uuid: str):
    """Get information about a specific client."""
    client = manager.get_client_info(client_uuid)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.post("/{client_uuid}/command", response_model=CommandResponse)
async def send_command(client_uuid: str, request: CommandRequest):
    """Send a command to a client."""
    client = manager.get_client_info(client_uuid)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    response = await manager.send_command(
        client_uuid,
        request.command,
        request.params
    )

    return response


@router.post("/{client_uuid}/refresh")
async def refresh_client_state(client_uuid: str):
    """Request client to send updated state."""
    response = await manager.send_command(client_uuid, "refresh_state")
    if not response.success:
        raise HTTPException(status_code=500, detail=response.error)
    return {"success": True}
