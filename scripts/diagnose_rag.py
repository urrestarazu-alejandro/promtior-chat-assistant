#!/usr/bin/env python
"""RAG diagnostic script - Shows what documents are retrieved for a question."""

import asyncio
import sys

from src.promtior_assistant.config import settings
from src.promtior_assistant.domain.models.embedding_metadata import EmbeddingMetadata
from src.promtior_assistant.infrastructure.factories import create_embeddings
from src.promtior_assistant.infrastructure.vector_store.chroma_adapter import (
    ChromaVectorStoreAdapter,
)


async def diagnose_query(question: str, k: int = 5):
    """Diagnose what documents are retrieved for a question.

    Args:
        question: The question to test
        k: Number of documents to retrieve
    """
    print(f"\n{'='*80}")
    print(f"🔍 RAG Diagnostic - Analyzing Question")
    print(f"{'='*80}\n")

    print(f"Question: {question}")
    print(f"Retrieving top {k} documents...\n")

    embeddings = create_embeddings()

    if settings.llm_provider == "openai" and settings.use_openai_embeddings:
        metadata = EmbeddingMetadata.from_openai(settings.openai_embedding_model)
    else:
        metadata = EmbeddingMetadata.from_ollama(settings.ollama_embedding_model)

    vector_store = ChromaVectorStoreAdapter(
        persist_directory=settings.chroma_persist_directory,
        embeddings=embeddings,
        embedding_metadata=metadata,
        validate_metadata=True,
    )

    documents = await vector_store.retrieve_documents(query=question, k=k)

    print(f"{'='*80}")
    print(f"📄 Retrieved {len(documents)} documents")
    print(f"{'='*80}\n")

    for i, doc in enumerate(documents, 1):
        print(f"--- Document {i} ---")
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"Type: {doc.metadata.get('type', 'Unknown')}")
        print(f"Content length: {len(doc.page_content)} characters")
        print(f"\nContent preview (first 500 chars):")
        print(f"{doc.page_content[:500]}...")
        print(f"\n{'='*80}\n")

    # Show if any document contains keywords
    keywords = [
        "found",
        "founded",
        "fundada",
        "2015",
        "2016",
        "2017",
        "2018",
        "creation",
        "established",
    ]

    print(f"🔎 Searching for keywords: {', '.join(keywords)}")
    print(f"{'='*80}\n")

    for i, doc in enumerate(documents, 1):
        found_keywords = [kw for kw in keywords if kw.lower() in doc.page_content.lower()]
        if found_keywords:
            print(f"✓ Document {i} contains: {', '.join(found_keywords)}")
        else:
            print(f"✗ Document {i} - no keywords found")

    print(f"\n{'='*80}")
    print(f"💡 Diagnostic complete!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/diagnose_rag.py 'Your question here'")
        print("\nExamples:")
        print("  uv run python scripts/diagnose_rag.py 'When was Promtior founded?'")
        print("  uv run python scripts/diagnose_rag.py '¿Cuándo fue fundada Promtior?'")
        sys.exit(1)

    question = sys.argv[1]
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    asyncio.run(diagnose_query(question, k))
