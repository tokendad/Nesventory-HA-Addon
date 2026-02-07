# Testing Phase 1

Quick guide for testing the Phase 1 implementation on your local Home Assistant.

## Prerequisites

- **Home Assistant**: Running at `192.168.1.103:8123`
- **NesVentory Backend**: Running and accessible
- Valid NesVentory credentials

## Installation Steps

### 1. Copy Integration to Home Assistant

From your HA config directory (typically `/config`):

```bash
# Create custom_components if it doesn't exist
mkdir -p custom_components

# Copy the integration
cp -r /data/HA-Nesventory/custom_components/nesventory custom_components/
```

Or use a symlink for easier development:

```bash
ln -s /data/HA-Nesventory/custom_components/nesventory custom_components/nesventory
```

### 2. Restart Home Assistant

Restart HA to load the new integration:
- `Settings` → `System` → `Restart`

Or via CLI:
```bash
ha core restart
```

### 3. Add the Integration

1. Go to `Settings` → `Devices & Services`
2. Click `+ Add Integration` (bottom right)
3. Search for "NesVentory"
4. Fill in the configuration:
   - **URL**: Your NesVentory URL (e.g., `http://192.168.1.X:8001`)
   - **Username**: Your NesVentory username
   - **Password**: Your NesVentory password
5. Click `Submit`

### 4. Verify Sensors

After successful setup, check for these sensors:

- `sensor.nesventory_total_items` - Should show count of items
- `sensor.nesventory_total_value` - Should show total $ value

View in:
- `Settings` → `Devices & Services` → `NesVentory` → Click device
- Or: `Developer Tools` → `States` → Search "nesventory"

## Testing Checklist

### Configuration Flow
- [ ] Integration appears in "Add Integration" search
- [ ] Configuration form displays correctly
- [ ] Validation works with correct credentials
- [ ] Error message shows for wrong credentials
- [ ] Error message shows for unreachable URL
- [ ] Can't add duplicate configurations

### Sensors
- [ ] Both sensors appear after setup
- [ ] `total_items` shows correct count
- [ ] `total_value` shows correct dollar amount
- [ ] Sensors update (wait 60s or restart HA)
- [ ] Attributes show last_update time
- [ ] Device info shows in UI

### Integration Management
- [ ] Can reload integration (Settings → Devices & Services → NesVentory → ⋮ → Reload)
- [ ] Can remove integration cleanly
- [ ] Re-adding works after removal

### Error Handling
- [ ] Stop NesVentory backend → sensors show "unavailable"
- [ ] Start NesVentory → sensors recover
- [ ] No errors in HA logs during normal operation

## Viewing Logs

### Via UI
`Settings` → `System` → `Logs`

Filter for: `nesventory`

### Via CLI
```bash
# Real-time log watching
tail -f /config/home-assistant.log | grep nesventory

# Or just grep recent logs
grep nesventory /config/home-assistant.log
```

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.nesventory: debug
```

Then restart HA.

## Debugging Common Issues

### Integration doesn't appear
**Solution**:
- Check manifest.json is valid JSON
- Restart HA completely
- Check logs for Python syntax errors

### "Cannot connect" error
**Solution**:
- Verify NesVentory URL is accessible from HA
- Try: `curl http://YOUR_NESVENTORY_URL/api/v1/items/`
- Check NesVentory is running
- Verify no firewall blocking

### "Invalid auth" error
**Solution**:
- Verify username/password are correct
- Check NesVentory authentication endpoint
- Review NesVentory logs for auth attempts

### Sensors show "Unknown"
**Solution**:
- Check coordinator is fetching data
- Enable debug logging
- Verify API endpoints match NesVentory
- Check item data structure in response

## Next Steps

After Phase 1 testing is successful:

1. Document any issues found
2. Verify API endpoint compatibility with actual NesVentory
3. Adjust field names if needed (value vs price, etc.)
4. Begin Phase 2 development

## Notes

- Default update interval: 60 seconds
- Timeout for API calls: 10 seconds
- All credentials stored securely in HA config entries
- No data cached beyond coordinator refresh

## Support

If you encounter issues:

1. Check logs for errors
2. Verify NesVentory API compatibility
3. Review DEVELOPMENT.md for detailed debugging
4. Open issue on GitHub with logs
