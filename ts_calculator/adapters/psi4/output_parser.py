"""Psi4 output parsers."""
from __future__ import annotations
import re
from pathlib import Path
from typing import List, Optional, Tuple

from domain.models import (
    Molecule, Atom, CalcType, CalcStatus,
    CalculationResult, FrequencyData, IRCData,
)


def parse_result(work_dir: Path, result: CalculationResult) -> CalculationResult:
    log = work_dir / "psi4.out"
    if not log.exists():
        result.status = CalcStatus.FAILED
        result.error_message = "psi4.out not found"
        return result

    text = log.read_text(encoding="utf-8", errors="replace")

    if "Psi4 exiting successfully" not in text:
        result.status = CalcStatus.FAILED
        result.error_message = _extract_error(text)
        return result

    if result.calc_type == CalcType.TS_OPT:
        _parse_ts_opt(text, work_dir, result)
    elif result.calc_type == CalcType.FREQUENCY:
        _parse_frequency(text, result)
    elif result.calc_type == CalcType.IRC:
        _parse_irc(text, work_dir, result)
    elif result.calc_type == CalcType.SINGLE_POINT:
        _parse_energy(text, result)

    result.status = CalcStatus.SUCCESS
    return result


def _parse_ts_opt(text: str, work_dir: Path, result: CalculationResult) -> None:
    result.energy = _extract_final_energy(text)
    # Optimized geometry is written to psi4_opt.xyz or parsed from output
    opt_xyz = work_dir / "psi4_opt.xyz"
    if opt_xyz.exists():
        result.molecule = Molecule.from_xyz_string(opt_xyz.read_text(encoding="utf-8"), name="ts_opt")
    else:
        result.molecule = _extract_last_geometry(text, result.molecule)


def _parse_frequency(text: str, result: CalculationResult) -> None:
    result.energy = _extract_final_energy(text)
    freqs = _extract_frequencies(text)
    zpe = _extract_zpe(text)
    result.frequency_data = FrequencyData(frequencies=freqs, zero_point_energy=zpe)


def _parse_irc(text: str, work_dir: Path, result: CalculationResult) -> None:
    # Parse IRC path from output
    forward_mols, forward_e = _extract_irc_path(text, "forward")
    reverse_mols, reverse_e = _extract_irc_path(text, "reverse")
    result.irc_data = IRCData(
        forward_path=forward_mols,
        reverse_path=reverse_mols,
        forward_energies=forward_e,
        reverse_energies=reverse_e,
    )


def _parse_energy(text: str, result: CalculationResult) -> None:
    result.energy = _extract_final_energy(text)


# --- Helper functions ---

def _extract_final_energy(text: str) -> Optional[float]:
    """Extract the last total energy from Psi4 output."""
    pattern = re.compile(r"Total Energy\s*=\s*([-\d.]+)", re.IGNORECASE)
    matches = pattern.findall(text)
    return float(matches[-1]) if matches else None


def _extract_frequencies(text: str) -> List[float]:
    """Extract vibrational frequencies (cm^-1) from Psi4 output."""
    freqs: List[float] = []
    pattern = re.compile(r"Freq\s*\[cm\^-1\]\s*=\s*([-\d.]+(?:\s+[-\d.]+)*)")
    for m in pattern.finditer(text):
        freqs.extend(float(v) for v in m.group(1).split())
    # Also handle imaginary frequencies marked as negative
    imag_pattern = re.compile(r"(-?\d+\.\d+)i?\s*cm\^-1")
    if not freqs:
        freqs = [float(m.group(1)) for m in imag_pattern.finditer(text)]
    return freqs


def _extract_zpe(text: str) -> Optional[float]:
    m = re.search(r"Zero-point correction=\s*([-\d.]+)", text)
    return float(m.group(1)) if m else None


def _extract_last_geometry(text: str, fallback: Optional[Molecule]) -> Optional[Molecule]:
    """Extract the last geometry block from Psi4 output."""
    # Psi4 prints geometry as a Z-matrix or Cartesian block
    pattern = re.compile(
        r"Center\s+X\s+Y\s+Z.*?\n((?:\s+\w+\s+[-\d.]+\s+[-\d.]+\s+[-\d.]+\n)+)",
        re.DOTALL,
    )
    matches = list(pattern.finditer(text))
    if not matches:
        return fallback
    block = matches[-1].group(1)
    atoms = []
    for line in block.strip().splitlines():
        parts = line.split()
        if len(parts) >= 4:
            atoms.append(Atom(symbol=parts[0], x=float(parts[1]),
                               y=float(parts[2]), z=float(parts[3])))
    if not atoms:
        return fallback
    return Molecule(atoms=tuple(atoms), name="ts_opt")


def _extract_irc_path(text: str, direction: str) -> Tuple[List[Molecule], List[float]]:
    """Placeholder: parse IRC geometries from Psi4 output."""
    # Psi4 writes IRC geometries inline; full parsing is complex.
    # Returns empty lists — can be extended per Psi4 version output format.
    return [], []


def _extract_error(text: str) -> str:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "PsiException" in line or "Error" in line:
            return "\n".join(lines[max(0, i - 1): i + 3])
    return "Unknown error (check psi4.out)"
