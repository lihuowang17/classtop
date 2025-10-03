import { onMounted, ref } from "vue";
import { isPinned, setFullTopbar, setThinTopbar } from "../TopBar/TopBar.vue";
import { current } from "../TopBar/components/Schedule.vue";


const mouseOn = ref(false)

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

async function init() {
    document.addEventListener('mouseenter', handleMouseEnter);
    document.addEventListener('mouseleave', handleMouseLeave);
}

export { mouseOn, init }