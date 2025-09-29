.PHONY: help start stop restart logs status clean

help:
	@echo "OpenSearch Commands:"
	@echo "  make start    - Start OpenSearch full-text search"
	@echo "  make stop     - Stop OpenSearch"
	@echo "  make restart  - Restart OpenSearch"
	@echo "  make logs     - Show OpenSearch logs"
	@echo "  make status   - Show container status"
	@echo "  make clean    - Remove container and volumes (DATA LOSS!)"

start:
	@echo "Starting OpenSearch..."
	docker compose up -d

stop:
	@echo "Stopping OpenSearch..."
	docker compose down

restart:
	@echo "Restarting OpenSearch..."
	docker compose down
	docker compose up -d

logs:
	@echo "OpenSearch logs:"
	docker compose logs -f

status:
	@echo "OpenSearch status:"
	@docker ps -f "name=vibes-opensearch" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

clean:
	@echo "WARNING: This will delete ALL OpenSearch data!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker compose down -v
	docker volume rm -f vibes-opensearch-data
	@echo "OpenSearch data removed!"
