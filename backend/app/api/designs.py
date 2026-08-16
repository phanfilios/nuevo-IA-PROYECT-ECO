from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.projects import get_project_or_404
from app.db.database import get_db
from app.models.design import DesignRecord, ZoneRecord
from app.models.project import ProjectRecord
from app.planning.constraints import validate_design
from app.schemas.design import Design, GenerationRequest, RegenerationRequest
from app.schemas.terrain import ParkRequirements, TerrainInput
from app.services.optimization_service import optimize_design
from app.services.planner_service import generate_alternatives, generate_initial_layout

router = APIRouter(tags=["designs"])


def get_design_or_404(design_id: str, db: Session) -> DesignRecord:
    design = db.get(DesignRecord, design_id)
    if design is None:
        raise HTTPException(status_code=404, detail="Design not found")
    return design


def store_design(db: Session, design: Design, *, commit: bool = True) -> DesignRecord:
    record = db.get(DesignRecord, design.id)
    if record is None:
        record = DesignRecord(
            id=design.id,
            project_id=design.project_id,
            alternative=design.alternative,
            payload=design.model_dump(mode="json"),
        )
        db.add(record)
        db.flush()
    else:
        record.alternative = design.alternative
        record.payload = design.model_dump(mode="json")
        record.zones.clear()
        db.flush()
    for zone in design.zones:
        record.zones.append(ZoneRecord(id=zone.id, zone_type=zone.type.value, payload=zone.model_dump(mode="json")))
    if commit:
        db.commit()
        db.refresh(record)
    return record


@router.post("/projects/{project_id}/designs/generate", response_model=list[Design])
def generate_project_designs(
    project_id: str, payload: GenerationRequest, db: Session = Depends(get_db)
) -> list[Design]:
    project = get_project_or_404(project_id, db)
    terrain = TerrainInput.model_validate(project.terrain)
    requirements = ParkRequirements.model_validate(project.requirements)
    alternatives = generate_alternatives(project.id, terrain, requirements, payload.weights)[: payload.alternatives]
    for design in alternatives:
        store_design(db, design, commit=False)
    db.commit()
    return alternatives


@router.get("/projects/{project_id}/designs", response_model=list[Design])
def list_project_designs(project_id: str, db: Session = Depends(get_db)) -> list[Design]:
    get_project_or_404(project_id, db)
    records = db.scalars(select(DesignRecord).where(DesignRecord.project_id == project_id).order_by(DesignRecord.created_at.desc())).all()
    return [record.as_schema() for record in records]


@router.get("/designs/{design_id}", response_model=Design)
def get_design(design_id: str, db: Session = Depends(get_db)) -> Design:
    return get_design_or_404(design_id, db).as_schema()


@router.post("/designs/{design_id}/regenerate", response_model=Design)
def regenerate_design(
    design_id: str, payload: RegenerationRequest, db: Session = Depends(get_db)
) -> Design:
    record = get_design_or_404(design_id, db)
    project = get_project_or_404(record.project_id, db)
    terrain = TerrainInput.model_validate(project.terrain)
    base_requirements = ParkRequirements.model_validate(project.requirements)
    requirements = base_requirements if payload.requirements is None else ParkRequirements.model_validate(
        {**base_requirements.model_dump(), **payload.requirements}
    )
    previous = record.as_schema()
    emphasis = "biodiversity" if "Biodiversity" in previous.alternative else "recreation" if "Recreation" in previous.alternative else "balanced"
    regenerated = generate_initial_layout(
        project.id, terrain, requirements, previous.alternative, emphasis, payload.weights
    ).model_copy(update={"id": design_id})
    store_design(db, regenerated)
    return regenerated


@router.post("/designs/{design_id}/validate", response_model=Design)
def validate_saved_design(design_id: str, db: Session = Depends(get_db)) -> Design:
    record = get_design_or_404(design_id, db)
    project = get_project_or_404(record.project_id, db)
    design = record.as_schema()
    validated = design.model_copy(
        update={
            "validation": validate_design(
                design, TerrainInput.model_validate(project.terrain), ParkRequirements.model_validate(project.requirements)
            )
        }
    )
    validated = optimize_design(validated, ParkRequirements.model_validate(project.requirements))
    store_design(db, validated)
    return validated
