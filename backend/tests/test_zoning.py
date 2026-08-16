from app.planning.constraints import validate_conservation_ratio, validate_zone_overlap
from app.planning.zoning import generate_zones
from app.schemas.design import ZoneType
from app.schemas.terrain import ParkRequirements, TerrainInput


def test_zoning_reserves_required_conservation_without_overlap():
    terrain = TerrainInput(width_m=100, length_m=100)
    requirements = ParkRequirements(conservation_percentage=42, recreation_percentage=20)
    _, zones = generate_zones(terrain, requirements)
    conservation = next(zone for zone in zones if zone.type == ZoneType.CONSERVATION)
    assert conservation.percentage == 42
    assert validate_zone_overlap(zones) == []
    assert validate_conservation_ratio(zones, requirements, terrain.total_area_m2 or 0) == []


def test_water_can_be_omitted_when_not_required():
    terrain = TerrainInput(width_m=100, length_m=100)
    _, zones = generate_zones(terrain, ParkRequirements(water_features_required=False))
    assert not any(zone.type == ZoneType.WATER for zone in zones)
