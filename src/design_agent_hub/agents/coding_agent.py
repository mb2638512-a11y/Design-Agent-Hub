"""Coding specialist: implementation plans and safe code-delivery checklists."""

from __future__ import annotations

from typing import ClassVar


class CodingSpecialistAgent:
    id = "coding"
    name = "Coding Agent"
    description = "Breaks software tasks into implementation steps, tests, and deployment checks; does not execute code."
    capabilities: ClassVar[list[str]] = [
        "code", "coding", "program", "programming", "python", "javascript", "typescript",
        "api", "backend", "frontend", "website", "web app", "bug", "debug", "refactor",
        "database", "deploy", "deployment", "script", "automation", "repository", "github",
    ]

    def match_score(self, task: str) -> int:
        normalized = task.casefold()
        return sum(2 for item in self.capabilities if item in normalized)

    async def run(self, task: str) -> dict[str, object]:
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "result_type": "implementation_plan",
            "execution_status": "plan_only",
            "task": task,
            "steps": [
                "Clarify expected behavior, inputs, outputs, and acceptance criteria.",
                "Inspect the existing repository and preserve its conventions before editing.",
                "Implement the smallest coherent change with input validation and safe error handling.",
                "Add unit tests for success paths, invalid input, and relevant failure cases.",
                "Run formatter, linter, tests, and security checks in CI.",
                "Document configuration, secrets, rollback, and deployment steps.",
            ],
            "limitations": [
                "This agent does not access or modify a repository, run code, or deploy services by itself.",
                "Never place credentials, tokens, or private customer data in prompts or commits.",
            ],
        }
