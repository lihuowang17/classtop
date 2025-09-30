# --8<-- [start:command]

from anyio.from_thread import start_blocking_portal
from pytauri import (
    builder_factory,
    context_factory,
    AppHandle,
)

from . import logger as _logger
from . import db as _db
from .tray import SystemTray
from .commands import commands
from .events import event_handler
from .schedule_manager import ScheduleManager

# --8<-- [end:command]


def main() -> int:
    # initialize logger
    try:
        _logger.init_logger()
    except Exception:
        # don't fail startup if logging can't initialize
        pass

    context = context_factory()
    with start_blocking_portal("asyncio") as portal:  # or `trio`
        app = builder_factory().build(
            context=context,
            invoke_handler=commands.generate_handler(portal),
        )

        # Get app handle for event emission
        app_handle = app.handle()

        # Initialize event handler with app handle and portal for thread safety
        event_handler.initialize(app_handle, portal)

        # Initialize database and schedule manager
        try:
            _db.init_db()

            # Initialize schedule manager with event handler
            schedule_manager = ScheduleManager(_db.DB_PATH, event_handler)
            _db.set_schedule_manager(schedule_manager)

            _logger.log_message("info", "Schedule manager initialized with event handler")
        except Exception as e:
            _logger.log_message("error", f"Failed to initialize database or schedule manager: {e}")
            pass

        # Setup system tray
        system_tray = SystemTray()
        success = system_tray.setup_tray(app_handle, portal)
        if not success:
            print("Warning: Failed to setup system tray")

        exit_code = app.run_return()
        return exit_code