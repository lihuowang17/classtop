"""Settings Manager - 统一管理应用设置"""
import sqlite3
import uuid
from pathlib import Path
from typing import Dict, Optional, Any
from . import logger


class SettingsManager:
    """设置管理器，负责设置的初始化、读取和更新"""

    # 默认设置项定义
    DEFAULT_SETTINGS = {
        # 通用设置
        'client_uuid': lambda: str(uuid.uuid4()),
        'server_url': '',

        # 外观设置
        'theme_mode': 'auto',  # auto, dark, light
        'theme_color': '#6750A4',  # Material Design default purple

        # 组件设置
        'show_clock': 'true',
        'show_schedule': 'true',

        # 课程设置
        'semester_start_date': '',
    }

    def __init__(self, db_path: Path, event_handler):
        """初始化设置管理器

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.event_handler = event_handler
        self.logger = logger
        self.logger.log_message("info", "SettingsManager initialized")

    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    def initialize_defaults(self) -> None:
        """初始化默认设置（如果不存在）"""
        self.logger.log_message("info", "Initializing default settings")

        with self.get_connection() as conn:
            cur = conn.cursor()

            for key, default_value in self.DEFAULT_SETTINGS.items():
                # 检查设置是否已存在
                cur.execute("SELECT value FROM settings WHERE key=?", (key,))
                existing = cur.fetchone()

                if not existing:
                    # 如果默认值是函数（如 uuid），调用它
                    value = default_value() if callable(default_value) else default_value
                    cur.execute(
                        "INSERT INTO settings(key, value) VALUES(?, ?)",
                        (key, str(value))
                    )
                    self.logger.log_message("debug", f"Initialized setting: {key} = {value}")

            conn.commit()

        self.logger.log_message("info", "Default settings initialized")

    def get_setting(self, key: str) -> Optional[str]:
        """获取单个设置值

        Args:
            key: 设置键名

        Returns:
            设置值，如果不存在返回 None
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM settings WHERE key=?", (key,))
            row = cur.fetchone()
            return row[0] if row else None

    def set_setting(self, key: str, value: str) -> bool:
        """设置单个设置值

        Args:
            key: 设置键名
            value: 设置值

        Returns:
            是否成功
        """
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO settings(key, value) VALUES(?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                    (key, str(value))
                )
                conn.commit()
                
            # Emit event if handler is available
            if self.event_handler:
                self.event_handler.emit_setting_update(key, value)

            self.logger.log_message("info", f"Setting updated: {key} = {value}")
            return True
        except Exception as e:
            self.logger.log_message("error", f"Error setting {key}: {e}")
            return False

    def get_all_settings(self) -> Dict[str, str]:
        """获取所有设置

        Returns:
            设置字典 {key: value}
        """
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT key, value FROM settings")
            return {k: v for k, v in cur.fetchall()}

    def update_multiple(self, settings: Dict[str, str]) -> bool:
        """批量更新设置

        Args:
            settings: 设置字典

        Returns:
            是否全部成功
        """
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                for key, value in settings.items():
                    cur.execute(
                        "INSERT INTO settings(key, value) VALUES(?, ?) "
                        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                        (key, str(value))
                    )
                conn.commit()

            # Emit batch update event
            if self.event_handler:
                self.event_handler.emit_settings_batch_updated(list(settings.keys()))

            self.logger.log_message("info", f"Updated {len(settings)} settings")
            return True
        except Exception as e:
            self.logger.log_message("error", f"Error updating settings: {e}")
            return False

    def regenerate_uuid(self) -> str:
        """重新生成客户端 UUID

        Returns:
            新的 UUID
        """
        new_uuid = str(uuid.uuid4())
        self.set_setting('client_uuid', new_uuid)
        self.logger.log_message("info", f"Regenerated client UUID: {new_uuid}")
        return new_uuid

    def reset_to_defaults(self, exclude_keys: Optional[list] = None) -> bool:
        """重置设置为默认值

        Args:
            exclude_keys: 要排除的设置键列表（不重置）

        Returns:
            是否成功
        """
        exclude_keys = exclude_keys or []

        try:
            for key, default_value in self.DEFAULT_SETTINGS.items():
                if key not in exclude_keys:
                    value = default_value() if callable(default_value) else default_value
                    self.set_setting(key, str(value))

            self.logger.log_message("info", "Settings reset to defaults")
            return True
        except Exception as e:
            self.logger.log_message("error", f"Error resetting settings: {e}")
            return False