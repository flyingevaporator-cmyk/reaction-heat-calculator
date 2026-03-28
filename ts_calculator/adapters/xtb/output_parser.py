"""xTB output parsers."""
from __future__ import annotations
import re
from pathlib import Path
from typing import List, Optional, Tuple

from domain.models import Molecule, NEBData, CalculationResult, CalcStatus


def parse_neb_result(work_dir: Path, result: CalculationResult) -> CalculationResult:
    """Parse xTB NEB output to extract TS guess structure and path energies."""
    # xTB NEB writes xtbpath_MEP.xyz (all images concatenated)
    mep_file = work_dir / "xtbpath_MEP.xyz"
    ts_file = work_dir / "xtbpath_TS.xyz"

    if not mep_file.exists():
        result.status = CalcStatus.FAILED
        result.error_message = "xtbpath_MEP.xyz not found"
        return result

    images, energies = _read_mep_xyz(mep_file)
    if not images:
        result.status = CalcStatus.FAILED
        result.error_message = "Failed to parse NEB path"
        return result

    # Highest energy image → TS guess
    ts_idx = energies.index(max(energies))

    # TS structure (prefer dedicated file if exists)
    if ts_file.exists():
        ts_mol = Molecule.from_xyz_string(ts_file.read_text(encoding="utf-8"), name="ts_guess")
    else:
        ts_mol = images[ts_idx]

    result.molecule = ts_mol
    result.energy = energies[ts_idx]
    result.neb_data = NEBData(images=images, energies=energies, ts_image_index=ts_idx)
    result.status = CalcStatus.SUCCESS
    return result


def _read_mep_xyz(path: Path) -> Tuple[List[Molecule], List[float]]:
    """Read concatenated XYZ file from NEB path."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    images: List[Molecule] = []
    energies: List[float] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        try:
            n_atoms = int(line)
        except ValueError:
            i += 1
            continue
        comment = lines[i + 1] if i + 1 < len(lines) else ""
        # Try to extract energy from comment line (xTB writes "energy: X" or just a float)
        energy = _parse_energy_from_comment(comment)
        xyz_block = "\n".join(lines[i: i + n_atoms + 2])
        mol = Molecule.from_xyz_string(xyz_block, name=f"image_{len(images)}")
        images.append(mol)
        energies.append(energy)
        i += n_atoms + 2

    # Normalize energies relative to first image
    if energies:
        e0 = energies[0]
        energies = [e - e0 for e in energies]
    return images, energies


def _parse_energy_from_comment(comment: str) -> float:
    # xTB comment format: "SCF done     -10.123456" or just "-10.123456"
    m = re.search(r"[-+]?\d+\.\d+", comment)
    return float(m.group()) if m else 0.0


def parse_opt_result(work_dir: Path, result: CalculationResult) -> CalculationResult:
    """Parse xTB optimization output (xtbopt.xyz)."""
    opt_file = work_dir / "xtbopt.xyz"
    if not opt_file.exists():
        result.status = CalcStatus.FAILED
        result.error_message = "xtbopt.xyz not found"
        return result
    result.molecule = Molecule.from_xyz_string(
        opt_file.read_text(encoding="utf-8"), name="opt_structure"
    )
    result.energy = _parse_final_energy(work_dir / "xtb.out")
    result.status = CalcStatus.SUCCESS
    return result


def _parse_final_energy(log_path: Path) -> Optional[float]:
    if not log_path.exists():
        return None
    pattern = re.compile(r"TOTAL ENERGY\s+([-\d.]+)")
    energy = None
    for line in log_path.read_text(encoding="utf-8").splitlines():
        m = pattern.search(line)
        if m:
            energy = float(m.group(1))
    return energy
