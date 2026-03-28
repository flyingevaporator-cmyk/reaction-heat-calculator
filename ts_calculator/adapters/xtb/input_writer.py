"""xTB input file generation."""
from __future__ import annotations
from pathlib import Path
from typing import List, Optional

from domain.models import Molecule, CalcType
from adapters.base import CalcParams


def write_xyz(molecule: Molecule, path: Path) -> None:
    path.write_text(molecule.to_xyz_string(), encoding="utf-8")


def build_neb_command(
    reactant_file: str,
    product_file: str,
    params: CalcParams,
    n_images: int = 12,
) -> List[str]:
    """Build xTB NEB command."""
    cmd = [
        "xtb", reactant_file,
        "--path", product_file,
        "--neb",
        f"--nimages", str(n_images),
        "--input", "xtb_neb.inp",
    ]
    if params.n_cores > 1:
        cmd += ["--parallel", str(params.n_cores)]
    return cmd


def write_neb_input(params: CalcParams, path: Path) -> None:
    """Write $path block for NEB settings."""
    extra = params.extra
    content = "$path\n"
    content += f"  nrun={extra.get('nrun', 1)}\n"
    content += f"  nopt={extra.get('nopt', 500)}\n"
    content += f"  anopt={extra.get('anopt', 10)}\n"
    content += f"  kpush={extra.get('kpush', 0.003)}\n"
    content += f"  kpull={extra.get('kpull', -0.015)}\n"
    content += f"  ppull={extra.get('ppull', 0.05)}\n"
    content += f"  alp={extra.get('alp', 1.2)}\n"
    content += "$end\n"
    path.write_text(content, encoding="utf-8")


def build_tsopt_command(xyz_file: str, params: CalcParams) -> List[str]:
    """Build xTB TS optimization command."""
    cmd = ["xtb", xyz_file, "--ohess", "--input", "xtb_ts.inp"]
    if params.n_cores > 1:
        cmd += ["--parallel", str(params.n_cores)]
    return cmd


def write_tsopt_input(params: CalcParams, path: Path) -> None:
    content = "$opt\n"
    content += "  optlevel=tight\n"
    content += "$end\n"
    path.write_text(content, encoding="utf-8")
