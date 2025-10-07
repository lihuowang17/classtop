"""Data models for admin server."""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class ClientStatus(str, Enum):
    """Client connection status."""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


class ClientInfo(BaseModel):
    """Information about a connected client."""
    uuid: str
    status: ClientStatus
    last_seen: datetime
    settings: Optional[Dict[str, str]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class CommandRequest(BaseModel):
    """Command to send to client."""
    command: str
    params: Optional[Dict[str, Any]] = None


class CommandResponse(BaseModel):
    """Response from client command."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


class SettingUpdate(BaseModel):
    """Setting update request."""
    key: str
    value: str


class BatchSettingUpdate(BaseModel):
    """Batch setting update request."""
    settings: Dict[str, str]


# Camera models
class CameraInfo(BaseModel):
    """Camera information."""
    index: int
    name: str
    resolutions: List[Dict[str, Any]]


class EncoderInfo(BaseModel):
    """Encoder information."""
    name: str
    type: str
    description: str
    is_hardware: bool


class CameraStatus(BaseModel):
    """Camera recording/streaming status."""
    camera_name: str
    camera_index: int
    encoder: str
    resolution: str
    is_streaming: bool
    is_recording: bool
    current_recording: Optional[str] = None


class RecordingRequest(BaseModel):
    """Recording start request."""
    camera_index: int = 0
    filename: Optional[str] = None
    codec_type: Optional[str] = None  # 'H.264' or 'H.265'
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[int] = None
    preset: Optional[str] = None
    bitrate: Optional[str] = None


class CameraCommandRequest(BaseModel):
    """Camera command request."""
    camera_index: int = 0
