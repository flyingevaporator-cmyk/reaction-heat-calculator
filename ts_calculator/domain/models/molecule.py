"""Molecule data model."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass(frozen=True)
class Atom:
    symbol: str
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Molecule:
    atoms: Tuple[Atom, ...]
    charge: int = 0
    multiplicity: int = 1
    name: str = ""

    @classmethod
    def from_xyz_string(cls, xyz: str, charge: int = 0, multiplicity: int = 1, name: str = "") -> "Molecule":
        """Parse XYZ format string (with or without header lines)."""
        lines = xyz.strip().splitlines()
        # Skip count line and comment line if present
        start = 0
        if lines and lines[0].strip().isdigit():
            start = 2  # skip atom-count line + comment line
        atoms = []
        for line in lines[start:]:
            parts = line.split()
            if len(parts) < 4:
                continue
            try:
                atoms.append(Atom(symbol=parts[0], x=float(parts[1]), y=float(parts[2]), z=float(parts[3])))
            except ValueError:
                continue
        return cls(atoms=tuple(atoms), charge=charge, multiplicity=multiplicity, name=name)

    def to_xyz_string(self, comment: str = "") -> str:
        """Serialize to XYZ format string."""
        lines = [str(len(self.atoms)), comment or self.name]
        for a in self.atoms:
            lines.append(f"{a.symbol:4s}  {a.x:14.8f}  {a.y:14.8f}  {a.z:14.8f}")
        return "\n".join(lines) + "\n"

    @property
    def n_atoms(self) -> int:
        return len(self.atoms)
