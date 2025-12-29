# Feature Specification: Social Media Blocker App

## User Stories

### User Story 1 - Dashboard & Profile
**Acceptance Scenarios**:
1. **Given** the app is launched, **When** the user views the home screen, **Then** they see their profile picture and name in the top left.
2. **Given** the app is launched, **When** the user clicks the settings button (top right), **Then** they are navigated to a settings page (Profile, Password, Email).

### User Story 2 - Blocking Duration
**Acceptance Scenarios**:
1. **Given** the user is on the dashboard, **When** they select a preset duration (1hr, 2hr, 3hr, 4hr), **Then** the blocking timer is set for that duration.
2. **Given** the user is on the dashboard, **When** they select "Custom", **Then** they can input a start time and end time.

### User Story 3 - Site Management
**Acceptance Scenarios**:
1. **Given** the user is on the dashboard, **When** they view the site list, **Then** they see a dropdown/list of currently blocked sites.
2. **Given** the user wants to block a new site, **When** they click "Add" and enter a URL, **Then** the site is added to the list.
3. **Given** a site is selected, **When** the user clicks "Delete", **Then** the site is removed from the list.

### User Story 4 - Blocking Enforcement
**Acceptance Scenarios**:
1. **Given** a blocking session is active, **When** the user tries to access a blocked site, **Then** the request is intercepted/blocked (simulated via Proxy/Network logic).

## Requirements

### Functional Requirements
1. **UI Layout**:
    - **Header**: Profile info (left), Settings icon (right).
    - **Main Content**: Two-column layout.
        - **Col 1 (Time)**: Buttons for 1h, 2h, 3h, 4h. Custom time picker (Start/End).
        - **Col 2 (Sites)**: Dropdown/List of sites. "Add" button. "Delete" button.
    - **Footer**: Placeholder for Announcement/Advertisement.
2. **Data Persistence**:
    - User profile and blocked sites list must be saved to a local JSON file.
3. **Blocking Logic**:
    - Implement a service/module structure for Network/Proxy blocking.
    - For the MVP, this can be a toggleable state that logs "Blocking [Site]" or simulates a proxy start.

### Technical Requirements
- **Language**: Python
- **Framework**: Kivy (for mobile UI)
- **Storage**: JSON
- **Platform**: Android/iOS (via Kivy/Buildozer), testable on Windows.

## Success Criteria
- App launches with the described UI layout.
- User can add/remove sites from the list, persisting to JSON.
- User can select a timer, which updates the app state.
- "Blocking" state is visually indicated or logged.
