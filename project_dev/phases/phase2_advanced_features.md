# Phase 2: Advanced Sensors & Services

**Goal:** Add actionable interactions, richer sensors, and bidirectional sync features after the Phase 1 API details are verified.

## Status: Not Started — awaiting Phase 1 follow-up items
## Last Updated: 2026-05-04

## Dependencies
- Phase 1 implementation is complete
- Resolve the remaining Phase 1 follow-up items before advanced feature work:
  - Verify the real NesVentory auth endpoint (currently assumed to be `/api/v1/auth/login`)
  - Confirm the correct item value field (`value` vs `price`)

## Objectives
- [ ] Resolve Phase 1 API/schema follow-up items
- [ ] Add automated unit tests with >80% coverage
- [ ] Add an options flow for reconfiguration
- [ ] Implement token refresh / reconnection handling
- [ ] Implement custom services for adding and syncing items
- [ ] Add category-specific sensors
- [ ] Add location-specific sensors
- [ ] Enable voice assistant integration
- [ ] Import HA devices and rooms into NesVentory

## Tasks

### 1. Resolve Phase 1 Follow-up Items
Close the API compatibility gaps before expanding the integration surface area.

**Requirements:**
- Verify the live NesVentory authentication endpoint and response schema
- Confirm the item value field used for total inventory value calculations
- Update the API client/coordinator assumptions after verification
- Re-run manual validation after any API/schema fixes

### 2. Unit Tests
Set up the automated test suite that is currently missing.

**Requirements:**
- Use `pytest` and `pytest-homeassistant-custom-component`
- Add tests for `config_flow.py`
- Add tests for `coordinator.py`
- Add tests for `sensor.py`
- Add tests for `api_client.py`
- Target >80% coverage for the integration package

**Deliverables:**
- Test configuration for the repository
- Initial automated test suite covering Phase 1 behavior
- Coverage reporting in local/CI workflows

### 3. Options Flow
Allow users to reconfigure the integration after initial setup.

**Requirements:**
- Let users update URL and credentials without deleting/re-adding the config entry
- Support future category/location sensor configuration through the same options flow
- Update `strings.json` with options flow labels and errors
- Preserve HA best practices for config entry updates

**Deliverables:**
- Update `custom_components/nesventory/config_flow.py` with options flow support
- Update `custom_components/nesventory/strings.json`

### 4. Token Refresh / Reconnection
Improve reliability when tokens expire or the backend restarts.

**Requirements:**
- Detect authentication failures during regular API calls
- Re-authenticate automatically when a token expires or becomes invalid
- Retry the failed request after a successful re-authentication
- Ensure coordinator refreshes recover without forcing the user to reload the integration

### 5. Quick Add Service
Create a service to quickly add items to NesVentory.

**Service:** `nesventory.add_quick_item`

**Parameters:**
- `name` (string, required): Item name
- `location` (string, optional): Location ID or name (default: "Inbox")
- `status` (string, optional): Item status (default: "Review Needed")

**Requirements:**
- Create `custom_components/nesventory/services.yaml` before service registration so Home Assistant exposes the service correctly
- Call the NesVentory API to create an item
- Likely use `POST /api/v1/items/` for item creation (**needs verification against the real API**)
- Handle API errors gracefully
- Return success/failure status
- Support voice assistant integration

**Deliverables:**
- Update `custom_components/nesventory/__init__.py` with service registration
- Create `custom_components/nesventory/services.yaml`
- Add service handler logic

**Use Cases:**
- Voice command: *"Hey Google, ask NesVentory to add AA Batteries"*
- Automation: Auto-add items when scanning barcodes
- Dashboard button: Quick add from HA UI

### 6. Category Sensors
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
- Update `strings.json` with new UI labels

### 7. Location-Based Sensors
Similar to categories, but for locations/rooms.

**Sensors:**
- `sensor.nesventory_location_<name>`: Count items in specific location
  - Example: `sensor.nesventory_location_garage`
  - Example: `sensor.nesventory_location_kitchen`

**Requirements:**
- User configures locations through options flow
- Fetch available locations from NesVentory API
- Create sensors dynamically

### 8. Enhanced Attributes
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
- [ ] Automated tests run locally and in CI
- [ ] Test coverage is >80% for the integration package
- [ ] Options flow allows reconfiguration
- [ ] Token expiry/re-authentication recovery works
- [ ] Service can be called from Developer Tools
- [ ] Service creates items in NesVentory correctly
- [ ] Voice commands work through HA Assist
- [ ] Category sensors appear and update
- [ ] Location sensors appear and update
- [ ] Sensors show useful attributes

### 9. Home Assistant Device Import
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

### 10. Area/Room Synchronization
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
- Do not start service or dynamic sensor work until the Phase 1 API verification items are resolved
- `services.yaml` is required before Home Assistant services will be properly described in the UI
- Keep performance in mind with many sensors
- Consider caching API responses
- Test with large inventories (100+ items)
- HA device import should be optional feature
- Respect user's privacy - only import what they explicitly allow
- Consider rate limiting for bulk imports
