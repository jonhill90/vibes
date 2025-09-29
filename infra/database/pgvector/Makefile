.PHONY: help start stop restart logs status clean test

help:
	@echo "PGVector Commands:"
	@echo "  make start    - Start PGVector database"
	@echo "  make stop     - Stop PGVector"
	@echo "  make restart  - Restart PGVector"
	@echo "  make logs     - Show PGVector logs"
	@echo "  make status   - Show container status"
	@echo "  make test     - Test vector operations"
	@echo "  make clean    - Remove container and volumes (DATA LOSS!)"
	@echo ""
	@echo "Connection:"
	@echo "  Host: postgresql://postgres:vibes123@localhost:5435/vectors"
	@echo "  Container: postgresql://postgres:vibes123@vibes-pgvector:5432/vectors"

start:
	@echo "Starting PGVector database..."
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.example"; \
		cp .env.example .env; \
	fi
	docker compose up -d

stop:
	@echo "Stopping PGVector..."
	docker compose down

restart:
	@echo "Restarting PGVector..."
	docker compose down
	docker compose up -d

logs:
	@echo "PGVector logs:"
	docker compose logs -f

status:
	@echo "PGVector status:"
	@docker ps -f "name=vibes-pgvector" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

test:
	@echo "Testing PGVector operations..."
	@docker exec vibes-pgvector psql -U postgres -d vectors -c "\
		SELECT 'Vector extension loaded' as status, extversion \
		FROM pg_extension WHERE extname = 'vector';" 2>/dev/null || echo "Container not running"
	@docker exec vibes-pgvector psql -U postgres -d vectors -c "\
		SELECT * FROM document_stats;" 2>/dev/null || echo "Container not running"

clean:
	@echo "WARNING: This will delete ALL PGVector data!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker compose down -v
	docker volume rm -f vibes-pgvector-data
	@echo "PGVector data removed!"
