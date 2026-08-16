from __future__ import annotations

import json

from app.schemas.design import Design


def export_design_to_geojson(design: Design) -> bytes:
    features = [
        {
            "type": "Feature",
            "id": "terrain-boundary",
            "geometry": {"type": "Polygon", "coordinates": [[list(point) for point in design.boundary]]},
            "properties": {"kind": "boundary", "project_id": design.project_id},
        }
    ]
    for zone in design.zones:
        features.append(
            {
                "type": "Feature",
                "id": zone.id,
                "geometry": {"type": "Polygon", "coordinates": [[list(point) for point in zone.polygon]]},
                "properties": {
                    "kind": "zone",
                    "zone_type": zone.type.value,
                    "area_m2": zone.area_m2,
                    "percentage": zone.percentage,
                    "priority": zone.priority,
                    **zone.metadata,
                },
            }
        )
    for path in design.paths:
        features.append(
            {
                "type": "Feature",
                "id": path.id,
                "geometry": {"type": "LineString", "coordinates": [list(point) for point in path.coordinates]},
                "properties": {"kind": "path", "path_type": path.type.value, "length_m": path.length_m, **path.metadata},
            }
        )
    collection = {
        "type": "FeatureCollection",
        "name": f"ecopark-{design.id}",
        "properties": {"preliminary": True, "score": design.score},
        "features": features,
    }
    return json.dumps(collection, ensure_ascii=False, indent=2).encode("utf-8")
