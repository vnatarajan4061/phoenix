import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context

# Import your models and database config
from database import models  # noqa: F401 - Import to register models with Base
from sqlalchemy import engine_from_config, pool

from common.database.base import Base
from common.database.config import get_database_url

ingest_mlb_dir = Path(__file__).resolve().parents[1]
src_dir = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(ingest_mlb_dir))

config = context.config

database_url = get_database_url()
sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
config.set_main_option("sqlalchemy.url", sync_database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
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
