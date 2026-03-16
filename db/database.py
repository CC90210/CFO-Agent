"""
db/database.py
--------------
Database engine, session factory, and helpers for Atlas Trading Agent.

Usage
-----
    from db.database import init_db, get_session

    # At application startup:
    init_db()

    # In business logic:
    with get_session() as session:
        trades = session.query(Trade).all()
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import settings
from db.models import Base

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  Engine creation
# ─────────────────────────────────────────────────────────────────────────────


def _build_engine() -> Engine:
    """
    Create and return a SQLAlchemy engine from settings.

    SQLite gets ``check_same_thread=False`` and WAL mode for
    concurrent write safety in async contexts. PostgreSQL uses the
    URL as-is.
    """
    db_url = settings.database.database_url
    is_sqlite = db_url.startswith("sqlite")

    connect_args: dict[str, object] = {}
    if is_sqlite:
        connect_args["check_same_thread"] = False

    engine = create_engine(
        db_url,
        connect_args=connect_args,
        # Echo SQL only at DEBUG level to avoid log spam in production
        echo=settings.logging.log_level == "DEBUG",
        # Connection pool — SQLite in-process doesn't need a pool
        pool_pre_ping=True,
    )

    if is_sqlite:
        _enable_sqlite_wal(engine)

    logger.info("Database engine created: %s", db_url.split("?")[0])
    return engine


def _enable_sqlite_wal(engine: Engine) -> None:
    """
    Switch SQLite to WAL (Write-Ahead Log) journal mode.

    WAL allows concurrent reads during writes, which is important
    when the engine heartbeat and the trade logger run in parallel.
    """

    @event.listens_for(engine, "connect")
    def set_wal_mode(dbapi_conn: object, _connection_record: object) -> None:
        # dbapi_conn is a plain sqlite3 connection at this point
        cursor = dbapi_conn.cursor()  # type: ignore[attr-defined]
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Module-level singletons — built once on import
_engine: Engine = _build_engine()
_SessionFactory: sessionmaker[Session] = sessionmaker(
    bind=_engine, autocommit=False, autoflush=False
)


# ─────────────────────────────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────────────────────────────


def init_db() -> None:
    """
    Create all tables defined in ``db.models`` if they don't yet exist.

    Safe to call multiple times (CREATE TABLE IF NOT EXISTS semantics).
    Intended to be called once at application startup in ``main.py``.
    """
    logger.info("Initialising database tables...")
    Base.metadata.create_all(bind=_engine)
    logger.info("Database ready.")


def get_engine() -> Engine:
    """Return the module-level SQLAlchemy engine."""
    return _engine


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Provide a transactional database session as a context manager.

    Automatically commits on clean exit and rolls back + re-raises
    on any exception.

    Example::

        with get_session() as session:
            session.add(Trade(...))
            # commit happens automatically on exit
    """
    session: Session = _SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def health_check() -> bool:
    """
    Execute a trivial query to verify the database connection is alive.

    Returns True on success, False on failure.
    """
    try:
        with get_session() as session:
            session.execute(text("SELECT 1"))
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Database health check failed: %s", exc)
        return False
