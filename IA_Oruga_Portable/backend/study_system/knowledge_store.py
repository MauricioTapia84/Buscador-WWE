"""Knowledge base access helpers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from .config import KNOWLEDGE_ROOT, SUBJECTS, subject_path
from .models import DocumentSource


def list_subject_directories() -> list[Path]:
    """Return the configured subject folders that exist in knowledge/."""
    folders: list[Path] = []
    for subject_name in SUBJECTS.values():
        folder = KNOWLEDGE_ROOT / subject_name
        if folder.exists():
            folders.append(folder)
    return folders


def resolve_subject_folder(subject_key: str) -> Path:
    """Resolve a subject key into a knowledge/ folder."""
    return subject_path(subject_key)


def find_markdown_files(folder: Path, query: str | None = None) -> list[Path]:
    """Return Markdown files matching the query or all files in a folder."""
    if not folder.exists():
        return []

    files = sorted(folder.rglob("*.md"))
    if not query:
        return files

    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return [path for path in files if pattern.search(path.stem) or pattern.search(path.read_text(encoding="utf-8", errors="ignore"))]


def read_markdown(path: Path) -> str:
    """Read a Markdown file safely."""
    return path.read_text(encoding="utf-8", errors="ignore")


def build_source_index(paths: Iterable[Path], subject: str) -> list[DocumentSource]:
    """Build source objects from a list of Markdown paths."""
    sources: list[DocumentSource] = []
    for path in paths:
        sources.append(
            DocumentSource(
                path=path,
                subject=subject,
                title=path.stem.replace("_", " "),
                source_type=path.suffix.lstrip("."),
            )
        )
    return sources


def collect_context(paths: Iterable[Path], max_chars: int = 12000) -> str:
    """Concatenate selected knowledge files into a bounded context string."""
    chunks: list[str] = []
    remaining = max_chars
    for path in paths:
        text = read_markdown(path).strip()
        if not text:
            continue
        header = f"\n\n### Fuente: {path}\n"
        chunk = header + text
        if len(chunk) > remaining:
            chunks.append(chunk[:remaining])
            break
        chunks.append(chunk)
        remaining -= len(chunk)
        if remaining <= 0:
            break
    return "".join(chunks)
