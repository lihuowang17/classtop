"""WebSocket client for connecting to admin server."""
import asyncio
import json
from typing import Optional, Dict, Any, Callable
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException
from . import logger


class WebSocketClient:
    """WebSocket client that connects to admin server."""

    def __init__(self, server_url: str, client_uuid: str, settings_manager, portal):
        """
        Initialize WebSocket client.

        Args:
            server_url: Admin server URL (e.g., ws://localhost:8000)
            client_uuid: Client UUID for identification
            settings_manager: Settings manager instance
            portal: Async portal for running async tasks
        """
        self.server_url = server_url.strip()
        self.client_uuid = client_uuid
        self.settings_manager = settings_manager
        self.portal = portal
        self.logger = logger

        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        self.reconnect_delay = 5  # seconds
        self.heartbeat_interval = 30  # seconds

        # Task references
        self._connect_task: Optional[asyncio.Task] = None
        self._listen_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start WebSocket client with auto-reconnect."""
        if self.running:
            self.logger.log_message("warning", "WebSocket client already running")
            return

        if not self.server_url:
            self.logger.log_message("warning", "Server URL not configured, WebSocket client not started")
            return

        self.running = True
        self._connect_task = asyncio.create_task(self._connect_loop())
        self.logger.log_message("info", f"WebSocket client started, connecting to {self.server_url}")

    async def stop(self):
        """Stop WebSocket client."""
        self.running = False

        # Cancel tasks
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._listen_task:
            self._listen_task.cancel()
        if self._connect_task:
            self._connect_task.cancel()

        # Close connection
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

        self.logger.log_message("info", "WebSocket client stopped")

    async def _connect_loop(self):
        """Connection loop with auto-reconnect."""
        while self.running:
            try:
                # Build WebSocket URL
                ws_url = self.server_url.replace('http://', 'ws://').replace('https://', 'wss://')
                if not ws_url.startswith('ws://') and not ws_url.startswith('wss://'):
                    ws_url = f'ws://{ws_url}'
                ws_url = f"{ws_url.rstrip('/')}/ws/{self.client_uuid}"

                self.logger.log_message("info", f"Connecting to admin server: {ws_url}")

                async with websockets.connect(ws_url, ping_interval=20, ping_timeout=10) as websocket:
                    self.websocket = websocket
                    self.logger.log_message("info", "Connected to admin server")

                    # Send initial state
                    await self._send_state_update()

                    # Start heartbeat
                    self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

                    # Listen for messages
                    await self._listen()

            except ConnectionClosed:
                self.logger.log_message("warning", "Connection to admin server closed")
            except WebSocketException as e:
                self.logger.log_message("error", f"WebSocket error: {e}")
            except Exception as e:
                self.logger.log_message("error", f"Error connecting to admin server: {e}")

            # Cleanup
            self.websocket = None
            if self._heartbeat_task:
                self._heartbeat_task.cancel()
                self._heartbeat_task = None

            # Reconnect delay
            if self.running:
                self.logger.log_message("info", f"Reconnecting in {self.reconnect_delay} seconds...")
                await asyncio.sleep(self.reconnect_delay)

    async def _listen(self):
        """Listen for messages from server."""
        if not self.websocket:
            return

        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError as e:
                    self.logger.log_message("error", f"Invalid JSON from server: {e}")
                except Exception as e:
                    self.logger.log_message("error", f"Error handling message: {e}")
        except ConnectionClosed:
            pass

    async def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming message from server."""
        message_type = data.get('type')

        if message_type == 'command':
            await self._handle_command(data)
        else:
            self.logger.log_message("warning", f"Unknown message type: {message_type}")

    async def _handle_command(self, data: Dict[str, Any]):
        """Handle command from server."""
        request_id = data.get('request_id')
        command = data.get('command')
        params = data.get('params', {})

        self.logger.log_message("info", f"Received command: {command}")

        try:
            # Execute command
            result = await self._execute_command(command, params)

            # Send response
            response = {
                'type': 'response',
                'request_id': request_id,
                'success': True,
                'data': result
            }
        except Exception as e:
            self.logger.log_message("error", f"Error executing command {command}: {e}")
            response = {
                'type': 'response',
                'request_id': request_id,
                'success': False,
                'error': str(e)
            }

        if self.websocket:
            await self.websocket.send(json.dumps(response))

    async def _execute_command(self, command: str, params: Dict[str, Any]) -> Any:
        """Execute a command and return result."""
        from . import db as _db

        # Map commands to functions
        if command == 'get_all_settings':
            if self.settings_manager:
                return self.settings_manager.get_all_settings()
            return {}

        elif command == 'get_setting':
            key = params.get('key')
            if self.settings_manager and key:
                return self.settings_manager.get_setting(key)
            return None

        elif command == 'set_setting':
            key = params.get('key')
            value = params.get('value')
            if self.settings_manager and key:
                success = self.settings_manager.set_setting(key, str(value))
                return {'success': success}
            return {'success': False}

        elif command == 'update_settings_batch':
            settings = params.get('settings', {})
            if self.settings_manager:
                success = self.settings_manager.update_multiple(settings)
                return {'success': success}
            return {'success': False}

        elif command == 'refresh_state':
            await self._send_state_update()
            return {'success': True}

        # Camera commands
        elif command == 'camera_initialize':
            if not _db.camera_manager:
                return {'success': False, 'message': 'Camera manager not available'}
            success = _db.camera_manager.initialize()
            if success:
                cameras = _db.camera_manager.get_cameras()
                return {'success': True, 'camera_count': len(cameras), 'cameras': cameras}
            return {'success': False, 'message': 'Failed to initialize camera'}

        elif command == 'camera_get_cameras':
            if not _db.camera_manager:
                return {'cameras': []}
            return {'cameras': _db.camera_manager.get_cameras()}

        elif command == 'camera_get_encoders':
            if not _db.camera_manager:
                return {'h264': {'available': 0, 'encoders': []}, 'h265': {'available': 0, 'encoders': []}}
            return _db.camera_manager.get_encoders()

        elif command == 'camera_start_recording':
            if not _db.camera_manager:
                return {'success': False, 'message': 'Camera manager not available'}
            success = _db.camera_manager.start_recording(
                camera_index=params.get('camera_index', 0),
                filename=params.get('filename'),
                codec_type=params.get('codec_type'),
                width=params.get('width'),
                height=params.get('height'),
                fps=params.get('fps'),
                preset=params.get('preset'),
                bitrate=params.get('bitrate')
            )
            return {'success': success}

        elif command == 'camera_stop_recording':
            if not _db.camera_manager:
                return {'success': False, 'message': 'Camera manager not available'}
            success = _db.camera_manager.stop_recording(params.get('camera_index', 0))
            return {'success': success}

        elif command == 'camera_get_status':
            if not _db.camera_manager:
                return {'status': {'active_cameras': 0, 'streamers': {}}}
            status = _db.camera_manager.get_status(params.get('camera_index'))
            return {'status': status}

        elif command == 'camera_start_streaming':
            if not _db.camera_manager:
                return {'success': False, 'message': 'Camera manager not available'}
            success = _db.camera_manager.start_streaming(params.get('camera_index', 0))
            return {'success': success}

        elif command == 'camera_stop_streaming':
            if not _db.camera_manager:
                return {'success': False, 'message': 'Camera manager not available'}
            success = _db.camera_manager.stop_streaming(params.get('camera_index', 0))
            return {'success': success}

        elif command == 'camera_start_preview':
            if not _db.camera_manager:
                return {'success': False, 'message': 'Camera manager not available'}
            fps = params.get('fps', 10)
            success = _db.camera_manager.start_preview(params.get('camera_index', 0), fps)
            return {'success': success}

        elif command == 'camera_stop_preview':
            if not _db.camera_manager:
                return {'success': False, 'message': 'Camera manager not available'}
            success = _db.camera_manager.stop_preview(params.get('camera_index', 0))
            return {'success': success}

        else:
            raise ValueError(f"Unknown command: {command}")

    async def _heartbeat_loop(self):
        """Send periodic heartbeat to server."""
        while self.running and self.websocket:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                if self.websocket:
                    heartbeat = {
                        'type': 'heartbeat',
                        'timestamp': asyncio.get_event_loop().time()
                    }
                    await self.websocket.send(json.dumps(heartbeat))

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_message("error", f"Error sending heartbeat: {e}")
                break

    async def _send_state_update(self):
        """Send state update to server."""
        if not self.websocket:
            return

        try:
            # Collect current state
            state_data = {}

            # Get settings
            if self.settings_manager:
                state_data['settings'] = self.settings_manager.get_all_settings()

            # Send update
            message = {
                'type': 'state_update',
                'data': state_data
            }

            await self.websocket.send(json.dumps(message))
            self.logger.log_message("debug", "Sent state update to admin server")

        except Exception as e:
            self.logger.log_message("error", f"Error sending state update: {e}")

    def update_server_url(self, new_url: str):
        """Update server URL and reconnect."""
        if new_url != self.server_url:
            self.server_url = new_url.strip()
            self.logger.log_message("info", f"Server URL updated to: {self.server_url}")

            # Restart connection
            if self.running:
                asyncio.create_task(self._restart_connection())

    async def _restart_connection(self):
        """Restart connection with new URL."""
        if self.websocket:
            await self.websocket.close()

    def send_camera_frame(self, camera_index: int, frame_base64: str):
        """Send camera frame to server (non-blocking).

        Args:
            camera_index: Camera index
            frame_base64: Base64 encoded JPEG frame
        """
        if not self.websocket or not self.running:
            return

        # Send frame asynchronously without blocking
        message = {
            'type': 'camera_frame',
            'camera_index': camera_index,
            'frame': frame_base64
        }

        # Use portal to send from non-async thread
        async def send_frame():
            try:
                if self.websocket:
                    await self.websocket.send(json.dumps(message))
            except Exception as e:
                # Silently fail for frame transmission errors
                pass

        try:
            if self.portal:
                self.portal.start_task_soon(send_frame)
        except Exception:
            pass  # Silently fail if portal unavailable
