"""Custom exceptions for the application."""


class PromtiorError(Exception):
    """Base exception for Promtior application."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(PromtiorError):
    """Exception for validation errors."""

    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class BusinessRuleError(PromtiorError):
    """Exception for business rule violations."""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class LLMProviderError(PromtiorError):
    """Exception for LLM provider errors."""

    def __init__(self, message: str):
        super().__init__(message, status_code=503)


class AuthenticationError(PromtiorError):
    """Exception for authentication errors."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)
