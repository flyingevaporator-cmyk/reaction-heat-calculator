"""PySCF engine adapter (subprocess-based for GUI safety)."""
from __future__ import annotations
import shutil
import sys
from pathlib import Path
from typing import List, Optional

from adapters.base import EngineAdapterBase, InputBundle, CalcParams
from domain.models import Molecule, CalcType, CalculationResult, CalcStatus
from . import output_parser


_PYSCF_SCRIPT_TEMPLATE = '''\
import sys, json
from pyscf import gto, scf, mp, cc, dft

# --- Molecule ---
mol = gto.Mole()
mol.atom = """{atom_block}"""
mol.charge = {charge}
mol.spin = {spin}
mol.basis = "{basis}"
mol.verbose = 4
mol.output = "pyscf.out"
mol.build()

# --- Method ---
method = "{method}"
results = {{}}

if method in ("dft", "rks", "uks"):
    from pyscf import dft as _dft
    mf = _dft.RKS(mol) if mol.spin == 0 else _dft.UKS(mol)
    mf.xc = "{xc}"
    mf.kernel()
    results["energy"] = float(mf.e_tot)

elif method == "mp2":
    mf = scf.RHF(mol) if mol.spin == 0 else scf.UHF(mol)
    mf.kernel()
    mp2 = mp.MP2(mf)
    mp2.kernel()
    results["energy"] = float(mf.e_tot + mp2.e_corr)

elif method in ("ccsd", "ccsd(t)"):
    mf = scf.RHF(mol) if mol.spin == 0 else scf.UHF(mol)
    mf.kernel()
    ccsd = cc.CCSD(mf)
    ccsd.kernel()
    e_ccsd = mf.e_tot + ccsd.e_corr
    if method == "ccsd(t)":
        e_t = ccsd.ccsd_t()
        results["energy"] = float(e_ccsd + e_t)
    else:
        results["energy"] = float(e_ccsd)

with open("pyscf_result.json", "w") as f:
    json.dump(results, f)

print("PySCF calculation completed successfully.")
'''


class PySCFAdapter(EngineAdapterBase):
    engine_name = "pyscf"

    def check_installation(self) -> bool:
        try:
            import importlib
            return importlib.util.find_spec("pyscf") is not None
        except Exception:
            return False

    def get_supported_calc_types(self) -> List[CalcType]:
        return [CalcType.SINGLE_POINT]

    def prepare_input(
        self,
        molecule: Molecule,
        params: CalcParams,
        work_dir: Path,
        aux_molecules: Optional[List[Molecule]] = None,
    ) -> InputBundle:
        work_dir.mkdir(parents=True, exist_ok=True)

        atom_block = "\n".join(
            f"{a.symbol} {a.x:.8f} {a.y:.8f} {a.z:.8f}" for a in molecule.atoms
        )
        spin = molecule.multiplicity - 1
        method = params.method.lower()
        xc = params.extra.get("xc", "b3lyp")
        basis = params.basis or "cc-pvtz"

        script = _PYSCF_SCRIPT_TEMPLATE.format(
            atom_block=atom_block,
            charge=molecule.charge,
            spin=spin,
            basis=basis,
            method=method,
            xc=xc,
        )

        input_files = {"pyscf_calc.py": script}
        cmd = [sys.executable, "pyscf_calc.py"]

        return InputBundle(command=cmd, input_files=input_files, work_dir=work_dir)

    def parse_output(self, result: CalculationResult) -> CalculationResult:
        return output_parser.parse_result(Path(result.work_dir), result)
