"""Psi4 input file generation."""
from __future__ import annotations
from domain.models import Molecule, CalcType
from adapters.base import CalcParams

_TS_OPT_TEMPLATE = """\
molecule mol {{
  {charge} {multiplicity}
{coords}
}}

set {{
  basis {basis}
  reference {reference}
  scf_type df
  maxiter 200
  e_convergence 1e-8
  d_convergence 1e-8
  {extra_globals}
}}

{method_setup}

optimize('{method}', engine='optking')
"""

_FREQ_TEMPLATE = """\
molecule mol {{
  {charge} {multiplicity}
{coords}
}}

set {{
  basis {basis}
  reference {reference}
  scf_type df
  {extra_globals}
}}

{method_setup}

frequencies('{method}')
"""

_IRC_TEMPLATE = """\
molecule mol {{
  {charge} {multiplicity}
{coords}
}}

set {{
  basis {basis}
  reference {reference}
  scf_type df
  {extra_globals}
}}

set optking {{
  irc_direction forward
  irc_step_size 0.1
  irc_points {irc_points}
}}

{method_setup}

irc('{method}')
"""

_SP_TEMPLATE = """\
molecule mol {{
  {charge} {multiplicity}
{coords}
}}

set {{
  basis {basis}
  reference {reference}
  scf_type df
  {extra_globals}
}}

{method_setup}

energy('{method}')
"""


def _format_coords(mol: Molecule) -> str:
    return "\n".join(
        f"  {a.symbol:4s}  {a.x:14.8f}  {a.y:14.8f}  {a.z:14.8f}"
        for a in mol.atoms
    )


def _reference(multiplicity: int) -> str:
    return "uhf" if multiplicity > 1 else "rhf"


def _method_setup(method: str, basis: str) -> str:
    """Additional set blocks needed for specific methods."""
    m = method.lower()
    if "d3" in m or "d3bj" in m:
        return ""  # Psi4 handles D3 via method name e.g. b3lyp-d3bj
    if m in ("mp2", "ri-mp2"):
        return f"set mp2_type df\n"
    return ""


def build_input(mol: Molecule, params: CalcParams) -> str:
    basis = params.basis or "6-31g(d)"
    coords = _format_coords(mol)
    ref = _reference(mol.multiplicity)
    extra = params.extra.get("extra_globals", "")
    method = params.method
    setup = _method_setup(method, basis)

    if params.calc_type == CalcType.TS_OPT:
        # Force Hessian at first step for TS optimization
        extra_for_tsopt = "full_hess_every 0\n  " + extra
        return _TS_OPT_TEMPLATE.format(
            charge=mol.charge, multiplicity=mol.multiplicity,
            coords=coords, basis=basis, reference=ref,
            extra_globals=extra_for_tsopt,
            method_setup=setup, method=method,
        )
    elif params.calc_type == CalcType.FREQUENCY:
        return _FREQ_TEMPLATE.format(
            charge=mol.charge, multiplicity=mol.multiplicity,
            coords=coords, basis=basis, reference=ref,
            extra_globals=extra, method_setup=setup, method=method,
        )
    elif params.calc_type == CalcType.IRC:
        irc_points = params.extra.get("irc_points", 20)
        return _IRC_TEMPLATE.format(
            charge=mol.charge, multiplicity=mol.multiplicity,
            coords=coords, basis=basis, reference=ref,
            extra_globals=extra, method_setup=setup,
            method=method, irc_points=irc_points,
        )
    elif params.calc_type == CalcType.SINGLE_POINT:
        return _SP_TEMPLATE.format(
            charge=mol.charge, multiplicity=mol.multiplicity,
            coords=coords, basis=basis, reference=ref,
            extra_globals=extra, method_setup=setup, method=method,
        )
    else:
        raise ValueError(f"Psi4 adapter does not support {params.calc_type}")
