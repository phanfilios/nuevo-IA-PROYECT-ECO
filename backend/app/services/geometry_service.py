"""Narrow service façade retained for future adapters; geometry stays deterministic."""

from app.geometry.calculations import calculate_area, calculate_perimeter, distance
from app.geometry.polygons import buffer_geometry, centroid, contains, difference, intersection, union

__all__ = [
    "calculate_area", "calculate_perimeter", "distance", "buffer_geometry", "centroid",
    "contains", "difference", "intersection", "union",
]
