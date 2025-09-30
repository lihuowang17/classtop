"""
System tray functionality for ClassTop application.
"""

import os
from typing import Optional

from pytauri.tray import TrayIcon, TrayIconEvent, MouseButton
from pytauri.menu import Menu, MenuItem, PredefinedMenuItem
from pytauri.image import Image
from pytauri import AppHandle, Manager
from . import logger


class SystemTray:
    """Handles system tray icon and menu functionality."""

    def __init__(self):
        self.tray: Optional[TrayIcon] = None
        self.portal = None
        self.app_handle: Optional[AppHandle] = None

    def toggle_window(self, window_name: str) -> bool:
        """Toggle window visibility using PyTauri API"""
        try:
            # Get the window by name
            window = Manager.get_webview_window(self.app_handle, window_name)
            if not window:
                logger.log_message("error", f"Window '{window_name}' not found")
                return False

            # Check if window is visible and toggle
            is_visible = window.is_visible()

            if is_visible:
                window.hide()
            else:
                window.show()
                # Try to focus the window after showing
                try:
                    window.set_focus()
                except:
                    pass  # Focus might fail on some systems

            return not is_visible
        except Exception as e:
            logger.log_message("error", f"Error toggling window: {e}")
            return False

    def handle_tray_event(self, tray: TrayIcon, event: TrayIconEvent):
        """Handle system tray icon events"""
        if isinstance(event, TrayIconEvent.Click):
            # Left click - toggle main window
            if event.button == MouseButton.Left:
                self.toggle_window("main")

    def handle_menu_event(self, app, event):
        """Handle menu item clicks"""
        try:
            # event is the menu item id as a string
            if event == "show_topbar":
                # Toggle topbar window
                self.toggle_window("topbar")

            elif event == "quit":
                # Quit the application
                if self.app_handle:
                    self.app_handle.exit(0)

        except Exception as e:
            logger.log_message("error", f"Error handling menu event: {e}")

    def create_tray_menu(self) -> Menu:
        """Create the system tray context menu"""
        # Create menu with items using the correct API
        menu_items = [
            MenuItem.with_id(self.app_handle, "show_topbar", "Show/Hide Topbar", True),
            PredefinedMenuItem.separator(self.app_handle),
            MenuItem.with_id(self.app_handle, "quit", "Quit", True)
        ]

        menu = Menu.with_items(self.app_handle, menu_items)
        return menu

    def setup_tray(self, app_handle, portal) -> bool:
        """
        Setup system tray icon and menu.

        Args:
            app_handle: The Tauri app handle
            portal: The asyncio portal for async operations

        Returns:
            bool: True if setup successful, False otherwise
        """
        try:
            # Store references for event handlers (must be before create_tray_menu)
            self.portal = portal
            self.app_handle = app_handle

            # Create tray icon using app handle
            self.tray = TrayIcon(app_handle)

            # Set tray icon (using 32x32.png for system tray)
            icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "icons", "32x32.png")

            # Load icon as Image object
            with open(icon_path, 'rb') as f:
                icon_data = f.read()
            icon_image = Image.from_bytes(icon_data)
            self.tray.set_icon(icon_image)

            # Set tooltip
            self.tray.set_tooltip("ClassTop - System Tray")

            # Create and set menu (after app_handle is set)
            menu = self.create_tray_menu()
            self.tray.set_menu(menu)
            self.tray.set_show_menu_on_left_click(False)  # 左键不弹菜单

            # Set event handlers
            self.tray.on_tray_icon_event(self.handle_tray_event)
            self.tray.on_menu_event(self.handle_menu_event)

            # Make tray visible
            self.tray.set_visible(True)

            return True

        except Exception as e:
            logger.log_message("error", f"Error setting up system tray: {e}")
            return False