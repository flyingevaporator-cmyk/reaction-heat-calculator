"""FastAPI backend for reaction heat energy calculation."""

import asyncio
import json
import uuid
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from mol_converter import canonical_smiles, smiles_to_xyz
from xtb_runner import run_xtb_ohess

# --- Constants ---
HARTREE_TO_KJMOL = 2625.5

# --- App Setup ---
app = FastAPI(title="Reaction Heat Energy Calculator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-memory cache (canonical SMILES -> result) ---
enthalpy_cache: dict[str, dict] = {}


# --- Request/Response Models ---
class MoleculeInput(BaseModel):
    smiles: str
    role: str  # "reactant" or "product"
    coefficient: int


class CalculateRequest(BaseModel):
    molecules: list[MoleculeInput]


class MoleculeResult(BaseModel):
    smiles: str
    canonical_smiles: str
    role: str
    coefficient: int
    enthalpy_hartree: Optional[float] = None
    total_energy_hartree: Optional[float] = None
    status: str  # "success" or "error"
    error: Optional[str] = None


class CalculateResponse(BaseModel):
    status: str  # "success", "partial_failure", "error"
    reaction_enthalpy_hartree: Optional[float] = None
    reaction_enthalpy_kjmol: Optional[float] = None
    is_exothermic: Optional[bool] = None
    molecule_results: list[MoleculeResult] = []


# --- Core computation ---
def compute_molecule(smiles: str) -> dict:
    """Compute enthalpy for a single molecule.

    Steps:
        1. Convert SMILES to 3D XYZ via RDKit
        2. Run xTB --ohess
        3. Return parsed enthalpy
    """
    canon = canonical_smiles(smiles)

    # Check cache
    if canon in enthalpy_cache:
        return enthalpy_cache[canon]

    # SMILES -> XYZ
    try:
        xyz_block = smiles_to_xyz(canon)
    except ValueError as e:
        return {
            "status": "error",
            "error": str(e),
            "enthalpy_hartree": None,
            "total_energy_hartree": None,
        }

    # Run xTB
    result = run_xtb_ohess(xyz_block)

    # Cache successful results
    if result["status"] == "success":
        enthalpy_cache[canon] = result

    return result


def compute_reaction_enthalpy(
    molecules: list[MoleculeInput], results: dict[str, dict]
) -> tuple[Optional[float], Optional[float], Optional[bool]]:
    """Compute reaction enthalpy from individual molecule enthalpies.

    Formula:
        DeltaH_rxn = sum(coeff * H(T) for products)
                   - sum(coeff * H(T) for reactants)

    Returns:
        (delta_h_hartree, delta_h_kjmol, is_exothermic) or (None, None, None) on failure
    """
    h_products = 0.0
    h_reactants = 0.0

    for mol in molecules:
        canon = canonical_smiles(mol.smiles)
        mol_result = results.get(canon)
        if mol_result is None or mol_result["status"] != "success":
            return None, None, None

        enthalpy = mol_result["enthalpy_hartree"]
        if enthalpy is None:
            return None, None, None

        if mol.role == "product":
            h_products += mol.coefficient * enthalpy
        else:
            h_reactants += mol.coefficient * enthalpy

    delta_h_hartree = h_products - h_reactants
    delta_h_kjmol = delta_h_hartree * HARTREE_TO_KJMOL
    is_exothermic = delta_h_kjmol < 0

    return delta_h_hartree, delta_h_kjmol, is_exothermic


# --- API Endpoints ---


@app.post("/api/calculate")
async def calculate(req: CalculateRequest):
    """Calculate reaction enthalpy with SSE progress streaming.

    Returns a Server-Sent Events stream:
        - progress events as each molecule is computed
        - final result event with the reaction enthalpy
    """

    async def event_stream():
        # Deduplicate molecules by canonical SMILES
        unique_smiles = list({canonical_smiles(m.smiles) for m in req.molecules})
        total = len(unique_smiles)

        results: dict[str, dict] = {}

        for i, smi in enumerate(unique_smiles):
            # Send progress event
            progress = {
                "type": "progress",
                "completed": i,
                "total": total,
                "current_smiles": smi,
            }
            yield f"data: {json.dumps(progress)}\n\n"

            # Compute (run in thread to avoid blocking)
            result = await asyncio.to_thread(compute_molecule, smi)
            results[smi] = result

        # Compute reaction enthalpy
        delta_h, delta_h_kj, is_exo = compute_reaction_enthalpy(
            req.molecules, results
        )

        # Build molecule results
        molecule_results = []
        for mol in req.molecules:
            canon = canonical_smiles(mol.smiles)
            mol_result = results.get(canon, {})
            molecule_results.append(
                {
                    "smiles": mol.smiles,
                    "canonical_smiles": canon,
                    "role": mol.role,
                    "coefficient": mol.coefficient,
                    "enthalpy_hartree": mol_result.get("enthalpy_hartree"),
                    "total_energy_hartree": mol_result.get("total_energy_hartree"),
                    "status": mol_result.get("status", "error"),
                    "error": mol_result.get("error"),
                }
            )

        # Determine overall status
        all_success = all(r.get("status") == "success" for r in results.values())
        any_success = any(r.get("status") == "success" for r in results.values())

        if all_success and delta_h is not None:
            status = "success"
        elif any_success:
            status = "partial_failure"
        else:
            status = "error"

        # Send final result
        final = {
            "type": "result",
            "status": status,
            "reaction_enthalpy_hartree": delta_h,
            "reaction_enthalpy_kjmol": round(delta_h_kj, 2) if delta_h_kj is not None else None,
            "is_exothermic": is_exo,
            "molecule_results": molecule_results,
        }
        yield f"data: {json.dumps(final)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/api/calculate-sync")
async def calculate_sync(req: CalculateRequest) -> CalculateResponse:
    """Synchronous calculation endpoint (simpler, no streaming).

    Blocks until all molecules are computed, then returns the full result.
    """
    unique_smiles = list({canonical_smiles(m.smiles) for m in req.molecules})
    results: dict[str, dict] = {}

    for smi in unique_smiles:
        result = await asyncio.to_thread(compute_molecule, smi)
        results[smi] = result

    delta_h, delta_h_kj, is_exo = compute_reaction_enthalpy(req.molecules, results)

    molecule_results = []
    for mol in req.molecules:
        canon = canonical_smiles(mol.smiles)
        mol_result = results.get(canon, {})
        molecule_results.append(
            MoleculeResult(
                smiles=mol.smiles,
                canonical_smiles=canon,
                role=mol.role,
                coefficient=mol.coefficient,
                enthalpy_hartree=mol_result.get("enthalpy_hartree"),
                total_energy_hartree=mol_result.get("total_energy_hartree"),
                status=mol_result.get("status", "error"),
                error=mol_result.get("error"),
            )
        )

    all_success = all(r.get("status") == "success" for r in results.values())
    any_success = any(r.get("status") == "success" for r in results.values())

    if all_success and delta_h is not None:
        status = "success"
    elif any_success:
        status = "partial_failure"
    else:
        status = "error"

    return CalculateResponse(
        status=status,
        reaction_enthalpy_hartree=delta_h,
        reaction_enthalpy_kjmol=round(delta_h_kj, 2) if delta_h_kj is not None else None,
        is_exothermic=is_exo,
        molecule_results=molecule_results,
    )


@app.get("/api/cache")
async def get_cache():
    """Return cached molecule results (for debugging)."""
    return {
        "cache_size": len(enthalpy_cache),
        "entries": {
            smi: {
                "enthalpy_hartree": data.get("enthalpy_hartree"),
                "total_energy_hartree": data.get("total_energy_hartree"),
            }
            for smi, data in enthalpy_cache.items()
        },
    }


@app.delete("/api/cache")
async def clear_cache():
    """Clear the enthalpy cache."""
    enthalpy_cache.clear()
    return {"status": "cleared"}


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
