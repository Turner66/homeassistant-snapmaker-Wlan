"""Sensor platform for Snapmaker J1."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import SnapmakerJ1Api

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: dict[str, Any],
    async_add_entities: AddEntitiesCallback,
    discovery_info: dict[str, Any] | None = None,
) -> None:
    """Set up Snapmaker J1 sensors."""
    # ⚠️ TEMPORARY: Hardcoded IP (will be replaced by config_flow)
    api = SnapmakerJ1Api(host="192.168.1.100")

    async_add_entities(
        [
            SnapmakerJ1StatusSensor(api),
            SnapmakerJ1JobProgressSensor(api),
            SnapmakerJ1JobNameSensor(api),
        ]
    )


class SnapmakerJ1StatusSensor(SensorEntity):
    """Sensor showing the Snapmaker J1 printer status."""

    _attr_name = "Snapmaker J1 Status"
    _attr_icon = "mdi:printer-3d"
    _attr_unique_id = "snapmaker_j1_status"

    def __init__(self, api: SnapmakerJ1Api) -> None:
        """Initialize the status sensor."""
        self._api = api
        self._attr_native_value = STATE_UNAVAILABLE

    async def async_update(self) -> None:
        """Fetch state from the printer."""
        data = self._api.get_status()

        if not data:
            _LOGGER.debug("No status data received from Snapmaker J1")
            self._attr_native_value = STATE_UNAVAILABLE
            return

        # Extract normalized state
        state = data.get("state", "unknown")
        self._attr_native_value = state
        _LOGGER.debug("Snapmaker J1 status updated: %s", state)


class SnapmakerJ1JobProgressSensor(SensorEntity):
    """Sensor showing the job progress percentage."""

    _attr_name = "Snapmaker J1 Job Progress"
    _attr_icon = "mdi:progress-clock"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_unique_id = "snapmaker_j1_job_progress"

    def __init__(self, api: SnapmakerJ1Api) -> None:
        """Initialize the progress sensor."""
        self._api = api
        self._attr_native_value = None

    async def async_update(self) -> None:
        """Fetch job progress from the printer."""
        data = self._api.get_job_progress()

        if not data:
            _LOGGER.debug("No job progress data received from Snapmaker J1")
            self._attr_native_value = None
            return

        # Extract progress percentage (assume 0-100 or need to calculate)
        progress = data.get("progress")
        if progress is not None:
            self._attr_native_value = int(progress)
            _LOGGER.debug("Snapmaker J1 job progress: %d%%", progress)
        else:
            # Try to calculate from current_line and total_lines
            current = data.get("current_line", 0)
            total = data.get("total_lines", 0)
            if total > 0:
                calculated = int((current / total) * 100)
                self._attr_native_value = calculated
                _LOGGER.debug(
                    "Snapmaker J1 job progress (calculated): %d%%", calculated
                )


class SnapmakerJ1JobNameSensor(SensorEntity):
    """Sensor showing the current job name."""

    _attr_name = "Snapmaker J1 Job Name"
    _attr_icon = "mdi:file-document"
    _attr_unique_id = "snapmaker_j1_job_name"

    def __init__(self, api: SnapmakerJ1Api) -> None:
        """Initialize the job name sensor."""
        self._api = api
        self._attr_native_value = None

    async def async_update(self) -> None:
        """Fetch job name from the printer."""
        data = self._api.get_job_progress()

        if not data:
            _LOGGER.debug("No job data received from Snapmaker J1")
            self._attr_native_value = None
            return

        job_name = data.get("job_name")
        if job_name:
            self._attr_native_value = job_name
            _LOGGER.debug("Snapmaker J1 job name: %s", job_name)
