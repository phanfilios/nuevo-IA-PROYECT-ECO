from __future__ import annotations

from collections.abc import Iterable

from shapely.geometry import GeometryCollection, Polygon
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

Point = tuple[float, float]


def _coordinates(geometry: BaseGeometry) -> list[Point]:
    if geometry.is_empty:
        return []
    if geometry.geom_type != "Polygon":
        raise ValueError(f"Expected a Polygon, received {geometry.geom_type}")
    return [(round(x, 6), round(y, 6)) for x, y in geometry.exterior.coords]


def create_rectangle(width_m: float, length_m: float, origin: Point = (0, 0)) -> Polygon:
    if width_m <= 0 or length_m <= 0:
        raise ValueError("Rectangle dimensions must be positive")
    x, y = origin
    return Polygon([(x, y), (x + width_m, y), (x + width_m, y + length_m), (x, y + length_m)])


def create_polygon(points: Iterable[Point]) -> Polygon:
    polygon = Polygon(list(points))
    if not polygon.is_valid or polygon.area <= 0:
        raise ValueError("Polygon must be valid and have a positive area")
    return polygon


def polygon_coordinates(geometry: BaseGeometry) -> list[Point]:
    return _coordinates(geometry)


def buffer_geometry(geometry: BaseGeometry, distance_m: float) -> BaseGeometry:
    if distance_m == 0:
        return geometry
    result = geometry.buffer(distance_m)
    if result.is_empty or not result.is_valid:
        raise ValueError("Buffer produced invalid geometry")
    return result


def intersection(left: BaseGeometry, right: BaseGeometry) -> BaseGeometry:
    return left.intersection(right)


def difference(left: BaseGeometry, right: BaseGeometry) -> BaseGeometry:
    return left.difference(right)


def union(geometries: Iterable[BaseGeometry]) -> BaseGeometry:
    return unary_union(list(geometries))


def contains(container: BaseGeometry, candidate: BaseGeometry) -> bool:
    return container.covers(candidate)


def overlaps(left: BaseGeometry, right: BaseGeometry, tolerance_m2: float = 1e-6) -> bool:
    return left.intersection(right).area > tolerance_m2


def centroid(geometry: BaseGeometry) -> Point:
    center = geometry.centroid
    return (round(center.x, 6), round(center.y, 6))


def as_polygon(geometry: BaseGeometry) -> Polygon:
    """Return a single polygon, rejecting multi-part results that the MVP schema cannot represent."""
    if isinstance(geometry, Polygon):
        return geometry
    if isinstance(geometry, GeometryCollection) and len(geometry.geoms) == 1:
        item = geometry.geoms[0]
        if isinstance(item, Polygon):
            return item
    raise ValueError("Operation resulted in multipart geometry")
