from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MaintenanceLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TerrainInput(BaseModel):
    """Measured site data. The MVP accepts a rectangular site only."""

    model_config = ConfigDict(extra="forbid")

    width_m: float = Field(gt=5, le=10_000)
    length_m: float = Field(gt=5, le=10_000)
    total_area_m2: float | None = Field(default=None, gt=25)
    terrain_shape: Literal["rectangle"] = "rectangle"
    slope_percent: float = Field(default=0, ge=0, le=100)
    climate: str = Field(default="temperate", min_length=2, max_length=80)
    soil_type: str = Field(default="loam", min_length=2, max_length=80)
    water_availability: str = Field(default="medium", min_length=2, max_length=80)
    existing_vegetation: str = Field(default="none", max_length=500)
    existing_structures: str = Field(default="none", max_length=500)

    @model_validator(mode="after")
    def validate_supplied_area(self) -> "TerrainInput":
        calculated = self.width_m * self.length_m
        if self.total_area_m2 is not None and abs(self.total_area_m2 - calculated) > max(1, calculated * 0.02):
            raise ValueError("total_area_m2 must match width_m × length_m within 2%")
        self.total_area_m2 = calculated
        return self


class ParkRequirements(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conservation_percentage: float = Field(default=35, ge=5, le=85)
    recreation_percentage: float = Field(default=20, ge=0, le=60)
    education_percentage: float = Field(default=8, ge=0, le=30)
    accessibility_required: bool = True
    water_features_required: bool = True
    pedestrian_paths_required: bool = True
    bicycle_paths_required: bool = False
    lighting_required: bool = False
    estimated_budget: float | None = Field(default=None, gt=0, le=1_000_000_000)
    target_biodiversity: int = Field(default=7, ge=1, le=10)
    maintenance_level: MaintenanceLevel = MaintenanceLevel.MEDIUM

    @model_validator(mode="after")
    def validate_land_request(self) -> "ParkRequirements":
        if self.conservation_percentage + self.recreation_percentage + self.education_percentage > 93:
            raise ValueError("conservation, recreation and education percentages must leave at least 7% flexible space")
        return self
