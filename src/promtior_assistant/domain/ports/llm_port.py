"""Port (interface) for LLM providers."""

from typing import Protocol


class LLMPort(Protocol):
    """Port for Language Model providers.

    This interface defines the contract that all LLM adapters must implement.
    Following the Dependency Inversion Principle, the domain layer depends on
    this abstraction, not on concrete implementations.
    """

    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate text from a prompt.

        Args:
            prompt: Input prompt for the LLM
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            Generated text

        Raises:
            Exception: If generation fails
        """
        ...

    @property
    def model_name(self) -> str:
        """Get the model name.

        Returns:
            Model identifier
        """
        ...
