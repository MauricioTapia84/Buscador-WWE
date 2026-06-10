"""Content reader that extracts and packages knowledge from course documents."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .backend import StudyBackend
from .knowledge_store import find_markdown_files, resolve_subject_folder
from .models import TutorResponse


@dataclass(slots=True)
class ContentReadResult:
    """Result returned by the content reader."""

    subject: str
    files: list[Path]
    context: str


def locate_relevant_files(subject_key: str, query: str) -> list[Path]:
    """Find the most relevant knowledge files for a query."""
    folder = resolve_subject_folder(subject_key)
    files = find_markdown_files(folder, query=query)
    if files:
        return files
    return find_markdown_files(folder)


def read_topic_context(subject_key: str, query: str, max_files: int = 3) -> ContentReadResult:
    """Build a compact context from the most relevant files."""
    files = locate_relevant_files(subject_key, query)[:max_files]
    backend = StudyBackend()
    search_result = backend.search(query=query, subject_key=subject_key, top_k=max_files)
    context = "\n\n".join(
        f"### Fuente: {hit.chunk.path}\n\n{hit.chunk.text.strip()}"
        for hit in search_result.hits
    )
    return ContentReadResult(subject=subject_key, files=files, context=context)


def summarize_content(subject: str, query: str, context: str) -> TutorResponse:
    """Produce a structured summary response from the selected context."""
    answer = (
        f"Tema consultado: {query}\n\n"
        "Resumen generado a partir del knowledge base disponible.\n\n"
        f"Contexto base:\n{context[:4000]}"
    )
    return TutorResponse(subject=subject, answer=answer)
