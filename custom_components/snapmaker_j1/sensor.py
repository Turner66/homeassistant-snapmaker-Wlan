"""Sensor platform for Snapmaker J1."""

from __future__ import annotations

import logging
from typing import Any

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
            SnapmakerJ1WorkflowStateSensor(api, entry.entry_id),
            SnapmakerJ1ProgressSensor(api, entry.entry_id),
            SnapmakerJ1FileNameSensor(api, entry.entry_id),
        ],
        update_before_add=True,
    )


class SnapmakerJ1BaseSensor(SensorEntity):
    """Base sensor for Snapmaker J1."""

    _attr_should_poll = True

    def __init__(self, api: SnapmakerJ1Api, entry_id: str) -> None:
        self._api = api
        self._entry_id = entry_id
        self._status_cache: dict[str, Any] = {}

    async def _refresh_status(self) -> dict[str, Any]:
        """Refresh cached status from API."""
        try:
            self._status_cache = await self._api.get_status()
        except Exception as err:
            _LOGGER.error("Failed to refresh Snapmaker J1 status: %s", err)
            self._status_cache = {}

        return self._status_cache


class SnapmakerJ1WorkflowStateSensor(SnapmakerJ1BaseSensor):
    """Sensor showing the Snapmaker workflow state."""

    _attr_name = "Snapmaker J1 Status"
    _attr_icon = "mdi:printer-3d"

    def __init__(self, api: SnapmakerJ1Api, entry_id: str) -> None:
        super().__init__(api, entry_id)
        self._attr_unique_id = f"{entry_id}_workflow_state"
        self._attr_native_value = STATE_UNAVAILABLE

    async def async_update(self) -> None:
        """Update workflow state."""
        status = await self._refresh_status()

        workflow_state = status.get("workflow_state")
        if not workflow_state:
            self._attr_native_value = STATE_UNAVAILABLE
            return

        self._attr_native_value = workflow_state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        marlin_state = self._status_cache.get("marlin_state", {})
        marlin_settings = self._status_cache.get("marlin_settings", {})

        return {
            "marlin_state": marlin_state,
            "marlin_settings": marlin_settings,
        }


class SnapmakerJ1ProgressSensor(SnapmakerJ1BaseSensor):
    """Sensor showing print progress."""

    _attr_name = "Snapmaker J1 Print Progress"
    _attr_icon = "mdi:progress-clock"
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, api: SnapmakerJ1Api, entry_id: str) -> None:
        super().__init__(api, entry_id)
        self._attr_unique_id = f"{entry_id}_print_progress"
        self._attr_native_value = None

    async def async_update(self) -> None:
        """Update progress value."""
        status = await self._refresh_status()
        marlin_state = status.get("marlin_state", {})

        # Luban-derived fields are not fully confirmed yet, so try multiple keys safely.
        progress = (
            marlin_state.get("progress")
            or marlin_state.get("fileProgress")
            or marlin_state.get("printProgress")
        )

        if progress is None:
            self._attr_native_value = None
            return

        try:
            self._attr_native_value = int(progress)
        except (TypeError, ValueError):
            _LOGGER.debug("Could not parse Snapmaker J1 progress value: %s", progress)
            self._attr_native_value = None


class SnapmakerJ1FileNameSensor(SnapmakerJ1BaseSensor):
    """Sensor showing current file name."""

    _attr_name = "Snapmaker J1 Current File"
    _attr_icon = "mdi:file-document"

    def __init__(self, api: SnapmakerJ1Api, entry_id: str) -> None:
        super().__init__(api, entry_id)
        self._attr_unique_id = f"{entry_id}_current_file"
        self._attr_native_value = None

    async def async_update(self) -> None:
        """Update current file name."""
        status = await self._refresh_status()
        marlin_state = status.get("marlin_state", {})

        file_name = (
            marlin_state.get("fileName")
            or marlin_state.get("filename")
            or marlin_state.get("currentFile")
        )

        self._attr_native_value = file_name
