import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context

# Import your models and database config
from database import models  # noqa: F401 - Import to register models with Base
from sqlalchemy import engine_from_config, pool

from common.database.base import Base
from common.database.config import get_database_url

# Add parent directories to sys.path to allow imports
# Go up 2 levels to get to ingest-mlb directory
ingest_mlb_dir = Path(__file__).resolve().parents[1]
# Go up to src directory
src_dir = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(ingest_mlb_dir))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set sqlalchemy.url from DATABASE_URL in .env file
# This is required because engine_from_config() expects it to be set
# For migrations, we need to use a sync driver (psycopg2) instead of async (asyncpg)
database_url = get_database_url()
# Replace asyncpg with psycopg2 for synchronous migrations
sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
config.set_main_option("sqlalchemy.url", sync_database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
