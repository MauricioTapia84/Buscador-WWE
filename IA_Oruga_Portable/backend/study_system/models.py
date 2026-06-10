"""Shared data models for the study system."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

SubjectKey = Literal["preprocesamiento", "programacion", "inferencia", "calculo"]
RequestType = Literal["summary", "question", "quiz", "project", "routing"]
QuizFormat = Literal["multiple_choice", "true_false", "short_answer", "mixed"]
DifficultyLevel = Literal["basic", "intermediate", "advanced"]


@dataclass(slots=True)
class DocumentSource:
    """Reference to a source file in the course material."""

    path: Path
    subject: str
    title: str
    source_type: str


@dataclass(slots=True)
class KnowledgeItem:
    """A chunk or topic extracted from a knowledge document."""

    source: DocumentSource
    heading: str
    content: str
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TutorResponse:
    """Structured response returned by a tutor agent."""

    subject: str
    answer: str
    source_paths: list[Path] = field(default_factory=list)
    follow_up_questions: list[str] = field(default_factory=list)


@dataclass(slots=True)
class QuizQuestion:
    """Single question inside a quiz pack."""

    prompt: str
    options: list[str] = field(default_factory=list)
    answer: str = ""
    explanation: str = ""
    difficulty: DifficultyLevel = "basic"


@dataclass(slots=True)
class QuizPack:
    """Collection of quiz questions and metadata."""

    subject: str
    topic: str
    format: QuizFormat
    questions: list[QuizQuestion] = field(default_factory=list)
    instructions: str = ""


@dataclass(slots=True)
class OrchestratorRequest:
    """Normalized user request routed by the orchestrator."""

    query: str
    request_type: RequestType
    subject_key: SubjectKey | None = None
    topic: str | None = None
    quiz_count: int = 5
    difficulty: DifficultyLevel = "basic"
    quiz_format: QuizFormat = "mixed"
