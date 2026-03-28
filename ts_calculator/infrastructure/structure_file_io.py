"""Read/write molecular structure files (XYZ, SDF, MOL2)."""
from __future__ import annotations
from pathlib import Path
from typing import List

from domain.models import Molecule, Atom


class StructureFileIO:

    @staticmethod
    def read(path: Path) -> Molecule:
        suffix = path.suffix.lower()
        if suffix == ".xyz":
            return StructureFileIO._read_xyz(path)
        elif suffix in (".sdf", ".mol"):
            return StructureFileIO._read_sdf(path)
        elif suffix == ".mol2":
            return StructureFileIO._read_mol2(path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

    @staticmethod
    def write_xyz(molecule: Molecule, path: Path, comment: str = "") -> None:
        path.write_text(molecule.to_xyz_string(comment), encoding="utf-8")

    # --- Internal readers ---

    @staticmethod
    def _read_xyz(path: Path) -> Molecule:
        text = path.read_text(encoding="utf-8")
        return Molecule.from_xyz_string(text, name=path.stem)

    @staticmethod
    def _read_sdf(path: Path) -> Molecule:
        """Minimal SDF/MOL reader (V2000 only)."""
        lines = path.read_text(encoding="utf-8").splitlines()
        # counts line is line index 3
        counts = lines[3].split()
        n_atoms = int(counts[0])
        atoms: List[Atom] = []
        for i in range(4, 4 + n_atoms):
            parts = lines[i].split()
            atoms.append(Atom(symbol=parts[3], x=float(parts[0]),
                              y=float(parts[1]), z=float(parts[2])))
        return Molecule(atoms=tuple(atoms), name=path.stem)

    @staticmethod
    def _read_mol2(path: Path) -> Molecule:
        """Minimal MOL2 reader."""
        text = path.read_text(encoding="utf-8")
        atoms: List[Atom] = []
        in_atom_section = False
        for line in text.splitlines():
            if "@<TRIPOS>ATOM" in line:
                in_atom_section = True
                continue
            if in_atom_section:
                if line.startswith("@"):
                    break
                parts = line.split()
                if len(parts) < 5:
                    continue
                # parts: id name x y z type ...
                symbol = parts[5].split(".")[0] if len(parts) > 5 else parts[1]
                atoms.append(Atom(symbol=symbol, x=float(parts[2]),
                                  y=float(parts[3]), z=float(parts[4])))
        return Molecule(atoms=tuple(atoms), name=path.stem)
