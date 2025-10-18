"""SQLite database layer for LMS."""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class LMSDatabase:
    """LMS 本地数据库"""

    def __init__(self, db_path: str = "lms.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # 返回字典格式
        self.init_db()
        logger.info(f"LMS database initialized at {db_path}")

    def init_db(self):
        """初始化数据库"""
        cursor = self.conn.cursor()

        # LMS 配置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lms_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 客户端注册信息
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                uuid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                ip_address TEXT,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'online',
                metadata TEXT
            )
        """)

        # 连接历史
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS connection_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_uuid TEXT NOT NULL,
                event_type TEXT NOT NULL,
                connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                disconnected_at TIMESTAMP,
                ip_address TEXT
            )
        """)

        # 命令执行日志
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_uuid TEXT NOT NULL,
                command TEXT NOT NULL,
                params TEXT,
                response TEXT,
                success BOOLEAN,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # CCTV 事件日志
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cctv_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_uuid TEXT NOT NULL,
                event_type TEXT NOT NULL,
                camera_id TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()
        logger.info("Database tables created successfully")

    def get_config(self, key: str) -> Optional[str]:
        """获取配置"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM lms_config WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result[0] if result else None

    def set_config(self, key: str, value: str):
        """设置配置"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO lms_config (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value))
        self.conn.commit()

    def register_client(self, uuid: str, name: str, ip: str, metadata: dict = None):
        """注册客户端"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO clients (uuid, name, ip_address, last_seen, status, metadata)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, 'online', ?)
        """, (uuid, name, ip, json.dumps(metadata) if metadata else None))
        self.conn.commit()
        logger.info(f"Client registered: {uuid} ({name}) from {ip}")

    def update_client_status(self, uuid: str, status: str):
        """更新客户端状态"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE clients SET status = ?, last_seen = CURRENT_TIMESTAMP
            WHERE uuid = ?
        """, (status, uuid))
        self.conn.commit()

    def log_connection(self, uuid: str, event_type: str, ip: str):
        """记录连接事件"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO connection_logs (client_uuid, event_type, ip_address)
            VALUES (?, ?, ?)
        """, (uuid, event_type, ip))
        self.conn.commit()

    def log_command(self, uuid: str, command: str, params: dict, response: dict, success: bool):
        """记录命令执行"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO command_logs (client_uuid, command, params, response, success)
            VALUES (?, ?, ?, ?, ?)
        """, (uuid, command, json.dumps(params), json.dumps(response), success))
        self.conn.commit()

    def log_cctv_event(self, uuid: str, event_type: str, camera_id: str = None, details: dict = None):
        """记录 CCTV 事件"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO cctv_logs (client_uuid, event_type, camera_id, details)
            VALUES (?, ?, ?, ?)
        """, (uuid, event_type, camera_id, json.dumps(details) if details else None))
        self.conn.commit()

    def get_online_clients(self) -> List[Dict]:
        """获取在线客户端"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT uuid, name, ip_address, last_seen, status
            FROM clients
            WHERE status = 'online'
            ORDER BY last_seen DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_all_clients(self) -> List[Dict]:
        """获取所有客户端"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT uuid, name, ip_address, last_seen, status, metadata
            FROM clients
            ORDER BY last_seen DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_client_stats(self, uuid: str) -> Dict:
        """获取客户端统计"""
        cursor = self.conn.cursor()

        # 命令执行统计
        cursor.execute("""
            SELECT
                COUNT(*) as total_commands,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_commands,
                MAX(executed_at) as last_command_time
            FROM command_logs
            WHERE client_uuid = ?
        """, (uuid,))
        result = cursor.fetchone()

        return {
            "total_commands": result[0] or 0,
            "successful_commands": result[1] or 0,
            "last_command_time": result[2]
        }

    def get_command_history(self, uuid: str, limit: int = 50) -> List[Dict]:
        """获取命令历史"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT command, params, response, success, executed_at
            FROM command_logs
            WHERE client_uuid = ?
            ORDER BY executed_at DESC
            LIMIT ?
        """, (uuid, limit))
        return [dict(row) for row in cursor.fetchall()]

    def get_cctv_events(self, uuid: str, limit: int = 100) -> List[Dict]:
        """获取 CCTV 事件"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT event_type, camera_id, details, created_at
            FROM cctv_logs
            WHERE client_uuid = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (uuid, limit))
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """关闭数据库连接"""
        self.conn.close()
        logger.info("Database connection closed")
