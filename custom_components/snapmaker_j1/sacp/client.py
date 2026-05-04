"""High-level SACP client for Snapmaker J1."""

from __future__ import annotations

import logging

from .models import MachineInfo, PrintInfo, RuntimeState
from .transport import SacpTransport

_LOGGER = logging.getLogger(__name__)


class SacpClient:
    """High-level Snapmaker SACP client."""

    def __init__(self, host: str, port: int = 8888, timeout: int = 5) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.transport = SacpTransport(host, port, timeout)

        self.token: str = ""
        self.machine_info = MachineInfo()
        self.print_info = PrintInfo()
        self.runtime_state = RuntimeState()

    async def connect_tcp(self) -> bool:
        """Open raw TCP connection."""
        return await self.transport.connect()

    async def disconnect_tcp(self) -> None:
        """Close raw TCP connection."""
        await self.transport.disconnect()

    async def wifi_connection(
        self,
        host_name: str,
        client_name: str,
        token: str = "",
    ) -> bool:
        """Establish Snapmaker Wi-Fi session.

        TODO:
        Implement using real SACP packet framing once protocol.py is finalized.
        """
        self.token = token
        raise NotImplementedError("wifi_connection not implemented yet")

    async def wifi_connection_close(self) -> bool:
        """Close Wi-Fi session."""
        raise NotImplementedError("wifi_connection_close not implemented yet")

    async def heartbeat(self) -> bool:
        """Send or maintain heartbeat."""
        raise NotImplementedError("heartbeat not implemented yet")

    async def get_machine_info(self) -> MachineInfo:
        """Read machine info."""
        raise NotImplementedError("get_machine_info not implemented yet")

    async def get_printing_file_info(self) -> PrintInfo:
        """Read active printing file info."""
        raise NotImplementedError("get_printing_file_info not implemented yet")

    async def pause_print(self) -> bool:
        """Pause current print."""
        raise NotImplementedError("pause_print not implemented yet")

    async def resume_print(self) -> bool:
        """Resume current print."""
        raise NotImplementedError("resume_print not implemented yet")

    async def stop_print(self) -> bool:
        """Stop current print."""
        raise NotImplementedError("stop_print not implemented yet")
