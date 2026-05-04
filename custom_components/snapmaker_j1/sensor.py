"""Sensor platform for Snapmaker J1."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Snapmaker J1 sensors from config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SnapmakerJ1StatusSensor(entry.entry_id, data)])


class SnapmakerJ1StatusSensor(SensorEntity):
    """Very basic placeholder sensor."""

    _attr_name = "Snapmaker J1 Status"
    _attr_icon = "mdi:printer-3d"

    def __init__(self, entry_id: str, data: dict) -> None:
        self._attr_unique_id = f"{entry_id}_status"
        self._data = data
        self._attr_native_value = "configured"

    @property
    def extra_state_attributes(self):
        return {
            "host": self._data.get("host"),
            "port": self._data.get("port"),
            "timeout": self._data.get("timeout"),
        }
