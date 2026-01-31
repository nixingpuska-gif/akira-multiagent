"""Self-modification pipeline (ASCII only)."""

from .analyzer import SelfModAnalyzer
from .patcher import SelfModPatcher
from .sandbox import SelfModSandbox

__all__ = [
    "SelfModAnalyzer",
    "SelfModPatcher",
    "SelfModSandbox",
]
