// Frontend helper utilities for calling Python backend (pytauri) commands.
// Uses @tauri-apps/api/tauri invoke. Import these helpers in your Vue components.

import { invoke } from '@tauri-apps/api/tauri';

async function setConfig(key, value) {
  try {
    const res = await invoke('set_config', { key, value });
    return res; // { key, value }
  } catch (err) {
    console.error('setConfig failed', err);
    throw err;
  }
}

async function getConfig(key) {
  try {
    const res = await invoke('get_config', { key });
    return res; // { key, value }
  } catch (err) {
    console.error('getConfig failed', err);
    throw err;
  }
}

async function listConfigs() {
  try {
    const res = await invoke('list_configs');
    return res; // { key: value, ... }
  } catch (err) {
    console.error('listConfigs failed', err);
    throw err;
  }
}

async function logMessage(level, message) {
  try {
    const res = await invoke('log_message', { level, message });
    return res; // { ok: true }
  } catch (err) {
    console.error('logMessage failed', err);
    throw err;
  }
}

async function getLogs(maxLines = 200) {
  try {
    const res = await invoke('get_logs', { max_lines: maxLines });
    return res; // { lines: [...] }
  } catch (err) {
    console.error('getLogs failed', err);
    throw err;
  }
}

export { setConfig, getConfig, listConfigs, logMessage, getLogs };
