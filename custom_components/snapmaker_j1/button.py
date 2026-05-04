"""Button platform for Snapmaker J1."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
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
    """Set up Snapmaker J1 buttons from config entry."""
    api: SnapmakerJ1Api = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            SnapmakerJ1PauseButton(api, entry.entry_id),
            SnapmakerJ1ResumeButton(api, entry.entry_id),
            SnapmakerJ1StopButton(api, entry.entry_id),
        ]
    )


class SnapmakerJ1BaseButton(ButtonEntity):
    """Base button for Snapmaker J1."""

    def __init__(self, api: SnapmakerJ1Api, entry_id: str) -> None:
        self._api = api
        self._entry_id = entry_id


class SnapmakerJ1PauseButton(SnapmakerJ1BaseButton):
    """Button to pause current print."""

    _attr_name = "Snapmaker J1 Pause"
    _attr_icon = "mdi:pause"

    def __init__(self, api: SnapmakerJ1Api, entry_id: str) -> None:
        super().__init__(api, entry_id)
        self._attr_unique_id = f"{entry_id}_pause"

    async def async_press(self) -> None:
        """Pause current print."""
        ok = await self._api.pause_print()
        if not ok:
            _LOGGER.warning("Failed to pause Snapmaker J1 print")


class SnapmakerJ1ResumeButton(SnapmakerJ1BaseButton):
    """Button to resume current print."""

    _attr_name = "Snapmaker J1 Resume"
    _attr_icon = "mdi:play"

    def __init__(self, api: SnapmakerJ1Api, entry_id: str) -> None:
        super().__init__(api, entry_id)
        self._attr_unique_id = f"{entry_id}_resume"

    async def async_press(self) -> None:
        """Resume current print."""
        ok = await self._api.resume_print()
        if not ok:
            _LOGGER.warning("Failed to resume Snapmaker J1 print")


class SnapmakerJ1StopButton(SnapmakerJ1BaseButton):
    """Button to stop current print."""

    _attr_name = "Snapmaker J1 Stop"
    _attr_icon = "mdi:stop"

    def __init__(self, api: SnapmakerJ1Api, entry_id: str) -> None:
        super().__init__(api, entry_id)
        self._attr_unique_id = f"{entry_id}_stop"

    async def async_press(self) -> None:
        """Stop current print."""
        ok = await self._api.stop_print()
        if not ok:
            _LOGGER.warning("Failed to stop Snapmaker J1 print")
``
