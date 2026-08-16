from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.schemas.project import Project
from app.schemas.terrain import ParkRequirements, TerrainInput


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserRecord(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class ProjectRecord(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, default="")
    terrain: Mapped[dict] = mapped_column(JSON)
    requirements: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
    designs: Mapped[list["DesignRecord"]] = relationship(back_populates="project", cascade="all, delete-orphan")

    def as_schema(self) -> Project:
        return Project(
            id=self.id,
            name=self.name,
            description=self.description,
            terrain=TerrainInput.model_validate(self.terrain),
            requirements=ParkRequirements.model_validate(self.requirements),
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


class TerrainInputRecord(Base):
    """Normalized terrain table kept alongside the project JSON snapshot for future querying."""

    __tablename__ = "terrain_inputs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), unique=True)
    payload: Mapped[dict] = mapped_column(JSON)


class PlantSpeciesRecord(Base):
    __tablename__ = "plant_species"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(200), unique=True)
    payload: Mapped[dict] = mapped_column(JSON)
