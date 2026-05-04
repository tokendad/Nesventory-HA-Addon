"""API client for NesVentory."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
from aiohttp import ClientError

from .const import (
    API_CATEGORIES_ENDPOINT,
    API_ITEMS_ENDPOINT,
    API_LOCATIONS_ENDPOINT,
    DEFAULT_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class NesVentoryApiClient:
    """API client for communicating with NesVentory."""

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the API client.

        Args:
            base_url: Base URL of NesVentory instance (e.g., http://192.168.1.100:8001)
            username: NesVentory username
            password: NesVentory password
            session: aiohttp ClientSession

        """
        self._base_url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._session = session
        self._token: str | None = None

    async def authenticate(self) -> bool:
        """Authenticate with NesVentory and obtain bearer token.

        Returns:
            True if authentication successful, False otherwise

        """
        try:
            async with asyncio.timeout(DEFAULT_TIMEOUT):
                url = f"{self._base_url}/api/v1/auth/login"
                data = {
                    "username": self._username,
                    "password": self._password,
                }

                async with self._session.post(url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        self._token = result.get("access_token")
                        _LOGGER.debug("Authentication successful")
                        return True

                    _LOGGER.error(
                        "Authentication failed with status %s", response.status
                    )
                    return False

        except asyncio.TimeoutError:
            _LOGGER.error("Timeout during authentication")
            return False
        except ClientError as err:
            _LOGGER.error("Client error during authentication: %s", err)
            return False
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOGGER.exception("Unexpected error during authentication: %s", err)
            return False

    async def test_connection(self) -> bool:
        """Test connection to NesVentory.

        Returns:
            True if connection successful, False otherwise

        """
        try:
            if not self._token:
                if not await self.authenticate():
                    return False

            async with asyncio.timeout(DEFAULT_TIMEOUT):
                url = f"{self._base_url}{API_ITEMS_ENDPOINT}"

                async with self._session.get(
                    url, headers=self._get_headers()
                ) as response:
                    if response.status == 200:
                        _LOGGER.debug("Connection test successful")
                        return True

                    _LOGGER.error(
                        "Connection test failed with status %s", response.status
                    )
                    return False

        except asyncio.TimeoutError:
            _LOGGER.error("Timeout during connection test")
            return False
        except ClientError as err:
            _LOGGER.error("Client error during connection test: %s", err)
            return False
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOGGER.exception("Unexpected error during connection test: %s", err)
            return False

    async def _get_json(self, url: str, *, _retry: bool = True) -> Any:
        """Perform an authenticated GET request, re-authenticating once on 401.

        Args:
            url: Full URL to request.
            _retry: Internal flag — set to False on the retry to prevent recursion.

        Returns:
            Parsed JSON response body.

        Raises:
            aiohttp.ClientResponseError: On non-2xx status (after retry).
            asyncio.TimeoutError: On timeout.
            ClientError: On other network errors.

        """
        if not self._token:
            await self.authenticate()

        async with asyncio.timeout(DEFAULT_TIMEOUT):
            async with self._session.get(url, headers=self._get_headers()) as response:
                if response.status == 401 and _retry:
                    _LOGGER.debug(
                        "Received 401 from %s — token may have expired, re-authenticating",
                        url,
                    )
                    self._token = None
                    if await self.authenticate():
                        return await self._get_json(url, _retry=False)
                    # Re-auth failed — let raise_for_status surface the 401
                response.raise_for_status()
                return await response.json()

    async def get_items(self) -> list[dict[str, Any]]:
        """Get all items from NesVentory.

        Returns:
            List of item dictionaries

        Raises:
            ClientError: If request fails
            asyncio.TimeoutError: On timeout

        """
        url = f"{self._base_url}{API_ITEMS_ENDPOINT}"
        try:
            result = await self._get_json(url)
            return result if isinstance(result, list) else []
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout while fetching items")
            raise
        except ClientError as err:
            _LOGGER.error("Error fetching items: %s", err)
            raise

    async def get_total_items_count(self) -> int:
        """Get total count of items.

        Returns:
            Total number of items

        """
        try:
            items = await self.get_items()
            return len(items)
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOGGER.error("Error getting total items count: %s", err)
            return 0

    async def get_total_value(self) -> float:
        """Get total value of all items.

        Returns:
            Total value of inventory

        """
        try:
            items = await self.get_items()
            total = 0.0
            for item in items:
                value = item.get("value", 0) or item.get("price", 0) or 0
                total += float(value)
            return total
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOGGER.error("Error calculating total value: %s", err)
            return 0.0

    async def get_locations(self) -> list[dict[str, Any]]:
        """Get all locations from NesVentory.

        Returns:
            List of location dictionaries

        Raises:
            ClientError: If request fails
            asyncio.TimeoutError: On timeout

        """
        url = f"{self._base_url}{API_LOCATIONS_ENDPOINT}"
        try:
            result = await self._get_json(url)
            return result if isinstance(result, list) else []
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout while fetching locations")
            raise
        except ClientError as err:
            _LOGGER.error("Error fetching locations: %s", err)
            raise

    async def get_categories(self) -> list[dict[str, Any]]:
        """Get all categories from NesVentory.

        Returns:
            List of category dictionaries

        Raises:
            ClientError: If request fails
            asyncio.TimeoutError: On timeout

        """
        url = f"{self._base_url}{API_CATEGORIES_ENDPOINT}"
        try:
            result = await self._get_json(url)
            return result if isinstance(result, list) else []
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout while fetching categories")
            raise
        except ClientError as err:
            _LOGGER.error("Error fetching categories: %s", err)
            raise

    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests.

        Returns:
            Dictionary of request headers

        """
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers
