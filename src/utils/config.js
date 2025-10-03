// Frontend helper utilities for calling Python backend (pytauri) commands.
// Uses PyTauri's pyInvoke API.

import { pyInvoke } from 'tauri-plugin-pytauri-api';

async function setConfig(key, value) {
  try {
    await pyInvoke('set_config', { key, value });
    return { key, value };
  } catch (err) {
    console.error('setConfig failed', err);
    throw err;
  }
}

async function getConfig(key) {
  try {
    const value = await pyInvoke('get_config', { key });
    return value;
  } catch (err) {
    console.error('getConfig failed', err);
    throw err;
  }
}

async function listConfigs() {
  try {
    const configs = await pyInvoke('list_configs');
    return configs;
  } catch (err) {
    console.error('listConfigs failed', err);
    throw err;
  }
}

async function logMessage(level, message) {
  try {
    await pyInvoke('log_message', { level, message });
    return { ok: true };
  } catch (err) {
    console.error('logMessage failed', err);
    throw err;
  }
}

async function getLogs(maxLines = 200) {
  try {
    const logs = await pyInvoke('get_logs', { max_lines: maxLines });
    return { lines: logs };
  } catch (err) {
    console.error('getLogs failed', err);
    throw err;
  }
}

export { setConfig, getConfig, listConfigs, logMessage, getLogs };
