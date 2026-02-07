# NesVentory Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/tokendad/Nesventory-HA-Addon.svg)](https://github.com/tokendad/Nesventory-HA-Addon/releases)

A Home Assistant integration for [NesVentory](https://github.com/tokendad/NesVentory), enabling seamless interaction between your inventory management system and smart home.

## Features

### Current Features
- 🚧 **In Development** - Initial setup and structure

### Planned Features

#### NesVentory → Home Assistant
- 📊 **Dashboard Sensors** - Display total items, total value, and category counts
- 🗣️ **Voice Commands** - Add items using Home Assistant Assist/voice
- 🔔 **Low Stock Alerts** - Trigger automations when inventory runs low
- 📍 **Room Context** - Use presence detection for room-based inventory views

#### Home Assistant → NesVentory (Bidirectional Sync)
- 📱 **Device Import** - Bulk import HA devices with rich metadata (manufacturer, model, serial numbers)
- 🏠 **Area Synchronization** - Auto-sync HA rooms/areas to NesVentory locations
- 🔧 **Smart Home Asset Management** - Track all smart home devices in your inventory
- 📝 **Rich Metadata** - Leverage HA's device information for better tracking

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

### Available Sensors (Planned)

- `sensor.nesventory_total_items` - Total number of items in inventory
- `sensor.nesventory_total_value` - Total value of all items
- `sensor.nesventory_category_*` - Items by category (configurable)
- `sensor.nesventory_location_*` - Items by location (configurable)

### Services (Planned)

- `nesventory.add_quick_item` - Quickly add an item via voice or automation
- `nesventory.import_ha_devices` - Import Home Assistant devices into NesVentory
- `nesventory.sync_ha_areas` - Synchronize HA areas to NesVentory locations

## Development

This integration is under active development. Check the [project development documentation](project_dev/PROJECT_OVERVIEW.md) for detailed planning and roadmap.

### Development Phases

- **Phase 1**: Basic Connection & Sensors
- **Phase 2**: Advanced Features & Bidirectional Sync
- **Phase 3**: Publishing & Distribution

See [project_dev/phases/](project_dev/phases/) for detailed phase documentation.

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

This project is licensed under the same license as the main NesVentory project.

## Acknowledgments

- Thanks to [@philhawthorne](https://github.com/philhawthorne) for suggesting the bidirectional integration feature
- Built for the Home Assistant community
- Powered by [NesVentory](https://github.com/tokendad/NesVentory)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.
