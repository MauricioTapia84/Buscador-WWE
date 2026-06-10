"""Core configuration layer for the study system."""

from .settings import KNOWLEDGE_ROOT, REPO_ROOT, SEMESTER_ROOT, SUBJECTS, is_knowledge_ready, subject_path

__all__ = [
    "REPO_ROOT",
    "SEMESTER_ROOT",
    "KNOWLEDGE_ROOT",
    "SUBJECTS",
    "is_knowledge_ready",
    "subject_path",
]
