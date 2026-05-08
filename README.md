# NesVentory Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/tokendad/Nesventory-HA-Addon.svg)](https://github.com/tokendad/Nesventory-HA-Addon/releases)
[![CI](https://github.com/tokendad/Nesventory-HA-Addon/actions/workflows/validate.yml/badge.svg)](https://github.com/tokendad/Nesventory-HA-Addon/actions/workflows/validate.yml)

A Home Assistant integration for [NesVentory](https://github.com/tokendad/NesVentory), enabling seamless interaction between your inventory management system and smart home.

## Features

### ✅ Implemented (v0.2.1)

#### NesVentory → Home Assistant
- 📊 **Dashboard Sensors** — Total items, total value, per-category counts, per-location counts
- 🗣️ **Voice Commands** — Add items using `nesventory.add_quick_item` via HA Assist/automations
- 🔔 **Rich Attributes** — Items by status, category breakdown, value by category on every sensor
- ⚙️ **Options Flow** — Reconfigure scan interval and tracked categories/locations without restart

#### Home Assistant → NesVentory (Bidirectional Sync)
- 📱 **Device Import** — Bulk-import HA device registry entries via `nesventory.import_ha_devices`
- 🏠 **Area Synchronization** — Push HA areas to NesVentory locations via `nesventory.sync_ha_areas`

### 🔜 Planned (Phase 3)
- 🔔 **Low Stock Alerts** — Trigger automations when inventory drops below threshold
- 📍 **Room Context** — Presence-based room-scoped inventory views
- 📦 **HACS Default Repository** — Submission to HACS default store

## Requirements

- **Home Assistant** 2024.1.0 or newer
- **NesVentory** backend instance running and accessible
- Valid NesVentory user account

## Installation

### HACS (Recommended - Coming Soon)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add `https://github.com/tokendad/Nesventory-HA-Addon` as an "Integration"
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/tokendad/Nesventory-HA-Addon/releases)
2. Copy the `custom_components/nesventory` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

### Initial Setup

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "NesVentory"
4. Enter your NesVentory details:
   - **URL**: Your NesVentory instance URL (e.g., `http://192.168.1.100:8001`)
   - **Username**: Your NesVentory username
   - **Password**: Your NesVentory password
5. Click **Submit**

### Options (Reconfiguration)

After setup, click **Configure** on the NesVentory integration card to adjust:

| Option | Default | Description |
|---|---|---|
| Scan interval | 60 s | How often to poll NesVentory (30–3600 s) |
| Tracked categories | _(none)_ | Category names to create individual sensors for |
| Tracked locations | _(none)_ | Location names to create individual sensors for |

Changes apply immediately — no HA restart required.

### Available Sensors

| Entity ID | Description | Attributes |
|---|---|---|
| `sensor.nesventory_total_items` | Total item count | `items_by_status`, `items_by_category` (top 5) |
| `sensor.nesventory_total_value` | Total inventory value | `value_by_category` (top 5) |
| `sensor.nesventory_category_<name>` | Items in a category | Configured via options flow |
| `sensor.nesventory_location_<name>` | Items at a location | Configured via options flow |

### Services

#### `nesventory.add_quick_item`

Quickly add an inventory item from an automation or voice command.

```yaml
service: nesventory.add_quick_item
data:
  name: "Philips Hue Bulb"
  quantity: 2
  location: "Office"       # optional
  category: "Smart Lights" # optional
```

#### `nesventory.import_ha_devices`

Bulk-import Home Assistant devices into NesVentory as inventory items.

```yaml
service: nesventory.import_ha_devices
data:
  area_filter: "Living Room" # optional — leave blank to import all devices
```

#### `nesventory.sync_ha_areas`

Push all Home Assistant areas to NesVentory as locations (skips existing ones).

```yaml
service: nesventory.sync_ha_areas
```

## Development

### Development Phases

| Phase | Status | Description |
|---|---|---|
| **Phase 1** | ✅ Complete | Core sensors, config flow, CI, translations |
| **Phase 2** | ✅ Complete | Services, options flow, dynamic sensors, unit tests (111 tests) |
| **Phase 2b** | 🔜 Planned | Network discovery services |
| **Phase 3** | 🔜 Planned | HACS default repo submission |

See [project_dev/phases/](project_dev/phases/) for detailed documentation on each phase.

### Running Tests

```bash
pip install pytest pytest-asyncio aiohttp voluptuous
pytest tests/ -v
```

### Code Quality

```bash
pip install black isort pylint
black custom_components/nesventory/
isort custom_components/nesventory/
pylint custom_components/nesventory/
```

### Debug Logging

Add to your HA `configuration.yaml`, then restart:

```yaml
logger:
  default: info
  logs:
    custom_components.nesventory: debug
```

## Contributing

Contributions are welcome! Please:

1. Check existing [issues](https://github.com/tokendad/Nesventory-HA-Addon/issues)
2. Fork the repository
3. Create a feature branch
4. Submit a pull request

## Support

- **Issues**: [GitHub Issues](https://github.com/tokendad/Nesventory-HA-Addon/issues)
- **Main Project**: [NesVentory](https://github.com/tokendad/NesVentory)

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Thanks to [@philhawthorne](https://github.com/philhawthorne) for suggesting the bidirectional integration feature
- Built for the Home Assistant community
- Powered by [NesVentory](https://github.com/tokendad/NesVentory)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.
