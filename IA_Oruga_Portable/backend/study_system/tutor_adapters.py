"""Adapters that expose the shared backend to the subject tutors."""

from __future__ import annotations

from .backend import StudyBackend
from .models import TutorResponse

BACKEND = StudyBackend()


def answer_subject(subject_key: str, subject_name: str, query: str) -> TutorResponse:
    """Answer a question using the shared semantic backend."""
    return BACKEND.answer(subject=subject_name, query=query, subject_key=subject_key)


def generate_quiz(subject_name: str, topic: str, count: int = 5, difficulty: str = "basic", quiz_format: str = "mixed"):
    """Generate a quiz pack through the shared backend."""
    return BACKEND.build_quiz(subject=subject_name, topic=topic, count=count, difficulty=difficulty, quiz_format=quiz_format)
