from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from shapely.geometry import Polygon

from app.geometry.calculations import calculate_area
from app.geometry.polygons import create_rectangle, polygon_coordinates
from app.schemas.design import Zone, ZoneType
from app.schemas.terrain import ParkRequirements, TerrainInput


@dataclass(frozen=True)
class LayoutTargets:
    conservation_percentage: float
    recreation_percentage: float
    education_percentage: float
    water_percentage: float
    rest_percentage: float


def targets_for_requirements(requirements: ParkRequirements, emphasis: str = "balanced") -> LayoutTargets:
    conservation = requirements.conservation_percentage
    recreation = requirements.recreation_percentage
    education = requirements.education_percentage
    if emphasis == "biodiversity":
        conservation = min(85, conservation + 10)
        recreation *= 0.8
    elif emphasis == "recreation":
        recreation = min(60, recreation + 10)

    water = 6.0 if requirements.water_features_required else 0.0
    rest = 4.0
    # Keep at least 7% as flexible open meadow and entrance space. The requested
    # conservation portion is never scaled down because it is a hard constraint.
    available = max(0.0, 93.0 - conservation)
    requested = recreation + education + water + rest
    factor = min(1.0, available / requested) if requested else 1.0
    return LayoutTargets(conservation, recreation * factor, education * factor, water * factor, rest * factor)


def _zone(zone_type: ZoneType, polygon: Polygon, total_area: float, priority: int = 5, **metadata: str) -> Zone:
    area = calculate_area(polygon)
    return Zone(
        id=f"zone-{uuid4().hex[:12]}",
        type=zone_type,
        polygon=polygon_coordinates(polygon),
        area_m2=area,
        percentage=round(area / total_area * 100, 2),
        priority=priority,
        metadata=metadata,
    )


def generate_zones(
    terrain: TerrainInput, requirements: ParkRequirements, emphasis: str = "balanced"
) -> tuple[Polygon, list[Zone]]:
    """Pack non-overlapping rectangular zones inside the rectangular MVP terrain."""
    width, length, total = terrain.width_m, terrain.length_m, terrain.total_area_m2
    assert total is not None
    boundary = create_rectangle(width, length)
    targets = targets_for_requirements(requirements, emphasis)
    conservation_width = width * targets.conservation_percentage / 100
    zones: list[Zone] = [
        _zone(
            ZoneType.CONSERVATION,
            create_rectangle(conservation_width, length),
            total,
            priority=10,
            habitat="protected habitat",
        )
    ]

    remaining_width = width - conservation_width
    if remaining_width <= 0:
        raise ValueError("No usable area remains outside conservation zone")

    y = 0.0

    def add_band(zone_type: ZoneType, percent: float, priority: int, **metadata: str) -> None:
        nonlocal y
        if percent <= 0:
            return
        area = total * percent / 100
        height = area / remaining_width
        polygon = create_rectangle(remaining_width, height, (conservation_width, y))
        zones.append(_zone(zone_type, polygon, total, priority=priority, **metadata))
        y += height

    add_band(ZoneType.WATER, targets.water_percentage, 8, feature="retention pond")
    add_band(ZoneType.RECREATION, targets.recreation_percentage, 7, use="flexible recreation")
    add_band(ZoneType.EDUCATION, targets.education_percentage, 7, use="outdoor education")
    add_band(ZoneType.REST_AREA, targets.rest_percentage, 5, use="shaded rest")

    residual_height = length - y
    if residual_height <= 0.5:
        raise ValueError("Requirements leave insufficient flexible space for the entrance")

    entrance_width = min(8.0, max(2.0, remaining_width * 0.35))
    entrance_height = min(6.0, max(1.0, residual_height * 0.4))
    entrance = create_rectangle(entrance_width, entrance_height, (width - entrance_width, y))
    zones.append(_zone(ZoneType.ENTRANCE, entrance, total, priority=10, access="primary"))

    # Split the remaining meadow around the entrance so the geometric validator
    # can prove that every polygon is non-overlapping.
    left_width = remaining_width - entrance_width
    if left_width > 0.01:
        zones.append(
            _zone(
                ZoneType.MEADOW,
                create_rectangle(left_width, residual_height, (conservation_width, y)),
                total,
                priority=3,
                habitat="pollinator meadow",
            )
        )
    upper_height = residual_height - entrance_height
    if upper_height > 0.01:
        zones.append(
            _zone(
                ZoneType.MEADOW,
                create_rectangle(entrance_width, upper_height, (width - entrance_width, y + entrance_height)),
                total,
                priority=3,
                habitat="pollinator meadow",
            )
        )
    return boundary, zones
