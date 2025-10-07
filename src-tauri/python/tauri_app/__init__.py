# --8<-- [start:command]

from . import logger as _logger

# --8<-- [end:command]


def main() -> int:
    # initialize logger
    try:
        _logger.init_logger()
    except Exception:
        # don't fail startup if logging can't initialize
        pass
    
    from anyio.from_thread import start_blocking_portal

    from pytauri import (
        builder_factory,
        context_factory
    )
    
    from .tray import SystemTray
    from .commands import commands
    from .events import event_handler
    from .schedule_manager import ScheduleManager
    from .settings_manager import SettingsManager
    from .camera_manager import CameraManager
    from .api_server import APIServer
    from . import db as _db

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

        # Initialize database and managers
        try:
            _db.init_db()

            # Initialize settings manager and default settings
            settings_manager = SettingsManager(_db.DB_PATH, event_handler)
            _db.set_settings_manager(settings_manager)
            settings_manager.initialize_defaults()
            _logger.log_message(
                "info", "Settings manager initialized with defaults")

            # Initialize schedule manager with event handler
            schedule_manager = ScheduleManager(_db.DB_PATH, event_handler)
            _db.set_schedule_manager(schedule_manager)

            # Initialize WebSocket client for admin server (before camera manager)
            ws_client = None
            try:
                from .websocket_client import WebSocketClient

                server_url = settings_manager.get_setting('server_url')
                client_uuid = settings_manager.get_setting('client_uuid')

                if server_url and client_uuid:
                    ws_client = WebSocketClient(server_url, client_uuid, settings_manager, portal)
                    # Note: ws_client.start() will be called after camera_manager initialization
                    _logger.log_message("info", "WebSocket client created")
                else:
                    _logger.log_message("info", "WebSocket client not created: server_url or client_uuid not configured")
            except Exception as e:
                _logger.log_message("error", f"Failed to create WebSocket client: {e}")

            # Initialize camera manager if enabled (with WebSocket client reference)
            camera_enabled = settings_manager.get_setting('camera_enabled')
            if camera_enabled == 'true':
                try:
                    camera_manager = CameraManager(settings_manager, event_handler, ws_client)
                    _db.set_camera_manager(camera_manager)
                    camera_manager.initialize()
                except Exception as e:
                    _logger.log_message(
                        "warning", f"Failed to initialize camera manager: {e}")

            # Start WebSocket client after camera manager is initialized
            if ws_client:
                try:
                    portal.call(ws_client.start)
                    _logger.log_message("info", "WebSocket client started")
                except Exception as e:
                    _logger.log_message("error", f"Failed to start WebSocket client: {e}")

            _logger.log_message(
                "info", "All managers initialized successfully")

            # Initialize and start API server if enabled
            try:
                api_enabled = settings_manager.get_setting('api_server_enabled')
                if api_enabled == 'true':
                    api_server = APIServer(_db.DB_PATH, schedule_manager, settings_manager)
                    api_host = settings_manager.get_setting('api_server_host') or '0.0.0.0'
                    api_port = int(settings_manager.get_setting('api_server_port') or 8765)
                    api_server.start(host=api_host, port=api_port)
                    _logger.log_message(
                        "info", f"API server started on {api_host}:{api_port}")
            except Exception as e:
                _logger.log_message(
                    "warning", f"Failed to start API server: {e}")

        except Exception as e:
            _logger.log_message(
                "error", f"Failed to initialize database or managers: {e}")
            pass

        # Setup system tray
        system_tray = SystemTray()
        success = system_tray.setup_tray(app_handle, portal)
        if not success:
            print("Warning: Failed to setup system tray")

        exit_code = app.run_return()
        return exit_code
