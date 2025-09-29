.PHONY: help start stop restart logs status clean

help:
	@echo "Neo4j Commands:"
	@echo "  make start    - Start Neo4j knowledge graph database"
	@echo "  make stop     - Stop Neo4j"
	@echo "  make restart  - Restart Neo4j"
	@echo "  make logs     - Show Neo4j logs"
	@echo "  make status   - Show container status"
	@echo "  make clean    - Remove container and volumes (DATA LOSS!)"

start:
	@echo "Starting Neo4j..."
	docker compose up -d

stop:
	@echo "Stopping Neo4j..."
	docker compose down

restart:
	@echo "Restarting Neo4j..."
	docker compose down
	docker compose up -d

logs:
	@echo "Neo4j logs:"
	docker compose logs -f

status:
	@echo "Neo4j status:"
	@docker ps -f "name=vibes-neo4j" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

clean:
	@echo "WARNING: This will delete ALL Neo4j data!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	docker compose down -v
	docker volume rm -f vibes-neo4j-data vibes-neo4j-logs vibes-neo4j-import vibes-neo4j-plugins
	@echo "Neo4j data removed!"
