"""Semantic search adapter for the study system."""

from __future__ import annotations

from ..search_backend import (
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
