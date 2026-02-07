# Phase 2: Advanced Sensors & Services

**Goal:** Add actionable interactions and category-specific sensors.

## Status: Not Started

## Dependencies
- Phase 1 must be completed and tested

## Objectives
- [ ] Implement custom service for adding items
- [ ] Add category-specific sensors
- [ ] Enable voice assistant integration
- [ ] Implement bidirectional HA ↔ NesVentory data sync
- [ ] Import HA devices and rooms into NesVentory

## Tasks

### 1. Quick Add Service
Create a service to quickly add items to NesVentory.

**Service:** `nesventory.add_quick_item`

**Parameters:**
- `name` (string, required): Item name
- `location` (string, optional): Location ID or name (default: "Inbox")
- `status` (string, optional): Item status (default: "Review Needed")

**Requirements:**
- Call NesVentory API to create item
- Handle API errors gracefully
- Return success/failure status
- Support voice assistant integration

**Deliverables:**
- Update `custom_components/nesventory/__init__.py` with service registration
- Create/update `custom_components/nesventory/services.yaml`
- Add service handler logic

**Use Cases:**
- Voice command: *"Hey Google, ask NesVentory to add AA Batteries"*
- Automation: Auto-add items when scanning barcodes
- Dashboard button: Quick add from HA UI

### 2. Category Sensors
Allow users to track specific categories as individual sensors.

**Configurable Sensors:**
- `sensor.nesventory_category_<name>`: Count items in specific category
  - Example: `sensor.nesventory_category_pantry`
  - Example: `sensor.nesventory_category_freezer`

**Requirements:**
- User configures categories through options flow
- Each category gets its own sensor entity
- Sensors update with Phase 1 sensors
- Show category details in attributes

**Deliverables:**
- Update `custom_components/nesventory/config_flow.py` with options flow
- Update `custom_components/nesventory/sensor.py` with dynamic sensors
- Update strings.json with new UI labels

### 3. Location-Based Sensors
Similar to categories, but for locations/rooms.

**Sensors:**
- `sensor.nesventory_location_<name>`: Count items in specific location
  - Example: `sensor.nesventory_location_garage`
  - Example: `sensor.nesventory_location_kitchen`

**Requirements:**
- User configures locations through options flow
- Fetch available locations from NesVentory API
- Create sensors dynamically

### 4. Enhanced Attributes
Add richer data to existing sensors.

**For Total Items Sensor:**
- Last update timestamp
- Items by status breakdown
- Items by category breakdown (top 5)

**For Total Value Sensor:**
- Currency unit
- Value by category (top 5)
- Last update timestamp

## Testing Checklist
- [ ] Service can be called from Developer Tools
- [ ] Service creates items in NesVentory correctly
- [ ] Voice commands work through HA Assist
- [ ] Category sensors appear and update
- [ ] Location sensors appear and update
- [ ] Options flow allows reconfiguration
- [ ] Sensors show useful attributes

### 5. Home Assistant Device Import
Import devices from HA into NesVentory with rich metadata.

**Service:** `nesventory.import_ha_devices`

**Parameters:**
- `area_filter` (string, optional): Import only devices from specific area
- `device_type` (string, optional): Filter by device type (lights, switches, etc.)
- `import_all` (boolean, default: false): Import all HA devices
- `sync_areas` (boolean, default: true): Create NesVentory locations from HA areas

**Requirements:**
- Access HA device registry via API
- Fetch device attributes:
  - Name
  - Manufacturer
  - Model
  - Serial number (if available)
  - MAC address (if available)
  - Area/Room assignment
  - Device type/category
- Create items in NesVentory with HA metadata
- Map HA areas to NesVentory locations
- Handle devices without area assignments
- Store HA entity IDs for future sync

**Deliverables:**
- Device import service handler
- HA device registry API integration
- Area/location mapping logic
- Documentation for import feature

**Use Cases:**
- Initial bulk import of smart home devices
- Periodic sync to catch new HA devices
- Selective import by room (e.g., "Import all kitchen devices")
- Asset management for smart home equipment

### 6. Area/Room Synchronization
Keep HA areas in sync with NesVentory locations.

**Service:** `nesventory.sync_ha_areas`

**Requirements:**
- Fetch all HA areas/rooms
- Create corresponding locations in NesVentory
- Option for one-time sync vs continuous monitoring
- Handle area renames in HA
- Store mapping between HA area IDs and NesVentory location IDs

**Configuration Options:**
- Enable/disable auto-sync
- Sync direction (HA → NesVentory only for now)
- Prefix for imported locations (e.g., "HA: Kitchen")

## Future Enhancements (Not in this phase)
- Barcode scanning integration
- Image upload support
- Batch operations
- Custom templates
- Bidirectional sync (NesVentory → HA)
- Device state monitoring (online/offline)

## Notes
- Keep performance in mind with many sensors
- Consider caching API responses
- Test with large inventories (100+ items)
- HA device import should be optional feature
- Respect user's privacy - only import what they explicitly allow
- Consider rate limiting for bulk imports
