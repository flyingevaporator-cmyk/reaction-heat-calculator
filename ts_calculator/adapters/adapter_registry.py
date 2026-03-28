"""Registry for engine adapters."""
from __future__ import annotations
from typing import Dict, List, Optional

from .base import EngineAdapterBase
from domain.models import CalcType


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters: Dict[str, EngineAdapterBase] = {}

    def register(self, adapter: EngineAdapterBase) -> None:
        self._adapters[adapter.engine_name] = adapter

    def get(self, engine_name: str) -> Optional[EngineAdapterBase]:
        return self._adapters.get(engine_name)

    def available_engines(self) -> List[str]:
        """Return engines whose binaries/packages are installed."""
        return [name for name, a in self._adapters.items() if a.check_installation()]

    def find_for_calc_type(self, calc_type: CalcType) -> List[EngineAdapterBase]:
        """Return available adapters that support the given CalcType."""
        return [
            a for a in self._adapters.values()
            if calc_type in a.get_supported_calc_types() and a.check_installation()
        ]


# Module-level singleton
_registry: Optional[AdapterRegistry] = None


def get_registry() -> AdapterRegistry:
    global _registry
    if _registry is None:
        _registry = _build_default_registry()
    return _registry


def _build_default_registry() -> AdapterRegistry:
    from adapters.xtb.adapter import XtbAdapter
    from adapters.psi4.adapter import Psi4Adapter
    from adapters.pyscf.adapter import PySCFAdapter

    registry = AdapterRegistry()
    registry.register(XtbAdapter())
    registry.register(Psi4Adapter())
    registry.register(PySCFAdapter())
    return registry
