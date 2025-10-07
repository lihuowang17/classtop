"""WebSocket connection manager for handling multiple clients."""
import asyncio
import json
from datetime import datetime
from typing import Dict, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from models import ClientInfo, ClientStatus, CommandRequest, CommandResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections from multiple clients."""

    def __init__(self):
        # Active connections: {client_uuid: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}

        # Client information: {client_uuid: ClientInfo}
        self.clients: Dict[str, ClientInfo] = {}

        # Pending responses: {request_id: asyncio.Future}
        self.pending_requests: Dict[str, asyncio.Future] = {}

        # Viewer connections for camera preview: {viewer_id: {websocket, watching_client}}
        self.viewers: Dict[str, Dict[str, Any]] = {}

        self._request_counter = 0

    async def connect(self, websocket: WebSocket, client_uuid: str, client_ip: str = None):
        """Accept a new client connection."""
        await websocket.accept()

        self.active_connections[client_uuid] = websocket

        # Update or create client info
        if client_uuid in self.clients:
            self.clients[client_uuid].status = ClientStatus.ONLINE
            self.clients[client_uuid].last_seen = datetime.now()
            self.clients[client_uuid].ip_address = client_ip
        else:
            self.clients[client_uuid] = ClientInfo(
                uuid=client_uuid,
                status=ClientStatus.ONLINE,
                last_seen=datetime.now(),
                ip_address=client_ip
            )

        logger.info(f"Client {client_uuid} connected from {client_ip}")

    def disconnect(self, client_uuid: str):
        """Remove a client connection."""
        if client_uuid in self.active_connections:
            del self.active_connections[client_uuid]

        if client_uuid in self.clients:
            self.clients[client_uuid].status = ClientStatus.OFFLINE
            self.clients[client_uuid].last_seen = datetime.now()

        logger.info(f"Client {client_uuid} disconnected")

    async def send_message(self, client_uuid: str, message: Dict[str, Any]) -> bool:
        """Send a message to a specific client."""
        if client_uuid not in self.active_connections:
            logger.warning(f"Client {client_uuid} not connected")
            return False

        try:
            websocket = self.active_connections[client_uuid]
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"Error sending message to {client_uuid}: {e}")
            self.disconnect(client_uuid)
            return False

    async def send_command(self, client_uuid: str, command: str, params: Optional[Dict[str, Any]] = None, timeout: float = 30.0) -> CommandResponse:
        """
        Send a command to client and wait for response.

        Args:
            client_uuid: Target client UUID
            command: Command name
            params: Command parameters
            timeout: Timeout in seconds

        Returns:
            CommandResponse from the client
        """
        if client_uuid not in self.active_connections:
            return CommandResponse(success=False, error="Client not connected")

        # Generate request ID
        self._request_counter += 1
        request_id = f"req_{self._request_counter}_{datetime.now().timestamp()}"

        # Create future for response
        future = asyncio.Future()
        self.pending_requests[request_id] = future

        # Send command
        message = {
            "type": "command",
            "request_id": request_id,
            "command": command,
            "params": params or {}
        }

        success = await self.send_message(client_uuid, message)
        if not success:
            del self.pending_requests[request_id]
            return CommandResponse(success=False, error="Failed to send command")

        # Wait for response
        try:
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            del self.pending_requests[request_id]
            return CommandResponse(success=False, error="Command timeout")
        except Exception as e:
            if request_id in self.pending_requests:
                del self.pending_requests[request_id]
            return CommandResponse(success=False, error=str(e))

    async def handle_message(self, client_uuid: str, message: Dict[str, Any]):
        """Handle incoming message from client."""
        message_type = message.get("type")

        if message_type == "response":
            # Handle command response
            request_id = message.get("request_id")
            if request_id in self.pending_requests:
                response = CommandResponse(
                    success=message.get("success", False),
                    data=message.get("data"),
                    error=message.get("error")
                )
                self.pending_requests[request_id].set_result(response)
                del self.pending_requests[request_id]

        elif message_type == "heartbeat":
            # Update last seen time
            if client_uuid in self.clients:
                self.clients[client_uuid].last_seen = datetime.now()

        elif message_type == "state_update":
            # Update client state
            if client_uuid in self.clients:
                data = message.get("data", {})
                if "settings" in data:
                    self.clients[client_uuid].settings = data["settings"]
                self.clients[client_uuid].last_seen = datetime.now()

        elif message_type == "camera_frame":
            # Broadcast camera frame to all viewers
            await self.broadcast_camera_frame(client_uuid, message)

        else:
            logger.warning(f"Unknown message type from {client_uuid}: {message_type}")

    async def listen_to_client(self, client_uuid: str):
        """Listen to messages from a client."""
        websocket = self.active_connections.get(client_uuid)
        if not websocket:
            return

        try:
            while True:
                message = await websocket.receive_json()
                await self.handle_message(client_uuid, message)
        except WebSocketDisconnect:
            self.disconnect(client_uuid)
        except Exception as e:
            logger.error(f"Error listening to client {client_uuid}: {e}")
            self.disconnect(client_uuid)

    def get_client_info(self, client_uuid: str) -> Optional[ClientInfo]:
        """Get information about a specific client."""
        return self.clients.get(client_uuid)

    def get_all_clients(self) -> Dict[str, ClientInfo]:
        """Get information about all clients."""
        return self.clients

    def get_online_clients(self) -> Dict[str, ClientInfo]:
        """Get information about online clients."""
        return {
            uuid: info for uuid, info in self.clients.items()
            if info.status == ClientStatus.ONLINE
        }

    async def add_viewer(self, websocket: WebSocket, viewer_id: str, client_uuid: str):
        """Add a viewer websocket connection for camera preview.

        Args:
            websocket: Viewer's websocket connection
            viewer_id: Unique viewer ID
            client_uuid: Client UUID to watch
        """
        await websocket.accept()
        self.viewers[viewer_id] = {
            'websocket': websocket,
            'watching_client': client_uuid
        }
        logger.info(f"Viewer {viewer_id} connected to watch client {client_uuid}")

    def remove_viewer(self, viewer_id: str):
        """Remove a viewer connection."""
        if viewer_id in self.viewers:
            del self.viewers[viewer_id]
            logger.info(f"Viewer {viewer_id} disconnected")

    async def broadcast_camera_frame(self, client_uuid: str, frame_message: Dict[str, Any]):
        """Broadcast camera frame to all viewers watching this client.

        Args:
            client_uuid: Source client UUID
            frame_message: Frame message containing camera_index and frame data
        """
        # Find all viewers watching this client
        viewers_to_remove = []

        for viewer_id, viewer_info in self.viewers.items():
            if viewer_info['watching_client'] == client_uuid:
                try:
                    await viewer_info['websocket'].send_json({
                        'type': 'camera_frame',
                        'client_uuid': client_uuid,
                        'camera_index': frame_message.get('camera_index'),
                        'frame': frame_message.get('frame')
                    })
                except Exception as e:
                    logger.error(f"Error sending frame to viewer {viewer_id}: {e}")
                    viewers_to_remove.append(viewer_id)

        # Remove disconnected viewers
        for viewer_id in viewers_to_remove:
            self.remove_viewer(viewer_id)


# Global instance
manager = WebSocketManager()
