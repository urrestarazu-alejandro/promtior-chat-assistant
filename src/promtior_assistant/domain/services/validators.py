"""Domain validators for input/output validation."""

import re
from html import escape


class InputValidator:
    """Validate and sanitize user input."""

    MAX_LENGTH = 2000
    MIN_LENGTH = 3

    FORBIDDEN_PATTERNS = [
        r"<script",
        r"javascript:",
        r"on\w+\s*=",
        r"import\s+",
        r"exec\s*\(",
        r"eval\s*\(",
    ]

    @classmethod
    def validate(cls, question: str) -> str:
        """Validate question input.

        Args:
            question: User question

        Returns:
            Validated and sanitized question

        Raises:
            ValueError: If input is invalid
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        question = question.strip()

        if len(question) < cls.MIN_LENGTH:
            raise ValueError(f"Question too short (min {cls.MIN_LENGTH} chars)")

        if len(question) > cls.MAX_LENGTH:
            raise ValueError(f"Question too long (max {cls.MAX_LENGTH} chars)")

        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, question, re.IGNORECASE):
                raise ValueError("Question contains forbidden patterns")

        question = escape(question)

        return question


class OutputValidator:
    """Validate AI output quality."""

    HALLUCINATION_PATTERNS = [
        r"\[insert.*\]",
        r"\[.*date.*\]",
        r"\[.*year.*\]",
        r"\[.*number.*\]",
        r"\[\d{4}\]",
        r"according to my knowledge",
        r"based on my knowledge",
        r"my training data",
        r"as an AI (model|assistant|language model)",
        r"I am (an AI|a language model)",
        r"I apologize, but I",
    ]

    @staticmethod
    def validate(answer: str) -> str:
        """Validate AI answer output.

        Args:
            answer: AI-generated answer

        Returns:
            Validated answer

        Raises:
            ValueError: If output is invalid
        """
        if not answer or not answer.strip():
            raise ValueError("Empty response from AI")

        if len(answer.strip()) < 5:
            raise ValueError("Response too short to be valid")

        answer_lower = answer.lower()
        for pattern in OutputValidator.HALLUCINATION_PATTERNS:
            if re.search(pattern, answer_lower, re.IGNORECASE):
                raise ValueError(f"AI output contains placeholder or hallucination: {pattern}")

        return answer.strip()
