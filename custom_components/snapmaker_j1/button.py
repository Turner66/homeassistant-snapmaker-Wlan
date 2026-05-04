"""Button platform for Snapmaker J1."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
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
    """Set up Snapmaker J1 buttons."""
    # ⚠️ TEMPORARY: Hardcoded IP (will be replaced by config_flow)
    api = SnapmakerJ1Api(host="192.168.1.100")

    async_add_entities(
        [
            SnapmakerJ1PauseButton(api),
            SnapmakerJ1ResumeButton(api),
            SnapmakerJ1StopButton(api),
        ]
    )


class SnapmakerJ1PauseButton(ButtonEntity):
    """Button to pause the current print job."""

    _attr_name = "Snapmaker J1 Pause"
    _attr_icon = "mdi:pause"
    _attr_unique_id = "snapmaker_j1_pause_button"

    def __init__(self, api: SnapmakerJ1Api) -> None:
        """Initialize the pause button."""
        self._api = api

    async def async_press(self) -> None:
        """Handle button press to pause print."""
        success = self._api.pause_print()
        if success:
            _LOGGER.info("Pause button pressed successfully")
        else:
            _LOGGER.warning("Failed to pause print via button")


class SnapmakerJ1ResumeButton(ButtonEntity):
    """Button to resume a paused print job."""

    _attr_name = "Snapmaker J1 Resume"
    _attr_icon = "mdi:play"
    _attr_unique_id = "snapmaker_j1_resume_button"

    def __init__(self, api: SnapmakerJ1Api) -> None:
        """Initialize the resume button."""
        self._api = api

    async def async_press(self) -> None:
        """Handle button press to resume print."""
        success = self._api.resume_print()
        if success:
            _LOGGER.info("Resume button pressed successfully")
        else:
            _LOGGER.warning("Failed to resume print via button")


class SnapmakerJ1StopButton(ButtonEntity):
    """Button to stop the current print job."""

    _attr_name = "Snapmaker J1 Stop"
    _attr_icon = "mdi:stop"
    _attr_unique_id = "snapmaker_j1_stop_button"

    def __init__(self, api: SnapmakerJ1Api) -> None:
        """Initialize the stop button."""
        self._api = api

    async def async_press(self) -> None:
        """Handle button press to stop print."""
        success = self._api.stop_print()
        if success:
            _LOGGER.info("Stop button pressed successfully")
        else:
            _LOGGER.warning("Failed to stop print via button")
