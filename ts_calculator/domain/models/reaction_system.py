"""Reaction system data model."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from .molecule import Molecule


@dataclass
class ReactionSystem:
    reactants: List[Molecule]
    products: List[Molecule]
    solvent: Optional[str] = None      # e.g. "water", "thf"
    temperature: float = 298.15        # K

    @property
    def reactant(self) -> Molecule:
        """Convenience accessor for single-reactant reactions."""
        if len(self.reactants) != 1:
            raise ValueError("Use .reactants for multi-reactant systems")
        return self.reactants[0]

    @property
    def product(self) -> Molecule:
        """Convenience accessor for single-product reactions."""
        if len(self.products) != 1:
            raise ValueError("Use .products for multi-product systems")
        return self.products[0]
