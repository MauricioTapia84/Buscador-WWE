"""Quiz generation utilities for study practice."""

from __future__ import annotations

from .models import QuizPack, QuizQuestion


def build_quiz_pack(subject: str, topic: str, count: int = 5, difficulty: str = "basic", quiz_format: str = "mixed") -> QuizPack:
    """Create a simple quiz pack scaffold."""
    questions = []
    for index in range(count):
        questions.append(
            QuizQuestion(
                prompt=f"Pregunta {index + 1} sobre {topic}",
                options=["Opción A", "Opción B", "Opción C", "Opción D"],
                answer="Opción A",
                explanation="Respuesta derivada del material del curso.",
                difficulty=difficulty,  # type: ignore[arg-type]
            )
        )
    return QuizPack(
        subject=subject,
        topic=topic,
        format=quiz_format,  # type: ignore[arg-type]
        questions=questions,
        instructions="Resuelve cada pregunta usando el material del curso como referencia.",
    )
