"""HTTP client for Open Wearables backend API."""

import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class OpenWearablesClient:
    """Client for interacting with Open Wearables REST API.

    Uses a persistent httpx.AsyncClient for connection pooling and efficiency.
    The client is lazily initialized on first request and reused for subsequent requests.
    """

    def __init__(self) -> None:
        self.base_url = settings.open_wearables_api_url.rstrip("/")
        self.timeout = settings.request_timeout
        self._api_key = settings.open_wearables_api_key.get_secret_value()
        self._http_client: httpx.AsyncClient | None = None

    def _ensure_configured(self) -> None:
        """Raise an error if the API key is not configured."""
        if not self._api_key:
            from app.config import _ENV_FILE

            raise ValueError(f"OPEN_WEARABLES_API_KEY is not configured. Please set it in: {_ENV_FILE}")

    @property
    def headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        return {
            "X-Open-Wearables-API-Key": self._api_key,
            "Content-Type": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client with connection pooling."""
        if self._http_client is None or self._http_client.is_closed:
            logger.debug("Creating new httpx.AsyncClient with connection pool")
            self._http_client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.headers,
                base_url=self.base_url,
            )
        return self._http_client

    async def close(self) -> None:
        """Close the HTTP client and release connections."""
        if self._http_client is not None and not self._http_client.is_closed:
            logger.debug("Closing httpx.AsyncClient")
            await self._http_client.aclose()
            self._http_client = None

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Make an HTTP request to the backend API."""
        self._ensure_configured()
        url = path  # base_url is set on the client
        logger.debug(f"Making {method} request to {self.base_url}{path}")

        http_client = await self._get_client()
        response = await http_client.request(
            method=method,
            url=url,
            **kwargs,
        )

        if response.status_code == 401:
            raise ValueError("Invalid API key. Check your OPEN_WEARABLES_API_KEY configuration.")
        if response.status_code == 404:
            raise ValueError(f"Resource not found: {path}")
        if response.status_code == 400:
            error_detail = response.text
            logger.error(f"Bad request to {self.base_url}{path}: {error_detail}")
            raise ValueError(f"Bad request to {path}: {error_detail}")

        response.raise_for_status()
        return response.json()

    async def get_users(self, search: str | None = None, limit: int = 100) -> dict[str, Any]:
        """
        List users accessible via the configured API key.

        Args:
            search: Optional search term to filter users by name/email
            limit: Maximum number of users to return

        Returns:
            Paginated response with users list
        """
        params: dict[str, Any] = {"limit": limit}
        if search:
            params["search"] = search

        return await self._request("GET", "/api/v1/users", params=params)

    async def get_user(self, user_id: str) -> dict[str, Any]:
        """
        Get a specific user by ID.

        Args:
            user_id: UUID of the user

        Returns:
            User details
        """
        return await self._request("GET", f"/api/v1/users/{user_id}")

    async def get_sleep_summaries(
        self,
        user_id: str,
        start_date: str,
        end_date: str,
        limit: int = 100,
    ) -> dict[str, Any]:
        """
        Get sleep summaries for a user within a date range.

        Args:
            user_id: UUID of the user
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            limit: Maximum number of records to return

        Returns:
            Paginated response with sleep summaries
        """
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
        }
        path = f"/api/v1/users/{user_id}/summaries/sleep"
        logger.info(f"get_sleep_summaries: user_id={user_id!r} (len={len(user_id) if user_id else 0})")
        return await self._request("GET", path, params=params)

    async def get_workouts(
        self,
        user_id: str,
        start_date: str,
        end_date: str,
        workout_type: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """
        Get workout events for a user within a date range.

        Args:
            user_id: UUID of the user
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            workout_type: Optional filter by workout type (e.g., "running", "cycling")
            limit: Maximum number of records to return

        Returns:
            Paginated response with workout events
        """
        params: dict[str, Any] = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
        }
        if workout_type:
            params["record_type"] = workout_type
        logger.info(f"get_workouts: user_id={user_id!r} (len={len(user_id) if user_id else 0})")
        return await self._request("GET", f"/api/v1/users/{user_id}/events/workouts", params=params)


# Singleton instance
client = OpenWearablesClient()
