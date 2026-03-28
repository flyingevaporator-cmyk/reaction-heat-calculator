"""xTB execution and output parsing for enthalpy calculations."""

import os
import re
import subprocess
import tempfile


def run_xtb_ohess(xyz_block: str, timeout: int = 300) -> dict:
    """Run xTB geometry optimization + frequency calculation.

    Executes `xtb molecule.xyz --ohess` in a temporary directory,
    then parses the output for thermochemical data.

    Args:
        xyz_block: XYZ format string (from RDKit).
        timeout: Maximum execution time in seconds.

    Returns:
        dict with keys:
            - status: "success" or "error"
            - enthalpy_hartree: float or None (H(T)/Eh at 298.15 K)
            - total_energy_hartree: float or None (electronic energy)
            - error: error message string or None
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        xyz_path = os.path.join(tmpdir, "molecule.xyz")
        with open(xyz_path, "w") as f:
            f.write(xyz_block)

        try:
            result = subprocess.run(
                ["xtb", xyz_path, "--ohess"],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmpdir,
            )
        except FileNotFoundError:
            return {
                "status": "error",
                "error": "xTB not found. Please install xTB (conda install conda-forge::xtb)",
                "enthalpy_hartree": None,
                "total_energy_hartree": None,
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": f"xTB timed out after {timeout}s",
                "enthalpy_hartree": None,
                "total_energy_hartree": None,
            }

        output = result.stdout

        # Check for xTB errors
        if result.returncode != 0:
            error_msg = result.stderr[-1000:] if result.stderr else "Unknown xTB error"
            return {
                "status": "error",
                "error": f"xTB exited with code {result.returncode}: {error_msg}",
                "enthalpy_hartree": None,
                "total_energy_hartree": None,
            }

        enthalpy = parse_enthalpy(output)
        total_energy = parse_total_energy(output)

        if enthalpy is None:
            return {
                "status": "error",
                "error": "Could not parse enthalpy from xTB output",
                "enthalpy_hartree": None,
                "total_energy_hartree": total_energy,
                "raw_output_tail": output[-2000:],
            }

        return {
            "status": "success",
            "enthalpy_hartree": enthalpy,
            "total_energy_hartree": total_energy,
            "error": None,
        }


def parse_enthalpy(output: str) -> float | None:
    """Parse TOTAL ENTHALPY from xTB output.

    Looks for the line:
        | TOTAL ENTHALPY          -X.XXXXXX Eh   |

    Args:
        output: Full xTB stdout string.

    Returns:
        Enthalpy value in Hartree, or None if not found.
    """
    # Primary: look for TOTAL ENTHALPY in the summary block
    match = re.search(r"TOTAL ENTHALPY\s+([-\d.]+)\s+Eh", output)
    if match:
        return float(match.group(1))

    # Fallback: parse from thermochemistry table
    # Table format:
    #   T/K    H(0)-H(T)+PV    H(T)/Eh    T*S/Eh    G(T)/Eh
    #   298.15  0.xxE-xx       -x.xxE+xx   ...       ...
    lines = output.split("\n")
    for i, line in enumerate(lines):
        if "H(T)/Eh" in line and "T/K" in line:
            for j in range(i + 1, min(i + 20, len(lines))):
                data_line = lines[j].strip()
                if not data_line or data_line.startswith("-"):
                    continue
                parts = data_line.split()
                if len(parts) >= 4:
                    try:
                        temp = float(parts[0])
                        if abs(temp - 298.15) < 0.1:
                            return float(parts[2])  # H(T)/Eh column
                    except ValueError:
                        continue

    return None


def parse_total_energy(output: str) -> float | None:
    """Parse TOTAL ENERGY from xTB summary block.

    Looks for:
        | TOTAL ENERGY    -X.XXXXXX Eh   |

    Args:
        output: Full xTB stdout string.

    Returns:
        Total energy in Hartree, or None if not found.
    """
    match = re.search(r"TOTAL ENERGY\s+([-\d.]+)\s+Eh", output)
    if match:
        return float(match.group(1))
    return None


def parse_free_energy(output: str) -> float | None:
    """Parse TOTAL FREE ENERGY from xTB summary block.

    Looks for:
        | TOTAL FREE ENERGY    -X.XXXXXX Eh   |

    Args:
        output: Full xTB stdout string.

    Returns:
        Gibbs free energy in Hartree, or None if not found.
    """
    match = re.search(r"TOTAL FREE ENERGY\s+([-\d.]+)\s+Eh", output)
    if match:
        return float(match.group(1))
    return None
