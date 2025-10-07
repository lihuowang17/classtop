"""
API Server for ClassTop - 集中管理服务器 API
Provides RESTful HTTP endpoints for remote management of ClassTop data.
"""

import json
import threading
from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    FastAPI = None
    print("Warning: FastAPI not installed. API server will not be available.")

from . import logger as _logger


class APIServer:
    """API Server for remote management."""

    def __init__(self, db_path, schedule_manager, settings_manager):
        """Initialize API server.

        Args:
            db_path: Database file path
            schedule_manager: ScheduleManager instance
            settings_manager: SettingsManager instance
        """
        self.db_path = db_path
        self.schedule_manager = schedule_manager
        self.settings_manager = settings_manager
        self.logger = _logger
        self.app = None
        self.server_thread = None
        self.enabled = False

        if FastAPI is None:
            self.logger.log_message("warning", "FastAPI not available, API server disabled")
            return

        self._init_app()

    def _init_app(self):
        """Initialize FastAPI application."""
        self.app = FastAPI(
            title="ClassTop API",
            description="集中管理服务器 API - Centralized management API for ClassTop",
            version="1.0.0",
            docs_url="/api/docs",
            redoc_url="/api/redoc"
        )

        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # 生产环境应该限制具体域名
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._register_routes()
        self.logger.log_message("info", "API server initialized")

    def _register_routes(self):
        """Register all API routes."""

        # ==================== Course Management ====================

        @self.app.get("/api/courses", tags=["Courses"])
        async def get_courses():
            """获取所有课程 / Get all courses."""
            try:
                courses = self.schedule_manager.get_courses()
                return {"success": True, "data": courses}
            except Exception as e:
                self.logger.log_message("error", f"API error getting courses: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/courses", tags=["Courses"])
        async def create_course(course: Dict[str, Any]):
            """创建课程 / Create a new course."""
            try:
                name = course.get("name")
                if not name:
                    raise HTTPException(status_code=400, detail="Course name is required")

                course_id = self.schedule_manager.add_course(
                    name=name,
                    teacher=course.get("teacher"),
                    location=course.get("location"),
                    color=course.get("color")
                )

                if course_id > 0:
                    return {
                        "success": True,
                        "data": {
                            "id": course_id,
                            "name": name,
                            "teacher": course.get("teacher"),
                            "location": course.get("location"),
                            "color": course.get("color")
                        }
                    }
                else:
                    raise HTTPException(status_code=500, detail="Failed to create course")
            except HTTPException:
                raise
            except Exception as e:
                self.logger.log_message("error", f"API error creating course: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/courses/{course_id}", tags=["Courses"])
        async def get_course(course_id: int):
            """获取单个课程 / Get a specific course."""
            try:
                courses = self.schedule_manager.get_courses()
                course = next((c for c in courses if c["id"] == course_id), None)

                if course:
                    return {"success": True, "data": course}
                else:
                    raise HTTPException(status_code=404, detail="Course not found")
            except HTTPException:
                raise
            except Exception as e:
                self.logger.log_message("error", f"API error getting course: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.put("/api/courses/{course_id}", tags=["Courses"])
        async def update_course(course_id: int, updates: Dict[str, Any]):
            """更新课程 / Update a course."""
            try:
                success = self.schedule_manager.update_course(course_id, **updates)

                if success:
                    return {"success": True, "message": "Course updated"}
                else:
                    raise HTTPException(status_code=404, detail="Course not found")
            except HTTPException:
                raise
            except Exception as e:
                self.logger.log_message("error", f"API error updating course: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/api/courses/{course_id}", tags=["Courses"])
        async def delete_course(course_id: int):
            """删除课程 / Delete a course."""
            try:
                success = self.schedule_manager.delete_course(course_id)

                if success:
                    return {"success": True, "message": "Course deleted"}
                else:
                    raise HTTPException(status_code=404, detail="Course not found")
            except HTTPException:
                raise
            except Exception as e:
                self.logger.log_message("error", f"API error deleting course: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== Schedule Management ====================

        @self.app.get("/api/schedule", tags=["Schedule"])
        async def get_schedule(week: Optional[int] = Query(None, description="Week number to filter by")):
            """获取课程表 / Get schedule entries."""
            try:
                schedule = self.schedule_manager.get_schedule(week)
                return {"success": True, "data": schedule}
            except Exception as e:
                self.logger.log_message("error", f"API error getting schedule: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/schedule", tags=["Schedule"])
        async def create_schedule_entry(entry: Dict[str, Any]):
            """添加课程表条目 / Create a schedule entry."""
            try:
                required_fields = ["course_id", "day_of_week", "start_time", "end_time"]
                for field in required_fields:
                    if field not in entry:
                        raise HTTPException(status_code=400, detail=f"Field '{field}' is required")

                entry_id = self.schedule_manager.add_schedule_entry(
                    course_id=entry["course_id"],
                    day_of_week=entry["day_of_week"],
                    start_time=entry["start_time"],
                    end_time=entry["end_time"],
                    weeks=entry.get("weeks"),
                    note=entry.get("note")
                )

                if entry_id > 0:
                    return {"success": True, "data": {"id": entry_id}}
                else:
                    raise HTTPException(status_code=500, detail="Failed to create schedule entry")
            except HTTPException:
                raise
            except Exception as e:
                self.logger.log_message("error", f"API error creating schedule entry: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/schedule/day/{day_of_week}", tags=["Schedule"])
        async def get_schedule_by_day(day_of_week: int, week: Optional[int] = Query(None)):
            """获取某天的课程表 / Get schedule for a specific day."""
            try:
                if not 1 <= day_of_week <= 7:
                    raise HTTPException(status_code=400, detail="day_of_week must be between 1-7")

                classes = self.schedule_manager.get_schedule_by_day(day_of_week, week)
                return {"success": True, "data": classes}
            except HTTPException:
                raise
            except Exception as e:
                self.logger.log_message("error", f"API error getting schedule by day: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/schedule/week", tags=["Schedule"])
        async def get_schedule_for_week(week: Optional[int] = Query(None)):
            """获取整周课程表 / Get schedule for entire week."""
            try:
                classes = self.schedule_manager.get_schedule_for_week(week)
                return {"success": True, "data": classes}
            except Exception as e:
                self.logger.log_message("error", f"API error getting weekly schedule: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/api/schedule/{entry_id}", tags=["Schedule"])
        async def delete_schedule_entry(entry_id: int):
            """删除课程表条目 / Delete a schedule entry."""
            try:
                success = self.schedule_manager.delete_schedule_entry(entry_id)

                if success:
                    return {"success": True, "message": "Schedule entry deleted"}
                else:
                    raise HTTPException(status_code=404, detail="Schedule entry not found")
            except HTTPException:
                raise
            except Exception as e:
                self.logger.log_message("error", f"API error deleting schedule entry: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== Settings Management ====================

        @self.app.get("/api/settings", tags=["Settings"])
        async def get_all_settings():
            """获取所有设置 / Get all settings."""
            try:
                settings = self.settings_manager.get_all_settings()
                return {"success": True, "data": settings}
            except Exception as e:
                self.logger.log_message("error", f"API error getting settings: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/settings/{key}", tags=["Settings"])
        async def get_setting(key: str):
            """获取单个设置 / Get a specific setting."""
            try:
                value = self.settings_manager.get_setting(key)

                if value is not None:
                    return {"success": True, "data": {"key": key, "value": value}}
                else:
                    raise HTTPException(status_code=404, detail="Setting not found")
            except HTTPException:
                raise
            except Exception as e:
                self.logger.log_message("error", f"API error getting setting: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.put("/api/settings", tags=["Settings"])
        async def update_settings(settings: Dict[str, str]):
            """批量更新设置 / Update multiple settings."""
            try:
                success = self.settings_manager.update_multiple(settings)

                if success:
                    return {"success": True, "message": "Settings updated"}
                else:
                    raise HTTPException(status_code=500, detail="Failed to update settings")
            except HTTPException:
                raise
            except Exception as e:
                self.logger.log_message("error", f"API error updating settings: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.put("/api/settings/{key}", tags=["Settings"])
        async def update_setting(key: str, value: Dict[str, str]):
            """更新单个设置 / Update a specific setting."""
            try:
                val = value.get("value")
                if val is None:
                    raise HTTPException(status_code=400, detail="Value is required")

                success = self.settings_manager.set_setting(key, val)

                if success:
                    return {"success": True, "message": "Setting updated"}
                else:
                    raise HTTPException(status_code=500, detail="Failed to update setting")
            except HTTPException:
                raise
            except Exception as e:
                self.logger.log_message("error", f"API error updating setting: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/settings/reset", tags=["Settings"])
        async def reset_settings(exclude: Optional[Dict[str, List[str]]] = None):
            """重置设置为默认值 / Reset settings to defaults."""
            try:
                exclude_keys = exclude.get("exclude", []) if exclude else []
                success = self.settings_manager.reset_to_defaults(exclude_keys)

                if success:
                    return {"success": True, "message": "Settings reset to defaults"}
                else:
                    raise HTTPException(status_code=500, detail="Failed to reset settings")
            except HTTPException:
                raise
            except Exception as e:
                self.logger.log_message("error", f"API error resetting settings: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== Week Management ====================

        @self.app.get("/api/week/current", tags=["Week"])
        async def get_current_week():
            """获取当前周次 / Get current week number."""
            try:
                from . import db as _db
                week = _db.get_calculated_week_number()
                semester_start = self.settings_manager.get_setting("semester_start_date")

                return {
                    "success": True,
                    "data": {
                        "week": week,
                        "semester_start_date": semester_start,
                        "is_calculated": bool(semester_start and semester_start.strip())
                    }
                }
            except Exception as e:
                self.logger.log_message("error", f"API error getting current week: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/week/semester-start", tags=["Week"])
        async def set_semester_start(data: Dict[str, str]):
            """设置学期开始日期 / Set semester start date."""
            try:
                date = data.get("date", "")
                self.settings_manager.set_setting("semester_start_date", date)

                from . import db as _db
                week = _db.get_calculated_week_number() if date else 1

                return {
                    "success": True,
                    "data": {
                        "semester_start_date": date,
                        "calculated_week": week
                    }
                }
            except Exception as e:
                self.logger.log_message("error", f"API error setting semester start: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== Statistics ====================

        @self.app.get("/api/statistics", tags=["Statistics"])
        async def get_statistics():
            """获取课程表统计信息 / Get schedule statistics."""
            try:
                stats = self.schedule_manager.get_statistics()
                return {"success": True, "data": stats}
            except Exception as e:
                self.logger.log_message("error", f"API error getting statistics: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== Logs ====================

        @self.app.get("/api/logs", tags=["Logs"])
        async def get_logs(max_lines: int = Query(200, description="Maximum number of log lines")):
            """获取应用日志 / Get application logs."""
            try:
                lines = _logger.tail_logs(max_lines)
                return {"success": True, "data": {"lines": lines}}
            except Exception as e:
                self.logger.log_message("error", f"API error getting logs: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== Health Check ====================

        @self.app.get("/api/health", tags=["System"])
        async def health_check():
            """健康检查 / Health check endpoint."""
            return {
                "success": True,
                "data": {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0.0"
                }
            }

        @self.app.get("/", tags=["System"])
        async def root():
            """根路径 / Root endpoint."""
            return {
                "message": "ClassTop API Server",
                "version": "1.0.0",
                "docs": "/api/docs"
            }

    def start(self, host: str = "0.0.0.0", port: int = 8765):
        """Start API server in a background thread.

        Args:
            host: Host to bind to
            port: Port to bind to
        """
        if self.app is None:
            self.logger.log_message("error", "Cannot start API server: FastAPI not available")
            return False

        if self.enabled:
            self.logger.log_message("warning", "API server already running")
            return False

        def run_server():
            try:
                self.logger.log_message("info", f"Starting API server on {host}:{port}")
                uvicorn.run(self.app, host=host, port=port, log_level="warning")
            except Exception as e:
                self.logger.log_message("error", f"API server error: {e}")

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.enabled = True
        self.logger.log_message("info", "API server started")
        return True

    def stop(self):
        """Stop API server."""
        if not self.enabled:
            self.logger.log_message("warning", "API server not running")
            return False

        self.enabled = False
        self.logger.log_message("info", "API server stopped")
        return True
