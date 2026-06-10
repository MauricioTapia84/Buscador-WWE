"""CLI entrypoint for the presentation layer."""

from __future__ import annotations

import argparse

from .. import is_knowledge_ready
from ..orchestrator import build_default_orchestrator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Study system CLI")
    parser.add_argument("query", help="User query to route through the orchestrator")
    parser.add_argument(
        "--mode",
        choices=["question", "summary", "quiz"],
        default="question",
        help="Type of request to execute",
    )
    parser.add_argument("--count", type=int, default=5, help="Number of quiz questions")
    parser.add_argument("--difficulty", default="basic", help="Quiz difficulty level")
    parser.add_argument("--format", default="mixed", help="Quiz format")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    orchestrator = build_default_orchestrator()

    if not is_knowledge_ready():
        print("El knowledge base todavía no está listo. Ejecuta scripts/extract_course_content.py primero.")
        return

    if args.mode == "question":
        result = orchestrator.handle_question(args.query)
        print(result.response_text)
        return

    if args.mode == "summary":
        result = orchestrator.handle_summary(args.query)
        print(result.response_text)
        return

    result = orchestrator.handle_quiz(args.query, count=args.count, difficulty=args.difficulty, quiz_format=args.format)
    print(result.response_text)
    if result.quiz_pack is not None:
        for index, question in enumerate(result.quiz_pack.questions, 1):
            print(f"\n{index}. {question.prompt}")
            for option in question.options:
                print(f"- {option}")


if __name__ == "__main__":
    main()
