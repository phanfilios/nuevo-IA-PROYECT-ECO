from __future__ import annotations

from app.schemas.design import PlantSpecies, VegetationRecommendation, Zone, ZoneType
from app.schemas.terrain import TerrainInput


PLANT_CATALOG = [
    PlantSpecies(name="Native oak (regional equivalent)", climate="temperate", soil="loam", water_requirement="medium", sunlight="full sun", ecological_value=9, maintenance_level="medium"),
    PlantSpecies(name="Native sedge (regional equivalent)", climate="temperate", soil="moist", water_requirement="high", sunlight="partial sun", ecological_value=8, maintenance_level="low"),
    PlantSpecies(name="Native flowering meadow mix", climate="temperate", soil="loam", water_requirement="low", sunlight="full sun", ecological_value=8, maintenance_level="low"),
]


def recommend_species(terrain: TerrainInput, zones: list[Zone]) -> list[VegetationRecommendation]:
    """Small, transparent MVP catalog. These are never agronomic prescriptions."""
    by_type = {zone.type: zone.id for zone in zones}
    recommendations: list[VegetationRecommendation] = []
    if ZoneType.CONSERVATION in by_type:
        recommendations.append(VegetationRecommendation(species=PLANT_CATALOG[0], zones=[by_type[ZoneType.CONSERVATION]]))
    if ZoneType.WATER in by_type:
        recommendations.append(VegetationRecommendation(species=PLANT_CATALOG[1], zones=[by_type[ZoneType.WATER]]))
    meadow_ids = [zone.id for zone in zones if zone.type == ZoneType.MEADOW]
    if meadow_ids:
        recommendations.append(VegetationRecommendation(species=PLANT_CATALOG[2], zones=meadow_ids))
    return recommendations


def calculate_vegetation_distribution(zones: list[Zone]) -> dict[str, float]:
    total = sum(zone.area_m2 for zone in zones)
    vegetated = sum(zone.area_m2 for zone in zones if zone.type in {ZoneType.CONSERVATION, ZoneType.MEADOW, ZoneType.WATER})
    return {"vegetated_area_m2": round(vegetated, 2), "vegetated_percentage": round(vegetated / total * 100, 2) if total else 0}
