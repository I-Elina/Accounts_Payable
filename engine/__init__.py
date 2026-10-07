"""Engine package — deterministic invoice decision engine.

Usage:
    from engine import run_engine, load_config

    result = run_engine("invoices.csv")
"""

from engine.api import run_engine
from engine.config_loader import load_config

__version__ = "1.0.0"
