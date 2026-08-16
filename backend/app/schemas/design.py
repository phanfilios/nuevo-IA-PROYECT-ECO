from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ZoneType(StrEnum):
    CONSERVATION = "CONSERVATION"
    FOREST = "FOREST"
    MEADOW = "MEADOW"
    WETLAND = "WETLAND"
    WATER = "WATER"
    RECREATION = "RECREATION"
    EDUCATION = "EDUCATION"
    PLAYGROUND = "PLAYGROUND"
    REST_AREA = "REST_AREA"
    PATH = "PATH"
    BIKE_PATH = "BIKE_PATH"
    SERVICE = "SERVICE"
    PARKING = "PARKING"
    ENTRANCE = "ENTRANCE"
    BUILDING = "BUILDING"


Point = tuple[float, float]


class Zone(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    type: ZoneType
    polygon: list[Point] = Field(min_length=4)
    area_m2: float = Field(ge=0)
    percentage: float = Field(ge=0, le=100)
    priority: int = Field(default=1, ge=1, le=10)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Path(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    type: ZoneType = ZoneType.PATH
    coordinates: list[Point] = Field(min_length=2)
    length_m: float = Field(ge=0)
    width_m: float = Field(default=2.0, gt=0, le=10)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WaterFeature(BaseModel):
    id: str
    zone_id: str
    type: str = "pond"
    area_m2: float = Field(ge=0)


class PlantSpecies(BaseModel):
    name: str
    climate: str
    soil: str
    water_requirement: str
    sunlight: str
    ecological_value: int = Field(ge=1, le=10)
    maintenance_level: str


class VegetationRecommendation(BaseModel):
    species: PlantSpecies
    zones: list[str]
    note: str = "Preliminary recommendation; verify with a local qualified agronomist."


class Metrics(BaseModel):
    total_area_m2: float
    conservation_area_m2: float
    conservation_percentage: float
    recreation_area_m2: float
    recreation_percentage: float
    water_area_m2: float
    path_length_m: float
    bicycle_path_length_m: float
    zone_count: int
    connectivity_index: float = Field(ge=0, le=100)
    ecological_index: float = Field(ge=0, le=100)
    overall_score: float = Field(ge=0, le=100)
    estimated_cost: float


class ValidationResult(BaseModel):
    valid: bool = True
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    score: float = Field(default=0, ge=0, le=100)


class Design(BaseModel):
    id: str
    project_id: str
    alternative: str
    boundary: list[Point]
    zones: list[Zone]
    paths: list[Path]
    vegetation: list[VegetationRecommendation] = Field(default_factory=list)
    water_features: list[WaterFeature] = Field(default_factory=list)
    metrics: Metrics
    validation: ValidationResult
    score: float = Field(ge=0, le=100)
    summary: str


class GenerationRequest(BaseModel):
    alternatives: int = Field(default=3, ge=1, le=3)
    weights: dict[str, float] | None = None


class RegenerationRequest(BaseModel):
    requirements: dict[str, Any] | None = None
    weights: dict[str, float] | None = None
