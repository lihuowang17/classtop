"""
Command handlers for ClassTop application.
"""

import sys
from typing import Optional, List, Dict

from pydantic import BaseModel
from pytauri import Commands

from . import logger as _logger
from . import db as _db


# Command registration
commands: Commands = Commands()


# Request/Response models
class Person(BaseModel):
    name: str


class Greeting(BaseModel):
    message: str


class LogRequest(BaseModel):
    level: Optional[str] = "info"
    message: str


class LogResponse(BaseModel):
    ok: bool


class LogsResponse(BaseModel):
    lines: List[str]


class SetConfigRequest(BaseModel):
    key: str
    value: str


class ConfigResponse(BaseModel):
    key: str
    value: Optional[str]


class GetLogsRequest(BaseModel):
    max_lines: Optional[int] = 200


class GetConfigRequest(BaseModel):
    key: str


# Command handlers
@commands.command()
async def greet(body: Person) -> Greeting:
    return Greeting(
        message=f"Hello, {body.name}! You've been greeted from Python {sys.version}!"
    )


@commands.command()
async def log_message(body: LogRequest) -> LogResponse:
    lvl = body.level or "info"
    _logger.log_message(lvl, body.message)
    return LogResponse(ok=True)


@commands.command()
async def get_logs(body: GetLogsRequest) -> LogsResponse:
    lines = _logger.tail_logs(int(body.max_lines or 200))
    return LogsResponse(lines=lines)


@commands.command()
async def set_config(body: SetConfigRequest) -> ConfigResponse:
    _db.set_config(body.key, body.value)
    return ConfigResponse(key=body.key, value=body.value)


@commands.command()
async def get_config(body: GetConfigRequest) -> ConfigResponse:
    val = _db.get_config(body.key)
    return ConfigResponse(key=body.key, value=val)


@commands.command()
async def list_configs() -> Dict[str, str]:
    return _db.list_configs()


# Schedule commands
class CourseRequest(BaseModel):
    name: str
    teacher: Optional[str] = None
    location: Optional[str] = None
    color: Optional[str] = None


class CourseResponse(BaseModel):
    id: int
    name: str
    teacher: Optional[str]
    location: Optional[str]
    color: Optional[str]


class ScheduleEntryRequest(BaseModel):
    course_id: int
    day_of_week: int
    start_time: str
    end_time: str
    weeks: Optional[List[int]] = None
    note: Optional[str] = None


class ScheduleEntryResponse(BaseModel):
    id: int
    course_id: int
    course_name: str
    teacher: Optional[str]
    location: Optional[str]
    color: Optional[str]
    day_of_week: int
    start_time: str
    end_time: str
    weeks: List[int]
    note: Optional[str]


class CurrentClassResponse(BaseModel):
    id: int
    name: str
    teacher: Optional[str]
    location: Optional[str]
    start_time: str
    end_time: str
    color: Optional[str]


class NextClassResponse(BaseModel):
    id: int
    name: str
    teacher: Optional[str]
    location: Optional[str]
    day_of_week: int
    start_time: str
    end_time: str
    color: Optional[str]


class WeekRequest(BaseModel):
    week: Optional[int] = None


@commands.command()
async def add_course(body: CourseRequest) -> CourseResponse:
    course_id = _db.add_course(body.name, body.teacher, body.location, body.color)
    return CourseResponse(
        id=course_id,
        name=body.name,
        teacher=body.teacher,
        location=body.location,
        color=body.color
    )


@commands.command()
async def get_courses() -> List[CourseResponse]:
    courses = _db.get_courses()
    return [CourseResponse(**course) for course in courses]


@commands.command()
async def update_course(body: Dict) -> Dict:
    course_id = body.pop("id")
    success = _db.update_course(course_id, **body)
    return {"success": success}


@commands.command()
async def delete_course(body: Dict) -> Dict:
    success = _db.delete_course(body["id"])
    return {"success": success}


@commands.command()
async def add_schedule_entry(body: ScheduleEntryRequest) -> Dict:
    entry_id = _db.add_schedule_entry(
        body.course_id,
        body.day_of_week,
        body.start_time,
        body.end_time,
        body.weeks,
        body.note
    )
    return {"id": entry_id, "success": entry_id > 0}


@commands.command()
async def get_schedule(body: WeekRequest) -> List[ScheduleEntryResponse]:
    schedule = _db.get_schedule(body.week)
    return [ScheduleEntryResponse(**entry) for entry in schedule]


@commands.command()
async def delete_schedule_entry(body: Dict) -> Dict:
    success = _db.delete_schedule_entry(body["id"])
    return {"success": success}


@commands.command()
async def get_current_class() -> Optional[CurrentClassResponse]:
    """DEPRECATED: Use get_schedule_by_day and calculate on frontend."""
    current = _db.get_current_class()
    if current:
        return CurrentClassResponse(**current)
    return None


@commands.command()
async def get_next_class() -> Optional[NextClassResponse]:
    """DEPRECATED: Use get_schedule_by_day and calculate on frontend."""
    next_class = _db.get_next_class()
    if next_class:
        return NextClassResponse(**next_class)
    return None


@commands.command()
async def get_last_class() -> Optional[NextClassResponse]:
    """DEPRECATED: Use get_schedule_by_day and calculate on frontend."""
    last_class = _db.get_last_class()
    if last_class:
        return NextClassResponse(**last_class)
    return None


class ScheduleByDayRequest(BaseModel):
    day_of_week: int
    week: Optional[int] = None


@commands.command()
async def get_schedule_by_day(body: ScheduleByDayRequest) -> List[NextClassResponse]:
    """Get all classes for a specific day, optionally filtered by week."""
    classes = _db.get_schedule_by_day(body.day_of_week, body.week)
    return [NextClassResponse(**cls) for cls in classes]


@commands.command()
async def get_schedule_for_week(body: WeekRequest) -> List[NextClassResponse]:
    """Get all classes for the entire week."""
    classes = _db.get_schedule_for_week(body.week)
    return [NextClassResponse(**cls) for cls in classes]


@commands.command()
async def get_current_week() -> Dict:
    """Get the current week number, either calculated or manually set."""
    week = _db.get_calculated_week_number()
    semester_start = _db.get_config("semester_start_date")
    return {
        "week": week,
        "semester_start_date": semester_start,
        "is_calculated": bool(semester_start and semester_start.strip())
    }


@commands.command()
async def get_calculated_week_number() -> int:
    """Get current week number (calculated from semester start date or fallback to manual)."""
    return _db.get_calculated_week_number()


@commands.command()
async def set_semester_start_date(body: Dict) -> Dict:
    """Set the semester start date for automatic week calculation."""
    start_date = body.get("date", "")
    _db.set_config("semester_start_date", start_date)

    # Calculate and return the current week
    if start_date:
        week = _db.get_calculated_week_number()
        return {"success": True, "semester_start_date": start_date, "calculated_week": week}
    else:
        return {"success": True, "semester_start_date": "", "calculated_week": 1}


# ========== Settings Management Commands ==========

@commands.command()
async def get_all_settings() -> Dict[str, str]:
    """Get all application settings."""
    return _db.list_configs()


@commands.command()
async def update_settings(body: Dict) -> Dict:
    """Update multiple settings at once."""
    settings = body.get("settings", {})

    if not settings:
        return {"success": False, "message": "No settings provided"}

    # Update through settings manager if available
    if _db.settings_manager:
        success = _db.settings_manager.update_multiple(settings)
        return {"success": success}
    else:
        # Fallback to individual updates
        for key, value in settings.items():
            _db.set_config(key, str(value))
        return {"success": True}


@commands.command()
async def regenerate_uuid() -> Dict:
    """Regenerate client UUID."""
    if _db.settings_manager:
        new_uuid = _db.settings_manager.regenerate_uuid()
        return {"success": True, "uuid": new_uuid}
    else:
        import uuid
        new_uuid = str(uuid.uuid4())
        _db.set_config('client_uuid', new_uuid)
        return {"success": True, "uuid": new_uuid}


@commands.command()
async def reset_settings(body: Dict) -> Dict:
    """Reset settings to default values."""
    exclude_keys = body.get("exclude", [])

    if _db.settings_manager:
        success = _db.settings_manager.reset_to_defaults(exclude_keys)
        return {"success": success}
    else:
        return {"success": False, "message": "Settings manager not available"}


# Camera commands
class CameraInitResponse(BaseModel):
    success: bool
    camera_count: int
    message: str


class CameraListResponse(BaseModel):
    cameras: List[Dict]


class CameraEncodersResponse(BaseModel):
    h264: Dict
    h265: Dict


class StartRecordingRequest(BaseModel):
    camera_index: int
    filename: Optional[str] = None
    codec_type: Optional[str] = None  # 'H.264' or 'H.265'
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[int] = None
    preset: Optional[str] = None
    bitrate: Optional[str] = None


class RecordingResponse(BaseModel):
    success: bool
    message: str


class StopRecordingRequest(BaseModel):
    camera_index: int


class CameraStatusRequest(BaseModel):
    camera_index: Optional[int] = None


class CameraStatusResponse(BaseModel):
    status: Dict


@commands.command()
async def initialize_camera() -> CameraInitResponse:
    """Initialize camera monitoring system."""
    if not _db.camera_manager:
        return CameraInitResponse(
            success=False,
            camera_count=0,
            message="Camera manager not available"
        )

    success = _db.camera_manager.initialize()
    if success:
        cameras = _db.camera_manager.get_cameras()
        return CameraInitResponse(
            success=True,
            camera_count=len(cameras),
            message=f"Camera system initialized with {len(cameras)} cameras"
        )
    else:
        return CameraInitResponse(
            success=False,
            camera_count=0,
            message="Failed to initialize camera system"
        )


@commands.command()
async def get_cameras() -> CameraListResponse:
    """Get list of available cameras."""
    if not _db.camera_manager:
        return CameraListResponse(cameras=[])

    cameras = _db.camera_manager.get_cameras()
    return CameraListResponse(cameras=cameras)


@commands.command()
async def get_camera_encoders() -> CameraEncodersResponse:
    """Get available video encoders."""
    if not _db.camera_manager:
        return CameraEncodersResponse(
            h264={"available": 0, "encoders": [], "preferred": "libx264"},
            h265={"available": 0, "encoders": [], "preferred": "libx265"}
        )

    encoders = _db.camera_manager.get_encoders()
    return CameraEncodersResponse(**encoders)


@commands.command()
async def start_camera_recording(body: StartRecordingRequest) -> RecordingResponse:
    """Start recording from camera."""
    if not _db.camera_manager:
        return RecordingResponse(
            success=False,
            message="Camera manager not available"
        )

    success = _db.camera_manager.start_recording(
        camera_index=body.camera_index,
        filename=body.filename,
        codec_type=body.codec_type,
        width=body.width,
        height=body.height,
        fps=body.fps,
        preset=body.preset,
        bitrate=body.bitrate
    )

    if success:
        return RecordingResponse(
            success=True,
            message=f"Recording started on camera {body.camera_index}"
        )
    else:
        return RecordingResponse(
            success=False,
            message=f"Failed to start recording on camera {body.camera_index}"
        )


@commands.command()
async def stop_camera_recording(body: StopRecordingRequest) -> RecordingResponse:
    """Stop recording from camera."""
    if not _db.camera_manager:
        return RecordingResponse(
            success=False,
            message="Camera manager not available"
        )

    success = _db.camera_manager.stop_recording(body.camera_index)

    if success:
        return RecordingResponse(
            success=True,
            message=f"Recording stopped on camera {body.camera_index}"
        )
    else:
        return RecordingResponse(
            success=False,
            message=f"Failed to stop recording on camera {body.camera_index}"
        )


@commands.command()
async def get_camera_status(body: CameraStatusRequest) -> CameraStatusResponse:
    """Get camera status."""
    if not _db.camera_manager:
        return CameraStatusResponse(status={"active_cameras": 0, "streamers": {}})

    status = _db.camera_manager.get_status(body.camera_index)
    return CameraStatusResponse(status=status)
