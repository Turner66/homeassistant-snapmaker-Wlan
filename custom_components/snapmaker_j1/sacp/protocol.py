"""SACP protocol helpers.

NOTE:
This file is currently only a scaffold.
The exact Snapmaker SACP frame/header format still needs to be confirmed
from the SACP SDK definitions.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SacpRequest:
    main_cmd: int
    sub_cmd: int
    peer_id: int
    payload: bytes = b""


@dataclass
class SacpResponse:
    main_cmd: int
    sub_cmd: int
    result: int
    payload: bytes = b""


def encode_request(request: SacpRequest) -> bytes:
    """Encode a request into SACP frame bytes.

    TODO:
    Replace this placeholder with the real SACP frame builder once the
    SDK header structure is mapped.
    """
    raise NotImplementedError("SACP frame encoding not implemented yet")


def decode_response(data: bytes) -> SacpResponse:
    """Decode a response from SACP frame bytes.

    TODO:
    Replace this placeholder with the real SACP frame parser once the
    SDK header structure is mapped.
    """
    raise NotImplementedError("SACP frame decoding not implemented yet")
``
