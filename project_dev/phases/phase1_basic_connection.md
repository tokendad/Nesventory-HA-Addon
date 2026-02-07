# Phase 1: Basic Connection & Sensor

**Goal:** Authenticate with NesVentory and show a "Total Items" sensor.

## Status: Not Started

## Objectives
- [ ] Create API client for NesVentory communication
- [ ] Implement configuration flow for user setup
- [ ] Create basic sensor entities

## Tasks

### 1. API Client (`api_client.py`)
Create a Python class to communicate with NesVentory's FastAPI backend.

**Requirements:**
- Endpoint: `/api/v1/items/` (GET) to count items
- Auth: Bearer Token authentication
- Error handling for connection issues
- Timeout handling

**Deliverables:**
- `custom_components/nesventory/api_client.py`

### 2. Config Flow (`config_flow.py`)
Implement UI-based configuration.

**Requirements:**
- Prompt for NesVentory URL (e.g., `http://192.168.1.100:8001`)
- Prompt for Username/Password
- Validate connection during setup
- Store credentials securely
- Handle authentication errors

**Deliverables:**
- `custom_components/nesventory/config_flow.py`
- `custom_components/nesventory/strings.json` (UI labels)

### 3. Basic Sensors (`sensor.py`)
Create initial sensor entities.

**Sensors to Implement:**
- `sensor.nesventory_total_items`: State = Count of all items
- `sensor.nesventory_total_value`: State = Sum of item values

**Requirements:**
- Poll NesVentory API at reasonable interval (configurable, default 60s)
- Handle API unavailability gracefully
- Update state properly
- Include useful attributes (last_update, etc.)

**Deliverables:**
- `custom_components/nesventory/sensor.py`

### 4. Core Files
Create required integration files.

**Files Needed:**
- `custom_components/nesventory/__init__.py` - Component setup/entry point
- `custom_components/nesventory/manifest.json` - HA metadata
- `custom_components/nesventory/const.py` - Constants (domain, defaults, etc.)
- `hacs.json` - HACS metadata (root level)
- `README.md` - Basic usage documentation

## Testing Checklist
- [ ] Can add integration through HA UI
- [ ] Connection validation works (both success and failure)
- [ ] Sensors appear in HA
- [ ] Sensors update correctly
- [ ] Error states handled gracefully
- [ ] Integration can be removed cleanly

## Dependencies
None (First phase)

## Blockers
None currently

## Notes
- Start with minimal viable implementation
- Focus on reliability over features
- Ensure proper error handling from the start
