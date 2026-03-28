"""Unit tests for Molecule model."""
from domain.models import Molecule

_H2_XYZ = """\
2
H2 molecule
H   0.000000   0.000000   0.000000
H   0.000000   0.000000   0.741000
"""


def test_from_xyz_string():
    mol = Molecule.from_xyz_string(_H2_XYZ)
    assert mol.n_atoms == 2
    assert mol.atoms[0].symbol == "H"
    assert abs(mol.atoms[1].z - 0.741) < 1e-6


def test_to_xyz_string_roundtrip():
    mol = Molecule.from_xyz_string(_H2_XYZ)
    xyz = mol.to_xyz_string()
    mol2 = Molecule.from_xyz_string(xyz)
    assert mol.n_atoms == mol2.n_atoms
    assert abs(mol.atoms[1].z - mol2.atoms[1].z) < 1e-6
