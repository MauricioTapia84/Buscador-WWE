"""Public facade for the study system.

The goal is to give the orchestrator a single entrypoint while keeping the
specialist components thin and reusable.
"""

from __future__ import annotations

from .backend import StudyBackend
from .orchestrator import StudyOrchestrator, build_default_orchestrator

__all__ = ["StudyBackend", "StudyOrchestrator", "build_default_orchestrator"]
