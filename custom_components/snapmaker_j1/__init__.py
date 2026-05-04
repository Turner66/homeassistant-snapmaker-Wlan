"""Snapmaker J1 integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "snapmaker_j1"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up integration from yaml (unused)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Snapmaker J1 from config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = dict(entry.data)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True
