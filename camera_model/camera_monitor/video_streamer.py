"""Video streaming and recording using OpenCV and FFmpeg."""
import subprocess
import os
import cv2
import threading
from datetime import datetime
from typing import Optional
from .config import MonitorConfig, CameraConfig, EncoderConfig, RecordingConfig, RecordingOptions, StreamingConfig


class VideoStreamer:
    """Handles video streaming and recording."""

    def __init__(
        self,
        camera_name: str,
        camera_index: int,
        encoder: str = "libx264",
        config: Optional[MonitorConfig] = None
    ):
        self.camera_name = camera_name
        self.camera_index = camera_index
        self.encoder = encoder
        self.config = config or MonitorConfig.create_default()

        self.width = self.config.camera.width
        self.height = self.config.camera.height
        self.fps = self.config.camera.fps

        self.cap: Optional[cv2.VideoCapture] = None
        self.record_process: Optional[subprocess.Popen] = None
        self.is_streaming = False
        self.is_recording = False
        self.current_frame = None
        self.frame_lock = threading.Lock()

        # Create recordings directory
        if self.config.recording.create_dir:
            os.makedirs(self.config.recording.output_dir, exist_ok=True)

    def set_resolution(self, width: int, height: int, fps: int):
        """Set video resolution and FPS."""
        self.width = width
        self.height = height
        self.fps = fps

    def start_streaming(self) -> bool:
        """Start video capture for streaming."""
        if self.is_streaming:
            return True

        try:
            # Open camera using DirectShow
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)

            if not self.cap.isOpened():
                return False

            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)

            self.is_streaming = True

            # Start frame capture thread
            self.capture_thread = threading.Thread(target=self._capture_frames, daemon=True)
            self.capture_thread.start()

            return True

        except Exception as e:
            print(f"Error starting stream: {e}")
            return False

    def _capture_frames(self):
        """Continuously capture frames from camera."""
        while self.is_streaming and self.cap:
            ret, frame = self.cap.read()
            if ret:
                with self.frame_lock:
                    self.current_frame = frame

    def get_frame(self):
        """Get current frame as JPEG bytes."""
        with self.frame_lock:
            if self.current_frame is not None:
                # Encode frame as JPEG with configured quality
                jpeg_quality = self.config.streaming.jpeg_quality
                ret, buffer = cv2.imencode('.jpg', self.current_frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
                if ret:
                    return buffer.tobytes()
        return None

    def stop_streaming(self) -> bool:
        """Stop video streaming."""
        if not self.is_streaming:
            return True

        try:
            self.is_streaming = False

            if self.cap:
                self.cap.release()
                self.cap = None

            return True
        except Exception as e:
            print(f"Error stopping stream: {e}")
            return False

    def start_recording(
        self,
        filename: Optional[str] = None,
        options: Optional[RecordingOptions] = None
    ) -> bool:
        """Start recording video to file.

        Args:
            filename: Custom filename (overrides options.filename)
            options: Recording options for customizing this recording

        Returns:
            True if successful, False otherwise
        """
        if self.is_recording:
            print(f"[Recording] Already recording to: {self.current_recording}")
            return True

        # Use provided options or create default
        opts = options or RecordingOptions()

        # Determine filename
        if filename:
            final_filename = filename
        elif opts.filename:
            final_filename = opts.filename
        else:
            timestamp = datetime.now().strftime(self.config.recording.filename_pattern)
            final_filename = f"{timestamp}.{self.config.recording.format}"

        filepath = os.path.join(self.config.recording.output_dir, final_filename)

        # Determine resolution (use options or default)
        width = opts.width or self.width
        height = opts.height or self.height
        fps = opts.fps or self.fps

        # Determine encoder
        encoder = self._select_encoder(opts)

        print(f"\n[Recording] Starting recording:")
        print(f"  Camera: {self.camera_name}")
        print(f"  Resolution: {width}x{height}@{fps}fps")
        print(f"  Encoder: {encoder}")
        print(f"  Output file: {filepath}")

        try:
            # FFmpeg command for recording - correct DirectShow usage
            cmd = [
                "ffmpeg",
                "-f", "dshow",
                "-video_size", f"{width}x{height}",
                "-framerate", str(fps),
            ]

            # Try to use MJPEG input format for better compatibility
            cmd.extend(["-vcodec", "mjpeg"])
            cmd.extend(["-i", f"video={self.camera_name}"])

            # Add encoder
            cmd.extend(["-c:v", encoder])

            # Build encoder parameters
            encoder_params = self._build_encoder_params(encoder, opts)
            cmd.extend(encoder_params)

            # Add custom FFmpeg arguments if provided
            if opts.custom_args:
                cmd.extend(opts.custom_args)
                print(f"  Custom args: {' '.join(opts.custom_args)}")

            cmd.extend(["-y", filepath])

            print(f"\n[Recording] FFmpeg command: {' '.join(cmd)}\n")

            # Use CREATE_NO_WINDOW on Windows to avoid console window
            creation_flags = 0
            if os.name == 'nt':
                creation_flags = subprocess.CREATE_NO_WINDOW

            self.record_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                creationflags=creation_flags
            )

            # Wait a moment and check if process is still running
            import time
            time.sleep(0.5)

            if self.record_process.poll() is not None:
                # Process has already terminated - error occurred
                stdout, stderr = self.record_process.communicate()
                print(f"[Recording] ERROR: FFmpeg process terminated immediately!")
                print(f"[Recording] stdout: {stdout.decode('utf-8', errors='ignore')}")
                print(f"[Recording] stderr: {stderr.decode('utf-8', errors='ignore')}")
                return False

            self.is_recording = True
            self.current_recording = filepath

            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitor_recording, daemon=True)
            self.monitor_thread.start()

            print(f"[Recording] Successfully started recording!\n")
            return True

        except Exception as e:
            print(f"[Recording] Exception while starting recording: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _monitor_recording(self):
        """Monitor recording process for errors."""
        try:
            while self.is_recording and self.record_process:
                try:
                    line = self.record_process.stderr.readline()
                    if not line:
                        break
                    line_str = line.decode('utf-8', errors='ignore').strip()
                    if line_str and ('error' in line_str.lower() or 'warning' in line_str.lower()):
                        print(f"[Recording] FFmpeg: {line_str}")
                except (ValueError, OSError):
                    # stderr was closed, exit gracefully
                    break
        except Exception as e:
            # Silently exit if any unexpected error occurs
            pass

    def stop_recording(self) -> bool:
        """Stop recording video."""
        if not self.is_recording or not self.record_process:
            print("[Recording] No active recording to stop")
            return True

        print(f"\n[Recording] Stopping recording: {self.current_recording}")

        try:
            # Send 'q' command to FFmpeg stdin to gracefully stop
            # This is the proper way to stop FFmpeg
            print("[Recording] Sending 'q' command to FFmpeg...")
            try:
                self.record_process.stdin.write(b'q\n')
                self.record_process.stdin.flush()
            except Exception as e:
                print(f"[Recording] Could not write to stdin: {e}")
                print("[Recording] Trying terminate instead...")
                self.record_process.terminate()

            # Wait for process to finish and finalize the video file
            print("[Recording] Waiting for FFmpeg to finalize the file...")
            try:
                stdout, stderr = self.record_process.communicate(timeout=10)
                print("[Recording] FFmpeg stopped gracefully")

                # Print last few lines of stderr for debugging
                stderr_lines = stderr.decode('utf-8', errors='ignore').strip().split('\n')
                if stderr_lines:
                    print("[Recording] Last FFmpeg output:")
                    for line in stderr_lines[-10:]:
                        if line.strip():
                            print(f"  {line}")

            except subprocess.TimeoutExpired:
                print("[Recording] Timeout waiting for FFmpeg, forcing kill...")
                self.record_process.kill()
                self.record_process.wait(timeout=2)

            self.is_recording = False
            self.record_process = None

            # Check if file was created
            if os.path.exists(self.current_recording):
                file_size = os.path.getsize(self.current_recording)
                print(f"[Recording] File created successfully: {self.current_recording}")
                print(f"[Recording] File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)\n")
            else:
                print(f"[Recording] WARNING: Output file not found: {self.current_recording}\n")

            return True

        except Exception as e:
            print(f"[Recording] Exception while stopping recording: {e}")
            import traceback
            traceback.print_exc()
            try:
                self.record_process.kill()
                self.is_recording = False
                self.record_process = None
            except:
                pass
            return False

    def get_status(self) -> dict:
        """Get current streaming/recording status."""
        return {
            "camera_name": self.camera_name,
            "camera_index": self.camera_index,
            "encoder": self.encoder,
            "resolution": f"{self.width}x{self.height}@{self.fps}fps",
            "is_streaming": self.is_streaming,
            "is_recording": self.is_recording,
            "current_recording": getattr(self, 'current_recording', None) if self.is_recording else None
        }

    def _select_encoder(self, opts: RecordingOptions) -> str:
        """Select encoder based on options.

        Args:
            opts: Recording options

        Returns:
            Encoder name to use
        """
        # If specific encoder provided, use it
        if opts.encoder:
            return opts.encoder

        # If codec type specified, find appropriate encoder
        if opts.codec_type:
            from .encoder_detector import EncoderDetector
            detector = EncoderDetector()
            detector.encoders = []  # Will use existing detection

            # Map codec type to encoder
            if opts.codec_type == 'H.265':
                # Try to get H.265 encoder
                if hasattr(self, 'encoder_detector'):
                    return self.encoder_detector.get_preferred_encoder('H.265')
                else:
                    # Fallback based on current encoder type
                    if 'nvenc' in self.encoder:
                        return 'hevc_nvenc'
                    elif 'qsv' in self.encoder:
                        return 'hevc_qsv'
                    elif 'amf' in self.encoder:
                        return 'hevc_amf'
                    else:
                        return 'libx265'
            else:  # H.264
                return self.encoder

        # Use default encoder
        return self.encoder

    def _build_encoder_params(self, encoder: str, opts: RecordingOptions) -> list:
        """Build FFmpeg encoder parameters.

        Args:
            encoder: Encoder name
            opts: Recording options

        Returns:
            List of FFmpeg parameters
        """
        params = []
        enc_cfg = self.config.encoder

        # Get pixel format (use option or config)
        pix_fmt = opts.pixel_format or enc_cfg.pixel_format
        params.extend(["-pix_fmt", pix_fmt])

        # Build parameters based on encoder type
        if "nvenc" in encoder:
            preset = opts.preset or enc_cfg.nvenc_preset
            bitrate = opts.bitrate or enc_cfg.nvenc_bitrate
            params.extend(["-preset", preset, "-b:v", bitrate])
            print(f"  Using NVENC: preset={preset}, bitrate={bitrate}, pixel_format={pix_fmt}")

        elif "qsv" in encoder:
            preset = opts.preset or enc_cfg.qsv_preset
            bitrate = opts.bitrate or enc_cfg.qsv_bitrate
            params.extend(["-preset", preset, "-b:v", bitrate])
            print(f"  Using QSV: preset={preset}, bitrate={bitrate}, pixel_format={pix_fmt}")

        elif "amf" in encoder:
            quality = opts.preset or enc_cfg.amf_quality  # Use preset field for quality
            bitrate = opts.bitrate or enc_cfg.amf_bitrate
            params.extend(["-quality", quality, "-b:v", bitrate])
            print(f"  Using AMF: quality={quality}, bitrate={bitrate}, pixel_format={pix_fmt}")

        elif "libx264" in encoder or "libx265" in encoder:
            preset = opts.preset or enc_cfg.software_preset
            params.extend(["-preset", preset])

            if opts.crf is not None:
                crf = opts.crf
            elif opts.bitrate:
                # If bitrate specified for software encoder, use it instead of CRF
                params.extend(["-b:v", opts.bitrate])
                print(f"  Using software encoder: preset={preset}, bitrate={opts.bitrate}, pixel_format={pix_fmt}")
                return params
            else:
                crf = enc_cfg.software_crf

            params.extend(["-crf", str(crf)])
            print(f"  Using software encoder: preset={preset}, CRF={crf}, pixel_format={pix_fmt}")

        return params

    def cleanup(self):
        """Clean up resources."""
        self.stop_streaming()
        self.stop_recording()
