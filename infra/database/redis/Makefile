.PHONY: help start stop restart logs status clean

help:
	@echo "Redis Commands:"
	@echo "  make start    - Start Redis cache server"
	@echo "  make stop     - Stop Redis"
	@echo "  make restart  - Restart Redis"
	@echo "  make logs     - Show Redis logs"
	@echo "  make status   - Show container status"
	@echo "  make clean    - Remove container and volumes (DATA LOSS!)"

start:
	@echo "Starting Redis..."
	docker compose up -d

stop:
	@echo "Stopping Redis..."
	docker compose down

restart:
	@echo "Restarting Redis..."
	docker compose down
	docker compose up -d

logs:
	@echo "Redis logs:"
	docker compose logs -f

status:
	@echo "Redis status:"
	@docker ps -f "name=vibes-redis" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

clean:
	@echo "WARNING: This will delete ALL Redis data!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker compose down -v
	docker volume rm -f vibes-redis-data
	@echo "Redis data removed!"
