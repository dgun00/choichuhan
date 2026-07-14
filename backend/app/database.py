from __future__ import annotations

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./localhub.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def apply_sqlite_compatibility_migrations() -> None:
    """
    이전 CRUD DB에 views/likes 컬럼이 없어도 그대로 사용할 수 있게 보정합니다.
    SQLite에서만 동작하며, 이미 컬럼이 있으면 아무 작업도 하지 않습니다.
    """
    if not DATABASE_URL.startswith("sqlite"):
        return

    inspector = inspect(engine)
    if "posts" not in inspector.get_table_names():
        return

    column_names = {column["name"] for column in inspector.get_columns("posts")}

    with engine.begin() as connection:
        if "views" not in column_names:
            connection.execute(
                text("ALTER TABLE posts ADD COLUMN views INTEGER NOT NULL DEFAULT 0")
            )
        if "likes" not in column_names:
            connection.execute(
                text("ALTER TABLE posts ADD COLUMN likes INTEGER NOT NULL DEFAULT 0")
            )
