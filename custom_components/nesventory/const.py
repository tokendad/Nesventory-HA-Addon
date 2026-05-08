"""Constants for the NesVentory integration."""

# CONF_URL, CONF_USERNAME, CONF_PASSWORD come from homeassistant.const — do not redefine here.

DOMAIN = "nesventory"

# Defaults
DEFAULT_SCAN_INTERVAL = 60  # seconds
DEFAULT_TIMEOUT = 10  # seconds

# API Endpoints
API_AUTH_ENDPOINT = "/api/token"
API_ITEMS_ENDPOINT = "/api/items/"
API_LOCATIONS_ENDPOINT = "/api/locations/"
API_TAGS_ENDPOINT = "/api/tags/"

# API write endpoints (same paths as read, just POST)
API_ITEMS_CREATE_ENDPOINT = "/api/items/"
API_LOCATIONS_CREATE_ENDPOINT = "/api/locations/"

# Config entry option keys
CONF_SCAN_INTERVAL = "scan_interval"
CONF_TRACKED_CATEGORIES = "tracked_categories"
CONF_TRACKED_LOCATIONS = "tracked_locations"

# Service names
SERVICE_ADD_QUICK_ITEM = "add_quick_item"
SERVICE_IMPORT_HA_DEVICES = "import_ha_devices"
SERVICE_SYNC_HA_AREAS = "sync_ha_areas"
