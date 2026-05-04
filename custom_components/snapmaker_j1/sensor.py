"""Sensor platform for Snapmaker J1."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SnapmakerJ1Coordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Snapmaker J1 sensors from config entry."""
    coordinator: SnapmakerJ1Coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            SnapmakerJ1StatusSensor(coordinator, entry.entry_id),
            SnapmakerJ1FileSensor(coordinator, entry.entry_id),
            SnapmakerJ1ProgressSensor(coordinator, entry.entry_id),
        ],
        update_before_add=True,
    )


class SnapmakerJ1StatusSensor(CoordinatorEntity, SensorEntity):
    """Status sensor."""

    _attr_name = "Snapmaker J1 Status"
    _attr_icon = "mdi:printer-3d"

    def __init__(self, coordinator: SnapmakerJ1Coordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_status"

    @property
    def native_value(self):
        runtime_state = self.coordinator.data.get("runtime_state")
        if not runtime_state:
            return STATE_UNAVAILABLE

        value = getattr(runtime_state, "workflow_status", None)
        return value or STATE_UNAVAILABLE


class SnapmakerJ1FileSensor(CoordinatorEntity, SensorEntity):
    """Current file sensor."""

    _attr_name = "Snapmaker J1 Current File"
    _attr_icon = "mdi:file-document"

    def __init__(self, coordinator: SnapmakerJ1Coordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_file"

    @property
    def native_value(self):
        print_info = self.coordinator.data.get("print_info")
        if not print_info:
            return None

        return getattr(print_info, "filename", None)


class SnapmakerJ1ProgressSensor(CoordinatorEntity, SensorEntity):
    """Print progress sensor."""

    _attr_name = "Snapmaker J1 Print Progress"
    _attr_icon = "mdi:progress-clock"
    _attr_native_unit_of_measurement = "%"

    def __init__(self, coordinator: SnapmakerJ1Coordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_progress"

    @property
    def native_value(self):
        print_info = self.coordinator.data.get("print_info")
        if not print_info:
            return None

        progress = getattr(print_info, "progress", None)
        if progress is None:
            return None

        try:
            return round(float(progress) * 100, 1)
        except (TypeError, ValueError):
            return None
