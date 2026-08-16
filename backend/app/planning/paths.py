from __future__ import annotations

from uuid import uuid4

from shapely.geometry import LineString, Polygon

from app.geometry.lines import line_coordinates, line_length
from app.geometry.polygons import centroid, create_polygon
from app.schemas.design import Path, Zone, ZoneType
from app.schemas.terrain import ParkRequirements


def _path(kind: ZoneType, coordinates: list[tuple[float, float]], width_m: float, **metadata: str) -> Path:
    line = LineString(coordinates)
    return Path(
        id=f"path-{uuid4().hex[:12]}",
        type=kind,
        coordinates=line_coordinates(line),
        length_m=line_length(line),
        width_m=width_m,
        metadata=metadata,
    )


def _center(zone: Zone) -> tuple[float, float]:
    return centroid(create_polygon(zone.polygon))


def generate_main_path(boundary: Polygon, zones: list[Zone]) -> Path:
    entrance = next(zone for zone in zones if zone.type == ZoneType.ENTRANCE)
    start = _center(entrance)
    min_x, min_y, max_x, max_y = boundary.bounds
    hub = ((min_x + max_x) / 2, (min_y + max_y) / 2)
    targets = [
        zone
        for zone in zones
        if zone.type in {ZoneType.CONSERVATION, ZoneType.RECREATION, ZoneType.EDUCATION, ZoneType.REST_AREA}
    ]
    # A single ordered trunk makes every primary zone reachable from the entrance.
    coordinates = [start, hub, *[_center(zone) for zone in targets]]
    return _path(ZoneType.PATH, coordinates, 3.0, class_name="main")


def generate_secondary_paths(zones: list[Zone], main_path: Path) -> list[Path]:
    hub = main_path.coordinates[1]
    targets = [zone for zone in zones if zone.type in {ZoneType.WATER, ZoneType.MEADOW}]
    return [_path(ZoneType.PATH, [hub, _center(zone)], 1.8, class_name="secondary") for zone in targets]


def generate_bicycle_paths(main_path: Path, enabled: bool) -> list[Path]:
    if not enabled:
        return []
    # Separate logical path layer; the parallel offset is deliberate and does not
    # replace the pedestrian trunk in accessibility checks.
    coordinates = [(x, y + 1.5) for x, y in main_path.coordinates]
    return [_path(ZoneType.BIKE_PATH, coordinates, 2.5, class_name="bicycle")]


def connect_zones(boundary: Polygon, zones: list[Zone], requirements: ParkRequirements) -> list[Path]:
    if not requirements.pedestrian_paths_required:
        return generate_bicycle_paths(generate_main_path(boundary, zones), requirements.bicycle_paths_required)
    main = generate_main_path(boundary, zones)
    return [main, *generate_secondary_paths(zones, main), *generate_bicycle_paths(main, requirements.bicycle_paths_required)]


def validate_path_network(paths: list[Path]) -> bool:
    return bool(paths) and any(path.type == ZoneType.PATH and path.length_m > 0 for path in paths)
