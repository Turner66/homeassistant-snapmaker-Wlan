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

# Normalized printer states
STATE_IDLE = "idle"
STATE_PRINTING = "printing"
STATE_PAUSED = "paused"
STATE_ERROR = "error"
STATE_UNKNOWN = "unknown"


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

    def _request_post(
        self, path: str, data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Perform a POST request to the Snapmaker J1 API."""
        url = f"{self._base_url}{path}"
        _LOGGER.debug("Snapmaker J1 POST request: %s", url)

        try:
            response = requests.post(url, json=data, timeout=self._timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as err:
            _LOGGER.error("Error communicating with Snapmaker J1: %s", err)
            return None

    def _normalize_state(self, raw_state: str) -> str:
        """Normalize printer state to Home Assistant standard.

        Maps various API states to normalized values:
        - idle, ready -> STATE_IDLE
        - printing, working -> STATE_PRINTING
        - paused, pause -> STATE_PAUSED
        - error, fault -> STATE_ERROR
        - unknown -> STATE_UNKNOWN
        """
        if not raw_state:
            return STATE_UNKNOWN

        state_lower = raw_state.lower().strip()

        if state_lower in ("idle", "ready"):
            return STATE_IDLE
        elif state_lower in ("printing", "working"):
            return STATE_PRINTING
        elif state_lower in ("paused", "pause"):
            return STATE_PAUSED
        elif state_lower in ("error", "fault"):
            return STATE_ERROR

        _LOGGER.debug("Unknown printer state: %s", raw_state)
        return STATE_UNKNOWN

    def get_status(self) -> Optional[Dict[str, Any]]:
        """
        Get current printer status.

        Returns a dict with normalized 'state' field and other status info.
        Expected fields:
        - state: normalized printer state (idle/printing/paused/error)
        - temperatures: dict with temperature data
        - job_progress: job progress information
        """
        data = self._request("/api/v1/status")

        if not data:
            return None

        # Normalize the state if present
        if "state" in data:
            data["state"] = self._normalize_state(data["state"])

        return data

    def get_job_progress(self) -> Optional[Dict[str, Any]]:
        """
        Get current job progress information.

        Returns job progress details including:
        - current_line: current line number
        - total_lines: total lines in job
        - progress: progress percentage (0-100)
        - estimated_time: estimated time remaining in seconds
        - job_name: name of the current job
        """
        return self._request("/api/v1/print_progress")

    def pause_print(self) -> bool:
        """
        Pause the current print job.

        Returns:
            True if pause was successful, False otherwise.
        """
        result = self._request_post("/api/v1/print_pause")
        if result is None:
            _LOGGER.warning("Failed to pause print")
            return False
        _LOGGER.info("Print paused successfully")
        return True

    def resume_print(self) -> bool:
        """
        Resume a paused print job.

        Returns:
            True if resume was successful, False otherwise.
        """
        result = self._request_post("/api/v1/print_resume")
        if result is None:
            _LOGGER.warning("Failed to resume print")
            return False
        _LOGGER.info("Print resumed successfully")
        return True

    def stop_print(self) -> bool:
        """
        Stop the current print job.

        Returns:
            True if stop was successful, False otherwise.
        """
        result = self._request_post("/api/v1/print_stop")
        if result is None:
            _LOGGER.warning("Failed to stop print")
            return False
        _LOGGER.info("Print stopped successfully")
        return True
