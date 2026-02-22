"""Tests for custom exceptions."""

from src.promtior_assistant.presentation.exceptions import (
    AuthenticationError,
    BusinessRuleError,
    LLMProviderError,
    PromtiorError,
    ValidationError,
)


class TestPromtiorError:
    """Tests for base PromtiorError exception."""

    def test_basic_error(self):
        """Test creating a basic PromtiorError."""
        error = PromtiorError("Something went wrong")
        assert error.message == "Something went wrong"
        assert error.status_code == 500
        assert str(error) == "Something went wrong"

    def test_custom_status_code(self):
        """Test PromtiorError with custom status code."""
        error = PromtiorError("Service unavailable", status_code=503)
        assert error.status_code == 503


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_validation_error(self):
        """Test creating a ValidationError."""
        error = ValidationError("Invalid input")
        assert error.message == "Invalid input"
        assert error.status_code == 422
        assert str(error) == "Invalid input"


class TestBusinessRuleError:
    """Tests for BusinessRuleError exception."""

    def test_business_rule_error(self):
        """Test creating a BusinessRuleError."""
        error = BusinessRuleError("Business rule violated")
        assert error.message == "Business rule violated"
        assert error.status_code == 400


class TestLLMProviderError:
    """Tests for LLMProviderError exception."""

    def test_llm_provider_error(self):
        """Test creating a LLMProviderError."""
        error = LLMProviderError("LLM service failed")
        assert error.message == "LLM service failed"
        assert error.status_code == 503


class TestAuthenticationError:
    """Tests for AuthenticationError exception."""

    def test_authentication_error_default(self):
        """Test AuthenticationError with default message."""
        error = AuthenticationError()
        assert error.message == "Authentication failed"
        assert error.status_code == 401

    def test_authentication_error_custom(self):
        """Test AuthenticationError with custom message."""
        error = AuthenticationError("Invalid API key")
        assert error.message == "Invalid API key"
        assert error.status_code == 401
