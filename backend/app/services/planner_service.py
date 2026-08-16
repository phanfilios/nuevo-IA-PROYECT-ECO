from __future__ import annotations

from shapely.geometry import LineString
from shapely.ops import unary_union

from app.geometry.polygons import polygon_coordinates
from app.planning.constraints import (
    CONSERVATION_TYPES,
    RECREATION_TYPES,
    estimate_cost,
    validate_design,
)
from app.planning.paths import connect_zones
from app.planning.vegetation import recommend_species
from app.planning.zoning import generate_zones
from app.schemas.design import Design, Metrics, ValidationResult, WaterFeature, ZoneType
from app.schemas.terrain import ParkRequirements, TerrainInput
from app.services.optimization_service import optimize_design


ALTERNATIVES = [
    ("Alternative A — Biodiversity", "biodiversity"),
    ("Alternative B — Balanced", "balanced"),
    ("Alternative C — Recreation", "recreation"),
]


def _connectivity_index(zones, paths) -> float:
    lines = [LineString(path.coordinates) for path in paths if path.type == ZoneType.PATH]
    targets = [
        zone
        for zone in zones
        if zone.type in {ZoneType.ENTRANCE, ZoneType.CONSERVATION, ZoneType.RECREATION, ZoneType.EDUCATION, ZoneType.REST_AREA}
    ]
    if not lines or not targets:
        return 0.0
    network = unary_union(lines)
    connected = sum(network.distance(LineString(zone.polygon).centroid) <= 2 for zone in targets)
    return round(connected / len(targets) * 100, 2)


def calculate_metrics(terrain: TerrainInput, zones, paths, score: float = 0) -> Metrics:
    total = terrain.total_area_m2 or 0
    conservation = sum(zone.area_m2 for zone in zones if zone.type in CONSERVATION_TYPES)
    recreation = sum(zone.area_m2 for zone in zones if zone.type in RECREATION_TYPES)
    water = sum(zone.area_m2 for zone in zones if zone.type == ZoneType.WATER)
    pedestrian = sum(path.length_m for path in paths if path.type == ZoneType.PATH)
    bicycle = sum(path.length_m for path in paths if path.type == ZoneType.BIKE_PATH)
    ecological = min(100.0, conservation / total * 130 + water / total * 200 + 8) if total else 0.0
    return Metrics(
        total_area_m2=round(total, 2),
        conservation_area_m2=round(conservation, 2),
        conservation_percentage=round(conservation / total * 100, 2) if total else 0,
        recreation_area_m2=round(recreation, 2),
        recreation_percentage=round(recreation / total * 100, 2) if total else 0,
        water_area_m2=round(water, 2),
        path_length_m=round(pedestrian, 2),
        bicycle_path_length_m=round(bicycle, 2),
        zone_count=len(zones),
        connectivity_index=_connectivity_index(zones, paths),
        ecological_index=round(ecological, 2),
        overall_score=score,
        estimated_cost=estimate_cost(zones, paths),
    )


def generate_initial_layout(
    project_id: str,
    terrain: TerrainInput,
    requirements: ParkRequirements,
    alternative: str = "Alternative B — Balanced",
    emphasis: str = "balanced",
    weights: dict[str, float] | None = None,
) -> Design:
    """Deterministic terrain → zones → paths → validation pipeline."""
    boundary, zones = generate_zones(terrain, requirements, emphasis)
    paths = connect_zones(boundary, zones, requirements)
    water_features = [
        WaterFeature(id=f"water-{zone.id}", zone_id=zone.id, area_m2=zone.area_m2)
        for zone in zones
        if zone.type == ZoneType.WATER
    ]
    provisional = Design(
        id="pending",
        project_id=project_id,
        alternative=alternative,
        boundary=polygon_coordinates(boundary),
        zones=zones,
        paths=paths,
        vegetation=recommend_species(terrain, zones),
        water_features=water_features,
        metrics=calculate_metrics(terrain, zones, paths),
        validation=ValidationResult(),
        score=0,
        summary="Pending deterministic validation.",
    )
    validation = validate_design(provisional, terrain, requirements)
    provisional = provisional.model_copy(update={"validation": validation})
    optimized = optimize_design(provisional, requirements, weights)
    return optimized.model_copy(
        update={
            "id": f"design-{__import__('uuid').uuid4().hex}",
            "summary": generate_design_summary(optimized),
        }
    )


def generate_alternatives(
    project_id: str, terrain: TerrainInput, requirements: ParkRequirements, weights: dict[str, float] | None = None
) -> list[Design]:
    return [
        generate_initial_layout(project_id, terrain, requirements, alternative=name, emphasis=emphasis, weights=weights)
        for name, emphasis in ALTERNATIVES
    ]


def explain_design(design: Design) -> str:
    return (
        f"{design.alternative}: {design.metrics.conservation_percentage:.1f}% conservation, "
        f"{design.metrics.recreation_percentage:.1f}% recreation, and "
        f"{design.metrics.path_length_m:.0f} m of pedestrian paths."
    )


def recommend_modifications(design: Design, requirements: ParkRequirements) -> list[str]:
    suggestions: list[str] = []
    if design.metrics.conservation_percentage < requirements.conservation_percentage:
        suggestions.append("Increase the protected conservation zone before adding new programmed uses.")
    if design.metrics.connectivity_index < 100:
        suggestions.append("Add direct accessible links to disconnected primary zones.")
    if requirements.water_features_required and design.metrics.water_area_m2 == 0:
        suggestions.append("Reserve a water-management area and commission hydrology review.")
    return suggestions or ["No automatic modification is required; complete professional site review before implementation."]


def generate_design_summary(design: Design) -> str:
    return (
        f"{explain_design(design)} Preliminary concept only; it does not replace architecture, engineering, "
        "hydrology, environmental, regulatory or permitting studies."
    )
