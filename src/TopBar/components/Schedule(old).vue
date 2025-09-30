<template>
  <div class="schedule-container">
    <mdui-linear-progress
      class="currentClass"
      :class="{ 'break-time': isBreakTime }"
      :value="progress"
      :data-text="displayText">
    </mdui-linear-progress>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { getCurrentClass, getNextClass, getLastClass } from '../../utils/schedule.js';
import { listen } from '@tauri-apps/api/event';

const currentClass = ref(null);
const nextClass = ref(null);
const lastClass = ref(null);
const displayText = ref('暂无课程');
const progress = ref(0);
const currentTime = ref(new Date());
const isBreakTime = ref(false);
let intervalId = null;
let updateIntervalId = null;
let unlistenScheduleUpdate = null;
// 节流上次刷新的时间（ms），避免 updateDisplay 每秒导致频繁 updateClasses 调用
let lastRefreshAt = 0;
const REFRESH_THROTTLE_MS = 10_000;

// 辅助：把 "HH:MM" 转为当天的秒数
const parseTimeToSeconds = (time) => {
  const [h = 0, m = 0] = (time || '').split(':').map(Number);
  return (Number(h) || 0) * 3600 + (Number(m) || 0) * 60;
};

// 格式化剩余时间
const formatRemainingTime = (seconds) => {
  seconds = Math.max(0, Math.floor(seconds));
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  if (hours > 0) return `${hours}小时${minutes}分钟`;
  if (minutes > 0) return `${minutes}分钟${secs}秒`;
  return `${secs}秒`;
};

// 获取今天的ISO weekday (1=Mon,7=Sun) 基于 currentTime 以保持一致性
const getTodayISO = () => {
  const day = currentTime.value.getDay();
  return day === 0 ? 7 : day;
};

// 简单的数值约束
const clamp01 = (v) => Math.max(0, Math.min(1, v));

// 计算进度（返回 0..1）
const calculateProgress = () => {
  const now = currentTime.value;
  const currentSeconds = now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds();

  // 当前有课 => 课堂进度
  if (currentClass.value) {
    const startSeconds = parseTimeToSeconds(currentClass.value.start_time);
    const endSeconds = parseTimeToSeconds(currentClass.value.end_time);
    if (currentSeconds < startSeconds) return 0;
    if (currentSeconds >= endSeconds) return 1;
    return clamp01((currentSeconds - startSeconds) / Math.max(1, endSeconds - startSeconds));
  }

  // 课间且知道下一节课 => 倒计时进度（剩余/总课间）
  if (isBreakTime.value && nextClass.value) {
    const todayISO = getTodayISO();
    const nextDay = Number(nextClass.value.day_of_week);
    if (nextDay === todayISO) {
      const nextStart = parseTimeToSeconds(nextClass.value.start_time);
      // 课间开始优先依据上一节课结束，否则假定最多1小时课间
      let breakStart = Math.max(0, nextStart - 3600);
      if (lastClass.value && Number(lastClass.value.day_of_week) === todayISO) {
        breakStart = parseTimeToSeconds(lastClass.value.end_time);
      }
      if (currentSeconds < breakStart) return 0;
      const total = Math.max(1, nextStart - breakStart);
      const remaining = Math.max(0, nextStart - currentSeconds);
      // 0 表示刚开始，1 表示即将结束 -> 使用 (total- elapsed)/total
      return clamp01((total - (currentSeconds - breakStart)) / total);
    }
  }

  return 0;
};

// 节流式更新课程数据（避免短时间内重复触发）
const tryRefreshClasses = async (force = false) => {
  const now = Date.now();
  if (!force && now - lastRefreshAt < REFRESH_THROTTLE_MS) return;
  lastRefreshAt = now;
  await updateClasses();
};

// 更新显示文本与进度
const updateDisplay = () => {
  const now = currentTime.value;
  const currentSeconds = now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds();

  if (currentClass.value) {
    // 当前有课
    isBreakTime.value = false;
    const { name, location, start_time, end_time } = currentClass.value;
    const endSeconds = parseTimeToSeconds(end_time);

    // 如果课程刚结束（或马上结束），准备显示课间信息并在必要时切换
    if (currentSeconds >= endSeconds - 1 && nextClass.value) {
      const nextDay = Number(nextClass.value.day_of_week);
      if (nextDay === getTodayISO()) {
        isBreakTime.value = true;
        const remainingSeconds = parseTimeToSeconds(nextClass.value.start_time) - currentSeconds;
        displayText.value = `下一节: ${nextClass.value.name}${nextClass.value.location || ''} (${formatRemainingTime(remainingSeconds)}后)`;
        progress.value = calculateProgress();
        // 课程数据可能已发生变化，节流刷新
        tryRefreshClasses();
        return;
      }
    }

    displayText.value = `${name}${location ? `(${location})` : ''} (${start_time}-${end_time})`;
    progress.value = calculateProgress();
    return;
  }

  if (nextClass.value) {
    // 课间/无当前课
    isBreakTime.value = true;
    const { name, location, start_time, day_of_week } = nextClass.value;
    const nextStartSec = parseTimeToSeconds(start_time);
    const nextDay = Number(day_of_week);
    const todayISO = getTodayISO();

    if (nextDay === todayISO) {
      if (currentSeconds < nextStartSec) {
        const remaining = nextStartSec - currentSeconds;
        displayText.value = `下一节: ${name}${location ? `(${location})` : ''} (${formatRemainingTime(remaining)}后)`;
        progress.value = calculateProgress();
      } else {
        // 数据可能滞后，节流刷新一次
        displayText.value = `${name}${location ? `(${location})` : ''} (${start_time}开始)`;
        progress.value = 0;
        tryRefreshClasses();
      }
    } else {
      const dayNames = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'];
      const dayName = (nextDay >= 1 && nextDay <= 7) ? dayNames[nextDay] : '未知';
      displayText.value = `今日课程结束 - 下一节: ${dayName} ${name}`;
      progress.value = 0;
    }
    return;
  }

  // 没有任何课程
  isBreakTime.value = false;
  displayText.value = '暂无课程';
  progress.value = 0;
};

// 获取课程信息
const updateClasses = async () => {
  try {
    const [current, next, last] = await Promise.all([
      getCurrentClass(),
      getNextClass(),
      getLastClass()
    ]);
    currentClass.value = current || null;
    nextClass.value = next || null;
    lastClass.value = last || null;
    updateDisplay();
  } catch (error) {
    console.error('Failed to get classes:', error);
    displayText.value = '加载失败';
    progress.value = 0;
    isBreakTime.value = false;
  }
};

// 每秒更新时间和进度
const updateTimeAndProgress = () => {
  currentTime.value = new Date();
  updateDisplay();
};

onMounted(async () => {
  // 初次加载
  await updateClasses();

  // 定时：每5秒尝试更新课程列表（真实刷新受节流控制）
  intervalId = setInterval(() => tryRefreshClasses(), 5000);
  // 每秒更新当前时间与显示
  updateIntervalId = setInterval(updateTimeAndProgress, 1000);

  // 监听 backend 的推送以便即时更新（尽量保持简洁）
  try {
    unlistenScheduleUpdate = await listen('schedule-update', (event) => {
      // 直接强制刷新一次（不受节流限制）
      tryRefreshClasses(true);
    });
  } catch (error) {
    console.error('Failed to setup schedule update listener:', error);
  }
});

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId);
    intervalId = null;
  }
  if (updateIntervalId) {
    clearInterval(updateIntervalId);
    updateIntervalId = null;
  }
  if (typeof unlistenScheduleUpdate === 'function') {
    try { unlistenScheduleUpdate(); } catch (e) { /* ignore */ }
    unlistenScheduleUpdate = null;
  }
});
</script>

<style scoped>
.schedule-container {
  position: relative;
}

.currentClass {
  width: 12rem;
  height: 2rem;
  border-radius: 10px;
  position: relative;
}

/* 课间时间的样式 */
.currentClass.break-time {
  opacity: 0.8;
}

.currentClass::after {
  content: attr(data-text);
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: rgb(var(--mdui-color-on-surface));
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  pointer-events: none;
  z-index: 1;
}

@media (max-width: 800px) {
  .currentClass {
    width: 10rem;
    height: 1.8rem;
  }

  .currentClass::after {
    font-size: 0.75rem;
  }
}
</style>