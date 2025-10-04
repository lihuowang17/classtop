# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
## Project Overview

ClassTop is a desktop course management and display tool built with Tauri 2 + Vue 3 + PyTauri. It provides an always-on-top progress bar showing current/next classes and a full-featured management interface.

**Key Features:**
- Real-time course progress display with always-on-top transparent window
- Full course schedule CRUD operations
- SQLite-based data persistence
- System tray integration
- Automatic/manual week number calculation

## Tech Stack

**Frontend:**
- Vue 3 (Composition API) + Vue Router 4
- Vite 6 as build tool
- MDUI 2.1.4 (Material Design components)
- Less for styling

**Backend:**
- Tauri 2 framework (Rust)
- PyTauri 0.8 for Python-Rust integration
- Python 3.10+ backend logic
- SQLite database

## Development Commands

### Development Mode
```bash
npm run tauri dev
```
This starts both windows:
- **main** window (1200x800): Course management interface at `/#/`
- **topbar** window (1400x50): Always-on-top progress bar at `/#/topbar`

### Build for Production
```bash
npm run -- tauri build --config="src-tauri/tauri.bundle.json" -- --profile bundle-release
```
Build artifacts located at `src-tauri/target/bundle-release/`

### Frontend Only Development
```bash
npm run dev        # Start Vite dev server on port 1420
npm run build      # Build frontend to dist/
```

### Dependencies
```bash
npm install        # Install Node.js dependencies
```

## Architecture

### Dual-Window System
The application uses Tauri's multi-window feature with distinct purposes:

1. **TopBar Window** (`/#/topbar`):
   - Always-on-top, transparent, borderless window
   - Displays Clock.vue (left) + Schedule.vue (right)
   - Updates every second for progress, every 10s for data refresh
   - Configuration: `src-tauri/tauri.conf.json` lines 14-41

2. **Main Window** (`/#/`):
   - Standard window with navigation
   - Routes: Home, SchedulePage, Settings
   - Uses Main.vue wrapper component

### Python-Rust Communication Flow

```
Vue Frontend
  ↓ pyInvoke('command_name', params)
Python Commands (commands.py)
  ↓ uses
Database Layer (db.py) + Managers (schedule_manager.py, settings_manager.py)
  ↓ emits events via
Event Handler (events.py)
  ↓ Emitter.emit()
Vue Frontend receives events
```

**Key Pattern:** All Python commands are registered via `@commands.command()` decorator in `commands.py`. Frontend calls them using `pyInvoke()` from `tauri-plugin-pytauri-api`.

### Database Schema

SQLite database at runtime: `classtop.db`

**Tables:**
- `courses`: Course information (id, name, teacher, location, color)
- `schedule`: Schedule entries (id, course_id, day_of_week, start_time, end_time, weeks as JSON)
  - `day_of_week`: ISO format (1=Monday, 7=Sunday)
  - `weeks`: JSON array like `[1,2,3,...]` indicating which weeks this entry applies
- `config`: Key-value configuration store

### Event System

The application uses a singleton `EventHandler` (`events.py`) for real-time updates:

- **Thread-safe:** Uses async portal for cross-thread event emission
- **Events emitted:**
  - `schedule-update`: When courses/schedules change (types: course_added, course_updated, course_deleted, schedule_added, schedule_deleted)
  - `setting-update`: When single setting changes
  - `settings-batch-update`: When multiple settings update

Frontend components listen via Tauri event listeners to auto-refresh data.

### Week Number Calculation

Two modes (managed by `settings_manager.py`):

1. **Automatic (preferred):** Set `semester_start_date` in config, calculates current week from today's date
2. **Manual (deprecated):** Directly set `current_week` config value

Week calculation logic in `db.py:get_calculated_week_number()` - prioritizes semester_start_date if present.

### Schedule Display Logic

Located in `src/TopBar/components/Schedule.vue` and `src/utils/schedule.js`:

**States:**
1. **During class:** Shows course name, location, time range, progress bar (0-100%)
2. **Break time:** Shows "Next: [course]" with countdown timer
3. **Day ended:** Shows tomorrow's first class

**Important:** Uses `getScheduleForWeek()` to fetch entire week, then client-side calculates current/next class. This avoids deprecated server-side `get_current_class()` endpoints.

**Cross-day logic:** `findNextClassAcrossWeek()` in `schedule.js` handles next-day lookup when today's classes are over.

### Python Module Structure

`src-tauri/python/tauri_app/`:

- `__init__.py`: Application entry point, initializes all managers and event system
- `commands.py`: Pydantic-based command definitions for frontend-backend interface
- `db.py`: Raw SQLite operations, connection management
- `schedule_manager.py`: Business logic for schedule CRUD (uses db.py, emits events)
- `settings_manager.py`: Manages application settings with defaults
- `events.py`: Thread-safe singleton event handler
- `tray.py`: System tray menu (show/hide windows, quit)
- `logger.py`: Logging utilities with file rotation

**Initialization order** (in `__init__.py:main()`):
1. Logger
2. Async portal (for thread-safe async operations)
3. Event handler
4. Database
5. Settings manager (initializes defaults)
6. Schedule manager
7. System tray

### Frontend Module Structure

`src/`:

- `main.js`: App entry, router setup, MDUI import
- `App.vue`: Root component
- `Main.vue`: Layout wrapper for main window (navigation + router-view)
- `TopBar/TopBar.vue`: TopBar window root
- `TopBar/components/Clock.vue`: Time display
- `TopBar/components/Schedule.vue`: Course progress/countdown logic
- `pages/Home.vue`: Welcome page
- `pages/SchedulePage.vue`: Full course schedule management
- `pages/Settings.vue`: Week/semester settings
- `utils/schedule.js`: Shared utilities for time calculations, API calls (pyInvoke wrappers)
- `router/index.js`: Route definitions

## Important Patterns

### Adding a New Python Command

1. Define request/response models in `commands.py` using Pydantic
2. Add `@commands.command()` decorated async function
3. Implement logic (usually delegates to db.py or managers)
4. Export wrapper in `src/utils/schedule.js` using `pyInvoke()`
5. Add to capabilities if needed: `src-tauri/capabilities/default.json`

### Time Format Consistency

- **Storage:** HH:MM string format (e.g., "14:30")
- **Day of week:** ISO 8601 (1-7, Monday=1, Sunday=7)
- **Parsing:** Use `parseTime()` from `schedule.js` to get `{hour, minute}` objects
- **Progress calculation:** Include seconds for smooth progress bars (`calculateCourseProgress()`)

### Cross-day Schedule Queries

When today's classes end, frontend must query next day:
- Use `getScheduleForWeek()` to get all week data once
- Use `findNextClassAcrossWeek()` to find cross-day next class
- Avoids multiple Python calls and handles week wraparound

## Development Tips

- **Hot reload:** Frontend hot reloads automatically, but Python changes require restarting `npm run tauri dev`
- **Vite config:** MDUI components use custom elements (`tag.startsWith('mdui-')`), configured in `vite.config.js`
- **Database location:** Development DB is in Tauri's app data directory; check logs for exact path
- **Logging:** Python logs rotation-managed, accessible via `get_logs` command (max 200 lines default)
- **Build profiles:** Uses custom `bundle-release` profile (see `Cargo.toml` lines 36-41) for production builds

## Common Issues

### PyTauri Integration
- All Python dependencies must be available at runtime (PyTauri bundles Python environment)
- `pyInvoke()` is async - always await the call
- Event emission from non-async-loop threads uses the portal (handled automatically by EventHandler)

### Window Management
- TopBar window has `closable: false` to prevent accidental closure
- Both windows defined in `tauri.conf.json` app.windows array
- Main window starts hidden (`visible: false`), shown by system tray

### Week Calculation Edge Cases
- When semester_start_date is cleared, falls back to manual week (default 1)
- Week numbers calculated as floor((today - start_date).days / 7) + 1
- Frontend must call `get_current_week()` to get computed week info
