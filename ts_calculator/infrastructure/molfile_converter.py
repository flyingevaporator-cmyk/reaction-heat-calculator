"""Convert 2D Molfile to 3D Molecule using RDKit."""
from __future__ import annotations

from domain.models import Molecule
from domain.models.molecule import Atom

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    _HAS_RDKIT = True
except ImportError:
    _HAS_RDKIT = False


class RDKitNotAvailableError(ImportError):
    """Raised when RDKit is required but not installed."""
    pass


def molfile_to_molecule(
    molfile: str,
    charge: int = 0,
    multiplicity: int = 1,
    name: str = "",
    add_hs: bool = True,
    optimize: bool = True,
) -> Molecule:
    """Convert a V2000/V3000 Molfile string to a Molecule with 3D coordinates.

    Uses RDKit's ETKDG distance geometry for 3D embedding, optionally
    followed by MMFF force-field optimization for a clean starting geometry.

    Parameters
    ----------
    molfile : str
        Molfile (V2000 or V3000) content, e.g. from Ketcher export.
    charge, multiplicity : int
        Electronic state.
    name : str
        Optional molecule name.
    add_hs : bool
        If True, add explicit hydrogens before embedding.
    optimize : bool
        If True, run MMFF optimization after embedding.

    Returns
    -------
    Molecule
        Molecule with 3D coordinates.

    Raises
    ------
    RDKitNotAvailableError
        If rdkit is not installed.
    ValueError
        If the molfile cannot be parsed or 3D embedding fails.
    """
    if not _HAS_RDKIT:
        raise RDKitNotAvailableError(
            "RDKit is required for 2D→3D conversion. "
            "Install with: pip install rdkit"
        )

    mol = Chem.MolFromMolBlock(molfile, sanitize=True, removeHs=False)
    if mol is None:
        raise ValueError("Molfile could not be parsed by RDKit.")

    if add_hs:
        mol = Chem.AddHs(mol)

    # 3D coordinate generation via ETKDG (distance geometry)
    params = AllChem.ETKDGv3()
    params.randomSeed = 42  # reproducibility
    result = AllChem.EmbedMolecule(mol, params)
    if result == -1:
        # Fallback: try without distance bounds
        result = AllChem.EmbedMolecule(mol, randomSeed=42)
        if result == -1:
            raise ValueError(
                "3D coordinate generation failed. "
                "Check that the molecule structure is valid."
            )

    # Optional MMFF optimization for cleaner geometry
    if optimize:
        try:
            AllChem.MMFFOptimizeMolecule(mol, maxIters=200)
        except Exception:
            pass  # proceed with unoptimized coords

    # Extract atoms
    conf = mol.GetConformer()
    atoms = []
    for i in range(mol.GetNumAtoms()):
        pos = conf.GetAtomPosition(i)
        symbol = mol.GetAtomWithIdx(i).GetSymbol()
        atoms.append(Atom(symbol=symbol, x=pos.x, y=pos.y, z=pos.z))

    return Molecule(
        atoms=tuple(atoms),
        charge=charge,
        multiplicity=multiplicity,
        name=name or "ketcher",
    )


def molfile_to_molecules(
    molfile: str,
    charge: int = 0,
    multiplicity: int = 1,
    add_hs: bool = True,
    optimize: bool = True,
) -> list[Molecule]:
    """Split a multi-fragment Molfile into individual 3D Molecules.

    If the Molfile contains disconnected fragments (A + B drawn in one
    Ketcher canvas), each fragment becomes a separate Molecule.
    Single-fragment Molfiles return a one-element list.
    """
    if not _HAS_RDKIT:
        raise RDKitNotAvailableError(
            "RDKit is required for 2D→3D conversion. "
            "Install with: pip install rdkit"
        )

    mol = Chem.MolFromMolBlock(molfile, sanitize=True, removeHs=False)
    if mol is None:
        raise ValueError("Molfile could not be parsed by RDKit.")

    # Split into disconnected fragments
    frags = Chem.GetMolFrags(mol, asMols=True, sanitizeFrags=True)
    if not frags:
        raise ValueError("No fragments found in Molfile.")

    molecules = []
    for i, frag in enumerate(frags):
        if add_hs:
            frag = Chem.AddHs(frag)

        params = AllChem.ETKDGv3()
        params.randomSeed = 42 + i
        result = AllChem.EmbedMolecule(frag, params)
        if result == -1:
            result = AllChem.EmbedMolecule(frag, randomSeed=42 + i)
            if result == -1:
                raise ValueError(
                    f"Fragment {i + 1}: 3D coordinate generation failed."
                )

        if optimize:
            try:
                AllChem.MMFFOptimizeMolecule(frag, maxIters=200)
            except Exception:
                pass

        conf = frag.GetConformer()
        atoms = []
        for j in range(frag.GetNumAtoms()):
            pos = conf.GetAtomPosition(j)
            symbol = frag.GetAtomWithIdx(j).GetSymbol()
            atoms.append(Atom(symbol=symbol, x=pos.x, y=pos.y, z=pos.z))

        name = f"fragment_{i + 1}" if len(frags) > 1 else "ketcher"
        molecules.append(Molecule(
            atoms=tuple(atoms),
            charge=charge,
            multiplicity=multiplicity,
            name=name,
        ))

    return molecules


def is_rdkit_available() -> bool:
    """Check if RDKit is installed and importable."""
    return _HAS_RDKIT
