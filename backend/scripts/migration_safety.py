"""Check Alembic migration state before production deploy."""
import sys

from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine

from app.config import get_settings

HEAD = "007"


def main() -> int:
    settings = get_settings()
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        ctx = MigrationContext.configure(conn)
        current = ctx.get_current_revision()

    cfg = Config("alembic.ini")
    script = ScriptDirectory.from_config(cfg)
    head = script.get_current_head()

    print(f"Current revision: {current}")
    print(f"Head revision:    {head}")
    if current != head:
        print("UNSAFE: Run 'alembic upgrade head' before deploying.")
        return 1
    print("OK: Migrations up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
