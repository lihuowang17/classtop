<template>
  <div class="home">
    114514
    <mdui-button @click="toggleMainWindow">toggle main window</mdui-button>
  </div>
</template>

<script setup>
import { invoke } from '@tauri-apps/api/core';

const toggleMainWindow = async () => {
  await invoke('toggle_window', { windowName: 'main' });
};
</script>

<style scoped>
</style>
