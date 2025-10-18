use pyo3::prelude::*;
use tauri::{LogicalPosition, LogicalSize, Manager};

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

pub fn tauri_generate_context() -> tauri::Context {
    tauri::generate_context!()
}

// Window commands
#[tauri::command]
async fn setup_topbar_window(app_handle: tauri::AppHandle, height: u32) -> Result<(), String> {
    let window = app_handle
        .get_webview_window("topbar")
        .ok_or("Window not found")?;

    if let Ok(monitors) = window.available_monitors() {
        if let Some(monitor) = monitors.first() {
            // 获取 scale factor 用于转换物理像素到逻辑像素
            let scale_factor = monitor.scale_factor();

            // monitor.size() 返回物理像素，转换为逻辑像素
            let screen_size = monitor.size();
            let logical_screen_width = (screen_size.width as f64 / scale_factor) as u32;

            // 计算逻辑像素下的窗口宽度和位置
            let window_width = (logical_screen_width as f64 * 0.6) as u32;
            let window_x = (logical_screen_width as f64 * 0.2) as i32;

            // 使用 LogicalSize 和 LogicalPosition，Tauri 会自动处理 DPI 缩放
            window
                .set_size(LogicalSize::new(window_width, height))
                .map_err(|e| e.to_string())?;
            window
                .set_position(LogicalPosition::new(window_x, 0))
                .map_err(|e| e.to_string())?;
        }
    }

    Ok(())
}

#[tauri::command]
async fn resize_topbar_window(
    app_handle: tauri::AppHandle,
    width: u32,
    height: u32,
) -> Result<(), String> {
    let window = app_handle
        .get_webview_window("topbar")
        .ok_or("Window not found")?;

    if let Ok(monitors) = window.available_monitors() {
        if let Some(monitor) = monitors.first() {
            // 获取 scale factor 用于转换物理像素到逻辑像素
            let scale_factor = monitor.scale_factor();

            // monitor.size() 返回物理像素，转换为逻辑像素
            let screen_size = monitor.size();
            let logical_screen_width = (screen_size.width as f64 / scale_factor) as u32;

            // 计算逻辑像素下的窗口 x 位置（居中）
            let window_x = ((logical_screen_width - width) / 2) as i32;

            // 使用 LogicalSize 和 LogicalPosition，Tauri 会自动处理 DPI 缩放
            window
                .set_size(LogicalSize::new(width, height))
                .map_err(|e| e.to_string())?;
            window
                .set_position(LogicalPosition::new(window_x, 0))
                .map_err(|e| e.to_string())?;
        }
    }

    Ok(())
}

#[tauri::command]
async fn toggle_window(app_handle: tauri::AppHandle, window_name: String) -> Result<bool, String> {
    // Use the provided window name (e.g., "main", "topbar") instead of hard-coded "main"
    let window = app_handle
        .get_webview_window(&window_name)
        .ok_or("Window not found")?;

    let is_visible = window.is_visible().map_err(|e| e.to_string())?;

    if is_visible {
        window.hide().map_err(|e| e.to_string())?;
    } else {
        window.show().map_err(|e| e.to_string())?;
        // Try to focus the window after showing it
        window.set_focus().map_err(|e| e.to_string())?;
    }

    Ok(!is_visible)
}

#[pymodule(gil_used = false)]
#[pyo3(name = "ext_mod")]
pub mod ext_mod {
    use super::*;

    #[pymodule_init]
    fn init(module: &Bound<'_, PyModule>) -> PyResult<()> {
        pytauri::pymodule_export(
            module,
            // i.e., `context_factory` function of python binding
            |_args, _kwargs| Ok(tauri_generate_context()),
            // i.e., `builder_factory` function of python binding
            |_args, _kwargs| {
                let builder = tauri::Builder::default()
                    .plugin(tauri_plugin_clipboard_manager::init())
                    .plugin(tauri_plugin_opener::init())
                    .invoke_handler(tauri::generate_handler![
                        greet,
                        setup_topbar_window,
                        resize_topbar_window,
                        toggle_window
                    ]);
                Ok(builder)
            },
        )
    }
}
