.PHONY: help start stop restart logs status clean

help:
	@echo "Supabase Commands:"
	@echo "  make start    - Start full Supabase stack"
	@echo "  make stop     - Stop Supabase"
	@echo "  make restart  - Restart Supabase"
	@echo "  make logs     - Show Supabase logs"
	@echo "  make status   - Show container status"
	@echo "  make clean    - Remove containers and volumes (DATA LOSS!)"
	@echo ""
	@echo "Access:"
	@echo "  Studio:    http://localhost:3000"
	@echo "  API:       http://localhost:8000"
	@echo "  Database:  postgresql://postgres:password@localhost:5433/postgres"

start:
	@echo "Starting Supabase stack..."
	@if [ ! -f .env ]; then \
		echo "⚠️  Creating .env from .env.example - CHANGE THE PASSWORDS!"; \
		cp .env.example .env; \
	fi
	docker compose up -d

stop:
	@echo "Stopping Supabase..."
	docker compose down

restart:
	@echo "Restarting Supabase..."
	docker compose down
	docker compose up -d

logs:
	@echo "Supabase logs:"
	docker compose logs -f

status:
	@echo "Supabase status:"
	@docker ps -f "name=vibes-supabase" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

clean:
	@echo "WARNING: This will delete ALL Supabase data!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker compose down -v
	docker volume rm -f vibes-supabase-db-data vibes-supabase-vector-data
	@echo "Supabase data removed!"
