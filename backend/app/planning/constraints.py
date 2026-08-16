from __future__ import annotations

from collections.abc import Iterable

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from app.geometry.polygons import contains, create_polygon, overlaps
from app.schemas.design import Design, Path, ValidationResult, Zone, ZoneType
from app.schemas.terrain import ParkRequirements, TerrainInput

CONSERVATION_TYPES = {ZoneType.CONSERVATION, ZoneType.FOREST, ZoneType.WETLAND}
RECREATION_TYPES = {ZoneType.RECREATION, ZoneType.PLAYGROUND, ZoneType.REST_AREA}


def _zone_geometry(zone: Zone) -> Polygon:
    return create_polygon(zone.polygon)


def validate_area_constraints(boundary: Polygon, zones: Iterable[Zone]) -> list[str]:
    errors: list[str] = []
    for zone in zones:
        geometry = _zone_geometry(zone)
        if not contains(boundary, geometry):
            errors.append(f"Zone {zone.id} is outside the terrain boundary")
        if zone.area_m2 <= 0:
            errors.append(f"Zone {zone.id} has no area")
    return errors


def validate_zone_overlap(zones: list[Zone]) -> list[str]:
    errors: list[str] = []
    geometries = [(zone, _zone_geometry(zone)) for zone in zones]
    for index, (left_zone, left) in enumerate(geometries):
        for right_zone, right in geometries[index + 1 :]:
            if overlaps(left, right):
                errors.append(f"Zones {left_zone.id} and {right_zone.id} overlap")
    return errors


def validate_accessibility(zones: list[Zone], paths: list[Path], required: bool) -> list[str]:
    if not required:
        return []
    entrances = [zone for zone in zones if zone.type == ZoneType.ENTRANCE]
    pedestrian = [LineString(path.coordinates) for path in paths if path.type == ZoneType.PATH]
    if not entrances:
        return ["Accessibility requires at least one entrance"]
    if not pedestrian:
        return ["Accessibility requires a pedestrian path"]
    network = unary_union(pedestrian)
    if all(network.distance(Point(_zone_geometry(entry).centroid)) > 2 for entry in entrances):
        return ["No pedestrian path reaches an entrance"]
    return []


def validate_path_connectivity(zones: list[Zone], paths: list[Path]) -> list[str]:
    pedestrian = [LineString(path.coordinates) for path in paths if path.type == ZoneType.PATH]
    if not pedestrian:
        return ["No pedestrian path network was generated"]
    network = unary_union(pedestrian)
    targets = [
        zone
        for zone in zones
        if zone.type in {ZoneType.ENTRANCE, ZoneType.CONSERVATION, ZoneType.RECREATION, ZoneType.EDUCATION, ZoneType.REST_AREA}
    ]
    missing = [zone.id for zone in targets if network.distance(_zone_geometry(zone).centroid) > 2]
    return [f"Path network does not reach zone {zone_id}" for zone_id in missing]


def validate_conservation_ratio(zones: list[Zone], requirements: ParkRequirements, total_area_m2: float) -> list[str]:
    conservation = sum(zone.area_m2 for zone in zones if zone.type in CONSERVATION_TYPES)
    ratio = conservation / total_area_m2 * 100 if total_area_m2 else 0
    if ratio + 0.01 < requirements.conservation_percentage:
        return [f"Conservation ratio {ratio:.1f}% is below required {requirements.conservation_percentage:.1f}%"]
    return []


def validate_water_constraints(zones: list[Zone], requirements: ParkRequirements) -> list[str]:
    if requirements.water_features_required and not any(zone.type in {ZoneType.WATER, ZoneType.WETLAND} for zone in zones):
        return ["Water feature is required but missing"]
    return []


def validate_terrain_constraints(terrain: TerrainInput) -> list[str]:
    if terrain.slope_percent > 35:
        return ["Slope above 35% requires professional terrain engineering before any proposal"]
    return []


def estimate_cost(zones: list[Zone], paths: list[Path]) -> float:
    water_area = sum(zone.area_m2 for zone in zones if zone.type == ZoneType.WATER)
    path_cost = sum(path.length_m * path.width_m * (85 if path.type == ZoneType.PATH else 110) for path in paths)
    zone_cost = sum(zone.area_m2 * 12 for zone in zones if zone.type in RECREATION_TYPES)
    return round(path_cost + water_area * 55 + zone_cost, 2)


def validate_budget_constraints(zones: list[Zone], paths: list[Path], requirements: ParkRequirements) -> list[str]:
    if requirements.estimated_budget is None:
        return []
    cost = estimate_cost(zones, paths)
    if cost > requirements.estimated_budget:
        return [f"Estimated cost {cost:.0f} exceeds budget {requirements.estimated_budget:.0f}"]
    return []


def validate_design(design: Design, terrain: TerrainInput, requirements: ParkRequirements) -> ValidationResult:
    boundary = create_polygon(design.boundary)
    errors = [
        *validate_area_constraints(boundary, design.zones),
        *validate_zone_overlap(design.zones),
        *validate_accessibility(design.zones, design.paths, requirements.accessibility_required),
        *validate_path_connectivity(design.zones, design.paths),
        *validate_conservation_ratio(design.zones, requirements, terrain.total_area_m2 or 0),
        *validate_water_constraints(design.zones, requirements),
        *validate_terrain_constraints(terrain),
        *validate_budget_constraints(design.zones, design.paths, requirements),
    ]
    warnings: list[str] = [
        "Preliminary concept only: obtain local engineering, environmental, accessibility and permitting review."
    ]
    if terrain.slope_percent > 15:
        warnings.append("Moderate slope may require a detailed accessible-route and drainage assessment.")
    score = max(0.0, 100.0 - len(errors) * 20.0 - len(warnings[1:]) * 3.0)
    return ValidationResult(valid=not errors, errors=errors, warnings=warnings, score=score)
