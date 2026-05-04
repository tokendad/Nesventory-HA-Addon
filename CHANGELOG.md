# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
