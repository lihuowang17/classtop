import { onMounted, ref } from "vue";
import { isPinned, setFullTopbar, setThinTopbar, topbarType } from "../TopBar/TopBar.vue";
import { current } from "../TopBar/components/Schedule.vue";
import { settings } from "./globalVars";


const mouseOn = ref(false)
var lastClickTime = Date.now();

const handleMouseEnter = async () => {
    mouseOn.value = true

    try {
        await setFullTopbar()
    } catch (error) {
        console.error('Failed to toggle TopBar type:', error);
    }
};

const handleMouseLeave = async () => {
    mouseOn.value = false

    if (!isPinned.value && current) {
        try {
            await setThinTopbar()
        } catch (error) {
            console.error('Failed to toggle TopBar type:', error);
        }
    }
};

// 处理点击事件, 重置定时器
const handleClick = async () => {
    lastClickTime = Date.now();
    if(topbarType.value === 'thin') {
        try {
            await setFullTopbar()
        } catch (error) {
            console.error('Failed to toggle TopBar type:', error);
        }
    }
};

async function init() {
    if(settings.control_mode === 'touch') {
        mouseOn.value = false
        // 监听点击事件, 点击窗口任意位置都触发
        window.addEventListener('click', handleClick);
        // 创建永久定时器, 若没有点击超过4秒, 则隐藏TopBar
        setInterval(async () => {
            if (!mouseOn.value && !isPinned.value && current && lastClickTime + 4000 < Date.now() && topbarType.value === 'full') {
                try {
                    await setThinTopbar()
                } catch (error) {
                    console.error('Failed to toggle TopBar type:', error);
                }
            }
        }, 1000);
    } else if (settings.control_mode === 'mouse') {
        document.addEventListener('mouseenter', handleMouseEnter);
        document.addEventListener('mouseleave', handleMouseLeave);
    }
}

async function destroy() {
    document.removeEventListener('mouseenter', handleMouseEnter);
    document.removeEventListener('mouseleave', handleMouseLeave);
    window.removeEventListener('click', handleClick);
}

async function reset() {
    destroy()
    init()
}

export { mouseOn, init, destroy, reset }