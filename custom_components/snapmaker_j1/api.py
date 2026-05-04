"""
Snapmaker J1 API client.

This module handles all communication with the Snapmaker J1 3D printer.
Behavior is inspired by the official Snapmaker Luban software.

- Connection: WiFi
- Protocol: HTTP
- Default port: 8080
"""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

STATE_IDLE = "idle"
STATE_PRINTING = "printing"
STATE_PAUSED = "paused"
STATE_ERROR = "error"
STATE_UNKNOWN = "unknown"


class SnapmakerJ1Api:
    """API client for the Snapmaker J1."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int = 8080,
        timeout: int = 5,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._host = host
        self._port = port
        self._timeout = timeout
        self._base_url = f"http://{host}:{port}"

    async def _request(
        self, method: str, path: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        """Perform an HTTP request to the Snapmaker J1 API."""
        url = f"{self._base_url}{path}"
        _LOGGER.debug("Snapmaker J1 %s request: %s", method, url)

        try:
            async with self._session.request(
                method,
                url,
                json=data,
                timeout=aiohttp.ClientTimeout(total=self._timeout),
            ) as response:
                response.raise_for_status()

                # Manche APIs liefern evtl. leeren Body bei POST zurück
                if response.content_type == "application/json":
                    return await response.json()

                text = await response.text()
                if not text.strip():
                    return {}

                _LOGGER.debug("Non-JSON response from Snapmaker J1: %s", text)
                return {}

        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.error("Error communicating with Snapmaker J1: %s", err)
            return None

    def _normalize_state(self, raw_state: str | None) -> str:
        """Normalize printer state."""
        if not raw_state:
            return STATE_UNKNOWN

        state_lower = raw_state.lower().strip()

        if state_lower in ("idle", "ready"):
            return STATE_IDLE
        if state_lower in ("printing", "working", "running"):
            return STATE_PRINTING
        if state_lower in ("paused", "pause"):
            return STATE_PAUSED
        if state_lower in ("error", "fault"):
            return STATE_ERROR

        _LOGGER.debug("Unknown printer state: %s", raw_state)
        return STATE_UNKNOWN

    async def get_status(self) -> dict[str, Any] | None:
        """Get current printer status."""
        data = await self._request("GET", "/api/v1/status")
        if not data:
            return None

        if "state" in data:
            data["state"] = self._normalize_state(data.get("state"))

        return data

    async def get_job_progress(self) -> dict[str, Any] | None:
        """Get current job progress."""
        return await self._request("GET", "/api/v1/print_progress")

    async def pause_print(self) -> bool:
        """Pause the current print job."""
        result = await self._request("POST", "/api/v1/print_pause")
        return result is not None

    async def resume_print(self) -> bool:
        """Resume a paused print job."""
        result = await self._request("POST", "/api/v1/print_resume")
        return result is not None

    async def stop_print(self) -> bool:
        """Stop the current print job."""
        result = await self._request("POST", "/api/v1/print_stop")
        return result is not None
