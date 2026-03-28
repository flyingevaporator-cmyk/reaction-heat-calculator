"""Application configuration (TOML-backed)."""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]

try:
    import tomli_w
except ImportError:
    tomli_w = None  # type: ignore[assignment]

_DEFAULT_CONFIG: Dict[str, Any] = {
    "engines": {
        "xtb_path": "xtb",
        "psi4_python": "psi4",
    },
    "defaults": {
        "n_cores": 4,
        "memory_gb": 8.0,
    },
    "workspace": {
        "base_dir": "",   # empty = ~/.ts_calculator/workspaces
    },
}

_CONFIG_PATH = Path.home() / ".ts_calculator" / "config.toml"


class AppConfig:
    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        self._data = dict(_DEFAULT_CONFIG)
        if _CONFIG_PATH.exists():
            text = _CONFIG_PATH.read_text(encoding="utf-8")
            if tomllib is not None:
                user = tomllib.loads(text)
            else:
                from domain.presets.preset_library import _simple_toml_parse
                user = _simple_toml_parse(text)
            self._deep_merge(self._data, user)

    def _deep_merge(self, base: dict, override: dict) -> None:
        for k, v in override.items():
            if isinstance(v, dict) and isinstance(base.get(k), dict):
                self._deep_merge(base[k], v)
            else:
                base[k] = v

    def get(self, *keys: str, default: Any = None) -> Any:
        node = self._data
        for k in keys:
            if not isinstance(node, dict):
                return default
            node = node.get(k, default)  # type: ignore[assignment]
        return node

    def save(self) -> None:
        if tomli_w is None:
            return
        _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CONFIG_PATH.write_text(tomli_w.dumps(self._data), encoding="utf-8")


# Module-level singleton
_config: AppConfig | None = None


def get_config() -> AppConfig:
    global _config
    if _config is None:
        _config = AppConfig()
    return _config
