# Run the main ingestion script
run:
	@uv run main.py $(filter-out $@,$(MAKECMDGOALS))

# Database migrations
# Create a new migration with autogenerate
# Usage: make migrate-create MSG="add player stats table"
migrate-create:
	@if [ -z "$(MSG)" ]; then \
		echo "Error: MSG is required. Usage: make migrate-create MSG=\"your message\""; \
		exit 1; \
	fi
	@uv run alembic revision --autogenerate -m "$(MSG)"

# Apply all pending migrations to database
migrate-up:
	@uv run alembic upgrade head

# Rollback last migration
migrate-down:
	@uv run alembic downgrade -1

# Show current migration status
migrate-status:
	@uv run alembic current

# Show migration history
migrate-history:
	@uv run alembic history --verbose

%:
	@:

.PHONY: run migrate-create migrate-up migrate-down migrate-status migrate-history