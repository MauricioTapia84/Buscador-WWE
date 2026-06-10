"""Content service adapter for the study system."""

from __future__ import annotations

from ..content_reader import ContentReadResult, locate_relevant_files, read_topic_context, summarize_content

__all__ = ["ContentReadResult", "locate_relevant_files", "read_topic_context", "summarize_content"]
