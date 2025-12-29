# Technical Specification: Social Media Blocker App

## Technical Context
- **Language**: Python 3.x
- **Framework**: Kivy (latest stable version)
- **Dependencies**: `kivy`
- **Platform**: Cross-platform (Windows dev, Android/iOS target)

## Technical Implementation Brief

The application will be built using the Kivy framework to ensure cross-platform compatibility (Mobile/Desktop). It will follow a modular structure separating UI, Data, and Logic.

### Key Components:
1.  **App Core (`main.py`)**: The Kivy App class managing the screen manager and global state.
2.  **Data Layer (`models.py`)**: Handles loading and saving user preferences and blocked sites to a local JSON file (`user_data.json`).
3.  **Blocking Service (`blocking_service.py`)**: A module responsible for the "blocking" logic. For this MVP, it will simulate blocking by managing a state and logging actions, prepared for future proxy/network implementation.
4.  **UI Layout**:
    - **Dashboard**: A `GridLayout` or `BoxLayout` implementing the 2-column design.
    - **Settings**: A separate `Screen` for user profile management.

## Source Code Structure

```
Refocus/
├── main.py                 # Entry point, App class, UI wiring
├── refocus.kv              # Kivy UI layout definition (optional, or inline in main.py)
├── models.py               # Data persistence logic (JSON handling)
├── blocking_service.py     # Logic for blocking sites
├── data/
│   └── user_data.json      # Persistent storage
└── tests/
    ├── test_models.py      # Unit tests for data layer
    └── test_service.py     # Unit tests for blocking logic
```

## Contracts

### Data Model (`user_data.json`)
```json
{
  "user": {
    "username": "User",
    "email": "user@example.com",
    "profile_pic": "path/to/image.png"
  },
  "blocked_sites": [
    "facebook.com",
    "instagram.com"
  ],
  "settings": {
    "blocking_active": false,
    "block_until": null
  }
}
```

### API / Interfaces

**`models.py`**
- `DataManager.load_data() -> dict`
- `DataManager.save_data(data: dict)`
- `DataManager.add_site(url: str)`
- `DataManager.remove_site(url: str)`

**`blocking_service.py`**
- `BlockingService.start_blocking(duration_minutes: int, sites: list)`
- `BlockingService.stop_blocking()`
- `BlockingService.is_active() -> bool`

## Delivery Phases

### Phase 1: Core Logic & Data
- Implement `models.py` for JSON handling.
- Implement `blocking_service.py` (stub/logic).
- Create unit tests for these modules.
- **Deliverable**: Working data and logic layer with passing tests.

### Phase 2: Basic UI Skeleton & Navigation
- Set up `main.py` with Kivy.
- Create `ScreenManager` with `DashboardScreen` and `SettingsScreen`.
- Implement navigation between screens.
- **Deliverable**: App launches, can switch between Dashboard and Settings.

### Phase 3: Dashboard Implementation
- Implement the 2-column layout.
- Connect "Time" buttons to `BlockingService`.
- Connect "Site List" to `DataManager`.
- **Deliverable**: Functional Dashboard where buttons update state and data.

### Phase 4: Settings & Polish
- Implement Settings form (update username/email).
- Add placeholder for Ads.
- Final integration test.
- **Deliverable**: Complete MVP App.

## Verification Strategy

### Automated Testing
- **Unit Tests**: Use `unittest` for `models.py` and `blocking_service.py`.
- **Command**: `python -m unittest discover tests`

### Manual Verification (Agent)
- **UI Launch**: Run `python main.py` (Note: Agent cannot see the window, so verification relies on process exit codes and log outputs).
- **Log Verification**: The app should log key events (e.g., "Site added", "Blocking started"). The agent can run the app in a background process, perform actions (if possible via CLI args or just verify startup), and check logs.
- **File Verification**: Check `data/user_data.json` content after running tests/scripts to ensure persistence works.

### Helper Scripts
- `tests/verify_data.py`: A script to inspect `user_data.json` and assert its content matches expected values, useful for verifying state after UI interactions if UI automation is hard.
