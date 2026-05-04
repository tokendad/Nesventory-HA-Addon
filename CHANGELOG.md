# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Phase 2 — Advanced Sensors & Services

#### Added
- **Options flow**: reconfigure scan interval, category sensors, and location sensors via HA UI
- **`add_quick_item` service**: create inventory items from automations or voice commands
- **`import_ha_devices` service**: bulk-import HA device registry entries into NesVentory
- **`sync_ha_areas` service**: sync HA areas to NesVentory locations (creates missing locations)
- **Category sensors**: per-category item count sensors (configured via options flow)
- **Location sensors**: per-location item count sensors (configured via options flow)
- **Enhanced attributes** on Total Items: `items_by_status`, `items_by_category` (top 5)
- **Enhanced attributes** on Total Value: `value_by_category` (top 5)
- **Configurable scan interval**: adjustable in options flow (30–3600 s, default 60 s)
- **Auto-reload on options change**: scan interval and sensor list update without HA restart
- Unit test skeleton (`tests/conftest.py`, `tests/test_api_client.py`, `tests/test_coordinator.py`)

### Phase 1 (prior)

#### Added
- `translations/en.json` — required by HA UI translation system (mirrors `strings.json`)
- `services.yaml` — stub definitions for Phase 2 services: `add_quick_item`, `import_ha_devices`, `sync_ha_areas`
- `LICENSE` — MIT license
- `.github/workflows/validate.yml` — GitHub Actions CI: black, isort, pylint, manifest validation

### Changed
- `const.py` — removed redundant `CONF_URL = "url"` (already provided by `homeassistant.const`); added clarifying comment
- `__init__.py` — auth failure in `async_setup_entry` now raises `ConfigEntryAuthFailed` instead of returning `False`, so HA correctly surfaces credential issues to the user
- `coordinator.py` — `_async_update_data` now fetches items, locations, and categories **in parallel** via `asyncio.gather`; location/category failures are handled gracefully (empty list fallback) so a single endpoint outage won't fail the whole update; coordinator data dict now includes `locations` and `categories` keys
- `sensor.py` — `NesVentoryTotalValueSensor._attr_state_class` corrected from `SensorStateClass.TOTAL` to `SensorStateClass.MEASUREMENT` (inventory value is not monotonically increasing)
- `api_client.py` — extracted shared `_get_json()` helper; all GET endpoints (`get_items`, `get_locations`, `get_categories`) now automatically re-authenticate and retry once on HTTP 401, handling token expiry transparently; removed unused `ClientTimeout` import; removed orphaned `aiohttp` import from `config_flow.py`

### Fixed
- `config_flow.py` — removed unused `import aiohttp`

### Security
- No credentials, tokens, or IPs introduced in any file

## [0.1.0] - TBD

### Added
- Initial project structure
- HACS compatibility setup
- Development documentation
- Project planning and phase breakdown

[Unreleased]: https://github.com/tokendad/Nesventory-HA-Addon/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/tokendad/Nesventory-HA-Addon/releases/tag/v0.1.0
