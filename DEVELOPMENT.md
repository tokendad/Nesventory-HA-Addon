# Development Guide

This guide helps you set up a local development environment for the NesVentory Home Assistant integration.

## Prerequisites

- Home Assistant instance (for testing)
- NesVentory backend running and accessible
- Python 3.11+ (for local linting/testing)

## Local Testing Setup

### 1. Configure Local Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your local details (this file is git-ignored):

```env
# Your local Home Assistant instance
HA_URL=http://192.168.1.103:8123
HA_TOKEN=your_long_lived_access_token_here

# Your local NesVentory instance
NESVENTORY_URL=http://192.168.1.XXX:8001
NESVENTORY_USERNAME=your_username
NESVENTORY_PASSWORD=your_password
```

**IMPORTANT**: Never commit `.env` or any files containing your local IP addresses, tokens, or credentials.

### 2. Install in Home Assistant

#### Method 1: Symlink (Recommended for Development)

Create a symlink from your HA config directory to this repository:

```bash
# Navigate to your Home Assistant config directory
cd /data/Hassio

# Create custom_components directory if it doesn't exist
mkdir -p custom_components

# Symlink the integration
ln -s "/data/Projects/Nesventory /HA-Nesventory/custom_components/nesventory" custom_components/nesventory
```

#### Method 2: Manual Copy

Copy the integration to your HA custom_components:

```bash
cp -r custom_components/nesventory /data/Hassio/custom_components/
```

### 3. Restart Home Assistant

After installing the integration:

1. Restart Home Assistant
2. Check the logs for any errors: `Configuration` → `Logs`

### 4. Add Integration

1. Go to `Settings` → `Devices & Services`
2. Click `Add Integration`
3. Search for "NesVentory"
4. Enter your NesVentory instance details
5. Click `Submit`

## Development Workflow

### Making Changes

1. Edit files in `custom_components/nesventory/`
2. Restart Home Assistant (or reload the integration if supported)
3. Test your changes
4. Check logs for errors

### Checking Logs

View Home Assistant logs for debugging:

```bash
# From HA config directory
tail -f /data/Hassio/home-assistant.log | grep nesventory
```

Or use the UI: `Settings` → `System` → `Logs`

### Code Quality

Before committing, ensure code quality:

```bash
# Install development dependencies (optional)
pip install black isort pylint

# Format code
black custom_components/nesventory/
isort custom_components/nesventory/

# Lint code
pylint custom_components/nesventory/
```

## Testing

### Manual Testing Checklist

- [ ] Integration can be added through UI
- [ ] Connection validation works (success case)
- [ ] Connection validation fails appropriately (wrong credentials)
- [ ] Sensors appear after setup
- [ ] Sensors update with correct values
- [ ] Integration can be removed cleanly
- [ ] No errors in Home Assistant logs

### API Testing

Test API client independently:

```python
import asyncio
import aiohttp
from custom_components.nesventory.api_client import NesVentoryApiClient

async def test_client():
    async with aiohttp.ClientSession() as session:
        client = NesVentoryApiClient(
            base_url="http://YOUR_NESVENTORY_URL",
            username="your_username",
            password="your_password",
            session=session
        )

        # Test authentication
        auth_ok = await client.authenticate()
        print(f"Auth: {auth_ok}")

        # Test connection
        conn_ok = await client.test_connection()
        print(f"Connection: {conn_ok}")

        # Test data fetching
        count = await client.get_total_items_count()
        print(f"Total items: {count}")

        value = await client.get_total_value()
        print(f"Total value: ${value}")

asyncio.run(test_client())
```

## Debugging

### Common Issues

**Integration doesn't appear in UI**
- Restart Home Assistant
- Check `custom_components/nesventory/manifest.json` is valid
- Check logs for syntax errors

**Authentication fails**
- Verify NesVentory URL is correct
- Verify username/password are correct
- Check NesVentory is accessible from HA instance

**Sensors don't update**
- Check coordinator logs
- Verify API endpoints are correct
- Check NesVentory API response format

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.nesventory: debug
```

Restart Home Assistant to apply.

## Git Ignored Files

The following are git-ignored for security:

- `.env` - Your local environment variables
- `test_config.yaml` - Any local test configurations
- `local_testing/` - Local testing directory

**Never commit**:
- IP addresses (unless example)
- Passwords or tokens
- Personal configuration files

## Next Steps

After Phase 1 is complete and tested:

1. Update CHANGELOG.md
2. Tag a development release
3. Begin Phase 2 development

## Support

- Check [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- Review [project_dev/](project_dev/) for planning documents
- Open an issue for bugs or questions
