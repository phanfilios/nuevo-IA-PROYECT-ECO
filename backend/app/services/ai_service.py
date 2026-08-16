from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.terrain import ParkRequirements, TerrainInput
from app.settings import get_settings


class DesignSpecification(BaseModel):
    """Safe, coordinate-free handoff from the optional LLM layer to the planner."""

    emphasis: str = Field(pattern="^(biodiversity|balanced|recreation)$")
    conservation_target_percentage: float = Field(ge=0, le=100)
    recreation_target_percentage: float = Field(ge=0, le=100)
    educational_target_percentage: float = Field(ge=0, le=100)
    include_water: bool
    rationale: str = Field(max_length=1_000)


def interpret_user_requirements(terrain: TerrainInput, requirements: ParkRequirements) -> DesignSpecification:
    """Return a typed, coordinate-free specification.

    A future configured provider may enrich the rationale, but this contract is
    deliberately unable to carry geometry, exports, instructions or code.
    """
    _provider = get_settings().llm_provider  # Configuration remains server-side.
    emphasis = "biodiversity" if requirements.target_biodiversity >= 8 else "balanced"
    return DesignSpecification(
        emphasis=emphasis,
        conservation_target_percentage=requirements.conservation_percentage,
        recreation_target_percentage=requirements.recreation_percentage,
        educational_target_percentage=requirements.education_percentage,
        include_water=requirements.water_features_required,
        rationale=(
            f"Coordinate-free preliminary strategy for a {terrain.climate} site. "
            "The deterministic planner and validator retain final authority."
        ),
    )


def generate_design_strategy(specification: DesignSpecification) -> dict[str, str | float | bool]:
    """Convert an approved spec into planner parameters, never geometry."""
    return specification.model_dump()
