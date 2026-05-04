"""Sensor platform for Snapmaker J1."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
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

    # ⚠️ TEMPORÄR:
    # IP-Adresse hier fest eintragen (später Config Flow)
    api = SnapmakerJ1Api(host="192.168.1.100")

    async_add_entities([SnapmakerJ1StatusSensor(api)])


class SnapmakerJ1StatusSensor(SensorEntity):
    """Sensor showing the Snapmaker J1 printer status."""

    _attr_name = "Snapmaker J1 Status"
    _attr_icon = "mdi:printer-3d"

    def __init__(self, api: SnapmakerJ1Api) -> None:
        self._api = api
        self._attr_native_value = None

    async def update(self) -> None:
        """Fetch state from the printer."""
        data = self._api.get_status()

        if not data:
            _LOGGER.warning("No data received from Snapmaker J1")
            self._attr_native_value = "unavailable"
            return

        # ⚠️ Annahme: später exakt an API anpassen
        self._attr_native_value = data.get("state", "unknown")
