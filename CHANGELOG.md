# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- API client for NesVentory communication (`api_client.py`)
- Configuration flow for UI-based setup (`config_flow.py`)
- Data update coordinator for efficient polling (`coordinator.py`)
- Total items sensor (`sensor.nesventory_total_items`)
- Total value sensor (`sensor.nesventory_total_value`)
- Development environment setup with `.env.example`
- Comprehensive development guide (`DEVELOPMENT.md`)

### Security
- Added `.env` and local testing files to `.gitignore`
- Credentials never stored in code, only in Home Assistant config entries

### Planned (Future Phases)
- Quick add item service
- Category-specific sensors
- Location-based sensors
- HA device import functionality
- Area/room synchronization

## [0.1.0] - TBD

### Added
- Initial project structure
- HACS compatibility setup
- Development documentation
- Project planning and phase breakdown

[Unreleased]: https://github.com/tokendad/Nesventory-HA-Addon/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/tokendad/Nesventory-HA-Addon/releases/tag/v0.1.0
