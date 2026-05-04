"""Snapmaker J1 Home Assistant integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_TIMEOUT
from homeassistant.core import HomeAssistant

from .api import SnapmakerJ1Api

_LOGGER = logging.getLogger(__name__)

DOMAIN = "snapmaker_j1"
PLATFORMS = ["sensor", "button"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Snapmaker J1 from config entry."""
    api = SnapmakerJ1Api(
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT, 8080),
        timeout=entry.data.get(CONF_TIMEOUT, 5),
    )

    ok = await api.connect()
    if not ok:
        _LOGGER.error("Could not connect to Snapmaker J1 socket server")
        return False

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = api

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entry."""
    api = hass.data[DOMAIN].pop(entry.entry_id, None)
    if api:
        await api.disconnect()

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
