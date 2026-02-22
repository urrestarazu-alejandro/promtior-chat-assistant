.PHONY: install ollama dev ingest test clean help quickstart docker-build docker-run docker-dev docker-test docker-logs docker-shell docker-clean docker-rebuild docker-down

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

quickstart:  ## 🚀 One-line setup: install + ollama + ingest + dev server
	@echo "🚀 Starting Promtior RAG Assistant setup..."
	@echo ""
	@echo "Step 1/4: Installing dependencies..."
	@make install
	@echo ""
	@echo "Step 2/4: Setting up Ollama and downloading models..."
	@make ollama
	@echo ""
	@echo "Step 3/4: Ingesting data into ChromaDB..."
	@$(MAKE) quickstart-ingest
	@echo ""
	@echo "Step 4/4: Starting development server..."
	@echo "✅ Setup complete! Server will start now..."
	@echo "📝 Access the API at http://localhost:8000"
	@echo "💡 Try: curl 'http://localhost:8000/ask?q=What is Promtior?'"
	@$(MAKE) quickstart-dev

quickstart-ingest:
	LLM_PROVIDER=ollama OLLAMA_BASE_URL=http://localhost:11434 OLLAMA_MODEL=phi3:mini OLLAMA_EMBEDDING_MODEL=nomic-embed-text $(MAKE) ingest

quickstart-dev:
	LLM_PROVIDER=ollama OLLAMA_BASE_URL=http://localhost:11434 OLLAMA_MODEL=phi3:mini OLLAMA_EMBEDDING_MODEL=nomic-embed-text $(MAKE) dev

install:  ## Install dependencies
	uv sync --all-extras

ollama:  ## Start Ollama and pull models
	docker-compose up -d
	@echo "⏳ Waiting for Ollama to start..."
	@sleep 5
	docker-compose exec ollama ollama pull phi3:mini
	docker-compose exec ollama ollama pull nomic-embed-text
	@echo "✅ Ollama ready with phi3:mini!"
	@echo "💡 To use other models, edit .env and pull them:"
	@echo "   docker exec promtior-ollama ollama pull llama2"
	@echo "   docker exec promtior-ollama ollama pull gpt-oss:20b"

ingest:  ## Run data ingestion
	uv run python -m src.promtior_assistant.ingest

dev:  ## Run development server
	uv run uvicorn src.promtior_assistant.main:app --reload --host 0.0.0.0 --port 8000

test:  ## Run unit tests (fast, mocked)
	uv run pytest -v -m "not integration"

test-all:  ## Run all tests including integration (requires Ollama)
	uv run pytest -v

test-integration:  ## Run only integration tests (requires Ollama)
	uv run pytest -v -m integration

clean:  ## Clean cache files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache

# =============================================================================
# Docker Targets - Production & Development Containers
# =============================================================================

docker-build:  ## 🐳 Build optimized Docker image (production)
	@echo "🏗️  Building production Docker image..."
	docker build -f Dockerfile.optimized --target production -t promtior-assistant:latest .
	@echo "✅ Build complete!"
	@echo "📊 Image size:"
	@docker images promtior-assistant:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

docker-build-dev:  ## 🔧 Build development Docker image
	@echo "🏗️  Building development Docker image..."
	docker build -f Dockerfile.optimized --target development -t promtior-assistant:dev .
	@echo "✅ Development image built!"

docker-rebuild:  ## 🔄 Rebuild Docker image from scratch (no cache)
	@echo "🔄 Rebuilding without cache..."
	docker build -f Dockerfile.optimized --target production --no-cache -t promtior-assistant:latest .
	@echo "✅ Clean rebuild complete!"

docker-test:  ## 🧪 Test Docker build locally
	@echo "🧪 Testing Docker build..."
	@echo ""
	@echo "1️⃣  Building image..."
	@docker build -f Dockerfile.optimized --target production -t promtior-test . || exit 1
	@echo ""
	@echo "2️⃣  Checking image size..."
	@docker images promtior-test --format "Size: {{.Size}}"
	@echo ""
	@echo "3️⃣  Verifying non-root user..."
	@docker run --rm promtior-test whoami
	@echo ""
	@echo "4️⃣  Checking installed packages..."
	@docker run --rm promtior-test pip list | head -10
	@echo ""
	@echo "5️⃣  Testing health check endpoint (requires running container)..."
	@docker run -d --name promtior-test-container -p 8001:8000 promtior-test
	@echo "⏳ Waiting for container to start..."
	@sleep 10
	@curl -f http://localhost:8001/health && echo "✅ Health check passed!" || echo "❌ Health check failed"
	@docker stop promtior-test-container
	@docker rm promtior-test-container
	@docker rmi promtior-test
	@echo ""
	@echo "✅ All Docker tests passed!"

docker-run:  ## 🚀 Run production stack (app + Ollama)
	@echo "🚀 Starting production stack..."
	docker-compose -f docker-compose.full.yml up -d
	@echo "⏳ Waiting for services to be healthy..."
	@sleep 10
	@docker-compose -f docker-compose.full.yml ps
	@echo ""
	@echo "✅ Stack running!"
	@echo "📝 API: http://localhost:8000"
	@echo "🤖 Ollama: http://localhost:11434"
	@echo "💡 Try: curl 'http://localhost:8000/health'"

docker-dev:  ## 🔧 Run development stack with hot reload
	@echo "🔧 Starting development environment..."
	docker-compose -f docker-compose.full.yml -f docker-compose.dev.yml up
	@echo "✅ Development environment ready with hot reload!"

docker-logs:  ## 📋 View container logs
	docker-compose -f docker-compose.full.yml logs -f app

docker-logs-ollama:  ## 📋 View Ollama logs
	docker-compose -f docker-compose.full.yml logs -f ollama

docker-shell:  ## 🐚 Get shell access to app container
	docker-compose -f docker-compose.full.yml exec app /bin/sh

docker-ps:  ## 📊 Show running containers
	@docker-compose -f docker-compose.full.yml ps
	@echo ""
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

docker-clean:  ## 🧹 Stop containers and remove volumes
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose -f docker-compose.full.yml down -v
	@echo "✅ Containers and volumes removed!"

docker-clean-all:  ## 🗑️  Remove all Docker resources (containers, images, cache)
	@echo "⚠️  WARNING: This will remove all promtior Docker resources!"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	docker-compose -f docker-compose.full.yml down -v
	docker rmi promtior-assistant:latest promtior-assistant:dev 2>/dev/null || true
	docker system prune -f
	@echo "✅ All Docker resources cleaned!"

docker-down:  ## ⏹️  Stop all containers
	docker-compose -f docker-compose.full.yml down
