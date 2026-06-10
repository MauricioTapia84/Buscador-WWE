"""Data access layer for the study system."""

from .knowledge_repository import (
    build_source_index,
    collect_context,
    find_markdown_files,
    list_subject_directories,
    read_markdown,
    resolve_subject_folder,
)
from .semantic_search import (
    KnowledgeChunk,
    KnowledgeIndex,
    SearchHit,
    SearchResult,
    is_ready,
    load_knowledge_index,
    render_hits,
    search,
    search_subject,
)

__all__ = [
    "build_source_index",
    "collect_context",
    "find_markdown_files",
    "list_subject_directories",
    "read_markdown",
    "resolve_subject_folder",
    "KnowledgeChunk",
    "KnowledgeIndex",
    "SearchHit",
    "SearchResult",
    "is_ready",
    "load_knowledge_index",
    "render_hits",
    "search",
    "search_subject",
]
