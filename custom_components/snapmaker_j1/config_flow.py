"""Config flow for Snapmaker J1."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_TIMEOUT
from homeassistant.data_entry_flow import FlowResult

DOMAIN = "snapmaker_j1"

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 8888
DEFAULT_TIMEOUT = 5


async def validate_connection(host: str, port: int, timeout: int) -> bool:
    """Validate TCP reachability."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout,
        )
        writer.close()
        await writer.wait_closed()
        return True
    except Exception as err:
        _LOGGER.warning("TCP check failed for %s:%s -> %s", host, port, err)
        return False


class SnapmakerJ1ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Snapmaker J1 config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the user step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()

            ok = await validate_connection(
                user_input[CONF_HOST],
                user_input.get(CONF_PORT, DEFAULT_PORT),
                user_input.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
            )
            if not ok:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"Snapmaker J1 ({user_input[CONF_HOST]})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
                }
            ),
            errors=errors,
        )
