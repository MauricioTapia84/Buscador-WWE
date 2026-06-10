"""Configuration and path helpers for the study system."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SEMESTER_ROOT = REPO_ROOT / "Semestre 1 mención"
KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"
SUBJECTS = {
    "preprocesamiento": "PREPROCESAMIENTO de datos",
    "programacion": "Programación para ciencia de datos",
    "inferencia": "Inferencia Estadística",
    "calculo": "Herramientas de calculo diferencial",
}


def is_knowledge_ready() -> bool:
    """Return True when the generated knowledge base is available."""
    return KNOWLEDGE_ROOT.exists() and any(KNOWLEDGE_ROOT.rglob("*.md"))


def subject_path(subject_key: str) -> Path:
    """Return the folder for a given subject key."""
    subject_name = SUBJECTS.get(subject_key.lower())
    if subject_name is None:
        raise KeyError(f"Unknown subject key: {subject_key}")
    return KNOWLEDGE_ROOT / subject_name
