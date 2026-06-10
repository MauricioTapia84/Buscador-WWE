"""Subject registry and routing helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .config import SUBJECTS


@dataclass(frozen=True, slots=True)
class SubjectInfo:
    """Metadata for a course subject."""

    key: str
    name: str
    keywords: tuple[str, ...]


SUBJECT_REGISTRY: dict[str, SubjectInfo] = {
    "preprocesamiento": SubjectInfo(
        key="preprocesamiento",
        name=SUBJECTS["preprocesamiento"],
        keywords=("escalamiento", "outlier", "nulos", "encoding", "correlacion", "preprocesamiento", "eda"),
    ),
    "programacion": SubjectInfo(
        key="programacion",
        name=SUBJECTS["programacion"],
        keywords=("python", "git", "github", "optuna", "kmeans", "modelos", "programacion", "pandas"),
    ),
    "inferencia": SubjectInfo(
        key="inferencia",
        name=SUBJECTS["inferencia"],
        keywords=("estadistica", "inferencia", "probabilidad", "hipotesis", "muestreo"),
    ),
    "calculo": SubjectInfo(
        key="calculo",
        name=SUBJECTS["calculo"],
        keywords=("derivada", "integral", "limite", "calculo", "funcion"),
    ),
}


def infer_subject_key(query: str) -> str:
    """Infer the subject key from a natural language query."""
    lowered = query.lower()
    for key, info in SUBJECT_REGISTRY.items():
        if any(keyword in lowered for keyword in info.keywords):
            return key
    return "preprocesamiento"
