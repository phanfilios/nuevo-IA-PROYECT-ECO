from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.project import ProjectRecord, TerrainInputRecord
from app.schemas.project import Project, ProjectCreate, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_or_404(project_id: str, db: Session) -> ProjectRecord:
    project = db.get(ProjectRecord, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> Project:
    project = ProjectRecord(
        name=payload.name.strip(),
        description=payload.description.strip(),
        terrain=payload.terrain.model_dump(mode="json"),
        requirements=payload.requirements.model_dump(mode="json"),
    )
    db.add(project)
    db.flush()
    db.add(TerrainInputRecord(project_id=project.id, payload=payload.terrain.model_dump(mode="json")))
    db.commit()
    db.refresh(project)
    return project.as_schema()


@router.get("", response_model=list[Project])
def list_projects(db: Session = Depends(get_db)) -> list[Project]:
    projects = db.scalars(select(ProjectRecord).order_by(ProjectRecord.updated_at.desc())).all()
    return [project.as_schema() for project in projects]


@router.get("/{project_id}", response_model=Project)
def get_project(project_id: str, db: Session = Depends(get_db)) -> Project:
    return get_project_or_404(project_id, db).as_schema()


@router.patch("/{project_id}", response_model=Project)
def update_project(project_id: str, payload: ProjectUpdate, db: Session = Depends(get_db)) -> Project:
    project = get_project_or_404(project_id, db)
    if payload.name is not None:
        project.name = payload.name.strip()
    if payload.description is not None:
        project.description = payload.description.strip()
    if payload.terrain is not None:
        project.terrain = payload.terrain.model_dump(mode="json")
        terrain_row = db.scalar(select(TerrainInputRecord).where(TerrainInputRecord.project_id == project.id))
        if terrain_row is not None:
            terrain_row.payload = project.terrain
    if payload.requirements is not None:
        project.requirements = payload.requirements.model_dump(mode="json")
    db.commit()
    db.refresh(project)
    return project.as_schema()


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, db: Session = Depends(get_db)) -> Response:
    project = get_project_or_404(project_id, db)
    db.delete(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
