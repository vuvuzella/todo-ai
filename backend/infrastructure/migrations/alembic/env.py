from sqlalchemy.sql.expression import text
from logging.config import fileConfig

from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool

from alembic import context

from infrastructure.config import database_settings as migration_settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# inject database connection string
config.set_main_option("sqlalchemy.url", migration_settings.DB_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

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

def db_exists(db_name: str, db_url: str) -> bool:
    """Check if a database exists."""
    engine = create_engine(url=f"{db_url.rsplit('/', 1)[0]}")
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1 FROM pg_database WHERE datname = :dbname"), {'dbname': db_name})
        return result.scalar() is not None

def create_db(db_name: str, db_url: str) -> None:
    """Create a database."""
    engine = create_engine(url=f"{db_url.rsplit('/', 1)[0]}")

    with engine.connect() as connection:
        connection.execution_options(isolation_level="AUTOCOMMIT").execute(text(f"CREATE DATABASE {db_name}"))
        print(f"Database '{db_name}' created successfully.")

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    if not db_exists(migration_settings.DB_NAME, migration_settings.DB_URL):
        create_db(migration_settings.DB_NAME, migration_settings.DB_URL)
        print(f"db created: {migration_settings.DB_NAME}")
    else:
        print(f"database {migration_settings.DB_NAME} already exists")

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
