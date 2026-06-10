"""Subject-specific tutor logic for the study system."""

from __future__ import annotations

from .backend import StudyBackend
from .models import TutorResponse
from .subject_registry import infer_subject_key


BACKEND = StudyBackend()


def choose_subject_key(query: str) -> str:
    """Infer the subject from a natural-language query."""
    return infer_subject_key(query)


def answer_preprocesamiento(query: str) -> TutorResponse:
    """Answer a question using the pre-processing knowledge base."""
    return BACKEND.answer(subject="Preprocesamiento de Datos", query=query, subject_key="preprocesamiento")


def answer_programacion(query: str) -> TutorResponse:
    """Answer a question using the programming knowledge base."""
    return BACKEND.answer(subject="Programación para Ciencia de Datos", query=query, subject_key="programacion")


def answer_by_subject(subject_key: str, query: str) -> TutorResponse:
    """Route a question to the corresponding tutor."""
    if subject_key == "preprocesamiento":
        return answer_preprocesamiento(query)
    if subject_key == "programacion":
        return answer_programacion(query)
    subject_name = {
        "inferencia": "Inferencia Estadística",
        "calculo": "Herramientas de Cálculo Diferencial",
    }.get(subject_key, subject_key)
    return BACKEND.answer(subject=subject_name, query=query, subject_key=subject_key)
