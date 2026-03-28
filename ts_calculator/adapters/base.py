"""Abstract base class for all engine adapters."""
from __future__ import annotations
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional

from domain.models import Molecule, CalcType, CalculationResult


@dataclass
class InputBundle:
    """All files and arguments needed to launch a calculation."""
    command: List[str]                        # e.g. ["xtb", "input.xyz", "--opt"]
    input_files: Dict[str, str]               # filename → content to write before run
    work_dir: Path
    env_override: Dict[str, str] = field(default_factory=dict)


@dataclass
class CalcParams:
    """Common parameters shared across all engines."""
    calc_type: CalcType
    method: str                               # e.g. "b3lyp-d3bj", "mp2", "gfn2"
    basis: str = ""                           # empty for xTB (method implies basis)
    n_cores: int = 1
    memory_gb: float = 4.0
    extra: Dict[str, Any] = field(default_factory=dict)


class EngineAdapterBase(ABC):
    """Interface that all engine adapters must implement."""

    @property
    @abstractmethod
    def engine_name(self) -> str: ...

    @abstractmethod
    def check_installation(self) -> bool:
        """Return True if the engine binary/package is available."""
        ...

    @abstractmethod
    def get_supported_calc_types(self) -> List[CalcType]:
        """Return the CalcTypes this adapter supports."""
        ...

    @abstractmethod
    def prepare_input(
        self,
        molecule: Molecule,
        params: CalcParams,
        work_dir: Path,
        aux_molecules: Optional[List[Molecule]] = None,
    ) -> InputBundle:
        """Build input files and command for the calculation."""
        ...

    def run(self, bundle: InputBundle) -> subprocess.Popen:
        """Write input files and launch the engine process."""
        bundle.work_dir.mkdir(parents=True, exist_ok=True)
        for filename, content in bundle.input_files.items():
            (bundle.work_dir / filename).write_text(content, encoding="utf-8")

        import os
        env = os.environ.copy()
        env.update(bundle.env_override)

        return subprocess.Popen(
            bundle.command,
            cwd=bundle.work_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            env=env,
        )

    @abstractmethod
    def parse_output(self, result: CalculationResult) -> CalculationResult:
        """Parse engine output files and populate result fields."""
        ...
