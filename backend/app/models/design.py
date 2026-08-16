from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.schemas.design import Design


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DesignRecord(Base):
    __tablename__ = "designs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    alternative: Mapped[str] = mapped_column(String(80))
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    project: Mapped["ProjectRecord"] = relationship(back_populates="designs")
    zones: Mapped[list["ZoneRecord"]] = relationship(back_populates="design", cascade="all, delete-orphan")
    exports: Mapped[list["ExportRecord"]] = relationship(back_populates="design", cascade="all, delete-orphan")

    def as_schema(self) -> Design:
        return Design.model_validate(self.payload)


class ZoneRecord(Base):
    __tablename__ = "zones"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    design_id: Mapped[str] = mapped_column(ForeignKey("designs.id", ondelete="CASCADE"), index=True)
    zone_type: Mapped[str] = mapped_column(String(30))
    payload: Mapped[dict] = mapped_column(JSON)
    design: Mapped[DesignRecord] = relationship(back_populates="zones")


class ExportRecord(Base):
    __tablename__ = "exports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    design_id: Mapped[str] = mapped_column(ForeignKey("designs.id", ondelete="CASCADE"), index=True)
    export_type: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    design: Mapped[DesignRecord] = relationship(back_populates="exports")
