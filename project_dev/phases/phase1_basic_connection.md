# Phase 1: Basic Connection & Sensor

**Goal:** Authenticate with NesVentory and expose the core inventory sensors in Home Assistant.

## Status: Complete
## Last Updated: 2026-05-04

## Objectives
- [x] Create API client for NesVentory communication
- [x] Implement configuration flow for user setup
- [x] Create basic sensor entities
- [x] Add required integration metadata and documentation files

## Tasks

### 1. API Client (`api_client.py`)
Create a Python class to communicate with NesVentory's FastAPI backend.

**Implemented:**
- [x] Bearer token authentication flow
- [x] Item fetching via `/api/v1/items/`
- [x] Total item counting helper
- [x] Total value calculation helper
- [x] Location fetching helper
- [x] Category fetching helper
- [x] Connection test helper
- [x] Timeout and aiohttp error handling

**Deliverables:**
- [x] `custom_components/nesventory/api_client.py`

### 2. Config Flow (`config_flow.py`)
Implement UI-based configuration.

**Implemented:**
- [x] Prompt for NesVentory URL (e.g., `http://192.168.1.100:8001`)
- [x] Prompt for Username/Password
- [x] Validate authentication during setup
- [x] Validate API connectivity during setup
- [x] Store credentials in the Home Assistant config entry
- [x] Handle `CannotConnect` and `InvalidAuth` errors
- [x] Prevent duplicate entries by using `CONF_URL` as the unique ID

**Deliverables:**
- [x] `custom_components/nesventory/config_flow.py`
- [x] `custom_components/nesventory/strings.json` (UI labels)

### 3. Basic Sensors (`sensor.py` + `coordinator.py`)
Create initial sensor entities.

**Sensors Implemented:**
- [x] `sensor.nesventory_total_items`: State = Count of all items
- [x] `sensor.nesventory_total_value`: State = Sum of item values

**Implemented:**
- [x] `NesVentoryDataUpdateCoordinator` using `DataUpdateCoordinator`
- [x] 60 second polling interval via `DEFAULT_SCAN_INTERVAL`
- [x] Coordinator payload containing `{items, total_count, total_value}`
- [x] Graceful sensor state handling when coordinator data is unavailable
- [x] Device info and basic extra state attributes

**Deliverables:**
- [x] `custom_components/nesventory/coordinator.py`
- [x] `custom_components/nesventory/sensor.py`

### 4. Core Files
Create required integration files.

**Files Present:**
- [x] `custom_components/nesventory/__init__.py` - Component setup/entry point
- [x] `custom_components/nesventory/manifest.json` - HA metadata
- [x] `custom_components/nesventory/const.py` - Constants (domain, defaults, etc.)
- [x] `custom_components/nesventory/strings.json` - Config flow strings
- [x] `hacs.json` - HACS metadata (root level)
- [x] `README.md` - Basic usage documentation

## Testing Checklist
- [x] UI config flow is implemented for HA setup
- [x] Connection validation logic exists for auth, connectivity, and duplicate configuration handling
- [x] Coordinator-backed sensors are implemented for total items and total value
- [x] Integration setup/unload flow is implemented in `__init__.py`
- [ ] Automated unit tests exist
- [ ] Phase 1 behavior has been verified against the confirmed NesVentory auth endpoint and item value schema

## Dependencies
None (First phase)

## Known Issues / Follow-up for Phase 2
- [ ] Verify the actual NesVentory authentication endpoint; code still marks `/api/v1/auth/login` as TODO
- [ ] Confirm whether item value should come from `value`, `price`, or another field in the real API response
- [ ] Add automated unit tests; current validation is manual-only
- [ ] Create `custom_components/nesventory/services.yaml` before Home Assistant services are introduced
- [ ] Add an options flow so URL/credentials can be updated after initial setup
- [ ] Add token expiry retry/re-authentication logic so requests recover automatically after a 401/expired token
- [ ] Reconcile the initial plan with the current `hacs.json`; `render_readme` is present, but `filename` is not

## Notes
- Phase 1 is functionally complete for the initial integration milestone
- Remaining gaps are follow-up quality and compatibility items, not blockers for closing this phase
- Phase 2 should start by resolving the API verification and test coverage gaps above
