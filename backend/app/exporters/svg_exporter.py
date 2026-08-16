from __future__ import annotations

from html import escape

from app.schemas.design import Design, ZoneType

COLORS = {
    ZoneType.CONSERVATION: "#276749",
    ZoneType.FOREST: "#22543d",
    ZoneType.MEADOW: "#9bcf53",
    ZoneType.WETLAND: "#4f9d8d",
    ZoneType.WATER: "#3b82c4",
    ZoneType.RECREATION: "#f3bb54",
    ZoneType.EDUCATION: "#a78bfa",
    ZoneType.REST_AREA: "#e6d5b8",
    ZoneType.ENTRANCE: "#4a5568",
}


def _points(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in points)


def export_design_to_svg(design: Design) -> bytes:
    max_x = max(point[0] for point in design.boundary)
    max_y = max(point[1] for point in design.boundary)
    elements = [
        f'<rect x="0" y="0" width="{max_x}" height="{max_y}" fill="#eef7ed" stroke="#173b2b" stroke-width="0.8" />'
    ]
    for zone in design.zones:
        color = COLORS.get(zone.type, "#b7c6b4")
        elements.append(
            f'<polygon points="{_points(zone.polygon)}" fill="{color}" fill-opacity="0.8" stroke="#ffffff" stroke-width="0.35">'
            f'<title>{escape(zone.type.value)} — {zone.area_m2:.0f} m²</title></polygon>'
        )
    for path in design.paths:
        stroke = "#61737a" if path.type == ZoneType.BIKE_PATH else "#f9fafb"
        elements.append(
            f'<polyline points="{_points(path.coordinates)}" fill="none" stroke="{stroke}" '
            f'stroke-width="{path.width_m}" stroke-linecap="round" stroke-linejoin="round" />'
        )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {max_x} {max_y}" role="img" '
        f'aria-label="EcoPark preliminary design">{"".join(elements)}</svg>'
    )
    return svg.encode("utf-8")
