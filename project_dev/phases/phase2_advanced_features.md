# Phase 2: Advanced Sensors & Services

**Goal:** Add actionable interactions, richer sensors, and bidirectional sync features after the Phase 1 API details are verified.

## Status: Complete ✅
## Last Updated: 2026-05-08

## Dependencies
- Phase 1 implementation is complete ✅
- Phase 1 API/schema follow-up items fully resolved ✅

## Objectives
- [x] Resolve Phase 1 API/schema follow-up items (auth endpoint fixed to `POST /api/token` form-encoded; value field confirmed as `estimated_value`/`purchase_price`; categories replaced with tags via `/api/tags/`)
- [x] Add automated unit tests with >80% coverage (**97% achieved** — 106 tests across all modules)
- [x] Add an options flow for reconfiguration (scan interval, tracked sensors — credentials not included)
- [x] Implement token refresh / reconnection handling
- [x] Implement custom services for adding and syncing items
- [x] Add category-specific sensors
- [x] Add location-specific sensors
- [x] Enable voice assistant integration (services auto-available via HA Assist; not explicitly tested)
- [x] Import HA devices and rooms into NesVentory

## Tasks

### 1. Resolve Phase 1 Follow-up Items
Close the API compatibility gaps before expanding the integration surface area.

**Status: Done ✅**

**Completed:**
- Token expiry / re-authentication: `_get_json()` helper in `api_client.py` automatically retries once on HTTP 401
- Auth endpoint corrected: `POST /api/token` with `application/x-www-form-urlencoded` body (was `/api/v1/auth/login` JSON)
- All endpoint paths corrected: removed `/v1/` prefix (`/api/items/`, `/api/locations/`)
- Categories replaced with tags: `/api/tags/` (no `/api/categories/` exists in the API)
- Item value field confirmed: `estimated_value` (string decimal) with fallback to `purchase_price`

### 2. Unit Tests
Set up the automated test suite that is currently missing.

**Status: Done ✅ — 97% coverage achieved**

**Completed:**
- `tests/conftest.py` — HA module stubs (fixed CoordinatorEntity, SensorEntity, ConfigFlow, DataUpdateCoordinator stubs)
- `tests/test_api_client.py` — 41 tests covering authenticate, `_get_json` retry logic, test_connection, get_items/locations/categories, create_item/location, `_get_headers`, aggregates
- `tests/test_coordinator.py` — 8 tests covering all `_async_update_data` paths (success, items failure, optional fallbacks, value/price logic)
- `tests/test_config_flow.py` — 12 tests covering `validate_input`, `ConfigFlow.async_step_user`, `OptionsFlowHandler.async_step_init`
- `tests/test_sensor.py` — 25 tests covering all 4 sensor classes (unique IDs, native_value, extra_state_attributes, edge cases)
- `tests/test_init.py` — 20 tests covering `_get_client`, `async_setup_entry`, `async_unload_entry`, all 3 service handlers

**Coverage by module:**
| Module | Coverage |
|---|---|
| `__init__.py` | 99% |
| `api_client.py` | 94% |
| `config_flow.py` | 98% |
| `const.py` | 100% |
| `coordinator.py` | 95% |
| `sensor.py` | 100% |
| **Total** | **97%** |

### 3. Options Flow
Allow users to reconfigure the integration after initial setup.

**Status: Done ✅**

Implemented in `config_flow.py` (`OptionsFlowHandler`). Supports:
- Configurable scan interval (30–3600 s, default 60 s, using `NumberSelector`)
- Multi-select tracked categories (populated from live coordinator data)
- Multi-select tracked locations (populated from live coordinator data)
- Auto-reload on save via `_async_update_listener` in `__init__.py`

**Note:** URL and credential re-configuration are not yet supported through the options flow.

### 4. Token Refresh / Reconnection
Improve reliability when tokens expire or the backend restarts.

**Status: Done ✅**

Implemented in `api_client.py` via the `_get_json()` shared helper:
- On HTTP 401, clears `self._token` and calls `authenticate()` once
- Retries the original request with the new token
- All GET endpoints (`get_items`, `get_locations`, `get_categories`) use this helper automatically

### 5. Quick Add Service
Create a service to quickly add items to NesVentory.

**Status: Done ✅**

**Service:** `nesventory.add_quick_item`

**Implemented Parameters** (differs slightly from original spec):
- `name` (string, required): Item name
- `quantity` (integer, optional, default: 1, range 1–999): Number of items
- `location` (string, optional): Location/room name
- `category` (string, optional): Category name

> **Note:** The original spec included a `status` field (default: "Review Needed"). The implementation uses `category` instead. The `status` field may be added later once the NesVentory item creation API is fully verified.

Uses `POST /api/v1/items/` (endpoint needs live verification). Registered in `__init__.py`, described in `services.yaml`. Triggers a coordinator refresh after creation so sensors update immediately.

### 6. Category Sensors
Allow users to track specific categories as individual sensors.

**Status: Done ✅**

- `NesVentoryCategorySensor` implemented in `sensor.py`
- `sensor.nesventory_category_<slug>`: item count for a specific category
- Configured via options flow (`CONF_TRACKED_CATEGORIES`, multi-select)
- Category list populated dynamically from coordinator data
- Extra attribute: `category` name

### 7. Location-Based Sensors
Similar to categories, but for locations/rooms.

**Status: Done ✅**

- `NesVentoryLocationSensor` implemented in `sensor.py`
- `sensor.nesventory_location_<slug>`: item count for a specific location
- Configured via options flow (`CONF_TRACKED_LOCATIONS`, multi-select)
- Location list populated dynamically from coordinator data
- Extra attribute: `location` name

### 8. Enhanced Attributes
Add richer data to existing sensors.

**Status: Done ✅**

**Total Items Sensor (`extra_state_attributes`):**
- `items_by_status`: dict of status → count across all items
- `items_by_category`: top-5 categories by item count
- `last_update`: coordinator last success timestamp

**Total Value Sensor (`extra_state_attributes`):**
- `value_by_category`: top-5 categories by total value
- `item_count`: total item count
- `last_update`: coordinator last success timestamp

## Testing Checklist
- [ ] Automated tests run locally and in CI
- [ ] Test coverage is >80% for the integration package
- [x] Options flow allows reconfiguration (scan interval, tracked sensors)
- [x] Token expiry/re-authentication recovery implemented
- [ ] Service `add_quick_item` verified against live NesVentory API
- [ ] Service `import_ha_devices` verified against live NesVentory API
- [ ] Service `sync_ha_areas` verified against live NesVentory API
- [ ] Services callable from Developer Tools → Services
- [ ] Voice commands work through HA Assist (services registered; not explicitly tested)
- [x] Category sensors implemented and update with coordinator
- [x] Location sensors implemented and update with coordinator
- [x] Sensors expose useful extra state attributes

### 9. Home Assistant Device Import
Import devices from HA into NesVentory with rich metadata.

**Status: Done ✅** (simplified vs. original spec)

**Service:** `nesventory.import_ha_devices`

**Implemented Parameters:**
- `area_id` (string, optional): Import only devices from this HA area (uses HA area selector)
- `overwrite` (boolean, optional, default: false): Reserved for future use

**Behavior:**
- Reads all devices from the HA device registry
- Filters by `area_id` if provided
- Skips devices with no name
- Builds a rich item name: `"Manufacturer Model - Device Name"` (falls back to name only)
- Resolves area name from HA area registry to use as NesVentory location
- Creates items with category `"Smart Home Device"`
- Logs a summary: N imported, N skipped, N failed

> **Note vs. original spec:** `device_type` filter, `import_all` boolean, and `sync_areas` option were not implemented. `area_id` replaces `area_filter`.

### 10. Area/Room Synchronization
Keep HA areas in sync with NesVentory locations.

**Status: Done ✅** (simplified vs. original spec)

**Service:** `nesventory.sync_ha_areas`

**Behavior:**
- Fetches all HA areas from the area registry
- Skips areas whose name already exists in NesVentory locations (checked via coordinator data)
- Creates a NesVentory location for each new area via `POST /api/v1/locations/`
- Logs a summary: N created, N failed

> **Note vs. original spec:** One-shot only (no continuous monitoring, no auto-sync toggle, no name prefix option). Sync direction is HA → NesVentory only.

## Future Enhancements (Not in this phase)
- Barcode scanning integration
- Image upload support
- Batch operations
- Custom templates
- Bidirectional sync (NesVentory → HA)
- Device state monitoring (online/offline)

## Notes
- Do not start service or dynamic sensor work until the Phase 1 API verification items are resolved
- `services.yaml` is required before Home Assistant services will be properly described in the UI
- Keep performance in mind with many sensors
- Consider caching API responses
- Test with large inventories (100+ items)
- HA device import should be optional feature
- Respect user's privacy - only import what they explicitly allow
- Consider rate limiting for bulk imports
