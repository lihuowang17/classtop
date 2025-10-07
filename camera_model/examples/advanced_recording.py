"""Advanced recording example with RecordingOptions."""
from camera_monitor import CameraMonitor, RecordingOptions
import time


def example_h265_recording():
    """Example: Record with H.265 codec."""
    print("="*60)
    print("Example 1: Recording with H.265 codec")
    print("="*60)

    monitor = CameraMonitor().initialize()

    # Create recording options for H.265
    opts = RecordingOptions(codec_type='H.265')

    print("\nStarting H.265 recording...")
    monitor.start_recording(0, options=opts)

    time.sleep(5)

    monitor.stop_recording(0)
    print("✓ H.265 recording complete\n")

    monitor.cleanup()


def example_custom_resolution():
    """Example: Record with custom resolution and bitrate."""
    print("="*60)
    print("Example 2: Custom resolution and bitrate")
    print("="*60)

    monitor = CameraMonitor().initialize()

    # Create recording options with custom settings
    opts = RecordingOptions(
        width=1920,
        height=1080,
        fps=60,
        bitrate='15M'
    )

    print("\nStarting high-quality recording...")
    monitor.start_recording(0, options=opts)

    time.sleep(5)

    monitor.stop_recording(0)
    print("✓ High-quality recording complete\n")

    monitor.cleanup()


def example_specific_encoder():
    """Example: Use specific encoder."""
    print("="*60)
    print("Example 3: Using specific encoder")
    print("="*60)

    monitor = CameraMonitor().initialize()

    # Get available encoders
    encoders = monitor.get_encoders()
    print(f"\nAvailable H.265 encoders: {[e['name'] for e in encoders['h265']['encoders']]}")

    # Force use of specific encoder (e.g., HEVC NVENC)
    opts = RecordingOptions(
        encoder='hevc_nvenc',  # or 'libx265' for software
        preset='slow',         # Better quality
        bitrate='20M'          # High bitrate
    )

    print("\nStarting recording with HEVC NVENC...")
    monitor.start_recording(0, options=opts)

    time.sleep(5)

    monitor.stop_recording(0)
    print("✓ HEVC NVENC recording complete\n")

    monitor.cleanup()


def example_software_encoder_crf():
    """Example: Software encoder with CRF (constant rate factor)."""
    print("="*60)
    print("Example 4: Software encoder with CRF")
    print("="*60)

    monitor = CameraMonitor().initialize()

    # Use software encoder with CRF (lower = better quality, slower encoding)
    opts = RecordingOptions(
        encoder='libx265',    # Software H.265 encoder
        crf=18,               # High quality (0-51, lower is better)
        preset='slower'       # Slower encoding, better compression
    )

    print("\nStarting high-quality software encoding...")
    monitor.start_recording(0, options=opts)

    time.sleep(5)

    monitor.stop_recording(0)
    print("✓ High-quality software encoding complete\n")

    monitor.cleanup()


def example_multiple_recordings():
    """Example: Multiple recordings with different settings."""
    print("="*60)
    print("Example 5: Multiple recordings with different settings")
    print("="*60)

    monitor = CameraMonitor().initialize()

    # Recording 1: H.264 fast preset
    print("\n1. Recording with H.264 fast preset...")
    opts1 = RecordingOptions(
        codec_type='H.264',
        preset='fast',
        bitrate='5M',
        filename='test_h264_fast.mp4'
    )
    monitor.start_recording(0, options=opts1)
    time.sleep(3)
    monitor.stop_recording(0)
    print("   ✓ H.264 fast recording complete")

    time.sleep(1)

    # Recording 2: H.265 slow preset
    print("\n2. Recording with H.265 slow preset...")
    opts2 = RecordingOptions(
        codec_type='H.265',
        preset='slow',
        bitrate='5M',
        filename='test_h265_slow.mp4'
    )
    monitor.start_recording(0, options=opts2)
    time.sleep(3)
    monitor.stop_recording(0)
    print("   ✓ H.265 slow recording complete")

    time.sleep(1)

    # Recording 3: Low resolution for low bandwidth
    print("\n3. Recording low resolution for low bandwidth...")
    opts3 = RecordingOptions(
        width=640,
        height=480,
        fps=15,
        bitrate='1M',
        filename='test_low_res.mp4'
    )
    monitor.start_recording(0, options=opts3)
    time.sleep(3)
    monitor.stop_recording(0)
    print("   ✓ Low resolution recording complete")

    print("\n✓ All recordings complete!\n")

    monitor.cleanup()


def example_custom_ffmpeg_args():
    """Example: Using custom FFmpeg arguments."""
    print("="*60)
    print("Example 6: Custom FFmpeg arguments")
    print("="*60)

    monitor = CameraMonitor().initialize()

    # Use custom FFmpeg arguments for advanced control
    opts = RecordingOptions(
        codec_type='H.264',
        custom_args=[
            '-profile:v', 'high',     # H.264 profile
            '-level', '4.2',          # H.264 level
            '-g', '60',               # GOP size
            '-bf', '2',               # B-frames
        ]
    )

    print("\nStarting recording with custom FFmpeg arguments...")
    monitor.start_recording(0, options=opts)

    time.sleep(5)

    monitor.stop_recording(0)
    print("✓ Custom FFmpeg recording complete\n")

    monitor.cleanup()


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*12 + "Advanced Recording Examples" + " "*19 + "║")
    print("╚" + "="*58 + "╝")
    print("\n")

    try:
        # Run examples
        example_h265_recording()
        time.sleep(2)

        example_custom_resolution()
        time.sleep(2)

        example_specific_encoder()
        time.sleep(2)

        example_software_encoder_crf()
        time.sleep(2)

        example_multiple_recordings()
        time.sleep(2)

        example_custom_ffmpeg_args()

        print("\n")
        print("="*60)
        print("All examples completed successfully!")
        print("Check the 'recordings' directory for output files.")
        print("="*60)
        print("\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
