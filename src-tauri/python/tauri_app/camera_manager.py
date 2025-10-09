"""Camera Manager - 摄像头监控管理器"""
from pathlib import Path
from typing import Optional, Dict, List
import threading

from .camera_monitor import (
    CameraMonitor,
    MonitorConfig,
    RecordingOptions
)
from . import logger


class CameraManager:
    """摄像头管理器，负责摄像头的初始化、录制和状态管理"""

    def __init__(self, settings_manager, event_handler, websocket_client=None):
        """初始化摄像头管理器

        Args:
            settings_manager: 设置管理器实例
            event_handler: 事件处理器实例
            websocket_client: WebSocket客户端实例（用于发送视频帧）
        """
        self.settings_manager = settings_manager
        self.event_handler = event_handler
        self.websocket_client = websocket_client
        self.logger = logger
        self.monitor: Optional[CameraMonitor] = None
        self._lock = threading.Lock()
        self._initialized = False

        self.logger.log_message("info", "CameraManager initialized")

    def initialize(self) -> bool:
        """初始化摄像头监控系统

        Returns:
            是否成功初始化
        """
        with self._lock:
            if self._initialized:
                self.logger.log_message("warning", "CameraManager already initialized")
                return True

            try:
                # 从设置加载配置
                config = self._load_config_from_settings()

                # 创建并初始化 monitor
                self.monitor = CameraMonitor(config)
                self.monitor.initialize()

                self._initialized = True
                self.logger.log_message("info", "Camera monitoring system initialized")

                # 发送初始化事件
                if self.event_handler:
                    cameras = self.monitor.get_cameras()
                    encoders = self.monitor.get_encoders()
                    self.event_handler.emit_camera_initialized(
                        camera_count=len(cameras),
                        encoder_info=encoders
                    )

                return True

            except Exception as e:
                self.logger.log_message("error", f"Failed to initialize camera system: {e}")
                import traceback
                traceback.print_exc()
                return False

    def _load_config_from_settings(self) -> MonitorConfig:
        """从设置管理器加载配置

        Returns:
            MonitorConfig 实例
        """
        config = MonitorConfig()

        # 摄像头设置
        if width := self.settings_manager.get_setting('camera_width'):
            config.camera.width = int(width)
        if height := self.settings_manager.get_setting('camera_height'):
            config.camera.height = int(height)
        if fps := self.settings_manager.get_setting('camera_fps'):
            config.camera.fps = int(fps)
        if encoder_pref := self.settings_manager.get_setting('camera_encoder_preference'):
            config.camera.encoder_preference = encoder_pref

        # 编码器设置
        if nvenc_preset := self.settings_manager.get_setting('encoder_nvenc_preset'):
            config.encoder.nvenc_preset = nvenc_preset
        if nvenc_bitrate := self.settings_manager.get_setting('encoder_nvenc_bitrate'):
            config.encoder.nvenc_bitrate = nvenc_bitrate

        # 录制设置
        if output_dir := self.settings_manager.get_setting('recording_output_dir'):
            config.recording.output_dir = output_dir
        if filename_pattern := self.settings_manager.get_setting('recording_filename_pattern'):
            config.recording.filename_pattern = filename_pattern

        # 禁用 API（因为 classtop 已经有自己的 API）
        config.api.enabled = False

        # 启用详细日志
        config.verbose_logging = True

        return config

    def get_cameras(self) -> List[Dict]:
        """获取可用摄像头列表

        Returns:
            摄像头信息列表
        """
        if not self._initialized or not self.monitor:
            return []

        try:
            return self.monitor.get_cameras()
        except Exception as e:
            self.logger.log_message("error", f"Error getting cameras: {e}")
            return []

    def get_encoders(self) -> Dict:
        """获取可用编码器信息

        Returns:
            编码器信息字典
        """
        if not self._initialized or not self.monitor:
            return {"h264": {"available": 0, "encoders": []}, "h265": {"available": 0, "encoders": []}}

        try:
            return self.monitor.get_encoders()
        except Exception as e:
            self.logger.log_message("error", f"Error getting encoders: {e}")
            return {"h264": {"available": 0, "encoders": []}, "h265": {"available": 0, "encoders": []}}

    def start_recording(
        self,
        camera_index: int,
        filename: Optional[str] = None,
        codec_type: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fps: Optional[int] = None,
        preset: Optional[str] = None,
        bitrate: Optional[str] = None
    ) -> bool:
        """开始录制

        Args:
            camera_index: 摄像头索引
            filename: 可选的文件名
            codec_type: 编码类型 ('H.264' 或 'H.265')
            width: 可选的宽度
            height: 可选的高度
            fps: 可选的帧率
            preset: 可选的预设
            bitrate: 可选的比特率

        Returns:
            是否成功开始录制
        """
        if not self._initialized or not self.monitor:
            self.logger.log_message("error", "Camera system not initialized")
            return False

        try:
            # 创建录制选项
            opts = None
            if any([codec_type, width, height, fps, preset, bitrate, filename]):
                opts = RecordingOptions(
                    codec_type=codec_type,
                    width=width,
                    height=height,
                    fps=fps,
                    preset=preset,
                    bitrate=bitrate,
                    filename=filename
                )

            success = self.monitor.start_recording(camera_index, options=opts)

            if success:
                self.logger.log_message("info", f"Started recording on camera {camera_index}")

                # 发送录制开始事件
                if self.event_handler:
                    status = self.monitor.get_status(camera_index)
                    self.event_handler.emit_camera_recording_started(
                        camera_index=camera_index,
                        filename=status.get('current_recording', 'unknown')
                    )

            return success

        except Exception as e:
            self.logger.log_message("error", f"Error starting recording: {e}")
            import traceback
            traceback.print_exc()
            return False

    def stop_recording(self, camera_index: int) -> bool:
        """停止录制

        Args:
            camera_index: 摄像头索引

        Returns:
            是否成功停止录制
        """
        if not self._initialized or not self.monitor:
            self.logger.log_message("error", "Camera system not initialized")
            return False

        try:
            success = self.monitor.stop_recording(camera_index)

            if success:
                self.logger.log_message("info", f"Stopped recording on camera {camera_index}")

                # 发送录制停止事件
                if self.event_handler:
                    self.event_handler.emit_camera_recording_stopped(camera_index=camera_index)

            return success

        except Exception as e:
            self.logger.log_message("error", f"Error stopping recording: {e}")
            return False

    def start_streaming(self, camera_index: int) -> bool:
        """开始视频流

        Args:
            camera_index: 摄像头索引

        Returns:
            是否成功
        """
        if not self._initialized or not self.monitor:
            return False

        try:
            return self.monitor.start_streaming(camera_index)
        except Exception as e:
            self.logger.log_message("error", f"Error starting streaming: {e}")
            return False

    def stop_streaming(self, camera_index: int) -> bool:
        """停止视频流

        Args:
            camera_index: 摄像头索引

        Returns:
            是否成功
        """
        if not self._initialized or not self.monitor:
            return False

        try:
            return self.monitor.stop_streaming(camera_index)
        except Exception as e:
            self.logger.log_message("error", f"Error stopping streaming: {e}")
            return False

    def start_preview(self, camera_index: int = 0, fps: int = 10) -> bool:
        """开始视频预览（通过WebSocket发送帧）

        Args:
            camera_index: 摄像头索引
            fps: 预览帧率（默认10fps以节省带宽）

        Returns:
            是否成功
        """
        if not self._initialized or not self.monitor:
            return False

        try:
            # 首先确保流传输已启动
            if not self.monitor.start_streaming(camera_index):
                self.logger.log_message("error", f"Failed to start streaming for preview on camera {camera_index}")
                return False

            # 启动预览帧发送线程
            import threading
            import time
            import base64

            def preview_loop():
                interval = 1.0 / fps
                streamer = self.monitor.get_streamer(camera_index)

                while hasattr(self, '_preview_active') and self._preview_active.get(camera_index, False):
                    try:
                        # 获取当前帧
                        frame_bytes = streamer.get_frame()

                        if frame_bytes:
                            # 将帧编码为base64
                            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')

                            # 通过WebSocket客户端发送帧（如果有的话）
                            if hasattr(self, 'websocket_client') and self.websocket_client:
                                self.websocket_client.send_camera_frame(camera_index, frame_base64)

                        time.sleep(interval)
                    except Exception as e:
                        self.logger.log_message("error", f"Preview loop error: {e}")
                        break

            if not hasattr(self, '_preview_active'):
                self._preview_active = {}
            if not hasattr(self, '_preview_threads'):
                self._preview_threads = {}

            self._preview_active[camera_index] = True
            self._preview_threads[camera_index] = threading.Thread(target=preview_loop, daemon=True)
            self._preview_threads[camera_index].start()

            self.logger.log_message("info", f"Started preview on camera {camera_index} at {fps} fps")
            return True

        except Exception as e:
            self.logger.log_message("error", f"Error starting preview: {e}")
            return False

    def stop_preview(self, camera_index: int = 0) -> bool:
        """停止视频预览

        Args:
            camera_index: 摄像头索引

        Returns:
            是否成功
        """
        if not self._initialized or not self.monitor:
            return False

        try:
            # 停止预览线程
            if hasattr(self, '_preview_active') and camera_index in self._preview_active:
                self._preview_active[camera_index] = False

            self.logger.log_message("info", f"Stopped preview on camera {camera_index}")
            return True

        except Exception as e:
            self.logger.log_message("error", f"Error stopping preview: {e}")
            return False

    def get_status(self, camera_index: Optional[int] = None) -> Dict:
        """获取摄像头状态

        Args:
            camera_index: 摄像头索引，None 表示获取所有

        Returns:
            状态字典
        """
        if not self._initialized or not self.monitor:
            return {"active_cameras": 0, "streamers": {}}

        try:
            return self.monitor.get_status(camera_index)
        except Exception as e:
            self.logger.log_message("error", f"Error getting status: {e}")
            return {"active_cameras": 0, "streamers": {}}

    def cleanup(self):
        """清理资源"""
        with self._lock:
            if self.monitor:
                try:
                    self.monitor.cleanup()
                    self.logger.log_message("info", "Camera monitor cleaned up")
                except Exception as e:
                    self.logger.log_message("error", f"Error cleaning up: {e}")

            self._initialized = False
            self.monitor = None
