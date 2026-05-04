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
from typing import Any, Dict, Optional

import requests

_LOGGER = logging.getLogger(__name__)


class SnapmakerJ1Api:
    """API client for the Snapmaker J1."""

    def __init__(self, host: str, port: int = 8080, timeout: int = 5) -> None:
        """Initialize the API client.

        :param host: IP address or hostname of the Snapmaker J1
        :param port: HTTP port (default: 8080)
        :param timeout: request timeout in seconds
        """
        self._host = host
        self._port = port
        self._timeout = timeout
        self._base_url = f"http://{host}:{port}"

    def _request(self, path: str) -> Optional[Dict[str, Any]]:
        """Perform a GET request to the Snapmaker J1 API."""
        url = f"{self._base_url}{path}"
        _LOGGER.debug("Snapmaker J1 request: %s", url)

        try:
            response = requests.get(url, timeout=self._timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as err:
            _LOGGER.error("Error communicating with Snapmaker J1: %s", err)
            return None

    def get_status(self) -> Optional[Dict[str, Any]]:
        """
        Get current printer status.

        Expected to include:
        - printer state (idle / printing / paused)
        - temperatures
        - job progress
        """
        return self._request("/api/v1/status")
