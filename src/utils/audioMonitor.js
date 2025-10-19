/**
 * 音频监控工具集
 * 封装音频监控的核心逻辑和 API 调用
 */

import { ref } from 'vue';
import { Channel } from '@tauri-apps/api/core';
import { pyInvoke } from 'tauri-plugin-pytauri-api';

/**
 * 音频监控类型
 */
export const MonitorType = {
  MICROPHONE: 'microphone',
  SYSTEM: 'system',
  BOTH: 'both',
  ALL: 'all'
};

/**
 * 创建音频监控器
 * @returns {Object} 音频监控器实例
 */
export function useAudioMonitor() {
  // 状态
  const microphoneActive = ref(false);
  const systemActive = ref(false);

  const microphoneLevel = ref({
    rms: 0,
    db: -Infinity,
    peak: 0,
    timestamp: ''
  });

  const systemLevel = ref({
    rms: 0,
    db: -Infinity,
    peak: 0,
    timestamp: ''
  });

  // Channel 实例
  let audioChannel = null;

  /**
   * 启动音频监控
   * @param {string} type - 监控类型 ('microphone' | 'system' | 'both')
   * @returns {Promise<Object>} 响应对象
   */
  async function startMonitoring(type) {
    try {
      if (!audioChannel) {
        audioChannel = new Channel();

        // 设置 onmessage 处理器 - 根据 source 字段分发数据
        audioChannel.onmessage = (data) => {
          // 根据数据中的 source 字段来更新对应的状态
          if (data.source === 'microphone') {
            microphoneLevel.value = data;
          } else if (data.source === 'system') {
            systemLevel.value = data;
          }
        };
      }

      const response = await pyInvoke('start_audio_monitoring', {
        monitor_type: type,
        channel_id: audioChannel.toJSON()
      });

      if (response.success) {
        if (type === MonitorType.MICROPHONE) {
          microphoneActive.value = true;
        } else if (type === MonitorType.SYSTEM) {
          systemActive.value = true;
        } else if (type === MonitorType.BOTH) {
          microphoneActive.value = true;
          systemActive.value = true;
        }
      }

      return response;
    } catch (error) {
      console.error('Failed to start monitoring:', error);
      throw error;
    }
  }

  /**
   * 停止音频监控
   * @param {string} type - 监控类型 ('microphone' | 'system' | 'all')
   * @returns {Promise<Object>} 响应对象
   */
  async function stopMonitoring(type) {
    try {
      const response = await pyInvoke('stop_audio_monitoring', {
        monitor_type: type
      });

      if (response.success) {
        if (type === MonitorType.MICROPHONE || type === MonitorType.ALL) {
          microphoneActive.value = false;
          microphoneLevel.value = { rms: 0, db: -Infinity, peak: 0, timestamp: '' };
        }
        if (type === MonitorType.SYSTEM || type === MonitorType.ALL) {
          systemActive.value = false;
          systemLevel.value = { rms: 0, db: -Infinity, peak: 0, timestamp: '' };
        }

        // 清理 channel
        if (type === MonitorType.ALL && audioChannel) {
          audioChannel.onmessage = null;
          audioChannel = null;
        }
      }

      return response;
    } catch (error) {
      console.error('Failed to stop monitoring:', error);
      throw error;
    }
  }

  /**
   * 获取音频设备列表
   * @returns {Promise<Object>} 设备列表
   */
  async function getAudioDevices() {
    try {
      return await pyInvoke('get_audio_devices');
    } catch (error) {
      console.error('Failed to get audio devices:', error);
      throw error;
    }
  }

  /**
   * 格式化分贝值
   * @param {number} db - 分贝值
   * @returns {string} 格式化后的字符串
   */
  function formatDb(db) {
    // 处理各种边界情况
    if (db === null || db === undefined || !isFinite(db)) {
      return '-∞';
    }
    // -100 dB 作为静音阈值
    if (db <= -100) {
      return '-∞';
    }
    return db.toFixed(1);
  }

  /**
   * 清理资源
   */
  function cleanup() {
    if (microphoneActive.value || systemActive.value) {
      stopMonitoring(MonitorType.ALL);
    }
  }

  return {
    // 状态
    microphoneActive,
    systemActive,
    microphoneLevel,
    systemLevel,

    // 方法
    startMonitoring,
    stopMonitoring,
    getAudioDevices,
    formatDb,
    cleanup
  };
}

/**
 * 格式化音量数值
 * @param {number} value - 音量值 (0-1)
 * @param {number} precision - 精度
 * @returns {string} 格式化后的字符串
 */
export function formatValue(value, precision = 4) {
  if (value === null || value === undefined || isNaN(value)) {
    return '0.0000';
  }
  return value.toFixed(precision);
}

/**
 * 计算音量百分比
 * @param {number} peak - 峰值 (0-1)
 * @returns {number} 百分比 (0-100)
 */
export function calculatePercentage(peak) {
  if (peak === null || peak === undefined || isNaN(peak)) {
    return 0;
  }
  return peak * 100;
}
