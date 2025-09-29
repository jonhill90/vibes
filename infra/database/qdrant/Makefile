.PHONY: help start stop restart logs status clean

help:
	@echo "Qdrant Commands:"
	@echo "  make start    - Start Qdrant vector database"
	@echo "  make stop     - Stop Qdrant"
	@echo "  make restart  - Restart Qdrant"
	@echo "  make logs     - Show Qdrant logs"
	@echo "  make status   - Show container status"
	@echo "  make clean    - Remove container and volumes (DATA LOSS!)"

start:
	@echo "Starting Qdrant..."
	docker compose up -d

stop:
	@echo "Stopping Qdrant..."
	docker compose down

restart:
	@echo "Restarting Qdrant..."
	docker compose down
	docker compose up -d

logs:
	@echo "Qdrant logs:"
	docker compose logs -f

status:
	@echo "Qdrant status:"
	@docker ps -f "name=vibes-qdrant" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

clean:
	@echo "WARNING: This will delete ALL Qdrant data!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker compose down -v
	docker volume rm -f vibes-qdrant-data
	@echo "Qdrant data removed!"
