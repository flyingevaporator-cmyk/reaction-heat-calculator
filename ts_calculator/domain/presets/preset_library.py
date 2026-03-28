"""Loads preset parameter sets from TOML files."""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]


def _simple_toml_parse(text: str) -> Dict[str, Dict[str, Any]]:
    """Minimal TOML parser supporting [section] + key = value (str/int/float/bool)."""
    import re
    result: Dict[str, Dict[str, Any]] = {}
    current: Dict[str, Any] | None = None
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^\[(.+)\]$", line)
        if m:
            section = m.group(1).strip()
            current = {}
            result[section] = current
            continue
        if current is not None and "=" in line:
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            # Infer type
            if val.lower() in ("true", "false"):
                current[key] = val.lower() == "true"
            else:
                try:
                    current[key] = int(val)
                except ValueError:
                    try:
                        current[key] = float(val)
                    except ValueError:
                        current[key] = val
    return result

_PRESET_DIR = Path(__file__).parent


class PresetLibrary:
    def __init__(self) -> None:
        self._presets: Dict[str, Dict[str, Any]] = {}
        self._load_file("organic_presets.toml", prefix="organic")
        self._load_file("transition_metal_presets.toml", prefix="tm")

    def _load_file(self, filename: str, prefix: str) -> None:
        path = _PRESET_DIR / filename
        if not path.exists():
            return
        text = path.read_text(encoding="utf-8")
        if tomllib is not None:
            data = tomllib.loads(text)
        else:
            data = _simple_toml_parse(text)
        for key, vals in data.items():
            self._presets[f"{prefix}/{key}"] = vals

    def all_presets(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._presets)

    def labels(self) -> List[str]:
        return [v.get("label", k) for k, v in self._presets.items()]

    def get_by_label(self, label: str) -> Dict[str, Any]:
        for v in self._presets.values():
            if v.get("label") == label:
                return v
        return {}

    def get(self, key: str) -> Dict[str, Any]:
        return self._presets.get(key, {})

    def build_steps(self, preset_key: str) -> List[Dict[str, Any]]:
        """Return a list of step-param dicts for the given preset."""
        p = self._presets.get(preset_key, {})
        if not p:
            return []
        return [
            {"name": "neb",  "calc_type": "NEB",          "engine": "xtb",   "params": {"extra": {"n_images": p.get("neb_n_images", 12)}}},
            {"name": "tsopt","calc_type": "TS_OPT",        "engine": "psi4",  "params": {"method": p.get("ts_opt_method","b3lyp-d3bj"), "basis": p.get("ts_opt_basis","6-31g(d)")}},
            {"name": "freq", "calc_type": "FREQUENCY",     "engine": "psi4",  "params": {"method": p.get("freq_method","b3lyp-d3bj"),   "basis": p.get("freq_basis","6-31g(d)")}},
            {"name": "irc",  "calc_type": "IRC",           "engine": "psi4",  "params": {"method": p.get("dft_method","b3lyp-d3bj"),    "basis": p.get("dft_basis","6-31g(d)"), "extra": {"irc_points": p.get("irc_points", 20)}}},
            {"name": "ccsd", "calc_type": "SINGLE_POINT",  "engine": "pyscf", "params": {"method": "ccsd(t)", "basis": p.get("ccsd_basis","cc-pvtz")}, "enabled": False},
        ]
