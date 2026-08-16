from app.planning.constraints import validate_design, validate_path_connectivity
from app.schemas.design import ZoneType
from app.schemas.terrain import ParkRequirements, TerrainInput
from app.services.planner_service import generate_alternatives, generate_initial_layout


def test_planner_generates_valid_connected_layout():
    terrain = TerrainInput(width_m=120, length_m=80, slope_percent=8)
    requirements = ParkRequirements(conservation_percentage=35, recreation_percentage=20, bicycle_paths_required=True)
    design = generate_initial_layout("project-1", terrain, requirements)
    assert design.validation.valid
    assert design.metrics.connectivity_index == 100
    assert design.metrics.conservation_percentage >= 35
    assert any(path.type == ZoneType.BIKE_PATH for path in design.paths)
    assert validate_path_connectivity(design.zones, design.paths) == []


def test_generates_three_distinct_alternatives():
    terrain = TerrainInput(width_m=100, length_m=100)
    designs = generate_alternatives("project-1", terrain, ParkRequirements())
    assert len(designs) == 3
    assert len({design.id for design in designs}) == 3
    assert all(design.validation.valid for design in designs)
    assert designs[0].metrics.conservation_percentage > designs[2].metrics.conservation_percentage


def test_validator_detects_overlapping_zone():
    terrain = TerrainInput(width_m=100, length_m=100)
    requirements = ParkRequirements()
    design = generate_initial_layout("project-1", terrain, requirements)
    broken = design.model_copy(update={"zones": [*design.zones, design.zones[0].model_copy(update={"id": "duplicate-zone"})]})
    result = validate_design(broken, terrain, requirements)
    assert not result.valid
    assert any("overlap" in error for error in result.errors)
