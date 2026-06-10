"""Study orchestrator that coordinates content reader, tutors, and quiz generation."""

from __future__ import annotations

from dataclasses import dataclass

from .backend import StudyBackend
from .models import OrchestratorRequest, QuizPack, TutorResponse
from .routing import RequestRouter
from .subject_registry import SUBJECT_REGISTRY


@dataclass(slots=True)
class OrchestratorResult:
    """Unified output from the study orchestrator."""

    request: OrchestratorRequest
    response_text: str
    tutor_response: TutorResponse | None = None
    quiz_pack: QuizPack | None = None


class StudyOrchestrator:
    """Route study requests to the right specialist component."""

    def __init__(self) -> None:
        self.backend = StudyBackend()
        self.router = RequestRouter()

    def normalize_request(self, query: str, request_type: str = "question") -> OrchestratorRequest:
        """Build a normalized request from the raw query."""
        return self.router.build_request(query=query, request_type=request_type)

    def handle_question(self, query: str) -> OrchestratorResult:
        """Handle conceptual questions."""
        request = self.normalize_request(query, request_type="question")
        assert request.subject_key is not None
        tutor_response = self._ask_tutor(request.subject_key, query)
        return OrchestratorResult(
            request=request,
            response_text=tutor_response.answer,
            tutor_response=tutor_response,
        )

    def handle_summary(self, query: str) -> OrchestratorResult:
        """Handle summary requests by routing to the selected tutor."""
        request = self.normalize_request(query, request_type="summary")
        assert request.subject_key is not None
        tutor_response = self._ask_tutor(request.subject_key, query)
        return OrchestratorResult(
            request=request,
            response_text=tutor_response.answer,
            tutor_response=tutor_response,
        )

    def handle_quiz(self, query: str, count: int = 5, difficulty: str = "basic", quiz_format: str = "mixed") -> OrchestratorResult:
        """Generate a quiz pack for the requested topic."""
        request = self.normalize_request(query, request_type="quiz")
        assert request.subject_key is not None
        subject_name = SUBJECT_REGISTRY[request.subject_key].name
        quiz_pack = self.backend.build_quiz(subject=subject_name, topic=query, count=count, difficulty=difficulty, quiz_format=quiz_format)
        return OrchestratorResult(
            request=request,
            response_text=f"Quiz generado para {subject_name}: {query}",
            quiz_pack=quiz_pack,
        )

    def _ask_tutor(self, subject_key: str, query: str) -> TutorResponse:
        """Route the query through the shared semantic backend."""
        subject_name = SUBJECT_REGISTRY[subject_key].name
        return self.backend.answer(subject=subject_name, query=query, subject_key=subject_key)


def build_default_orchestrator() -> StudyOrchestrator:
    """Factory for the default orchestrator instance."""
    return StudyOrchestrator()
