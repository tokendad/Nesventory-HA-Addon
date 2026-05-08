# Phase 2b: Network Discovery Service

**Goal:** Add a passive network discovery service that finds IoT/network devices
not yet registered in HA's device registry and imports them as NesVentory inventory
items.

## Status: Planned — not started
## Last Updated: 2026-05-06

## Dependencies
- Phase 1 complete ✅
- Phase 2 complete ✅

---

## Problem & Approach

The existing `import_ha_devices` service imports devices HA already knows about.
This feature adds a **passive network discovery** service that reads from HA's
built-in mDNS/Zeroconf and SSDP caches to find devices **not yet registered in
HA's device registry**, then imports those unknowns as NesVentory inventory items.

No active scanning (no nmap, no ping sweeps). Zigbee/Z-Wave are excluded (already
covered by `import_ha_devices`). Discovered devices go to NesVentory only.

---

## New Service: `nesventory.discover_network_devices`

### Parameters

| Field | Type | Required | Description |
|---|---|---|---|
| `category` | string | no | NesVentory category to assign (default: `"Network Discovery"`) |
| `dry_run` | boolean | no | Log found devices without creating items (default: `false`) |

### Behavior

1. Read HA's SSDP scanner cache → UPnP devices (richest metadata: manufacturer, model, serial, friendly name)
2. Read HA's Zeroconf/mDNS cache → hostname, IP, service type (→ category hints)
3. De-duplicate across both sources by IP address
4. Cross-reference against HA device registry → skip anything already registered
5. Create one NesVentory item per unknown device (name = friendly name or hostname)
6. Log a summary: N found, N already-known (skipped), N created, N failed

### Category Mapping

| mDNS / SSDP service type | NesVentory category |
|---|---|
| `_googlecast._tcp` | Streaming Device |
| `_hap._tcp` | HomeKit Device |
| `_http._tcp` | Network Device |
| UPnP `urn:schemas-upnp-org:device:MediaRenderer` | Media Device |
| UPnP `urn:schemas-upnp-org:device:WANDevice` | Network Device |
| *(unknown)* | fallback to caller's `category` param |

---

## Files to Change

| File | Change |
|---|---|
| `custom_components/nesventory/const.py` | Add `SERVICE_DISCOVER_NETWORK = "discover_network_devices"` |
| `custom_components/nesventory/__init__.py` | Add `DISCOVER_NETWORK_SCHEMA`, `handle_discover_network_devices()`, register/unregister service |
| `custom_components/nesventory/services.yaml` | Add `discover_network_devices` block with `category` + `dry_run` fields |
| `tests/test_discover_service.py` | New: happy path, dry_run, all-devices-known, SSDP unavailable |
| `CHANGELOG.md` | Add to `[Unreleased]` |
| `README.md` | Add service to services table + YAML example |

> `strings.json` / `translations/en.json` — no changes needed; service descriptions
> live in `services.yaml` only and are not part of the config-flow UI.

---

## Implementation Tasks

1. Add `SERVICE_DISCOVER_NETWORK` constant to `const.py`
2. Implement `handle_discover_network_devices` in `__init__.py`:
   - Query `hass.components.ssdp` for all discovered UPnP root devices
   - Query `hass.components.zeroconf` for mDNS service records
   - De-duplicate by IP; cross-reference HA device registry; filter unknowns
   - Map service types to categories; call `client.create_item()` (or log if `dry_run`)
3. Wire schema + handler into `_register_services()` and `async_unload_entry()`
4. Add `discover_network_devices` block to `services.yaml`
5. Write `tests/test_discover_service.py` (happy path, dry_run, all-known, SSDP missing)
6. Update `README.md` + `CHANGELOG.md`

**Task dependencies:** 1 → 2 → 3; then 4, 5, 6 in parallel after 3.

---

## Key Technical Notes

- **SSDP access**: `homeassistant.components.ssdp.async_get_discovery_info_by_st(hass, st)` —
  query `"upnp:rootdevice"` and `"ssdp:all"` for broadest coverage.
  Available fields: `ATTR_UPNP_MANUFACTURER`, `ATTR_UPNP_MODEL_NAME`, `ATTR_UPNP_SERIAL`,
  `ATTR_UPNP_FRIENDLY_NAME`, `ATTR_SSDP_ST`, `ATTR_SSDP_LOCATION`.
- **Zeroconf access**: `homeassistant.components.zeroconf.async_get_async_instance(hass)` returns
  the aiozeroconf instance; iterate its cache for service records.
- **Guard**: wrap both sources in `try/except` — SSDP and Zeroconf may not be loaded if the user
  disabled network discovery in HA. Gracefully fall back to empty list with a warning log.
- **HA device registry cross-reference**: HA devices store connections as
  `(dr.CONNECTION_NETWORK_MAC, mac)` and `(dr.CONNECTION_UPNP, udn)`.
  Build a set of known MACs and UDNs before iterating discoveries to skip known devices.
- **No new pip dependencies** — SSDP and Zeroconf are HA built-in components.

---

## Out of Scope

- Active nmap-style scanning
- Zigbee / Z-Wave discovery (covered by `import_ha_devices`)
- Registering discovered devices into HA's device registry
- Continuous / scheduled discovery (one-shot service call only)

## Testing Checklist

- [ ] Service appears in Developer Tools → Services
- [ ] `dry_run: true` logs devices without creating NesVentory items
- [ ] Devices already in HA registry are skipped
- [ ] Unknown devices get correct category from service-type mapping
- [ ] SSDP/Zeroconf components unavailable → graceful empty result, no crash
- [ ] Summary log line appears: "N found, N skipped, N created, N failed"
