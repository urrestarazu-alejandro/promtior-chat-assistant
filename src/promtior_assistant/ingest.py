"""Data ingestion script for scraping and storing Promtior website content."""

import asyncio
import re
import shutil
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from .config import settings
from .domain.models.embedding_metadata import EmbeddingMetadata
from .infrastructure.embeddings.ollama_embeddings import CustomOllamaEmbeddings
from .infrastructure.vector_store.chroma_adapter import ChromaVectorStoreAdapter

PDF_DIR = Path(__file__).parent.parent.parent / "docs"


def preprocess_text(text: str) -> str:
    """Preprocess text to improve embedding quality.

    Following embedding-strategies best practices:
    - Remove excessive whitespace
    - Normalize unicode
    - Preserve paragraph structure
    - Clean special characters
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    text = re.sub(r"[^\S\n]{2,}", " ", text)

    text = text.strip()

    return text


def load_pdfs() -> list[Document]:
    """Load all PDFs from the docs directory."""
    if not PDF_DIR.exists():
        print(f"⚠️  PDF directory not found: {PDF_DIR}")
        return []

    pdf_files = list(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        print("⚠️  No PDF files found")
        return []

    documents = []
    for pdf_path in pdf_files:
        print(f"📄 Loading PDF: {pdf_path.name}")
        try:
            reader = PdfReader(str(pdf_path))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            text = preprocess_text(text)

            documents.append(
                Document(page_content=text, metadata={"source": str(pdf_path.name), "type": "pdf"})
            )
            print(f"   ✅ Extracted {len(text)} characters")
        except Exception as e:
            print(f"   ❌ Error loading {pdf_path.name}: {e}")

    return documents


def scrape_promtior_website() -> Document:
    """
    Scrape the Promtior website.

    Returns:
        Document with scraped content
    """
    url = "https://promtior.ai"
    print(f"🔍 Scraping {url}...")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract text
        text = soup.get_text(separator="\n", strip=True)

        text = preprocess_text(text)

        print(f"✅ Scraped {len(text)} characters")

        return Document(
            page_content=text,
            metadata={"source": url, "type": "website"},
        )
    except Exception as e:
        print(f"❌ Error scraping website: {e}")
        raise


def ingest_data():
    """
    Ingest data into ChromaDB.

    This function:
    1. Loads PDFs from docs directory (priority - detailed company info)
    2. Scrapes the Promtior website (supplementary info)
    3. Splits the text into chunks
    4. Generates embeddings
    5. Stores in ChromaDB
    """
    import logging

    logger = logging.getLogger(__name__)

    print("\n" + "=" * 60)
    print("🚀 Starting data ingestion...")
    print("=" * 60 + "\n")

    logger.info(f"Chroma persist directory: {settings.chroma_persist_directory}")

    all_documents = []

    # Step 1: Load PDFs first (priority - detailed company info like founding date)
    pdf_docs = load_pdfs()
    all_documents.extend(pdf_docs)
    logger.info(f"Total PDFs loaded: {len(pdf_docs)}")

    # Step 2: Scrape website (supplementary info)
    try:
        doc = scrape_promtior_website()
        all_documents.append(doc)
    except Exception as e:
        print(f"⚠️  Website scraping failed: {e}")
        logger.warning(f"Website scraping failed: {e}")

    logger.info(f"Total documents loaded: {len(all_documents)}")

    if not all_documents:
        raise ValueError("No documents to ingest")

    # Step 3: Split text into chunks (semantic chunking)
    print("\n✂️  Splitting text into chunks (semantic)...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
        length_function=len,
        separators=[
            "\n\n",
            "\n",
            ". ",
            "? ",
            "! ",
            "; ",
            ", ",
            " ",
            "",
        ],
        keep_separator=True,
    )
    chunks = text_splitter.split_documents(all_documents)
    print(f"✅ Created {len(chunks)} chunks")

    # Step 3: Initialize embeddings and metadata
    print("\n🧮 Initializing embeddings...")
    if settings.llm_provider == "openai" and settings.use_openai_embeddings:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")

        embeddings = OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
        )
        embedding_metadata = EmbeddingMetadata.from_openai(settings.openai_embedding_model)
        print(f"✅ Using OpenAI embeddings ({settings.openai_embedding_model})")
        print(f"   Dimension: {embedding_metadata.dimension}")
    else:
        embeddings = CustomOllamaEmbeddings(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embedding_model,
        )
        embedding_metadata = EmbeddingMetadata.from_ollama(settings.ollama_embedding_model)
        print(f"✅ Using Ollama embeddings ({settings.ollama_embedding_model})")
        print(f"   Dimension: {embedding_metadata.dimension}")

    # Step 4: Store in ChromaDB
    print("\n💾 Storing in ChromaDB...")
    print(f"   Directory: {settings.chroma_persist_directory}")
    print(f"   Provider: {embedding_metadata.provider.value}")

    # Remove existing ChromaDB directory if it exists (avoid readonly errors)
    chroma_path = Path(settings.chroma_persist_directory)
    if chroma_path.exists():
        print(f"   🗑️  Removing existing ChromaDB at {chroma_path}")
        shutil.rmtree(chroma_path)

    # Create adapter and add documents
    adapter = ChromaVectorStoreAdapter(
        persist_directory=settings.chroma_persist_directory,
        embeddings=embeddings,
        embedding_metadata=embedding_metadata,
        validate_metadata=False,
    )

    # Convert to domain Documents and add
    from .domain.ports.vector_store_port import Document as DomainDocument

    domain_chunks = [
        DomainDocument(page_content=chunk.page_content, metadata=chunk.metadata) for chunk in chunks
    ]

    asyncio.run(adapter.add_documents(domain_chunks))

    # Save metadata
    adapter.save_metadata()

    print("✅ ChromaDB populated successfully")
    print(f"✅ Embedding metadata saved")

    # Summary
    print("\n" + "=" * 60)
    print("✅ Data ingestion completed!")
    print("=" * 60)
    print(f"   Chunks stored: {len(chunks)}")
    print(f"   Environment: {settings.environment}")
    print(f"   Vector DB: {settings.chroma_persist_directory}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    ingest_data()
