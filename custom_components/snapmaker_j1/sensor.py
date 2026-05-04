"""Sensor platform for Snapmaker J1."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN
from .api import SnapmakerJ1Api

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Snapmaker J1 sensors from config entry."""
    api: SnapmakerJ1Api = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            SnapmakerJ1StatusSensor(api, entry.entry_id),
            SnapmakerJ1JobProgressSensor(api, entry.entry_id),
            SnapmakerJ1JobNameSensor(api, entry.entry_id),
        ]
    )


class SnapmakerJ1StatusSensor(SensorEntity):
    """Sensor showing the Snapmaker J1 printer status."""

    _attr_name = "Snapmaker J1 Status"
    _attr_icon = "mdi:printer-3d"

    def __init__(self, api: SnapmakerJ1Api, entry_id: str) -> None:
        self._api = api
        self._attr_native_value = STATE_UNAVAILABLE
        self._attr_unique_id = f"{entry_id}_status"

    async def async_update(self) -> None:
        """Fetch state from the printer."""
        data = await self._api.get_status()

        if not data:
            self._attr_native_value = STATE_UNAVAILABLE
            return

        self._attr_native_value = data.get("state", "unknown")


class SnapmakerJ1JobProgressSensor(SensorEntity):
    """Sensor showing the job progress percentage."""

    _attr_name = "Snapmaker J1 Job Progress"
    _attr_icon = "mdi:progress-clock"
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, api: SnapmakerJ1Api, entry_id: str) -> None:
        self._api = api
        self._attr_native_value = None
        self._attr_unique_id = f"{entry_id}_job_progress"

    async def async_update(self) -> None:
        """Fetch job progress from the printer."""
        data = await self._api.get_job_progress()

        if not data:
            self._attr_native_value = None
            return

        progress = data.get("progress")
        if progress is not None:
            self._attr_native_value = int(progress)
            return

        current = data.get("current_line", 0)
        total = data.get("total_lines", 0)
        if total > 0:
            self._attr_native_value = int((current / total) * 100)
        else:
            self._attr_native_value = None


class SnapmakerJ1JobNameSensor(SensorEntity):
    """Sensor showing the current job name."""

    _attr_name = "Snapmaker J1 Job Name"
    _attr_icon = "mdi:file-document"

    def __init__(self, api: SnapmakerJ1Api, entry_id: str) -> None:
        self._api = api
        self._attr_native_value = None
        self._attr_unique_id = f"{entry_id}_job_name"

    async def async_update(self) -> None:
        """Fetch job name from the printer."""
        data = await self._api.get_job_progress()

        if not data:
            self._attr_native_value = None
            return

        self._attr_native_value = data.get("job_name")
