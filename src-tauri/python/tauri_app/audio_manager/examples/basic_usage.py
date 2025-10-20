"""
基本使用示例
"""

import time
from audio_manager import AudioManager, AudioLevel
from audio_manager.utils import format_db, create_progress_bar


def main():
    """主函数"""
    # 创建音频管理器
    manager = AudioManager()
    
    # 列出所有设备
    print("=== 可用音频设备 ===")
    devices = manager.list_devices()
    print("\n输入设备:")
    for dev in devices['input']:
        print(f"  [{dev['id']}] {dev['name']} - {dev['channels']}ch @ {dev['sample_rate']}Hz")
    print("\n输出设备:")
    for dev in devices['output']:
        print(f"  [{dev['id']}] {dev['name']} - {dev['channels']}ch @ {dev['sample_rate']}Hz")
    
    # 存储最新的音频数据
    latest_mic = {'rms': 0, 'db': -float('inf'), 'peak': 0}
    latest_sys = {'rms': 0, 'db': -float('inf'), 'peak': 0}
    
    # 定义回调函数（只更新数据，不打印）
    def on_microphone_update(level: AudioLevel):
        latest_mic['rms'] = level.rms
        latest_mic['db'] = level.db
        latest_mic['peak'] = level.peak
    
    def on_system_update(level: AudioLevel):
        latest_sys['rms'] = level.rms
        latest_sys['db'] = level.db
        latest_sys['peak'] = level.peak
    
    print("\n=== 启动监控 ===")
    print("使用Windows Core Audio API监控系统音频输出\n")
    
    # 启动监控
    manager.start_microphone_monitoring(callback=on_microphone_update)
    manager.start_system_monitoring(callback=on_system_update)
    
    try:
        print("正在监控... 按 Ctrl+C 停止\n")
        
        while True:
            # 清除当前行并回到开头（使用ANSI转义序列）
            print('\033[2K\033[1G', end='')
            
            # 麦克风数据
            mic_db = format_db(latest_mic['db'], precision=1)
            mic_bar = create_progress_bar(min(latest_mic['peak'], 1.0))
            
            # 系统音频数据
            sys_db = format_db(latest_sys['db'], precision=1)
            sys_bar = create_progress_bar(min(latest_sys['peak'], 1.0))
            
            # 在同一位置更新显示
            output = (f"🎤 麦克风: {mic_db:>6} dB [{mic_bar}] {latest_mic['peak']:.3f}  |  "
                     f"🔊 系统: {sys_db:>6} dB [{sys_bar}] {latest_sys['peak']:.3f}")
            
            print(output, end='', flush=True)
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n停止监控...")
        manager.stop_all()
        print("已停止")


if __name__ == "__main__":
    main()