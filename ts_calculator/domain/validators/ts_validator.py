"""Validates transition state calculation results."""
from __future__ import annotations
from typing import List

from domain.models import FrequencyData, IRCData, Molecule


class TSValidator:
    def check_frequency(self, freq_data: FrequencyData) -> List[str]:
        """Return list of warning strings (empty = valid TS)."""
        warnings = []
        n_imag = freq_data.n_imaginary
        if n_imag == 0:
            warnings.append("虚振動数が0個です。この構造は極小点（反応物・生成物）です。")
        elif n_imag > 1:
            warnings.append(
                f"虚振動数が{n_imag}個検出されました（正常なTSは1個）。"
                "構造を確認してください。"
            )
        return warnings

    def check_irc(
        self,
        irc_data: IRCData,
        reactant: Molecule,
        product: Molecule,
        rmsd_threshold: float = 0.5,
    ) -> List[str]:
        """Check IRC endpoints connect to expected reactant/product."""
        warnings = []
        if not irc_data.forward_path or not irc_data.reverse_path:
            warnings.append("IRCパスが空です。計算が正常に完了したか確認してください。")
            return warnings

        fwd_end = irc_data.forward_path[-1]
        rev_end = irc_data.reverse_path[-1]

        if _rmsd(fwd_end, reactant) > rmsd_threshold and _rmsd(fwd_end, product) > rmsd_threshold:
            warnings.append("IRC順方向の終点が反応物・生成物のいずれにも一致しません。")
        if _rmsd(rev_end, reactant) > rmsd_threshold and _rmsd(rev_end, product) > rmsd_threshold:
            warnings.append("IRC逆方向の終点が反応物・生成物のいずれにも一致しません。")

        return warnings


def _rmsd(mol_a: Molecule, mol_b: Molecule) -> float:
    """Naive RMSD (no alignment) for same-atom-order molecules."""
    if mol_a.n_atoms != mol_b.n_atoms:
        return float("inf")
    total = sum(
        (a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2
        for a, b in zip(mol_a.atoms, mol_b.atoms)
    )
    return (total / mol_a.n_atoms) ** 0.5
