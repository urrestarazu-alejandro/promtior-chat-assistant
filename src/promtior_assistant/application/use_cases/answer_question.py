"""Use case: Answer a question using RAG."""

import asyncio
import logging

from ...domain.ports.llm_port import LLMPort
from ...domain.ports.vector_store_port import VectorStorePort
from ...domain.services.validators import InputValidator, OutputValidator

logger = logging.getLogger(__name__)


class AnswerQuestionUseCase:
    """Use case for answering questions using RAG.

    This use case orchestrates the RAG pipeline:
    1. Validate input
    2. Retrieve relevant documents
    3. Build context
    4. Generate answer with LLM
    5. Validate output
    """

    def __init__(
        self,
        llm: LLMPort,
        vector_store: VectorStorePort,
        input_validator: InputValidator,
        output_validator: OutputValidator,
    ):
        """Initialize use case with dependencies.

        Args:
            llm: LLM provider
            vector_store: Vector database
            input_validator: Input validation service
            output_validator: Output validation service
        """
        self._llm = llm
        self._vector_store = vector_store
        self._input_validator = input_validator
        self._output_validator = output_validator

    def _build_prompt(self, question: str, context: str) -> str:
        """Build optimized RAG prompt.

        Args:
            question: User question
            context: Retrieved context

        Returns:
            Formatted prompt
        """
        return f"""You are a helpful assistant. Use the context below to answer the question.

Context:
{context}

Question: {question}

Answer:"""

    async def execute(self, question: str) -> str:
        """Execute the use case.

        Args:
            question: User question

        Returns:
            Answer from RAG system

        Raises:
            ValueError: If input/output validation fails
            Exception: If RAG processing fails
        """
        validated_question = self._input_validator.validate(question)

        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                documents = await self._vector_store.retrieve_documents(
                    query=validated_question,
                    k=5,
                )

                context = "\n\n".join(doc.page_content for doc in documents)

                prompt = self._build_prompt(validated_question, context)

                answer = await self._llm.generate(prompt, temperature=0.1)

                validated_answer = self._output_validator.validate(answer)

                return validated_answer

            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2**attempt
                    logger.warning(
                        f"RAG call failed (attempt {attempt + 1}/{max_retries}), "
                        f"retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"RAG call failed after {max_retries} attempts: {e}")

        raise Exception(f"Failed to generate RAG answer after {max_retries} attempts: {last_error}")
