"""Reminder Manager - 课程提醒管理器"""
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Optional, Set
from . import logger


class ReminderManager:
    """管理课程提醒通知的后台任务"""

    def __init__(self, schedule_manager, settings_manager, app_handle=None):
        """初始化提醒管理器

        Args:
            schedule_manager: 课程表管理器
            settings_manager: 设置管理器
            app_handle: Tauri应用句柄，用于发送通知
        """
        self.schedule_manager = schedule_manager
        self.settings_manager = settings_manager
        self.app_handle = app_handle
        self.logger = logger

        # 跟踪已发送的提醒，避免重复发送 (格式: "entry_id_date")
        self.sent_reminders: Set[str] = set()

        # 后台任务
        self._task = None
        self._running = False

        self.logger.log_message("info", "ReminderManager initialized")

    def start(self):
        """启动提醒服务"""
        if self._running:
            self.logger.log_message("warning", "Reminder service already running")
            return

        self._running = True

        # 在新线程中运行异步事件循环
        def run_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._task = loop.create_task(self._reminder_loop())
            loop.run_until_complete(self._task)
            loop.close()

        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()

        self.logger.log_message("info", "Reminder service started")

    def stop(self):
        """停止提醒服务"""
        self._running = False
        if self._task:
            self._task.cancel()
        self.logger.log_message("info", "Reminder service stopped")

    async def _reminder_loop(self):
        """提醒循环 - 每分钟检查一次"""
        while self._running:
            try:
                await self._check_and_send_reminders()
                # 每60秒检查一次
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_message("error", f"Error in reminder loop: {e}")
                await asyncio.sleep(60)

    async def _check_and_send_reminders(self):
        """检查并发送课程提醒"""
        try:
            # 检查是否启用提醒
            enabled = self.settings_manager.get_setting('reminder_enabled')
            if enabled != 'true':
                return

            # 获取提醒提前时间
            reminder_minutes_str = self.settings_manager.get_setting('reminder_minutes')
            reminder_minutes = int(reminder_minutes_str) if reminder_minutes_str else 10

            # 获取当前时间和周数
            now = datetime.now()
            current_day = now.isoweekday()  # 1-7 (Monday-Sunday)
            current_time = now.strftime("%H:%M")

            # 计算当前周数
            week_number = self.schedule_manager.calculate_week_number(
                self.settings_manager.get_setting('semester_start_date')
            )

            # 获取今天的课程
            today_classes = self.schedule_manager.get_schedule_by_day(current_day, week_number)

            # 检查每节课
            for class_info in today_classes:
                start_time = class_info['start_time']
                class_id = class_info['id']

                # 生成唯一的提醒ID（包含日期，避免每天重复）
                reminder_id = f"{class_id}_{now.strftime('%Y-%m-%d')}"

                # 如果已经发送过这个提醒，跳过
                if reminder_id in self.sent_reminders:
                    continue

                # 计算距离上课的分钟数
                start_hour, start_minute = map(int, start_time.split(':'))
                start_datetime = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
                minutes_until_class = (start_datetime - now).total_seconds() / 60

                # 如果在提醒时间范围内（提前reminder_minutes分钟到上课时间之间）
                if 0 <= minutes_until_class <= reminder_minutes:
                    await self._send_notification(class_info, int(minutes_until_class))
                    self.sent_reminders.add(reminder_id)
                    self.logger.log_message("info", f"Sent reminder for class: {class_info['name']}")

            # 清理过期的提醒记录（超过24小时）
            self._cleanup_old_reminders()

        except Exception as e:
            self.logger.log_message("error", f"Error checking reminders: {e}")

    async def _send_notification(self, class_info: dict, minutes_until: int):
        """发送通知

        Args:
            class_info: 课程信息
            minutes_until: 距离上课还有多少分钟
        """
        try:
            course_name = class_info['name']
            location = class_info.get('location', '')
            teacher = class_info.get('teacher', '')

            # 构建通知标题和内容
            if minutes_until <= 0:
                title = f"课程即将开始: {course_name}"
            else:
                title = f"课程提醒: {course_name}"

            body_parts = [f"{minutes_until}分钟后上课"]
            if location:
                body_parts.append(f"地点: {location}")
            if teacher:
                body_parts.append(f"教师: {teacher}")

            body = " | ".join(body_parts)

            # 通过事件发送通知（前端监听后调用Tauri notification API）
            if self.app_handle:
                from .events import EventHandler
                event_handler = EventHandler.get_instance()
                if event_handler:
                    event_handler.emit_custom_event("course-reminder", {
                        "title": title,
                        "body": body,
                        "course_id": class_info['id'],
                        "course_name": course_name,
                        "start_time": class_info['start_time'],
                        "location": location,
                        "minutes_until": minutes_until
                    })

            self.logger.log_message("info", f"Notification sent: {title} - {body}")

        except Exception as e:
            self.logger.log_message("error", f"Error sending notification: {e}")

    def _cleanup_old_reminders(self):
        """清理超过1天的提醒记录"""
        today_str = datetime.now().strftime('%Y-%m-%d')
        self.sent_reminders = {
            r for r in self.sent_reminders
            if r.endswith(today_str)
        }

    def clear_sent_reminders(self):
        """手动清空已发送的提醒记录（用于测试）"""
        self.sent_reminders.clear()
        self.logger.log_message("info", "Cleared all sent reminders")
