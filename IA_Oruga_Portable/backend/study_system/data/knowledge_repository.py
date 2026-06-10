"""Knowledge repository adapter for the study system."""

from __future__ import annotations

from ..knowledge_store import build_source_index, collect_context, find_markdown_files, list_subject_directories, read_markdown, resolve_subject_folder

__all__ = [
    "build_source_index",
    "collect_context",
    "find_markdown_files",
    "list_subject_directories",
    "read_markdown",
    "resolve_subject_folder",
]
