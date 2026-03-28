"""Psi4 engine adapter."""
from __future__ import annotations
import shutil
from pathlib import Path
from typing import List, Optional

from adapters.base import EngineAdapterBase, InputBundle, CalcParams
from domain.models import Molecule, CalcType, CalculationResult, CalcStatus
from infrastructure.app_config import get_config
from . import input_writer, output_parser


class Psi4Adapter(EngineAdapterBase):
    engine_name = "psi4"

    def check_installation(self) -> bool:
        exe = get_config().get("engines", "psi4_python", default="psi4")
        return shutil.which(exe) is not None

    def get_supported_calc_types(self) -> List[CalcType]:
        return [CalcType.TS_OPT, CalcType.FREQUENCY, CalcType.IRC, CalcType.SINGLE_POINT, CalcType.OPT]

    def prepare_input(
        self,
        molecule: Molecule,
        params: CalcParams,
        work_dir: Path,
        aux_molecules: Optional[List[Molecule]] = None,
    ) -> InputBundle:
        work_dir.mkdir(parents=True, exist_ok=True)
        exe = get_config().get("engines", "psi4_python", default="psi4")

        psi4_input = input_writer.build_input(molecule, params)
        input_files = {
            "input.dat": psi4_input,
        }

        # Psi4 is invoked as: psi4 input.dat psi4.out -n <ncores>
        cmd = [exe, "input.dat", "psi4.out", "-n", str(params.n_cores)]
        if params.memory_gb:
            cmd += ["-m", f"{int(params.memory_gb * 1024)}mb"]

        return InputBundle(command=cmd, input_files=input_files, work_dir=work_dir)

    def parse_output(self, result: CalculationResult) -> CalculationResult:
        return output_parser.parse_result(Path(result.work_dir), result)
