from __future__ import annotations

from io import StringIO

import ezdxf

from app.schemas.design import Design, ZoneType

LAYER_BY_ZONE = {
    ZoneType.CONSERVATION: "ECO_CONSERVATION",
    ZoneType.FOREST: "ECO_FOREST",
    ZoneType.MEADOW: "ECO_MEADOW",
    ZoneType.WETLAND: "ECO_WATER",
    ZoneType.WATER: "ECO_WATER",
    ZoneType.RECREATION: "ECO_RECREATION",
    ZoneType.PLAYGROUND: "ECO_RECREATION",
    ZoneType.REST_AREA: "ECO_RECREATION",
    ZoneType.EDUCATION: "ECO_EDUCATION",
    ZoneType.PATH: "ECO_PATH",
    ZoneType.BIKE_PATH: "ECO_BIKE_PATH",
    ZoneType.BUILDING: "ECO_BUILDINGS",
    ZoneType.ENTRANCE: "ECO_ENTRANCE",
    ZoneType.SERVICE: "ECO_BUILDINGS",
    ZoneType.PARKING: "ECO_ENTRANCE",
}
LAYERS = [
    "ECO_BOUNDARY", "ECO_CONSERVATION", "ECO_FOREST", "ECO_MEADOW", "ECO_WATER",
    "ECO_RECREATION", "ECO_EDUCATION", "ECO_PATH", "ECO_BIKE_PATH", "ECO_BUILDINGS",
    "ECO_ENTRANCE", "ECO_LABELS",
]


def export_design_to_dxf(design: Design) -> bytes:
    """Create a standards-compatible R2013 DXF with one semantic layer per element."""
    document = ezdxf.new("R2013")
    for layer in LAYERS:
        if layer not in document.layers:
            document.layers.add(layer)
    modelspace = document.modelspace()
    modelspace.add_lwpolyline(design.boundary, close=True, dxfattribs={"layer": "ECO_BOUNDARY"})
    for zone in design.zones:
        layer = LAYER_BY_ZONE.get(zone.type, "ECO_BUILDINGS")
        modelspace.add_lwpolyline(zone.polygon, close=True, dxfattribs={"layer": layer})
        center_x = sum(point[0] for point in zone.polygon[:-1]) / max(1, len(zone.polygon) - 1)
        center_y = sum(point[1] for point in zone.polygon[:-1]) / max(1, len(zone.polygon) - 1)
        modelspace.add_text(zone.type.value, dxfattribs={"layer": "ECO_LABELS", "height": 1.5}).set_placement((center_x, center_y))
    for path in design.paths:
        modelspace.add_lwpolyline(path.coordinates, dxfattribs={"layer": LAYER_BY_ZONE[path.type], "const_width": path.width_m})
    document.header["$INSUNITS"] = 6  # meters
    stream = StringIO()
    document.write(stream)
    return stream.getvalue().encode("utf-8")
