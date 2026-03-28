"""WorkflowSession: holds all state for one TS calculation run."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Any

from domain.models import Molecule, ReactionSystem, CalculationResult, CalcType, CalcStatus


class StepStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    SUCCESS = auto()
    FAILED = auto()
    SKIPPED = auto()


@dataclass
class WorkflowStep:
    name: str
    calc_type: CalcType
    engine: str
    params: Dict[str, Any]           # serializable param dict
    enabled: bool = True
    status: StepStatus = StepStatus.PENDING
    result: Optional[CalculationResult] = None
    work_dir: Optional[str] = None


@dataclass
class WorkflowSession:
    session_id: str
    reaction_system: ReactionSystem
    steps: List[WorkflowStep]
    session_dir: str
    name: str = ""
    completed: bool = False

    def step_by_name(self, name: str) -> Optional[WorkflowStep]:
        return next((s for s in self.steps if s.name == name), None)

    def last_successful_molecule(self) -> Optional[Molecule]:
        """Return the most recent optimized structure from completed steps."""
        for step in reversed(self.steps):
            if step.status == StepStatus.SUCCESS and step.result and step.result.molecule:
                return step.result.molecule
        return self.reaction_system.reactants[0] if self.reaction_system.reactants else None

    # --- Serialization ---

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "name": self.name,
            "session_dir": self.session_dir,
            "completed": self.completed,
            "reaction_system": {
                "reactants": [_mol_to_dict(m) for m in self.reaction_system.reactants],
                "products": [_mol_to_dict(m) for m in self.reaction_system.products],
                "solvent": self.reaction_system.solvent,
                "temperature": self.reaction_system.temperature,
            },
            "steps": [_step_to_dict(s) for s in self.steps],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowSession":
        rs_data = data["reaction_system"]
        rs = ReactionSystem(
            reactants=[_mol_from_dict(m) for m in rs_data["reactants"]],
            products=[_mol_from_dict(m) for m in rs_data["products"]],
            solvent=rs_data.get("solvent"),
            temperature=rs_data.get("temperature", 298.15),
        )
        steps = [_step_from_dict(s) for s in data["steps"]]
        return cls(
            session_id=data["session_id"],
            reaction_system=rs,
            steps=steps,
            session_dir=data["session_dir"],
            name=data.get("name", ""),
            completed=data.get("completed", False),
        )


def _mol_to_dict(m: Molecule) -> Dict:
    return {
        "name": m.name,
        "charge": m.charge,
        "multiplicity": m.multiplicity,
        "atoms": [{"symbol": a.symbol, "x": a.x, "y": a.y, "z": a.z} for a in m.atoms],
    }


def _mol_from_dict(d: Dict) -> Molecule:
    from domain.models import Atom
    atoms = tuple(Atom(a["symbol"], a["x"], a["y"], a["z"]) for a in d["atoms"])
    return Molecule(atoms=atoms, charge=d["charge"], multiplicity=d["multiplicity"], name=d["name"])


def _step_to_dict(s: WorkflowStep) -> Dict:
    return {
        "name": s.name,
        "calc_type": s.calc_type.name,
        "engine": s.engine,
        "params": s.params,
        "enabled": s.enabled,
        "status": s.status.name,
        "work_dir": s.work_dir,
    }


def _step_from_dict(d: Dict) -> WorkflowStep:
    return WorkflowStep(
        name=d["name"],
        calc_type=CalcType[d["calc_type"]],
        engine=d["engine"],
        params=d["params"],
        enabled=d.get("enabled", True),
        status=StepStatus[d.get("status", "PENDING")],
        work_dir=d.get("work_dir"),
    )
