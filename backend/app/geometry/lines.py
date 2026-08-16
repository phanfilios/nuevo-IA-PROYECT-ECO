from __future__ import annotations

from collections.abc import Iterable

from shapely.geometry import LineString, Point
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

Coordinate = tuple[float, float]


def create_line(coordinates: Iterable[Coordinate]) -> LineString:
    line = LineString(list(coordinates))
    if not line.is_valid or line.length <= 0:
        raise ValueError("Line must contain at least two distinct points")
    return line


def line_coordinates(line: LineString) -> list[Coordinate]:
    return [(round(x, 6), round(y, 6)) for x, y in line.coords]


def line_length(line: LineString) -> float:
    return round(float(line.length), 2)


def connected_to_network(point: Coordinate, paths: Iterable[LineString], tolerance_m: float = 2.0) -> bool:
    network: BaseGeometry = unary_union(list(paths))
    return network.distance(Point(point)) <= tolerance_m
