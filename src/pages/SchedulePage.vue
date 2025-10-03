<template>
    <div class="schedule-page">
        <div class="schedule-header">
            <h1>课程表</h1>
            <div class="header-controls">
                <mdui-text-field
                    :value="semesterStartDate"
                    @input="semesterStartDate = $event.target.value"
                    @blur="handleSemesterStartDateChange"
                    type="date"
                    label="学期开始日期"
                    class="semester-date-picker">
                </mdui-text-field>

                <mdui-select
                    :value="currentWeek"
                    @change="handleWeekChange($event.target.value)"
                    class="week-selector">
                    <mdui-menu-item v-for="week in weekOptions" :key="week.value" :value="week.value">
                        {{ week.label }}
                    </mdui-menu-item>
                </mdui-select>

                <mdui-button-icon icon="add" @click="openCourseDialog"></mdui-button-icon>
                <mdui-button-icon icon="refresh" @click="loadSchedule"></mdui-button-icon>
            </div>
        </div>

        <div class="schedule-grid">
            <!-- 时间轴 -->
            <div class="time-axis">
                <div class="time-header"></div>
                <div v-for="slot in timeSlots" :key="slot.time" class="time-slot">
                    {{ slot.label }}
                </div>
            </div>

            <!-- 星期列 -->
            <div class="week-days">
                <div class="day-headers">
                    <div v-for="(day, index) in weekDays" :key="index" class="day-header"
                        :class="{ 'today': index + 1 === todayWeekday }">
                        {{ day }}
                    </div>
                </div>

                <div class="courses-grid">
                    <div v-for="day in 7" :key="day" class="day-column"
                        :class="{ 'today-column': day === todayWeekday }">
                        <div v-for="course in scheduledCourses[day]" :key="course.id" class="course-card"
                            :style="getCourseStyle(course)" @click="selectCourse(course)">
                            <div class="course-name">{{ course.course_name }}</div>
                            <div class="course-location">{{ course.location || '' }}</div>
                            <div class="course-time">{{ course.start_time }}-{{ course.end_time }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 课程对话框 -->
        <mdui-dialog :open="courseDialogOpen" :headline="getDialogTitle()" close-on-overlay-click close-on-esc>
            <form class="dialog-form">
                <mdui-text-field
                    :value="courseForm.name"
                    @input="courseForm.name = $event.target.value"
                    label="课程名称"
                    helper="必填">
                </mdui-text-field>

                <mdui-text-field
                    :value="courseForm.teacher"
                    @input="courseForm.teacher = $event.target.value"
                    label="教师">
                </mdui-text-field>

                <mdui-text-field
                    :value="courseForm.location"
                    @input="courseForm.location = $event.target.value"
                    label="上课地点">
                </mdui-text-field>

                <div class="color-picker">
                    <label>课程颜色</label>
                    <div class="color-options">
                        <div v-for="color in courseColors" :key="color" class="color-option"
                            :class="{ 'selected': courseForm.color === color }" :style="{ backgroundColor: color }"
                            @click="courseForm.color = color"></div>
                    </div>
                </div>

                <mdui-select
                    :value="scheduleForm.day_of_week"
                    @change="scheduleForm.day_of_week = $event.target.value"
                    label="星期">
                    <mdui-menu-item v-for="(day, index) in weekDays" :key="index" :value="index + 1">
                        {{ day }}
                    </mdui-menu-item>
                </mdui-select>

                <div class="time-inputs">
                    <mdui-text-field
                        :value="scheduleForm.start_time"
                        @input="scheduleForm.start_time = $event.target.value"
                        @blur="handleStartTimeChange($event.target.value)"
                        type="time"
                        label="开始时间"
                        placeholder="08:00">
                    </mdui-text-field>

                    <mdui-text-field
                        :value="scheduleForm.end_time"
                        @input="scheduleForm.end_time = $event.target.value"
                        @blur="handleEndTimeChange($event.target.value)"
                        type="time"
                        label="结束时间"
                        placeholder="09:50">
                    </mdui-text-field>
                </div>

                <mdui-text-field
                    :value="weeksInput"
                    @input="weeksInput = $event.target.value"
                    label="上课周数"
                    helper="例如: 1-8,10,12-16 表示第1-8周、第10周、第12-16周">
                </mdui-text-field>

                <mdui-text-field
                    :value="scheduleForm.note"
                    @input="scheduleForm.note = $event.target.value"
                    label="备注">
                </mdui-text-field>

                <div v-if="dialogMode === 'clone'" class="clone-notice">
                    <mdui-icon name="content_copy"></mdui-icon>
                    <span>克隆模式：将基于现有课程创建新的课程安排</span>
                </div>
            </form>

            <mdui-button slot="action" variant="text" @click="courseDialogOpen = false">取消</mdui-button>
            <mdui-button slot="action" variant="tonal" @click="saveCourse">
                {{ dialogMode === 'edit' ? '更新' : '保存' }}
            </mdui-button>
        </mdui-dialog>

        <!-- 课程详情对话框 -->
        <mdui-dialog :open="detailDialogOpen" @close="detailDialogOpen = false"
            :headline="selectedCourse ? selectedCourse.course_name : '课程详情'" close-on-overlay-click close-on-esc>
            <div v-if="selectedCourse" class="detail-content">
                <div class="detail-item">
                    <mdui-icon name="person"></mdui-icon>
                    <span>教师：{{ selectedCourse.teacher || '未设置' }}</span>
                </div>
                <div class="detail-item">
                    <mdui-icon name="location_on"></mdui-icon>
                    <span>地点：{{ selectedCourse.location || '未设置' }}</span>
                </div>
                <div class="detail-item">
                    <mdui-icon name="schedule"></mdui-icon>
                    <span>时间：{{ weekDays[selectedCourse.day_of_week - 1] }} {{ selectedCourse.start_time }}-{{
                        selectedCourse.end_time }}</span>
                </div>
                <div class="detail-item" v-if="selectedCourse.weeks && selectedCourse.weeks.length">
                    <mdui-icon name="date_range"></mdui-icon>
                    <span>周数：第 {{ selectedCourse.weeks.join(', ') }} 周</span>
                </div>
                <div class="detail-item" v-if="selectedCourse.note">
                    <mdui-icon name="notes"></mdui-icon>
                    <span>备注：{{ selectedCourse.note }}</span>
                </div>
            </div>

            <mdui-button slot="action" variant="text" @click="detailDialogOpen = false">关闭</mdui-button>
            <mdui-button slot="action" variant="text" @click="editCourse">编辑</mdui-button>
            <mdui-button slot="action" variant="text" @click="cloneCourse">克隆</mdui-button>
            <mdui-button slot="action" variant="text" @click="deleteCourseEntry">删除</mdui-button>
        </mdui-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import {
    weekDays,
    courseColors,
    generateTimeSlots,
    generateWeekOptions,
    getTodayWeekday,
    getCurrentWeek,
    getCurrentWeekInfo,
    setSemesterStartDate,
    getCourses,
    addCourse,
    getSchedule,
    addScheduleEntry,
    deleteScheduleEntry,
    groupScheduleByDay,
    calculateCoursePosition,
    updateCourse
} from '../utils/schedule.js';

// 数据状态
const currentWeek = ref(1);
const semesterStartDate = ref('');
const isCalculatedWeek = ref(false);
const courses = ref([]);
const schedule = ref([]);
const scheduledCourses = ref({});
const selectedCourse = ref(null);
const editingCourseId = ref(null);
const editingScheduleId = ref(null);

// UI状态
const courseDialogOpen = ref(false);
const detailDialogOpen = ref(false);
const dialogMode = ref('add');

// 表单数据
const courseForm = ref({
    name: '',
    teacher: '',
    location: '',
    color: courseColors[0]
});

const scheduleForm = ref({
    day_of_week: 1,
    start_time: '08:00',
    end_time: '09:50',
    note: ''
});

const weeksInput = ref('1-16');

// 计算属性
const timeSlots = computed(() => generateTimeSlots(8, 22));
const weekOptions = computed(() => generateWeekOptions(20));
const todayWeekday = computed(() => getTodayWeekday());

// 方法
const getDialogTitle = () => {
    switch (dialogMode.value) {
        case 'add': return '添加课程';
        case 'edit': return '编辑课程';
        case 'clone': return '克隆课程';
        default: return '课程';
    }
};

const loadSchedule = async () => {
    try {
        schedule.value = await getSchedule(currentWeek.value);
        scheduledCourses.value = groupScheduleByDay(schedule.value);
    } catch (error) {
        console.error('Failed to load schedule:', error);
    }
};

// 时间验证和处理
const handleStartTimeChange = (newStartTime) => {
    scheduleForm.value.start_time = newStartTime;

    // 如果开始时间晚于结束时间，自动调整结束时间
    if (newStartTime && scheduleForm.value.end_time) {
        const startMinutes = timeToMinutes(newStartTime);
        const endMinutes = timeToMinutes(scheduleForm.value.end_time);

        if (startMinutes >= endMinutes) {
            // 设置结束时间为开始时间后110分钟（一般课程时长）
            const newEndMinutes = startMinutes + 110;
            scheduleForm.value.end_time = minutesToTime(newEndMinutes);
        }
    }
};

const handleEndTimeChange = (newEndTime) => {
    // 如果结束时间早于开始时间，自动调整开始时间
    if (scheduleForm.value.start_time && newEndTime) {
        const startMinutes = timeToMinutes(scheduleForm.value.start_time);
        const endMinutes = timeToMinutes(newEndTime);

        if (endMinutes <= startMinutes) {
            // 设置开始时间为结束时间前110分钟
            const newStartMinutes = Math.max(0, endMinutes - 110);
            scheduleForm.value.start_time = minutesToTime(newStartMinutes);
        }
    }

    scheduleForm.value.end_time = newEndTime;
};

// 时间工具函数
const timeToMinutes = (timeStr) => {
    const [hours, minutes] = timeStr.split(':').map(Number);
    return hours * 60 + minutes;
};

const minutesToTime = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${String(Math.min(hours, 23)).padStart(2, '0')}:${String(mins).padStart(2, '0')}`;
};

const handleWeekChange = async (newWeek) => {
    currentWeek.value = parseInt(newWeek);
    await loadSchedule();
};

const handleSemesterStartDateChange = async () => {
    if (semesterStartDate.value) {
        const result = await setSemesterStartDate(semesterStartDate.value);
        if (result.success && result.calculated_week) {
            currentWeek.value = result.calculated_week;
            isCalculatedWeek.value = true;
            await loadSchedule();
        }
    } else {
        // 清除学期开始日期，回到手动模式
        await setSemesterStartDate('');
        isCalculatedWeek.value = false;
    }
};

const openCourseDialog = () => {
    dialogMode.value = 'add';
    editingCourseId.value = null;
    editingScheduleId.value = null;

    courseForm.value = {
        name: '',
        teacher: '',
        location: '',
        color: courseColors[Math.floor(Math.random() * courseColors.length)]
    };
    scheduleForm.value = {
        day_of_week: 1,
        start_time: '08:00',
        end_time: '09:50',
        note: ''
    };
    weeksInput.value = '1-16';
    courseDialogOpen.value = true;
};

const editCourse = () => {
    if (!selectedCourse.value) return;

    dialogMode.value = 'edit';
    editingCourseId.value = selectedCourse.value.course_id;
    editingScheduleId.value = selectedCourse.value.id;

    // 填充表单数据
    courseForm.value = {
        name: selectedCourse.value.course_name,
        teacher: selectedCourse.value.teacher || '',
        location: selectedCourse.value.location || '',
        color: selectedCourse.value.color || courseColors[0]
    };

    scheduleForm.value = {
        day_of_week: selectedCourse.value.day_of_week,
        start_time: selectedCourse.value.start_time,
        end_time: selectedCourse.value.end_time,
        note: selectedCourse.value.note || ''
    };

    weeksInput.value = selectedCourse.value.weeks
        ? formatWeeksForInput(selectedCourse.value.weeks)
        : '1-16';

    detailDialogOpen.value = false;
    courseDialogOpen.value = true;
};

const cloneCourse = () => {
    if (!selectedCourse.value) return;

    dialogMode.value = 'clone';
    editingCourseId.value = null;
    editingScheduleId.value = null;

    // 克隆当前课程数据，但修改一些默认值以区分
    courseForm.value = {
        name: `${selectedCourse.value.course_name} (副本)`,
        teacher: selectedCourse.value.teacher || '',
        location: selectedCourse.value.location || '',
        color: courseColors[Math.floor(Math.random() * courseColors.length)]
    };

    scheduleForm.value = {
        day_of_week: selectedCourse.value.day_of_week,
        start_time: selectedCourse.value.start_time,
        end_time: selectedCourse.value.end_time,
        note: selectedCourse.value.note || ''
    };

    weeksInput.value = selectedCourse.value.weeks
        ? formatWeeksForInput(selectedCourse.value.weeks)
        : '1-16';

    detailDialogOpen.value = false;
    courseDialogOpen.value = true;
};

const saveCourse = async () => {
    try {
        if (!courseForm.value.name.trim()) {
            alert('请输入课程名称');
            return;
        }

        const weeks = parseWeeks(weeksInput.value);

        if (dialogMode.value === 'edit') {
            // 更新模式
            // 首先更新课程信息
            await updateCourse(editingCourseId.value, courseForm.value);

            // 然后删除旧的课程安排并创建新的
            await deleteScheduleEntry(editingScheduleId.value);
            await addScheduleEntry({
                course_id: editingCourseId.value,
                day_of_week: scheduleForm.value.day_of_week,
                start_time: scheduleForm.value.start_time,
                end_time: scheduleForm.value.end_time,
                weeks: weeks,
                note: scheduleForm.value.note
            });
        } else {
            // 添加或克隆模式
            const course = await addCourse(courseForm.value);
            await addScheduleEntry({
                course_id: course.id,
                day_of_week: scheduleForm.value.day_of_week,
                start_time: scheduleForm.value.start_time,
                end_time: scheduleForm.value.end_time,
                weeks: weeks,
                note: scheduleForm.value.note
            });
        }

        // 重新加载
        await loadSchedule();
        courseDialogOpen.value = false;
    } catch (error) {
        console.error('Failed to save course:', error);
        alert('保存失败，请重试');
    }
};

const selectCourse = (course) => {
    selectedCourse.value = course;
    detailDialogOpen.value = true;
};

const deleteCourseEntry = async () => {
    if (selectedCourse.value) {
        try {
            await deleteScheduleEntry(selectedCourse.value.id);
            await loadSchedule();
            detailDialogOpen.value = false;
        } catch (error) {
            console.error('Failed to delete course entry:', error);
            alert('删除失败，请重试');
        }
    }
};

const getCourseStyle = (course) => {
    const position = calculateCoursePosition(course.start_time, course.end_time, 8, 60);
    return {
        top: `${position.top}px`,
        height: `${position.height}px`,
        backgroundColor: course.color || courseColors[0],
        opacity: 0.9
    };
};

const parseWeeks = (input) => {
    const weeks = [];
    const parts = input.split(',');

    parts.forEach(part => {
        const range = part.trim();
        if (range.includes('-')) {
            const [start, end] = range.split('-').map(Number);
            for (let i = start; i <= end; i++) {
                weeks.push(i);
            }
        } else {
            const week = parseInt(range);
            if (!isNaN(week)) {
                weeks.push(week);
            }
        }
    });

    return [...new Set(weeks)].sort((a, b) => a - b);
};

const formatWeeksForInput = (weeks) => {
    // 将周数数组转换为用户友好的字符串格式
    if (!weeks || weeks.length === 0) return '';

    const sortedWeeks = [...weeks].sort((a, b) => a - b);
    const ranges = [];
    let start = sortedWeeks[0];
    let end = sortedWeeks[0];

    for (let i = 1; i < sortedWeeks.length; i++) {
        if (sortedWeeks[i] === end + 1) {
            end = sortedWeeks[i];
        } else {
            if (start === end) {
                ranges.push(start.toString());
            } else if (end === start + 1) {
                ranges.push(start.toString());
                ranges.push(end.toString());
            } else {
                ranges.push(`${start}-${end}`);
            }
            start = end = sortedWeeks[i];
        }
    }

    // 处理最后一个范围
    if (start === end) {
        ranges.push(start.toString());
    } else if (end === start + 1) {
        ranges.push(start.toString());
        ranges.push(end.toString());
    } else {
        ranges.push(`${start}-${end}`);
    }

    return ranges.join(',');
};

onMounted(async () => {
    // 获取当前周数信息（包括是否自动计算）
    const weekInfo = await getCurrentWeekInfo();
    currentWeek.value = weekInfo.week;
    semesterStartDate.value = weekInfo.semester_start_date || '';
    isCalculatedWeek.value = weekInfo.is_calculated;

    await loadSchedule();
});
</script>

<style scoped>
.schedule-page {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
}

.schedule-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.schedule-header h1 {
    margin: 0;
    font-size: 28px;
}

.header-controls {
    display: flex;
    gap: 10px;
    align-items: center;
}

.week-selector {
    width: 120px;
}

.semester-date-picker {
    width: 180px;
}

.schedule-grid {
    display: flex;
    background: rgb(var(--mdui-color-surface));
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.time-axis {
    width: 60px;
    border-right: 1px solid rgb(var(--mdui-color-surface-variant));
}

.time-header {
    height: 50px;
    border-bottom: 1px solid rgb(var(--mdui-color-surface-variant));
}

.time-slot {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: rgb(var(--mdui-color-on-surface-variant));
    border-bottom: 1px solid rgba(var(--mdui-color-surface-variant), 0.3);
}

.week-days {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.day-headers {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    height: 50px;
    border-bottom: 1px solid rgb(var(--mdui-color-surface-variant));
}

.day-header {
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    color: rgb(var(--mdui-color-on-surface));
    border-right: 1px solid rgba(var(--mdui-color-surface-variant), 0.3);
}

.day-header:last-child {
    border-right: none;
}

.day-header.today {
    color: rgb(var(--mdui-color-primary));
    background-color: rgba(var(--mdui-color-primary), 0.1);
}

.courses-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    height: 840px;
    position: relative;
}

.day-column {
    position: relative;
    border-right: 1px solid rgba(var(--mdui-color-surface-variant), 0.3);
    background-image: repeating-linear-gradient(to bottom,
            transparent,
            transparent 59px,
            rgba(var(--mdui-color-surface-variant), 0.3) 59px,
            rgba(var(--mdui-color-surface-variant), 0.3) 60px);
}

.day-column:last-child {
    border-right: none;
}

.today-column {
    background-color: rgba(var(--mdui-color-primary), 0.03);
}

.course-card {
    position: absolute;
    left: 2px;
    right: 2px;
    border-radius: 8px;
    padding: 8px;
    color: white;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
    overflow: hidden;
}

.course-card:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    z-index: 10;
}

.course-name {
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.course-location {
    font-size: 12px;
    opacity: 0.95;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.course-time {
    font-size: 11px;
    opacity: 0.9;
    margin-top: 4px;
}

/* Dialog styles */
.dialog-form {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 16px 0;
}

.color-picker {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.color-picker label {
    font-size: 14px;
    color: rgb(var(--mdui-color-on-surface-variant));
}

.color-options {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.color-option {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    cursor: pointer;
    transition: transform 0.2s;
    border: 2px solid transparent;
}

.color-option:hover {
    transform: scale(1.1);
}

.color-option.selected {
    border-color: rgb(var(--mdui-color-primary));
    transform: scale(1.1);
}

.time-inputs {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

.detail-content {
    padding: 16px 0;
}

.detail-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    color: rgb(var(--mdui-color-on-surface));
}

.detail-item mdui-icon {
    color: rgb(var(--mdui-color-on-surface-variant));
    font-size: 20px;
}

.clone-notice {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px;
    background-color: rgba(var(--mdui-color-primary), 0.1);
    border-radius: 8px;
    color: rgb(var(--mdui-color-primary));
    font-size: 14px;
}

.clone-notice mdui-icon {
    font-size: 18px;
}
</style>
