import { listen } from '@tauri-apps/api/event';
import { isPermissionGranted, requestPermission, sendNotification } from '@tauri-apps/plugin-notification';

/**
 * Initialize notification listener for course reminders
 */
export async function initReminderNotifications() {
  // Request notification permission if not granted
  let permissionGranted = await isPermissionGranted();

  if (!permissionGranted) {
    const permission = await requestPermission();
    permissionGranted = permission === 'granted';
  }

  if (!permissionGranted) {
    console.warn('Notification permission not granted');
    return;
  }

  // Listen for course reminder events from backend
  await listen('course-reminder', (event) => {
    try {
      const payload = typeof event.payload === 'string' ? JSON.parse(event.payload) : event.payload;

      const { title, body, course_name, minutes_until } = payload;

      // Send system notification
      sendNotification({
        title: title || `课程提醒: ${course_name}`,
        body: body || `${minutes_until}分钟后上课`,
        icon: 'icons/icon.png', // Optional: add app icon
      });

      console.log('Course reminder notification sent:', payload);
    } catch (error) {
      console.error('Failed to send reminder notification:', error);
    }
  });

  console.log('Reminder notification listener initialized');
}
