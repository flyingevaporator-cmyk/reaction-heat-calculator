"""PySCF output parser."""
from __future__ import annotations
import json
from pathlib import Path

from domain.models import CalculationResult, CalcStatus


def parse_result(work_dir: Path, result: CalculationResult) -> CalculationResult:
    json_file = work_dir / "pyscf_result.json"
    log_file = work_dir / "pyscf.out"

    if not json_file.exists():
        result.status = CalcStatus.FAILED
        result.error_message = "pyscf_result.json not found — calculation may have crashed"
        if log_file.exists():
            tail = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
            result.error_message += "\n" + "\n".join(tail[-20:])
        return result

    data = json.loads(json_file.read_text(encoding="utf-8"))
    result.energy = data.get("energy")
    result.status = CalcStatus.SUCCESS
    return result
