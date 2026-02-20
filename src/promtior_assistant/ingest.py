"""Data ingestion script for scraping and storing Promtior website content."""

import os
import shutil
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from .config import settings
from .rag import CustomOllamaEmbeddings

PDF_DIR = Path(__file__).parent.parent.parent / "docs"


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

        # Clean up multiple newlines
        lines = (line.strip() for line in text.splitlines())
        text = "\n".join(line for line in lines if line)

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
    1. Scrapes the Promtior website
    2. Loads PDFs from docs directory
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

    # Step 1: Scrape website
    try:
        doc = scrape_promtior_website()
        all_documents.append(doc)
    except Exception as e:
        print(f"⚠️  Website scraping failed: {e}")
        logger.warning(f"Website scraping failed: {e}")

    # Step 2: Load PDFs
    pdf_docs = load_pdfs()
    all_documents.extend(pdf_docs)
    logger.info(f"Total documents loaded: {len(all_documents)}")

    if not all_documents:
        raise ValueError("No documents to ingest")

    # Step 3: Split text into chunks
    print("\n✂️  Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_documents(all_documents)
    print(f"✅ Created {len(chunks)} chunks")

    # Step 3: Initialize embeddings
    print("\n🧮 Initializing embeddings...")
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")

        embeddings = OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
        )
        print(f"✅ Using OpenAI embeddings ({settings.openai_embedding_model})")
    else:
        embeddings = CustomOllamaEmbeddings(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embedding_model,
        )
        print(f"✅ Using CustomOllama embeddings ({settings.ollama_embedding_model})")

    # Step 4: Store in ChromaDB
    print("\n💾 Storing in ChromaDB...")
    print(f"   Directory: {settings.chroma_persist_directory}")

    # Remove existing ChromaDB directory if it exists (avoid readonly errors)
    import shutil

    chroma_path = Path(settings.chroma_persist_directory)
    if chroma_path.exists():
        print(f"   🗑️  Removing existing ChromaDB at {chroma_path}")
        shutil.rmtree(chroma_path)

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=settings.chroma_persist_directory,
    )

    print("✅ ChromaDB populated successfully")

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
