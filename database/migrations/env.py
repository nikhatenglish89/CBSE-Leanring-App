import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Make `app` importable: database/migrations/env.py -> repo_root/backend
BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
sys.path.append(str(BACKEND_DIR))

from app.core.config import settings  # noqa: E402
from app.models.base import Base  # noqa: E402

# Import every module's models so they register on Base.metadata before
# autogenerate compares against the schema.
from app.modules.auth import models as auth_models  # noqa: E402,F401
from app.modules.banners import models as banners_models  # noqa: E402,F401
from app.modules.users import models as users_models  # noqa: E402,F401
from app.modules.classes import models as classes_models  # noqa: E402,F401
from app.modules.subjects import models as subjects_models  # noqa: E402,F401
from app.modules.courses import models as courses_models  # noqa: E402,F401
from app.modules.lessons import models as lessons_models  # noqa: E402,F401
from app.modules.materials import models as materials_models  # noqa: E402,F401
from app.modules.practice import models as practice_models  # noqa: E402,F401
from app.modules.interaction import models as interaction_models  # noqa: E402,F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

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
