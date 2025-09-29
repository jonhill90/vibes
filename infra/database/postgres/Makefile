.PHONY: help start stop restart logs status clean

help:
	@echo "PostgreSQL Commands:"
	@echo "  make start    - Start PostgreSQL with PGVector"
	@echo "  make stop     - Stop PostgreSQL"
	@echo "  make restart  - Restart PostgreSQL"
	@echo "  make logs     - Show PostgreSQL logs"
	@echo "  make status   - Show container status"
	@echo "  make clean    - Remove container and volumes (DATA LOSS!)"

start:
	@echo "Starting PostgreSQL..."
	docker compose up -d

stop:
	@echo "Stopping PostgreSQL..."
	docker compose down

restart:
	@echo "Restarting PostgreSQL..."
	docker compose down
	docker compose up -d

logs:
	@echo "PostgreSQL logs:"
	docker compose logs -f

status:
	@echo "PostgreSQL status:"
	@docker ps -f "name=vibes-postgres" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

clean:
	@echo "WARNING: This will delete ALL PostgreSQL data!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker compose down -v
	docker volume rm -f vibes-postgres-data
	@echo "PostgreSQL data removed!"
