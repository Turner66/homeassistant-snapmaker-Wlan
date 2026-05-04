"""Socket.IO based API client for Snapmaker J1."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import socketio

_LOGGER = logging.getLogger(__name__)

STATE_IDLE = "idle"
STATE_PRINTING = "printing"
STATE_PAUSED = "paused"
STATE_ERROR = "error"
STATE_UNKNOWN = "unknown"


class SnapmakerJ1Api:
    """Socket.IO API client for Snapmaker J1."""

    def __init__(self, host: str, port: int = 8080, timeout: int = 5) -> None:
        self._host = host
        self._port = port
        self._timeout = timeout
        self._base_url = f"http://{host}:{port}"

        self._token: str = ""
        self._sio = socketio.AsyncClient(reconnection=False)

        self._startup_event = asyncio.Event()
        self._connect_open_future: asyncio.Future | None = None
        self._pause_future: asyncio.Future | None = None
        self._resume_future: asyncio.Future | None = None
        self._stop_future: asyncio.Future | None = None

        self.workflow_state: str = STATE_UNKNOWN
        self.marlin_state: dict[str, Any] = {}
        self.marlin_settings: dict[str, Any] = {}

        self._register_handlers()

    def _register_handlers(self) -> None:
        @self._sio.on("startup")
        async def _on_startup(*args):
            _LOGGER.debug("Received startup event: %s", args)
            self._startup_event.set()

        @self._sio.on("connection:open")
        async def _on_connection_open(data):
            _LOGGER.debug("Received connection:open: %s", data)
            if isinstance(data, dict):
                token = data.get("data", {}).get("token")
                if token:
                    self._token = token

            if self._connect_open_future and not self._connect_open_future.done():
                self._connect_open_future.set_result(data)

        @self._sio.on("workflow:state")
        async def _on_workflow_state(data):
            _LOGGER.debug("Received workflow:state: %s", data)
            if isinstance(data, dict):
                raw = data.get("workflowState")
                self.workflow_state = self._normalize_state(raw)

        @self._sio.on("Marlin:state")
        async def _on_marlin_state(data):
            _LOGGER.debug("Received Marlin:state: %s", data)
            if isinstance(data, dict):
                self.marlin_state = data.get("state", {})

        @self._sio.on("Marlin:settings")
        async def _on_marlin_settings(data):
            _LOGGER.debug("Received Marlin:settings: %s", data)
            if isinstance(data, dict):
                self.marlin_settings = data.get("settings", {})

        @self._sio.on("connection:pauseGcode")
        async def _on_pause(data):
            if self._pause_future and not self._pause_future.done():
                self._pause_future.set_result(data)

        @self._sio.on("connection:resumeGcode")
        async def _on_resume(data):
            if self._resume_future and not self._resume_future.done():
                self._resume_future.set_result(data)

        @self._sio.on("connection:stopGcode")
        async def _on_stop(data):
            if self._stop_future and not self._stop_future.done():
                self._stop_future.set_result(data)

    def _normalize_state(self, raw_state: Any) -> str:
        if raw_state is None:
            return STATE_UNKNOWN

        state = str(raw_state).lower().strip()

        if state in ("idle", "ready"):
            return STATE_IDLE
        if state in ("running", "printing", "working"):
            return STATE_PRINTING
        if state in ("paused", "pause"):
            return STATE_PAUSED
        if state in ("error", "fault"):
            return STATE_ERROR

        return STATE_UNKNOWN

    async def connect(self) -> bool:
        """Connect socket and open machine connection."""
        self._startup_event.clear()

        url = self._base_url
        if self._token:
            url = f"{url}?token={self._token}"

        try:
            await self._sio.connect(url, wait_timeout=self._timeout)
            await asyncio.wait_for(self._startup_event.wait(), timeout=self._timeout)
        except Exception as err:
            _LOGGER.error("Socket.IO startup/connect failed: %s", err)
            return False

        self._connect_open_future = asyncio.get_running_loop().create_future()

        payload = {
            "eventName": "connection:open",
            "connectionType": "WiFi",
            "host": self._base_url,
            "address": self._host,
            "token": self._token,
            "port": "",
            "baudRate": 0,
            "protocol": "",
            "addByUser": True,
        }

        try:
            await self._sio.emit("connection:open", payload)
            result = await asyncio.wait_for(self._connect_open_future, timeout=self._timeout)
            _LOGGER.debug("Open machine result: %s", result)

            if isinstance(result, dict) and result.get("msg"):
                return False

            return True
        except Exception as err:
            _LOGGER.error("Machine open failed: %s", err)
            return False

    async def disconnect(self) -> None:
        """Disconnect from machine/socket."""
        try:
            await self._sio.emit("connection:close", {"eventName": "connection:close", "force": True})
        except Exception:
            pass

        if self._sio.connected:
            await self._sio.disconnect()

    async def pause_print(self) -> bool:
        self._pause_future = asyncio.get_running_loop().create_future()
        try:
            await self._sio.emit("connection:pauseGcode", {"eventName": "connection:pauseGcode"})
            await asyncio.wait_for(self._pause_future, timeout=self._timeout)
            return True
        except Exception as err:
            _LOGGER.error("Pause failed: %s", err)
            return False

    async def resume_print(self) -> bool:
        self._resume_future = asyncio.get_running_loop().create_future()
        try:
            await self._sio.emit("connection:resumeGcode", {"eventName": "connection:resumeGcode"})
            await asyncio.wait_for(self._resume_future, timeout=self._timeout)
            return True
        except Exception as err:
            _LOGGER.error("Resume failed: %s", err)
            return False

    async def stop_print(self) -> bool:
        self._stop_future = asyncio.get_running_loop().create_future()
        try:
            await self._sio.emit("connection:stopGcode", {"eventName": "connection:stopGcode"})
            await asyncio.wait_for(self._stop_future, timeout=self._timeout)
            return True
        except Exception as err:
            _LOGGER.error("Stop failed: %s", err)
            return False

    async def get_status(self) -> dict[str, Any]:
        """Return currently cached status from socket events."""
        return {
            "workflow_state": self.workflow_state,
            "marlin_state": self.marlin_state,
            "marlin_settings": self.marlin_settings,
        }
