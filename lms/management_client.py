"""Management-Server client for LMS registration and heartbeat."""
import requests
import uuid as uuid_lib
import socket
import time
import threading
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ManagementClient:
    """连接到 Management-Server 的客户端"""

    def __init__(self, management_url: str, lms_db):
        self.management_url = management_url
        self.lms_db = lms_db
        self.lms_uuid = self._get_or_create_uuid()
        self.api_key = None
        self.heartbeat_thread = None
        self.is_running = False

    def _get_or_create_uuid(self) -> str:
        """获取或创建 LMS UUID"""
        lms_uuid = self.lms_db.get_config('lms_uuid')

        if lms_uuid:
            logger.info(f"Using existing LMS UUID: {lms_uuid}")
            return lms_uuid
        else:
            lms_uuid = str(uuid_lib.uuid4())
            self.lms_db.set_config('lms_uuid', lms_uuid)
            logger.info(f"Generated new LMS UUID: {lms_uuid}")
            return lms_uuid

    def register(self) -> bool:
        """注册 LMS 到 Management-Server"""
        try:
            # 获取主机信息
            hostname = socket.gethostname()
            try:
                host_ip = socket.gethostbyname(hostname)
            except:
                host_ip = "127.0.0.1"

            data = {
                "lms_uuid": self.lms_uuid,
                "name": f"LMS-{hostname}",
                "host": host_ip,
                "port": 8000,  # LMS 端口
                "version": "1.0.0"
            }

            url = f"{self.management_url}/api/lms/register"
            logger.info(f"Registering LMS to Management-Server at {url}")

            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                self.api_key = result.get("data", {}).get("api_key")
                # 保存 API Key
                self.lms_db.set_config('api_key', self.api_key)
                logger.info(f"✓ LMS registered successfully: {self.lms_uuid}")
                return True
            else:
                logger.error(f"✗ Registration failed: {result.get('message')}")
                return False

        except requests.exceptions.ConnectionError:
            logger.warning(f"✗ Cannot connect to Management-Server at {self.management_url}")
            return False
        except Exception as e:
            logger.error(f"✗ LMS registration failed: {e}")
            return False

    def start_heartbeat(self):
        """启动心跳线程"""
        if self.is_running:
            logger.warning("Heartbeat already running")
            return

        # 尝试加载已保存的 API Key
        if not self.api_key:
            self.api_key = self.lms_db.get_config('api_key')

        if not self.api_key:
            logger.error("No API key available, cannot start heartbeat")
            return

        self.is_running = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
        logger.info("Heartbeat thread started")

    def _heartbeat_loop(self):
        """心跳循环"""
        while self.is_running:
            try:
                # 获取在线客户端列表
                clients = self.lms_db.get_online_clients()

                data = {
                    "lms_uuid": self.lms_uuid,
                    "client_count": len(clients),
                    "clients": [
                        {
                            "uuid": c["uuid"],
                            "name": c["name"],
                            "status": c["status"]
                        }
                        for c in clients
                    ]
                }

                headers = {"Authorization": f"Bearer {self.api_key}"}
                url = f"{self.management_url}/api/lms/heartbeat"

                response = requests.post(url, json=data, headers=headers, timeout=5)

                if response.status_code == 200:
                    logger.debug(f"✓ Heartbeat sent: {len(clients)} online clients")
                else:
                    logger.warning(f"✗ Heartbeat failed with status {response.status_code}")

            except requests.exceptions.ConnectionError:
                logger.debug("✗ Management-Server not reachable")
            except Exception as e:
                logger.error(f"✗ Heartbeat error: {e}")

            # 每30秒一次
            time.sleep(30)

    def stop_heartbeat(self):
        """停止心跳"""
        self.is_running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
        logger.info("Heartbeat thread stopped")

    def sync_client_data(self, client_uuid: str, client_data: dict) -> bool:
        """同步客户端数据到 Management-Server"""
        if not self.api_key:
            return False

        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            url = f"{self.management_url}/api/lms/sync-client"

            data = {
                "lms_uuid": self.lms_uuid,
                "client_uuid": client_uuid,
                "client_data": client_data
            }

            response = requests.post(url, json=data, headers=headers, timeout=10)
            return response.status_code == 200

        except Exception as e:
            logger.error(f"Failed to sync client data: {e}")
            return False
