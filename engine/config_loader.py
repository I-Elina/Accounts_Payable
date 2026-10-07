"""Load and validate engine configuration with deep-merge support."""

import json
from copy import deepcopy
from pathlib import Path


_DEFAULT_CONFIG_PATH = Path(__file__).parent / "config" / "default_config.json"


def _deep_merge(base: dict, overrides: dict) -> dict:
    """Recursively merge *overrides* into *base* (both dicts, returns new dict)."""
    result = deepcopy(base)
    for key, value in overrides.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def load_config(overrides: dict | None = None) -> dict:
    """Load default config, deep-merge *overrides*, validate and return.

    Raises:
        ValueError: If threshold constraints are violated.
    """
    with open(_DEFAULT_CONFIG_PATH, encoding="utf-8-sig") as f:
        cfg = json.load(f)

    if overrides:
        cfg = _deep_merge(cfg, overrides)

    # --- validation ---
    auto_pass = cfg["auto_pass_threshold"]
    exception_below = cfg["exception_below"]

    if not (0 <= exception_below < auto_pass <= 1):
        raise ValueError(
            f"Invalid thresholds: need 0 <= exception_below ({exception_below}) "
            f"< auto_pass_threshold ({auto_pass}) <= 1"
        )

    return cfg
