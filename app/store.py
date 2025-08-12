"""SQLite storage and Pydantic models for positions and settings."""
from __future__ import annotations

import datetime as dt
from typing import List, Optional, Dict, Any

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    select,
    update as sql_update,
    delete as sql_delete,
)
from sqlalchemy.orm import declarative_base, Session
from pydantic import BaseModel, validator

DB_PATH = "data/app.db"
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
Base = declarative_base()


class PositionORM(Base):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True)
    ticker = Column(String)
    type = Column(String)
    expiry = Column(String)
    long_strike = Column(Float)
    short_strike = Column(Float, nullable=True)
    entry_price = Column(Float)
    entry_date = Column(String, nullable=True)
    quantity = Column(Integer, default=1)
    previous_peak = Column(Float, nullable=True)
    enabled = Column(Integer, default=1)
    created_at = Column(String)
    updated_at = Column(String)


class SettingsORM(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    poll_minutes = Column(Integer, default=10)
    notify_slack = Column(Integer, default=0)
    notify_email = Column(Integer, default=0)
    notify_telegram = Column(Integer, default=0)


# ensure tables
Base.metadata.create_all(engine)


class PositionIn(BaseModel):
    """Input model for creating/updating a position."""

    ticker: str
    type: str
    expiry: str
    long_strike: float
    short_strike: Optional[float] = None
    entry_price: float
    entry_date: Optional[str] = None
    quantity: int = 1
    previous_peak: Optional[float] = None

    @validator("ticker")
    def upper_ticker(cls, v: str) -> str:  # noqa: D401
        """Ensure ticker is upper-case."""
        return v.upper()


class PositionOut(PositionIn):
    """Output model including position id and enabled flag."""

    id: int
    enabled: int
    created_at: str
    updated_at: str


class SettingsOut(BaseModel):
    """Application settings."""

    poll_minutes: int
    notify_slack: int
    notify_email: int
    notify_telegram: int


# CRUD helpers

def list_positions() -> List[PositionOut]:
    with Session(engine) as ses:
        rows = ses.execute(select(PositionORM)).scalars().all()
        return [PositionOut(**row.__dict__) for row in rows]


def get_position(pid: int) -> Optional[PositionOut]:
    with Session(engine) as ses:
        row = ses.get(PositionORM, pid)
        return PositionOut(**row.__dict__) if row else None


def create_position(data: Dict[str, Any]) -> PositionOut:
    now = dt.datetime.utcnow().isoformat()
    obj = PositionORM(**data, created_at=now, updated_at=now)
    with Session(engine) as ses:
        ses.add(obj)
        ses.commit()
        ses.refresh(obj)
        return PositionOut(**obj.__dict__)


def update_position(pid: int, data: Dict[str, Any]) -> Optional[PositionOut]:
    now = dt.datetime.utcnow().isoformat()
    with Session(engine) as ses:
        ses.execute(
            sql_update(PositionORM)
            .where(PositionORM.id == pid)
            .values(**data, updated_at=now)
        )
        ses.commit()
        row = ses.get(PositionORM, pid)
        return PositionOut(**row.__dict__) if row else None


def delete_position(pid: int) -> None:
    with Session(engine) as ses:
        ses.execute(sql_delete(PositionORM).where(PositionORM.id == pid))
        ses.commit()


def toggle_position(pid: int, enabled: int) -> Optional[PositionOut]:
    return update_position(pid, {"enabled": enabled})


def get_settings() -> SettingsOut:
    with Session(engine) as ses:
        row = ses.get(SettingsORM, 1)
        if not row:
            row = SettingsORM(id=1)
            ses.add(row)
            ses.commit()
            ses.refresh(row)
        return SettingsOut(
            poll_minutes=row.poll_minutes,
            notify_slack=row.notify_slack,
            notify_email=row.notify_email,
            notify_telegram=row.notify_telegram,
        )


def update_settings(**vals: Any) -> SettingsOut:
    with Session(engine) as ses:
        row = ses.get(SettingsORM, 1)
        if not row:
            row = SettingsORM(id=1)
            ses.add(row)
        for k, v in vals.items():
            setattr(row, k, v)
        ses.commit()
        ses.refresh(row)
        return SettingsOut(
            poll_minutes=row.poll_minutes,
            notify_slack=row.notify_slack,
            notify_email=row.notify_email,
            notify_telegram=row.notify_telegram,
        )
