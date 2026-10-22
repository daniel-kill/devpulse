import os
from pathlib import Path
from typing import Any

# Use standard library tomllib (Python 3.11+) with tomli fallback if available
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "devpulse" / "config.toml"

def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load configuration from config.toml if it exists, otherwise return defaults."""
    target = config_path or DEFAULT_CONFIG_PATH
    if target.exists() and tomllib is not None:
        try:
            with open(target, "rb") as f:
                return tomllib.load(f)
        except Exception:
            return {}
    return {}
