import io
import json

import ezdxf

from app.exporters.dxf_exporter import LAYERS, export_design_to_dxf
from app.exporters.geojson_exporter import export_design_to_geojson
from app.exporters.svg_exporter import export_design_to_svg
from app.schemas.terrain import ParkRequirements, TerrainInput
from app.services.planner_service import generate_initial_layout


def _design():
    return generate_initial_layout("project-export", TerrainInput(width_m=100, length_m=80), ParkRequirements())


def test_geojson_has_boundary_zones_and_paths():
    payload = json.loads(export_design_to_geojson(_design()))
    assert payload["type"] == "FeatureCollection"
    assert payload["features"][0]["properties"]["kind"] == "boundary"
    assert any(feature["geometry"]["type"] == "LineString" for feature in payload["features"])


def test_dxf_contains_required_layers_and_entities():
    document = ezdxf.read(io.StringIO(export_design_to_dxf(_design()).decode("utf-8")))
    layer_names = {layer.dxf.name for layer in document.layers}
    assert set(LAYERS).issubset(layer_names)
    assert len(document.modelspace()) > 3


def test_svg_is_renderable_document():
    svg = export_design_to_svg(_design()).decode("utf-8")
    assert svg.startswith("<svg")
    assert "polygon" in svg and "polyline" in svg
