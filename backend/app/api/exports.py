from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.designs import get_design_or_404
from app.db.database import get_db
from app.models.design import ExportRecord
from app.services.export_service import ExportValidationError, export_design

router = APIRouter(prefix="/designs/{design_id}/export", tags=["exports"])


def download_export(design_id: str, export_type: str, db: Session) -> Response:
    design = get_design_or_404(design_id, db).as_schema()
    try:
        content, media_type, extension = export_design(design, export_type)
    except ExportValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    db.add(ExportRecord(design_id=design_id, export_type=export_type))
    db.commit()
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{design.id}{extension}"'},
    )


@router.get("/dxf")
def export_dxf(design_id: str, db: Session = Depends(get_db)) -> Response:
    return download_export(design_id, "dxf", db)


@router.get("/geojson")
def export_geojson(design_id: str, db: Session = Depends(get_db)) -> Response:
    return download_export(design_id, "geojson", db)


@router.get("/svg")
def export_svg(design_id: str, db: Session = Depends(get_db)) -> Response:
    return download_export(design_id, "svg", db)
