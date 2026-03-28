"""xTB engine adapter."""
from __future__ import annotations
import shutil
from pathlib import Path
from typing import List, Optional

from adapters.base import EngineAdapterBase, InputBundle, CalcParams
from domain.models import Molecule, CalcType, CalculationResult, CalcStatus
from infrastructure.app_config import get_config
from . import input_writer, output_parser


class XtbAdapter(EngineAdapterBase):
    engine_name = "xtb"

    def check_installation(self) -> bool:
        exe = get_config().get("engines", "xtb_path", default="xtb")
        return shutil.which(exe) is not None

    def get_supported_calc_types(self) -> List[CalcType]:
        return [CalcType.NEB, CalcType.OPT]

    def prepare_input(
        self,
        molecule: Molecule,
        params: CalcParams,
        work_dir: Path,
        aux_molecules: Optional[List[Molecule]] = None,
    ) -> InputBundle:
        work_dir.mkdir(parents=True, exist_ok=True)
        exe = get_config().get("engines", "xtb_path", default="xtb")

        if params.calc_type == CalcType.NEB:
            if not aux_molecules:
                raise ValueError("NEB requires aux_molecules=[product]")
            product = aux_molecules[0]
            n_images = params.extra.get("n_images", 12)
            input_files = {
                "reactant.xyz": molecule.to_xyz_string(comment="reactant"),
                "product.xyz": product.to_xyz_string(comment="product"),
            }
            # Write NEB input inline
            from adapters.xtb.input_writer import write_neb_input
            import io, contextlib
            neb_inp_path = work_dir / "xtb_neb.inp"
            # We write it directly since prepare_input is called before run()
            buf = {}
            neb_inp_path.parent.mkdir(parents=True, exist_ok=True)

            neb_inp_content = _build_neb_inp(params, n_images)
            input_files["xtb_neb.inp"] = neb_inp_content

            cmd = [
                exe, "reactant.xyz",
                "--path", "product.xyz",
                "--neb",
                "--nimages", str(n_images),
                "--input", "xtb_neb.inp",
            ]
            if params.n_cores > 1:
                cmd += ["--parallel", str(params.n_cores)]

        elif params.calc_type == CalcType.OPT:
            input_files = {"input.xyz": molecule.to_xyz_string()}
            cmd = [exe, "input.xyz", "--opt", "tight"]
            if params.n_cores > 1:
                cmd += ["--parallel", str(params.n_cores)]
        else:
            raise ValueError(f"xTB adapter does not support {params.calc_type}")

        return InputBundle(command=cmd, input_files=input_files, work_dir=work_dir)

    def parse_output(self, result: CalculationResult) -> CalculationResult:
        work_dir = Path(result.work_dir)
        if result.calc_type == CalcType.NEB:
            return output_parser.parse_neb_result(work_dir, result)
        elif result.calc_type == CalcType.OPT:
            return output_parser.parse_opt_result(work_dir, result)
        return result


def _build_neb_inp(params: CalcParams, n_images: int) -> str:
    extra = params.extra
    lines = [
        "$path",
        f"  nrun={extra.get('nrun', 1)}",
        f"  nopt={extra.get('nopt', 500)}",
        f"  anopt={extra.get('anopt', 10)}",
        f"  kpush={extra.get('kpush', 0.003)}",
        f"  kpull={extra.get('kpull', -0.015)}",
        f"  ppull={extra.get('ppull', 0.05)}",
        f"  alp={extra.get('alp', 1.2)}",
        "$end",
    ]
    return "\n".join(lines) + "\n"
