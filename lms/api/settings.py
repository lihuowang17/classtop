"""Settings management API endpoints."""
from fastapi import APIRouter, HTTPException
from typing import Dict
from models import SettingUpdate, BatchSettingUpdate, CommandResponse
from websocket_manager import manager

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/{client_uuid}", response_model=Dict[str, str])
async def get_settings(client_uuid: str):
    """Get all settings from a client."""
    response = await manager.send_command(client_uuid, "get_all_settings")

    if not response.success:
        raise HTTPException(status_code=500, detail=response.error or "Failed to get settings")

    return response.data or {}


@router.get("/{client_uuid}/{key}")
async def get_setting(client_uuid: str, key: str):
    """Get a specific setting from a client."""
    response = await manager.send_command(
        client_uuid,
        "get_setting",
        {"key": key}
    )

    if not response.success:
        raise HTTPException(status_code=500, detail=response.error or "Failed to get setting")

    return {"key": key, "value": response.data}


@router.put("/{client_uuid}/{key}")
async def update_setting(client_uuid: str, key: str, update: SettingUpdate):
    """Update a specific setting on a client."""
    response = await manager.send_command(
        client_uuid,
        "set_setting",
        {"key": key, "value": update.value}
    )

    if not response.success:
        raise HTTPException(status_code=500, detail=response.error or "Failed to update setting")

    return {"success": True, "key": key, "value": update.value}


@router.post("/{client_uuid}/batch")
async def update_settings_batch(client_uuid: str, update: BatchSettingUpdate):
    """Update multiple settings on a client."""
    response = await manager.send_command(
        client_uuid,
        "update_settings_batch",
        {"settings": update.settings}
    )

    if not response.success:
        raise HTTPException(status_code=500, detail=response.error or "Failed to update settings")

    return {"success": True, "updated_count": len(update.settings)}
