.PHONY: install ollama dev ingest test clean help

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync --all-extras

ollama:  ## Start Ollama and pull models
	docker-compose up -d
	@echo "⏳ Waiting for Ollama to start..."
	@sleep 5
	docker-compose exec ollama ollama pull tinyllama
	docker-compose exec ollama ollama pull nomic-embed-text
	@echo "✅ Ollama ready with tinyllama!"
	@echo "💡 To use larger models, edit .env and pull them:"
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

docker-down:  ## Stop Ollama
	docker-compose down -v
