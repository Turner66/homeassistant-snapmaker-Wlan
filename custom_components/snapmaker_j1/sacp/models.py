"""Small internal data models for Snapmaker J1."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MachineInfo:
    machine_type: Optional[int] = None
    firmware_version: Optional[str] = None
    raw: dict | None = None


@dataclass
class PrintInfo:
    filename: str = ""
    total_lines: int = 0
    estimated_time_s: int = 0
    current_line: int = 0
    progress: float = 0.0
    elapsed_time_s: int = 0
    remaining_time_s: int = 0


@dataclass
class RuntimeState:
    workflow_status: str = "unknown"
    filename: str = ""
    progress: float = 0.0
    elapsed_time_s: int = 0
    remaining_time_s: int = 0
    nozzle_temp_left: Optional[float] = None
    nozzle_temp_right: Optional[float] = None
    bed_temp: Optional[float] = None
