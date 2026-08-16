from __future__ import annotations

from app.exporters.dxf_exporter import export_design_to_dxf
from app.exporters.geojson_exporter import export_design_to_geojson
from app.exporters.svg_exporter import export_design_to_svg
from app.schemas.design import Design


class ExportValidationError(ValueError):
    pass


def ensure_exportable(design: Design) -> None:
    if not design.validation.valid:
        raise ExportValidationError("Invalid designs cannot be exported: " + "; ".join(design.validation.errors))


def export_design(design: Design, export_type: str) -> tuple[bytes, str, str]:
    ensure_exportable(design)
    exporters = {
        "dxf": (export_design_to_dxf, "application/dxf", ".dxf"),
        "geojson": (export_design_to_geojson, "application/geo+json", ".geojson"),
        "svg": (export_design_to_svg, "image/svg+xml", ".svg"),
    }
    try:
        exporter, media_type, extension = exporters[export_type]
    except KeyError as exc:
        raise ValueError(f"Unsupported export format: {export_type}") from exc
    return exporter(design), media_type, extension
