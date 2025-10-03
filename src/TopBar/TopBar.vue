<template>
    <main class="top-bar-container">
        <div class="top-bar-content">
            <div class="left-section" v-if="settings.show_schedule">
                <Schedule :key="scheduleKey" />
            </div>

            <div class="center-section" v-if="settings.show_clock">
                <Clock />
            </div>

            <div class="right-section">
                <div class="control-buttons">
                    <mdui-button-icon id="pin-button" selectable icon="push_pin--outlined" selected-icon="push_pin"
                        @click="handlePin"></mdui-button-icon>
                    <mdui-button-icon icon="close" @click="handleClose"></mdui-button-icon>
                </div>
            </div>
        </div>
    </main>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import Clock from './components/Clock.vue';
import Schedule from './components/Schedule.vue';
import { loadSettings, settings } from '../utils/globalVars';

// 响应式数据
const isPinned = ref(false);
// 用于强制重载 Schedule 组件的 key
const scheduleKey = ref(Date.now());

// 初始化顶栏窗口
onMounted(async () => {
    try {
        await invoke('setup_topbar_window');
        document.body.style.borderRadius = "0 0 15px 15px";
    } catch (error) {
        console.error('Failed to setup top bar window:', error);
    }

    isPinned.value = false;

    // 监听设置更新事件
    try {
        await listen('setting-update', (event) => {
            console.log('Setting update received in TopBar:', event.payload);
            let value = event.payload.value;
            // 对于字符串'boolean'类型的设置，需要转换为布尔值
            if (value === 'true' || value === 'false') {
                value = value === 'true';
            }
            // 更新对应的设置
            settings[event.payload.key] = value;
        });

        // 监听批量设置更新事件 - 刷新 Schedule 组件
        await listen('settings-batch-update', (event) => {
            console.log('Batch settings update received in TopBar:', event.payload);

            // 检查是否更新了影响课表显示的设置
            const affectsSchedule = event.payload.updated_keys.some(key =>
                ['show_schedule', 'semester_start_date'].includes(key)
            );

            if (affectsSchedule) {
                console.log('Settings affecting schedule updated, reloading...');
                forceReloadSchedule();
            }

            // 重新加载所有设置以确保同步
            loadSettings();
        });
    } catch (error) {
        console.error('Failed to setup setting update listener:', error);
    }
});

const handlePin = function (e) {
    setTimeout(() => {
        // 加上50ms延时确保获取真实数据
        isPinned.value = e.target.hasAttribute("selected")
        console.log(isPinned.value)
    }, 50);
};

const handleClose = async () => {
    try {
        // Pass the window name so the Rust command knows which window to toggle
        await invoke('toggle_window', { windowName: 'topbar' });
    } catch (error) {
        console.error('Failed to close window:', error);
    }
};

// 暴露给父组件的方法
const forceReloadSchedule = () => {
    // 通过改变 key 的值强制重新挂载 Schedule 组件
    scheduleKey.value = Date.now();
};

defineExpose({
    toggleVisibility: handleClose,
    isPinned,
    forceReloadSchedule
});
</script>

<style scoped>
.top-bar-container {
    width: 100%;
    height: 100vh;
    backdrop-filter: blur(10px);
    border-radius: 0 0 15px 15px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    -webkit-app-region: drag;
}

.top-bar-content {
    display: flex;
    align-items: center;
    height: 100%;
    padding: 0 20px;
    position: relative;
}

.left-section {
    position: absolute;
    left: 20px;
    top: 50%;
    transform: translateY(-50%);
    z-index: 2;
}

.center-section {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    z-index: 1;
}

.right-section {
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    align-items: center;
    gap: 15px;
    z-index: 2;
}

.control-buttons {
    display: flex;
    gap: 8px;
}

.control-buttons mdui-button-icon {
    -webkit-app-region: no-drag;
}

@media (max-width: 800px) {
    .top-bar-content {
        padding: 0 15px;
    }

    .left-section {
        left: 15px;
    }

    .right-section {
        right: 15px;
        gap: 10px;
    }
}
</style>