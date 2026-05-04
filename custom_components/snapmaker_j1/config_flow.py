"""Config flow for Snapmaker J1 integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_TIMEOUT
from homeassistant.data_entry_flow import FlowResult

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def validate_connection(host: str, port: int, timeout: int) -> bool:
    """Validate that the host is reachable on the given TCP port."""
    try:
        conn = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        writer.close()
        await writer.wait_closed()
        return True
    except Exception as err:
        _LOGGER.warning("TCP connection test failed for %s:%s: %s", host, port, err)
        return False


class SnapmakerJ1ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Snapmaker J1."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()

            valid = await validate_connection(
                user_input[CONF_HOST],
                user_input.get(CONF_PORT, 8080),
                user_input.get(CONF_TIMEOUT, 5),
            )

            if not valid:
                errors["base"] = "cannot_connect"

            if not errors:
                return self.async_create_entry(
                    title=f"Snapmaker J1 ({user_input[CONF_HOST]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_PORT, default=8080): int,
                    vol.Optional(CONF_TIMEOUT, default=5): int,
                }
            ),
            errors=errors,
        )
