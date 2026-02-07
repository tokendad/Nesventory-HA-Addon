# Home Assistant Integration Plan

This document outlines the plan to create a Home Assistant (HA) integration for NesVentory, allowing users to interact with their inventory system directly from their smart home dashboard.

## 1. Value Proposition
Why connect NesVentory to Home Assistant?

### NesVentory → Home Assistant (Display & Control)
-   **Dashboard Widgets:** Display total item counts, total value, or specific category counts (e.g., "Pantry Items") on HA dashboards.
-   **Low Stock Alerts:** (Future) If quantity tracking is implemented, trigger HA automations when items run low (e.g., flash lights red, send notification to phone).
-   **Voice Add:** Use HA's Assist/Voice capabilities to add items to a "To Sort" list in NesVentory via voice commands.
-   **Room Context:** Use HA presence detection to trigger "Show me what's in this room" logic on a tablet dashboard.

### Home Assistant → NesVentory (Import & Sync)
-   **Device Import:** Import devices from HA with rich metadata (make, model, serial numbers, MAC addresses).
-   **Room/Area Sync:** Automatically sync HA rooms/areas to NesVentory locations.
-   **Automated Inventory:** Devices already tracked in HA can be bulk-imported into NesVentory with full details.
-   **Smart Home Asset Management:** Track all smart home devices alongside other inventory items.

## 2. HACS Publishing Requirements
To publish via HACS (Home Assistant Community Store), the repository must strictly adhere to specific structure and metadata requirements.

### Repository Structure
The integration can live in its own repository (recommended for cleaner separation) or within the main NesVentory repo (monorepo). For a monorepo approach, the structure should be:

```text
/
├── hacs.json                 # HACS metadata (Root)
├── custom_components/        # Integration folder
│   └── nesventory/           # The domain name
│       ├── __init__.py       # Component setup
│       ├── manifest.json     # HA metadata
│       ├── config_flow.py    # UI Configuration
│       ├── const.py          # Constants
│       ├── sensor.py         # Sensor entities
│       ├── strings.json      # Translations/Labels
│       └── services.yaml     # Custom services (e.g., add_item)
└── README.md                 # Documentation
```

### Critical Files

#### `hacs.json` (Root)
Tells HACS how to handle the repository.
```json
{
  "name": "NesVentory",
  "render_readme": true,
  "filename": "nesventory.zip" 
}
```
*Note: If using a monorepo, `content_in_root` is typically `false` (default).*

#### `manifest.json` (Inside `custom_components/nesventory/`)
Tells Home Assistant about the integration.
```json
{
  "domain": "nesventory",
  "name": "NesVentory",
  "codeowners": ["@tokendad"],
  "config_flow": true,
  "documentation": "https://github.com/tokendad/NesVentory",
  "issue_tracker": "https://github.com/tokendad/NesVentory/issues",
  "iot_class": "local_polling",
  "version": "0.1.0",
  "requirements": []
}
```

## 3. Implementation Plan

### Phase 1: Basic Connection & Sensor
**Goal:** Authenticate with NesVentory and show a "Total Items" sensor.

1.  **API Client:** Create a simple Python class (`api_client.py`) in the component folder to talk to NesVentory's FastAPI backend.
    *   Endpoint: `/api/v1/items/` (GET) to count items.
    *   Auth: Bearer Token (User will generate/provide or login via flow).
2.  **Config Flow (`config_flow.py`):**
    *   UI prompt for "URL" (e.g., `http://192.168.1.100:8001`) and "Username/Password".
    *   Validate connection during setup.
3.  **Sensor (`sensor.py`):**
    *   `sensor.nesventory_total_items`: State = Count of all items.
    *   `sensor.nesventory_total_value`: State = Sum of item values.

### Phase 2: Advanced Sensors & Services
**Goal:** actionable interactions and bidirectional data flow.

1.  **Service: `nesventory.add_quick_item`:**
    *   Accepts `name` string.
    *   Adds item to a default "Inbox" location with "Review Needed" status.
    *   Useful for voice commands: *"Hey Google, ask NesVentory to add AA Batteries"* -> Calls service.
2.  **Category Sensors:**
    *   Allow user to configure specific categories to track as sensors (e.g., "Freezer Items").
3.  **HA Device Import Service (`nesventory.import_ha_devices`):**
    *   Import devices from Home Assistant into NesVentory.
    *   Fetch device information: name, manufacturer, model, serial number, MAC address.
    *   Map HA areas/rooms to NesVentory locations.
    *   Support selective import (by area, device type, or all devices).
4.  **HA Area/Room Sync:**
    *   Option to automatically sync HA areas as NesVentory locations.
    *   Keep location names in sync with HA areas.

### Phase 3: Publishing
1.  **Separate Repo vs. Monorepo:** Decision needed. A separate repo (`NesVentory-HA`) is often easier for HACS versioning, as HACS releases are tied to GitHub releases. If using the main repo, every NesVentory release would trigger a HACS update, which might be noisy if the integration code hasn't changed. **Recommendation: Separate Repository.**
2.  **Submission:**
    *   Ensure repo is Public.
    *   Submit to `hacs/default` repository (optional, but makes it discoverable without adding custom repo URL).

## 4. Next Steps
1.  **Decision:** Should we create a new repository `NesVentory-HA` or build it inside `data/NesVentory`?
2.  **Development:** scaffolding the `custom_components/nesventory` directory.
