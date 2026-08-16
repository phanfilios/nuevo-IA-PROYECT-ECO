from __future__ import annotations

from app.schemas.design import Design, ZoneType
from app.schemas.terrain import ParkRequirements

DEFAULT_WEIGHTS = {
    "biodiversity": 0.25,
    "conservation": 0.20,
    "accessibility": 0.15,
    "connectivity": 0.15,
    "water": 0.10,
    "recreation": 0.05,
    "maintenance": 0.05,
    "budget": 0.05,
}


def validated_weights(weights: dict[str, float] | None) -> dict[str, float]:
    candidate = {**DEFAULT_WEIGHTS, **(weights or {})}
    if any(value < 0 for value in candidate.values()):
        raise ValueError("Optimization weights cannot be negative")
    total = sum(candidate.values())
    if total <= 0:
        raise ValueError("At least one optimization weight must be positive")
    return {key: value / total for key, value in candidate.items()}


def score_design(design: Design, requirements: ParkRequirements, weights: dict[str, float] | None = None) -> float:
    weights = validated_weights(weights)
    metrics = design.metrics
    conservation = min(100.0, metrics.conservation_percentage / requirements.conservation_percentage * 100)
    recreation = 100.0 if requirements.recreation_percentage == 0 else min(
        100.0, metrics.recreation_percentage / requirements.recreation_percentage * 100
    )
    water_present = any(zone.type in {ZoneType.WATER, ZoneType.WETLAND} for zone in design.zones)
    water = 100.0 if not requirements.water_features_required or water_present else 0.0
    accessibility = 100.0 if not any("Accessibility" in error or "entrance" in error for error in design.validation.errors) else 0.0
    budget = 100.0 if requirements.estimated_budget is None or metrics.estimated_cost <= requirements.estimated_budget else 0.0
    maintenance = {"low": 85.0, "medium": 92.0, "high": 100.0}[requirements.maintenance_level.value]
    components = {
        "biodiversity": metrics.ecological_index,
        "conservation": conservation,
        "accessibility": accessibility,
        "connectivity": metrics.connectivity_index,
        "water": water,
        "recreation": recreation,
        "maintenance": maintenance,
        "budget": budget,
    }
    score = sum(components[key] * weights[key] for key in weights)
    if not design.validation.valid:
        score = min(score, design.validation.score)
    return round(max(0, min(100, score)), 2)


def optimize_design(design: Design, requirements: ParkRequirements, weights: dict[str, float] | None = None) -> Design:
    """Score a valid deterministic alternative; future optimizers can replace this seam."""
    score = score_design(design, requirements, weights)
    metrics = design.metrics.model_copy(update={"overall_score": score})
    return design.model_copy(update={"score": score, "metrics": metrics})
