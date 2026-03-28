"""Engine-agnostic calculation result container."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Dict, Any

from .molecule import Molecule


class CalcType(Enum):
    NEB = auto()
    TS_OPT = auto()
    FREQUENCY = auto()
    IRC = auto()
    SINGLE_POINT = auto()
    OPT = auto()


class CalcStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class FrequencyData:
    frequencies: List[float]          # cm^-1, negative = imaginary
    zero_point_energy: Optional[float] = None   # Hartree

    @property
    def n_imaginary(self) -> int:
        return sum(1 for f in self.frequencies if f < 0)

    @property
    def imaginary_frequencies(self) -> List[float]:
        return [f for f in self.frequencies if f < 0]


@dataclass
class IRCData:
    forward_path: List[Molecule]
    reverse_path: List[Molecule]
    forward_energies: List[float]     # Hartree
    reverse_energies: List[float]     # Hartree


@dataclass
class NEBData:
    images: List[Molecule]
    energies: List[float]             # Hartree relative to image[0]
    ts_image_index: int               # index of highest energy image


@dataclass
class CalculationResult:
    calc_type: CalcType
    status: CalcStatus
    engine: str                       # "xtb" | "psi4" | "pyscf"
    work_dir: str

    # Common outputs
    energy: Optional[float] = None    # Hartree
    molecule: Optional[Molecule] = None  # optimized structure

    # Type-specific outputs
    frequency_data: Optional[FrequencyData] = None
    irc_data: Optional[IRCData] = None
    neb_data: Optional[NEBData] = None

    # Raw metadata
    wall_time_seconds: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
