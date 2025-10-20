"""
高级使用示例 - 展示更多API功能
"""

import time
from audio_manager import AudioManager, AudioLevel


def main():
    """高级功能示例"""
    
    # 使用上下文管理器自动管理资源
    with AudioManager() as manager:
        # 定义多个回调函数
        def log_callback(level: AudioLevel):
            """记录日志回调"""
            if level.peak > 0.8:  # 峰值超过80%
                print(f"\n⚠️  警告: 音量过高! Peak={level.peak:.2f}")
        
        def threshold_callback(level: AudioLevel):
            """阈值触发回调"""
            if level.db > -10:  # 高于-10dB
                print(f"\n🔔 触发阈值! dB={level.db:.1f}")
        
        # 添加多个回调
        manager.start_microphone_monitoring()
        manager.microphone_monitor.add_callback(log_callback)
        manager.microphone_monitor.add_callback(threshold_callback)
        
        manager.start_system_monitoring()
        
        print("监控中... (按Ctrl+C退出)")
        try:
            while True:
                # 获取当前响度
                mic_level = manager.get_microphone_level()
                sys_level = manager.get_system_level()
                
                if mic_level:
                    print(f"Mic: {mic_level}")
                if sys_level:
                    print(f"Sys: {sys_level}")
                
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n退出中...")
    
    # 上下文管理器会自动调用stop_all()
    print("已停止所有监控")


if __name__ == "__main__":
    main()
