# NesVentory HA Integration – Copilot Instructions

## What This Project Is

A Home Assistant (HA) custom integration that connects HA to a [NesVentory](https://github.com/tokendad/NesVentory) inventory management backend. Distributed via HACS. Currently in Phase 1 (basic sensors). Target HA version: 2024.1.0+.

## Code Quality

```bash
# Install dev tools (one-time)
pip install black isort pylint

# Format
black custom_components/nesventory/
isort custom_components/nesventory/

# Lint
pylint custom_components/nesventory/
```

There is no automated test suite. Testing is manual against a live HA instance. See `TESTING.md` for the checklist and `DEVELOPMENT.md` for the full workflow.

## Architecture

All integration code lives in `custom_components/nesventory/`. The data flow is:

```
config_flow.py  ──(validates credentials)──▶  api_client.py
__init__.py     ──(sets up per entry)──────▶  api_client.py
                                           ▶  coordinator.py  ──▶  sensor.py
```

- **`api_client.py`** (`NesVentoryApiClient`): All HTTP calls to NesVentory. Handles bearer token auth. Token stored as `self._token`.
- **`coordinator.py`** (`NesVentoryDataUpdateCoordinator`): HA `DataUpdateCoordinator` subclass that polls every 60 s. Stores `{"items": [...], "total_count": int, "total_value": float}`.
- **`sensor.py`**: Sensor entities extend `CoordinatorEntity`. Read state from `self.coordinator.data`.
- **`config_flow.py`**: UI-based setup. Raises `CannotConnect` / `InvalidAuth` sentinel exceptions that map to `strings.json` error keys. Deduplication uses `CONF_URL` as the unique ID.
- **`__init__.py`**: Entry point. Stores coordinator at `hass.data[DOMAIN][entry.entry_id]`. Only platform is `Platform.SENSOR`.

## Key Conventions

**Every module uses:**
```python
from __future__ import annotations
import logging
_LOGGER = logging.getLogger(__name__)
```

**All API calls use `asyncio.timeout(DEFAULT_TIMEOUT)` (not `async_timeout`):**
```python
async with asyncio.timeout(DEFAULT_TIMEOUT):
    async with self._session.get(url, headers=self._get_headers()) as response:
        ...
```

**Sensor unique IDs follow the pattern:** `{entry.entry_id}_{sensor_name}` (e.g. `abc123_total_items`).

**Device info is passed as a plain `dict`** (not `DeviceInfo` dataclass) with keys `identifiers`, `name`, `manufacturer`, `model`, `configuration_url`.

**Adding a new sensor:** Create a `CoordinatorEntity + SensorEntity` subclass in `sensor.py`, add it to the `entities` list in `async_setup_entry`, and ensure the coordinator's `_async_update_data` returns the data it needs.

**Adding a new API endpoint:** Add the path constant to `const.py`, add the method to `NesVentoryApiClient` following the existing pattern (check `self._token`, wrap in `asyncio.timeout`, catch `asyncio.TimeoutError` and `ClientError`).

## NesVentory API Notes

- Auth: `POST /api/v1/auth/login` → `{"access_token": "..."}` (⚠️ endpoint marked TODO – verify against actual NesVentory)
- Items: `GET /api/v1/items/`
- Locations: `GET /api/v1/locations/`
- Categories: `GET /api/v1/categories/`
- Item value field is ambiguous: code falls back `item.get("value", 0) or item.get("price", 0)` – confirm against actual API.
- All authenticated requests use `Authorization: Bearer <token>` header.

## Security

- Never commit `.env`, IP addresses, tokens, or passwords.
- Credentials are stored only in HA config entries (`entry.data`), not in code or constants.
- `hass.helpers.aiohttp_client.async_get_clientsession(hass)` must be used for the aiohttp session (not a manually created one).

## Debug Logging

Add to HA's `configuration.yaml` then restart:
```yaml
logger:
  default: info
  logs:
    custom_components.nesventory: debug
```

Watch logs: `tail -f /config/home-assistant.log | grep nesventory`

## Development Setup

```bash
cp .env.example .env   # fill in HA_TOKEN, NESVENTORY_URL/USERNAME/PASSWORD
                       # HA_URL is pre-filled: http://192.168.1.103:8123

# Symlink into HA config (recommended over copying):
ln -s "/data/Projects/Nesventory /HA-Nesventory/custom_components/nesventory" \
      /data/Hassio/custom_components/nesventory
```

**Local environment:**
- HA config root: `/data/Hassio/`
- HA UI: `http://192.168.1.103:8123`
- Dev HA account: username `Nesventory` (admin) — keep password in `.env`, never commit it
- Logs: `tail -f /data/Hassio/home-assistant.log | grep nesventory`

After changes: reload the integration from **Settings → Devices & Services → NesVentory → ⋮ → Reload** (or full HA restart for structural changes).

## Planned Work (not yet implemented)

- `services.yaml` and HA services (`nesventory.add_quick_item`, `nesventory.import_ha_devices`, `nesventory.sync_ha_areas`)
- Category and location sensors
- Phase 2: bidirectional sync (HA devices → NesVentory, HA areas → NesVentory locations)
- Phase 3: HACS default repository submission
