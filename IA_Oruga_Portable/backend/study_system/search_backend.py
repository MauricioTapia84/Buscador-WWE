"""Semantic search backend for the study system.

This module builds a lightweight semantic index over the generated knowledge base
and exposes reusable retrieval helpers for the orchestrator, content reader and tutors.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
import math
import re
from pathlib import Path
from typing import Iterable

from .config import KNOWLEDGE_ROOT, SUBJECTS

TOKEN_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_]+", re.UNICODE)
STOPWORDS = {
    "a", "acá", "algo", "al", "algunos", "ante", "antes", "aquí", "así", "aun", "aunque",
    "bajo", "bien", "cada", "como", "con", "contra", "cual", "cuales", "cuando", "de", "debe",
    "deben", "del", "desde", "donde", "dos", "el", "ella", "ellas", "ellos", "en", "entre",
    "era", "eras", "eres", "es", "esa", "esas", "ese", "eso", "esos", "esta", "estaba",
    "estaban", "estamos", "estan", "estar", "este", "esto", "estos", "fue", "fueron", "ha",
    "hasta", "hay", "la", "las", "le", "les", "lo", "los", "más", "me", "mi", "mis", "muy",
    "no", "nos", "nosotros", "o", "para", "pero", "por", "porque", "que", "quien", "se",
    "si", "sin", "sobre", "su", "sus", "también", "te", "tengo", "tenemos", "tener", "tiene",
    "tienen", "todo", "todos", "tu", "tus", "un", "una", "uno", "unos", "y", "ya", "yo",
}


@dataclass(slots=True)
class KnowledgeChunk:
    """Small searchable unit extracted from a markdown document."""

    path: Path
    subject: str
    heading: str
    text: str
    tokens: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SearchHit:
    """Search result returned by the semantic backend."""

    chunk: KnowledgeChunk
    score: float


@dataclass(slots=True)
class SearchResult:
    """Search response with ranking metadata."""

    query: str
    hits: list[SearchHit]


@dataclass(slots=True)
class KnowledgeIndex:
    """In-memory semantic index built from the generated knowledge base."""

    chunks: list[KnowledgeChunk]
    vocabulary: dict[str, int]
    idf: dict[str, float]
    tfidf_vectors: list[dict[str, float]]

    @property
    def size(self) -> int:
        return len(self.chunks)



def _normalize(text: str) -> list[str]:
    tokens = [token.lower() for token in TOKEN_RE.findall(text)]
    return [token for token in tokens if token not in STOPWORDS and len(token) > 1]



def _subject_name(path: Path) -> str:
    for subject_name in SUBJECTS.values():
        if subject_name in path.parts:
            return subject_name
    return "General"



def _chunk_markdown(text: str, max_chars: int = 1200) -> list[tuple[str, str]]:
    sections = re.split(r"\n(?=#{1,6}\s)|\n{2,}", text)
    chunks: list[tuple[str, str]] = []
    current_heading = "Contenido"
    current_text = ""

    for raw_section in sections:
        section = raw_section.strip()
        if not section:
            continue
        heading_match = re.match(r"^(#{1,6})\s+(.*)$", section)
        if heading_match:
            current_heading = heading_match.group(2).strip()
            section_body = section
        else:
            section_body = section

        if not current_text:
            current_text = section_body
        elif len(current_text) + len(section_body) + 2 <= max_chars:
            current_text = f"{current_text}\n\n{section_body}"
        else:
            chunks.append((current_heading, current_text.strip()))
            current_text = section_body

    if current_text.strip():
        chunks.append((current_heading, current_text.strip()))

    return chunks



def _load_markdown_chunks() -> list[KnowledgeChunk]:
    if not KNOWLEDGE_ROOT.exists():
        return []

    chunks: list[KnowledgeChunk] = []
    for path in sorted(KNOWLEDGE_ROOT.rglob("*.md")):
        if path.name == "INDEX.md":
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        subject = _subject_name(path)
        for heading, chunk_text in _chunk_markdown(text):
            tokens = _normalize(f"{heading}\n{chunk_text}")
            if not tokens:
                continue
            chunks.append(
                KnowledgeChunk(
                    path=path,
                    subject=subject,
                    heading=heading,
                    text=chunk_text,
                    tokens=tokens,
                )
            )
    return chunks



def _build_index(chunks: list[KnowledgeChunk]) -> KnowledgeIndex:
    vocabulary: dict[str, int] = {}
    document_frequency: dict[str, int] = {}
    for chunk in chunks:
        seen: set[str] = set()
        for token in chunk.tokens:
            if token not in vocabulary:
                vocabulary[token] = len(vocabulary)
            if token not in seen:
                document_frequency[token] = document_frequency.get(token, 0) + 1
                seen.add(token)

    total_docs = max(len(chunks), 1)
    idf = {
        token: math.log((1 + total_docs) / (1 + freq)) + 1.0
        for token, freq in document_frequency.items()
    }

    tfidf_vectors: list[dict[str, float]] = []
    for chunk in chunks:
        counts: dict[str, int] = {}
        for token in chunk.tokens:
            counts[token] = counts.get(token, 0) + 1
        total_tokens = max(len(chunk.tokens), 1)
        vector = {
            token: (count / total_tokens) * idf.get(token, 1.0)
            for token, count in counts.items()
        }
        tfidf_vectors.append(vector)

    return KnowledgeIndex(chunks=chunks, vocabulary=vocabulary, idf=idf, tfidf_vectors=tfidf_vectors)



@lru_cache(maxsize=1)
def load_knowledge_index() -> KnowledgeIndex:
    """Build and cache the knowledge index."""
    return _build_index(_load_markdown_chunks())



def is_ready() -> bool:
    """Return True when the knowledge base has indexed content."""
    return load_knowledge_index().size > 0



def _cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    dot_product = sum(left.get(token, 0.0) * right.get(token, 0.0) for token in set(left) | set(right))
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot_product / (left_norm * right_norm)



def _query_vector(query_tokens: list[str], idf: dict[str, float]) -> dict[str, float]:
    counts: dict[str, int] = {}
    for token in query_tokens:
        counts[token] = counts.get(token, 0) + 1
    total_tokens = max(len(query_tokens), 1)
    return {
        token: (count / total_tokens) * idf.get(token, 1.0)
        for token, count in counts.items()
    }



def search(query: str, subject: str | None = None, top_k: int = 5) -> SearchResult:
    """Search the knowledge base and return the most relevant chunks."""
    index = load_knowledge_index()
    query_tokens = _normalize(query)
    query_vector = _query_vector(query_tokens, index.idf)

    hits: list[SearchHit] = []
    query_lower = query.lower()
    for chunk, vector in zip(index.chunks, index.tfidf_vectors):
        if subject is not None and chunk.subject != subject:
            continue
        score = _cosine_similarity(query_vector, vector)
        if query_lower in chunk.text.lower() or query_lower in chunk.heading.lower():
            score += 0.2
        if any(token in chunk.tokens for token in query_tokens):
            score += 0.05
        if score <= 0.0:
            continue
        hits.append(SearchHit(chunk=chunk, score=score))

    hits.sort(key=lambda item: item.score, reverse=True)
    return SearchResult(query=query, hits=hits[:top_k])



def render_hits(result: SearchResult, max_chars: int = 6000) -> str:
    """Render search hits into a bounded context string for prompts."""
    if not result.hits:
        return ""

    lines: list[str] = []
    remaining = max_chars
    for index, hit in enumerate(result.hits, 1):
        chunk = hit.chunk
        block = (
            f"\n\n### Hit {index} | {chunk.subject} | {chunk.heading} | score={hit.score:.3f}\n"
            f"Fuente: {chunk.path}\n\n"
            f"{chunk.text.strip()}"
        )
        if len(block) > remaining:
            lines.append(block[:remaining])
            break
        lines.append(block)
        remaining -= len(block)
        if remaining <= 0:
            break
    return "".join(lines)



def search_subject(query: str, subject_key: str | None = None, top_k: int = 5) -> SearchResult:
    """Convenience helper that resolves subject keys and runs the search."""
    subject_name = None
    if subject_key is not None:
        subject_name = SUBJECTS.get(subject_key.lower(), subject_key)
    return search(query=query, subject=subject_name, top_k=top_k)
