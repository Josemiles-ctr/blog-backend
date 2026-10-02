import os
from collections.abc import Generator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from supabase import Client, create_client

from src.domain.entities import Base

# Anchored to the repository root instead of the working directory: bare
# load_dotenv() searches relative to how the process was launched, so running
# from anywhere but the project root silently lost DATABASE_URL.
PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")


def _require_env(key: str) -> str:
    value = os.getenv(key, "").strip()
    if not value:
        raise RuntimeError(
            f"{key} is not set. Copy .env.example to .env and fill in the value."
        )
    return value


def _normalize_url(url: str) -> str:
    # Supabase hands out a plain "postgresql://" URI, but SQLAlchemy maps that to
    # psycopg2. This project uses psycopg3, so we pin the driver when none is given.
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


_raw_url = _require_env("DATABASE_URL")

DATABASE_URL = _normalize_url(_raw_url)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

_supabase_client: Client | None = None


def get_supabase() -> Client:
    # Built on first use rather than at import: the API keys are not needed for
    # database access, and a missing key should not stop the app from booting.
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            _require_env("SUPABASE_URL"),
            _require_env("SUPABASE_KEY"),
        )
    return _supabase_client


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()