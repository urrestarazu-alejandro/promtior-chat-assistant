#!/bin/bash
# Script de prueba para el sistema de embedding metadata

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}   Testing Embedding Metadata System${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Función para mostrar pasos
step() {
    echo -e "${YELLOW}▶ $1${NC}"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

error() {
    echo -e "${RED}✗ $1${NC}"
}

# Paso 1: Verificar Ollama
step "Checking if Ollama is running..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    success "Ollama is running"
else
    error "Ollama is NOT running. Please start Ollama first."
    exit 1
fi

# Paso 2: Verificar modelos
step "Checking required models..."
if ollama list | grep -q "nomic-embed-text"; then
    success "nomic-embed-text model found"
else
    error "nomic-embed-text not found. Installing..."
    ollama pull nomic-embed-text
fi

if ollama list | grep -q "tinyllama"; then
    success "tinyllama model found"
else
    error "tinyllama not found. Installing..."
    ollama pull tinyllama
fi

# Paso 3: Configurar entorno
step "Setting up environment for Ollama..."
cat > .env << EOF
ENVIRONMENT=development
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
EOF
success "Environment configured"

# Paso 4: Limpiar ChromaDB anterior
step "Cleaning previous ChromaDB..."
if [ -d "data/chroma_db" ]; then
    rm -rf data/chroma_db
    success "Previous ChromaDB removed"
else
    success "No previous ChromaDB found"
fi

# Paso 5: Ejecutar ingesta
step "Running data ingestion..."
uv run python -m src.promtior_assistant.ingest

# Paso 6: Verificar metadata
step "Verifying embedding metadata..."
if [ -f "data/chroma_db/embedding_metadata.json" ]; then
    success "Metadata file created!"
    echo ""
    echo -e "${BLUE}Metadata content:${NC}"
    cat data/chroma_db/embedding_metadata.json | uv run python -m json.tool
    echo ""
else
    error "Metadata file NOT created"
    exit 1
fi

# Paso 7: Ejecutar tests
step "Running unit tests..."
uv run pytest -v -m "not integration" -q

echo ""
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}   ✓ All checks passed!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Start the server: ${BLUE}make dev${NC}"
echo "2. Test the API: ${BLUE}curl 'http://localhost:8000/ask?q=¿Qué es Promtior?'${NC}"
echo "3. View full guide: ${BLUE}docs/TESTING_EMBEDDING_METADATA.md${NC}"
echo ""
