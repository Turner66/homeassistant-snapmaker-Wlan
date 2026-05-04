"""Snapmaker J1 Home Assistant integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_TIMEOUT
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import SnapmakerJ1Coordinator
from .sacp.client import SacpClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Snapmaker J1 from a config entry."""
    client = SacpClient(
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT, 8888),
        timeout=entry.data.get(CONF_TIMEOUT, 5),
    )

    coordinator = SnapmakerJ1Coordinator(hass, client)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id, None)
        if coordinator and coordinator.client:
            await coordinator.client.disconnect_tcp()

    return unload_ok
