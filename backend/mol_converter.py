"""SMILES to 3D XYZ conversion using RDKit."""

from rdkit import Chem
from rdkit.Chem import AllChem, rdmolfiles


def smiles_to_xyz(smiles: str) -> str:
    """Convert SMILES string to XYZ block for xTB input.

    Workflow:
        1. Parse SMILES -> RDKit Mol
        2. Add explicit hydrogens
        3. Generate 3D conformer (ETKDGv3)
        4. Pre-optimize with MMFF94 (or UFF fallback)
        5. Export as XYZ block

    Args:
        smiles: A valid SMILES string.

    Returns:
        XYZ format string suitable for xTB input.

    Raises:
        ValueError: If SMILES is invalid or 3D embedding fails.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"RDKit could not parse SMILES: {smiles}")

    mol = Chem.AddHs(mol)

    # Generate 3D coordinates with ETKDGv3
    params = AllChem.ETKDGv3()
    params.randomSeed = 42
    result = AllChem.EmbedMolecule(mol, params)
    if result != 0:
        # Fallback: simpler embedding
        result = AllChem.EmbedMolecule(mol, randomSeed=42)
        if result != 0:
            raise ValueError(f"3D embedding failed for: {smiles}")

    # Pre-optimize geometry (gives xTB a better starting point)
    try:
        AllChem.MMFFOptimizeMolecule(mol, maxIters=200)
    except Exception:
        try:
            AllChem.UFFOptimizeMolecule(mol, maxIters=200)
        except Exception:
            pass  # Use unoptimized embedding as-is

    xyz_block = rdmolfiles.MolToXYZBlock(mol)
    return xyz_block


def canonical_smiles(smiles: str) -> str:
    """Return canonical SMILES for consistent cache keys.

    Args:
        smiles: Any valid SMILES string.

    Returns:
        Canonical SMILES string, or the original if parsing fails.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return smiles
    return Chem.MolToSmiles(mol)
