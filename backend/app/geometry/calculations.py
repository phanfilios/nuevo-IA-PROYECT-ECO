from __future__ import annotations

from shapely.geometry.base import BaseGeometry


def calculate_area(geometry: BaseGeometry) -> float:
    return round(float(geometry.area), 2)


def calculate_perimeter(geometry: BaseGeometry) -> float:
    return round(float(geometry.length), 2)


def distance(left: BaseGeometry, right: BaseGeometry) -> float:
    return round(float(left.distance(right)), 4)
