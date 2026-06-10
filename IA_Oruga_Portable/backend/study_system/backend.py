"""Shared backend facade used by the orchestrator and the specialist tutors."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .models import QuizPack, TutorResponse
from .quiz_generator import build_quiz_pack
from .search_backend import SearchResult, render_hits, search_subject


@dataclass(slots=True)
class StudyBackend:
    """Facade over search, retrieval and generation utilities."""

    def search(self, query: str, subject_key: str | None = None, top_k: int = 5) -> SearchResult:
        """Search the knowledge base using semantic ranking."""
        return search_subject(query=query, subject_key=subject_key, top_k=top_k)

    def answer(self, subject: str, query: str, subject_key: str | None = None, max_k: int = 3) -> TutorResponse:
        """Compose a tutor response from the best semantic hits."""
        result = self.search(query=query, subject_key=subject_key, top_k=max_k)
        context = render_hits(result)
        if not context:
            answer = (
                f"Tema consultado: {query}\n\n"
                "No se encontraron fragmentos relevantes en el knowledge base todavía."
            )
            return TutorResponse(subject=subject, answer=answer)

        source_paths = [hit.chunk.path for hit in result.hits]
        answer = (
            f"Tema consultado: {query}\n\n"
            f"Respuesta basada en los fragmentos más relevantes del knowledge base.\n\n"
            f"{context}"
        )
        return TutorResponse(subject=subject, answer=answer, source_paths=source_paths)

    def build_quiz(self, subject: str, topic: str, count: int = 5, difficulty: str = "basic", quiz_format: str = "mixed") -> QuizPack:
        """Create a quiz pack scaffold from the shared generator."""
        return build_quiz_pack(subject=subject, topic=topic, count=count, difficulty=difficulty, quiz_format=quiz_format)
