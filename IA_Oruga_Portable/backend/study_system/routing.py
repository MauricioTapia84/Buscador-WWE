"""Request routing helpers for the study orchestrator."""

from __future__ import annotations

from dataclasses import dataclass

from .models import OrchestratorRequest
from .subject_registry import infer_subject_key


@dataclass(slots=True)
class RequestRouter:
    """Normalize and route user requests to the appropriate study flow."""

    def build_request(self, query: str, request_type: str) -> OrchestratorRequest:
        """Create a normalized request object from raw user input."""
        subject_key = infer_subject_key(query)
        return OrchestratorRequest(query=query, request_type=request_type, subject_key=subject_key, topic=query)
