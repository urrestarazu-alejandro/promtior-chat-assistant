"""RAG chain implementation - backward compatibility module.

This module is kept for backward compatibility.
New code should use:
- domain.services.validators for InputValidator/OutputValidator
- infrastructure.persistence.usage_tracker for UsageTracker
- infrastructure.llm.ollama_adapter for CustomOllamaChat
- infrastructure.embeddings.ollama_embeddings for CustomOllamaEmbeddings
- services.rag_service for get_rag_answer
"""
