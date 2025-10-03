use pyo3::prelude::*;
use tauri::{Manager, PhysicalPosition, PhysicalSize};

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
async fn setup_topbar_window(app_handle: tauri::AppHandle) -> Result<(), String> {
    let window = app_handle
        .get_webview_window("topbar")
        .ok_or("Window not found")?;

    if let Ok(monitors) = window.available_monitors() {
        if let Some(monitor) = monitors.first() {
            let screen_size = monitor.size();
            let screen_width = screen_size.width;

            let window_width = (screen_width as f64 * 0.6) as u32;
            let window_x = (screen_width as f64 * 0.2) as i32;

            window
                .set_size(PhysicalSize::new(window_width, 50))
                .map_err(|e| e.to_string())?;
            window
                .set_position(PhysicalPosition::new(window_x, 0))
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
            let screen_size = monitor.size();
            let screen_width = screen_size.width;

            // Calculate x position to center the window horizontally
            let window_x = ((screen_width - width) / 2) as i32;

            window
                .set_size(PhysicalSize::new(width, height))
                .map_err(|e| e.to_string())?;
            window
                .set_position(PhysicalPosition::new(window_x, 0))
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
        let _ = window.set_focus().map_err(|e| e.to_string())?;
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
