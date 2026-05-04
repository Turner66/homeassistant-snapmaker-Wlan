"""Low-level TCP transport for Snapmaker SACP."""

from __future__ import annotations

import asyncio
import logging

_LOGGER = logging.getLogger(__name__)


class SacpTransport:
    """Simple async TCP transport for Snapmaker J1."""

    def __init__(self, host: str, port: int = 8888, timeout: int = 5) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None

    @property
    def connected(self) -> bool:
        """Return whether transport is connected."""
        return self.reader is not None and self.writer is not None

    async def connect(self) -> bool:
        """Open the TCP connection."""
        try:
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout,
            )
            _LOGGER.debug("Connected to SACP TCP %s:%s", self.host, self.port)
            return True
        except Exception as err:
            _LOGGER.error("SACP TCP connect failed: %s", err)
            self.reader = None
            self.writer = None
            return False

    async def disconnect(self) -> None:
        """Close the TCP connection."""
        if self.writer:
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except Exception:
                pass

        self.reader = None
        self.writer = None
        _LOGGER.debug("Disconnected from SACP TCP %s:%s", self.host, self.port)

    async def write(self, data: bytes) -> None:
        """Write bytes to the socket."""
        if not self.writer:
            raise RuntimeError("SACP transport is not connected")

        self.writer.write(data)
        await self.writer.drain()

    async def read(self, n: int = 4096) -> bytes:
        """Read bytes from the socket."""
        if not self.reader:
            raise RuntimeError("SACP transport is not connected")

        return await self.reader.read(n)

    async def readexactly(self, n: int) -> bytes:
        """Read exactly n bytes."""
        if not self.reader:
            raise RuntimeError("SACP transport is not connected")

        return await self.reader.readexactly(n)
