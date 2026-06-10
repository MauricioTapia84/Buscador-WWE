"""Study system package for the Science Data repository."""

from .backend import StudyBackend
from .config import KNOWLEDGE_ROOT, SEMESTER_ROOT, SUBJECTS, is_knowledge_ready
from .models import (
    DocumentSource,
    KnowledgeItem,
    OrchestratorRequest,
    QuizPack,
    QuizQuestion,
    TutorResponse,
)
from .orchestrator import StudyOrchestrator, build_default_orchestrator

from .core import REPO_ROOT, subject_path
from .data import (
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
from .domain import DifficultyLevel, RequestType, SubjectKey
from .presentation import OrchestratorResult

__all__ = [
    "KNOWLEDGE_ROOT",
    "REPO_ROOT",
    "SEMESTER_ROOT",
    "SUBJECTS",
    "is_knowledge_ready",
    "subject_path",
    "KnowledgeChunk",
    "KnowledgeIndex",
    "SearchHit",
    "SearchResult",
    "is_ready",
    "load_knowledge_index",
    "render_hits",
    "search",
    "search_subject",
    "DocumentSource",
    "DifficultyLevel",
    "KnowledgeItem",
    "OrchestratorRequest",
    "RequestType",
    "QuizPack",
    "QuizQuestion",
    "SubjectKey",
    "TutorResponse",
    "StudyBackend",
    "OrchestratorResult",
    "StudyOrchestrator",
    "build_default_orchestrator",
]
