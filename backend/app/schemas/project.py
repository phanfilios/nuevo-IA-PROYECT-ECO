from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .terrain import ParkRequirements, TerrainInput


class ProjectCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=1_000)
    terrain: TerrainInput
    requirements: ParkRequirements


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=1_000)
    terrain: TerrainInput | None = None
    requirements: ParkRequirements | None = None


class Project(BaseModel):
    id: str
    name: str
    description: str
    terrain: TerrainInput
    requirements: ParkRequirements
    created_at: datetime
    updated_at: datetime
