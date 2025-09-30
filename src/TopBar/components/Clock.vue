<template>
  <div class="clock-container">
    <div class="time-display ubuntu-medium">{{ formattedTime }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const currentTime = ref(new Date());
let timer = null;

const formattedTime = computed(() => {
  return currentTime.value.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });
});

const formattedDate = computed(() => {
  return currentTime.value.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    weekday: 'short'
  });
});

const updateTime = () => {
  currentTime.value = new Date();
};

onMounted(() => {
  updateTime();
  timer = setInterval(updateTime, 1000);
});

onUnmounted(() => {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
});
</script>

<style scoped>
.clock-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.time-display {
  font-size: 1.75rem;
  line-height: 1;
}

@media (max-width: 800px) {
  .time-display {
    font-size: 1.2rem;
  }
}
</style>