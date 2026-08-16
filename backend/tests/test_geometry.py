import pytest

from app.geometry.calculations import calculate_area, calculate_perimeter, distance
from app.geometry.polygons import (
    buffer_geometry,
    contains,
    create_polygon,
    create_rectangle,
    difference,
    intersection,
    overlaps,
    union,
)


def test_rectangle_area_perimeter_and_containment():
    terrain = create_rectangle(100, 50)
    inner = create_rectangle(10, 10, (5, 5))
    assert calculate_area(terrain) == 5000
    assert calculate_perimeter(terrain) == 300
    assert contains(terrain, inner)
    assert distance(terrain.boundary, inner) == 5


def test_intersection_difference_buffer_and_union():
    first = create_rectangle(10, 10)
    second = create_rectangle(10, 10, (5, 0))
    assert calculate_area(intersection(first, second)) == 50
    assert calculate_area(difference(first, second)) == 50
    assert calculate_area(union([first, second])) == 150
    assert buffer_geometry(first, 1).area > first.area
    assert overlaps(first, second)


def test_rejects_self_intersecting_polygon():
    with pytest.raises(ValueError):
        create_polygon([(0, 0), (10, 10), (10, 0), (0, 10)])
