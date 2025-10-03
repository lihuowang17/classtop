<template>
  <div class="schedule-container">
    <mdui-linear-progress class="currentClass" id="progress" :class="{ 'break-time': isBreakTime }" :value="progress"
      :data-text="displayText">
    </mdui-linear-progress>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import {
  getScheduleByDay,
  getScheduleForWeek,
  getCurrentWeek,
  findCurrentClass,
  findNextClass,
  findLastClass,
  findNextClassAcrossWeek,
  getTodayWeekday
} from '../../utils/schedule.js';
import { listen } from '@tauri-apps/api/event';

// 课程数据缓存
const todaySchedule = ref([]);
const weekSchedule = ref([]);
const currentWeek = ref(1);

// 显示状态
const displayText = ref('暂无课程');
const progress = ref(0);
const currentTime = ref(new Date());
const isBreakTime = ref(false);

let intervalId = null;
let updateIntervalId = null;
let unlistenScheduleUpdate = null;

let progressElement = null;

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

// 将时间字符串转为秒数
const timeToSeconds = (timeStr) => {
  const [h, m] = timeStr.split(':').map(Number);
  return h * 3600 + m * 60;
};

// 计算课程进度或课间进度
const calculateProgress = () => {
  const now = currentTime.value;
  const currentSeconds = now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds();

  // 查找当前课程和下一节课
  const current = findCurrentClass(todaySchedule.value, now);
  const next = findNextClass(todaySchedule.value, now);
  const last = findLastClass(todaySchedule.value, now);

  if (current) {
    // 当前有课 - 显示课程进度
    const startSeconds = timeToSeconds(current.start_time);
    const endSeconds = timeToSeconds(current.end_time);

    if (currentSeconds < startSeconds) return 0;
    if (currentSeconds >= endSeconds) return 1;
    return (currentSeconds - startSeconds) / (endSeconds - startSeconds);
  }

  if (next && isBreakTime.value && last) {
    // 课间 - 显示课间进度
    const breakStartSeconds = timeToSeconds(last.end_time);
    const breakEndSeconds = timeToSeconds(next.start_time);

    if (currentSeconds < breakStartSeconds) return 0;
    if (currentSeconds >= breakEndSeconds) return 1;

    const breakDuration = breakEndSeconds - breakStartSeconds;
    const elapsedTime = currentSeconds - breakStartSeconds;
    return (breakDuration - elapsedTime) / breakDuration;
  }

  return 0;
};

// 更新显示
const updateDisplay = () => {
  const now = currentTime.value;
  const currentSeconds = now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds();

  // 从缓存数据中查找当前状态
  const current = findCurrentClass(todaySchedule.value, now);
  const todayNext = findNextClass(todaySchedule.value, now);

  // 跨天查找下一节课
  const todayWeekday = getTodayWeekday();
  const nextAcrossWeek = findNextClassAcrossWeek(weekSchedule.value, todayWeekday, now);

  if (current) {
    // 当前有课
    isBreakTime.value = false;
    const { name, location, start_time, end_time } = current;

    // 检查是否即将结束
    const endSeconds = timeToSeconds(end_time);
    if (currentSeconds >= endSeconds - 1 && todayNext) {
      // 即将结束，提前切换到课间显示
      isBreakTime.value = true;
      const remainingSeconds = timeToSeconds(todayNext.start_time) - currentSeconds;
      const remainingTimeStr = formatRemainingTime(remainingSeconds);
      const nextLocation = todayNext.location ? ` @ ${todayNext.location}` : '';
      displayText.value = `下一节: ${todayNext.name}${nextLocation} (${remainingTimeStr}后)`;
      rewidthProgressBar();
    } else {
      const locationText = location ? ` @ ${location}` : '';
      displayText.value = `${name}${locationText} (${start_time}-${end_time})`;
      rewidthProgressBar();
    }

    progress.value = calculateProgress();
  } else if (todayNext) {
    // 今天还有课 - 课间
    isBreakTime.value = true;
    const remainingSeconds = timeToSeconds(todayNext.start_time) - currentSeconds;

    if (remainingSeconds > 0) {
      const remainingTimeStr = formatRemainingTime(remainingSeconds);
      const nextLocation = todayNext.location ? ` @ ${todayNext.location}` : '';
      displayText.value = `下一节: ${todayNext.name}${nextLocation} (${remainingTimeStr}后)`;
      rewidthProgressBar();
      progress.value = calculateProgress();
    } else {
      // 应该已经开始了，触发刷新
      const nextLocation = todayNext.location ? ` @ ${todayNext.location}` : '';
      displayText.value = `${todayNext.name}${nextLocation} (即将开始)`;
      rewidthProgressBar();
      progress.value = 0;
      loadScheduleData();
    }
  } else if (nextAcrossWeek && nextAcrossWeek.day_of_week !== todayWeekday) {
    // 今日课程结束，显示其他天的下一节课
    isBreakTime.value = false;
    const dayNames = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    const dayName = dayNames[nextAcrossWeek.day_of_week] || '未知';
    displayText.value = `今日课程结束 - 下一节: ${dayName} ${nextAcrossWeek.name}`;
    rewidthProgressBar();
    progress.value = 0;
  } else {
    // 没有任何课程
    isBreakTime.value = false;
    displayText.value = '暂无课程';
    rewidthProgressBar();
    progress.value = 0;
  }
};

// 加载课程数据
const loadScheduleData = async () => {
  try {
    // 获取当前周数
    const weekInfo = await getCurrentWeek();
    currentWeek.value = weekInfo.week;

    // 获取今天的weekday
    const today = getTodayWeekday();

    // 并发获取今天和本周的课程
    const [todayData, weekData] = await Promise.all([
      getScheduleByDay(today, currentWeek.value),
      getScheduleForWeek(currentWeek.value)
    ]);

    todaySchedule.value = todayData;
    weekSchedule.value = weekData;

    updateDisplay();
  } catch (error) {
    console.error('Failed to load schedule data:', error);
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

const rewidthProgressBar = () => {
  if (progressElement) {
    const text = displayText.value || '';
    // create hidden span to measure real rendered width
    const span = document.createElement('span');
    span.textContent = text;
    span.style.position = 'absolute';
    span.style.visibility = 'hidden';
    span.style.whiteSpace = 'nowrap';
    span.style.fontSize = '1rem';
    span.style.fontWeight = '500';
    span.style.fontFamily = getComputedStyle(progressElement).fontFamily || 'inherit';
    document.body.appendChild(span);
    const widthPx = span.getBoundingClientRect().width;
    document.body.removeChild(span);

    // convert px -> rem based on root font-size
    const rootFontSize = parseFloat(getComputedStyle(document.documentElement).fontSize) || 16;
    const widthRem = widthPx / rootFontSize;

    // add padding and clamp to reasonable bounds
    const paddedRem = widthRem + 1; // 1rem padding (adjust if needed)
    const minRem = 4;
    const maxRem = 24;
    progressElement.style.width = Math.min(maxRem, Math.max(minRem, paddedRem)) + 'rem';
  }
};

onMounted(async () => {
  // 初次加载
  await loadScheduleData();

  // 每10秒刷新课程数据（从后端）
  intervalId = setInterval(loadScheduleData, 10000);

  // 每秒更新显示（使用缓存数据）
  updateIntervalId = setInterval(updateTimeAndProgress, 1000);

  progressElement = document.getElementById('progress');

  // 监听课表更新事件
  try {
    unlistenScheduleUpdate = await listen('schedule-update', (event) => {
      console.log('Schedule update received:', event.payload);
      loadScheduleData();
    });
  } catch (error) {
    console.error('Failed to setup schedule update listener:', error);
  }
});

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId);
  }
  if (updateIntervalId) {
    clearInterval(updateIntervalId);
  }
  if (unlistenScheduleUpdate) {
    unlistenScheduleUpdate();
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
.currentClass.break-time {}

.currentClass::after {
  content: attr(data-text);
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: rgb(var(--mdui-color-on-surface));
  font-size: 1rem;
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