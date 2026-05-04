"""Constants for the NesVentory integration."""

# CONF_URL, CONF_USERNAME, CONF_PASSWORD come from homeassistant.const — do not redefine here.

DOMAIN = "nesventory"

# Defaults
DEFAULT_SCAN_INTERVAL = 60  # seconds
DEFAULT_TIMEOUT = 10  # seconds

# API Endpoints
API_ITEMS_ENDPOINT = "/api/v1/items/"
API_LOCATIONS_ENDPOINT = "/api/v1/locations/"
API_CATEGORIES_ENDPOINT = "/api/v1/categories/"
