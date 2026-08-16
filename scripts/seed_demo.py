"""Create a local deterministic demo project without using an external LLM."""

from app.db.database import SessionLocal, init_db
from app.models.project import ProjectRecord, TerrainInputRecord
from app.schemas.terrain import ParkRequirements, TerrainInput
from app.services.planner_service import generate_alternatives


def main() -> None:
    init_db()
    terrain = TerrainInput(width_m=125, length_m=80, climate="temperate", soil_type="loam")
    requirements = ParkRequirements(conservation_percentage=40, recreation_percentage=18, bicycle_paths_required=True)
    with SessionLocal() as db:
        project = ProjectRecord(
            name="Demo EcoPark",
            description="Deterministic local demo",
            terrain=terrain.model_dump(mode="json"),
            requirements=requirements.model_dump(mode="json"),
        )
        db.add(project)
        db.flush()
        db.add(TerrainInputRecord(project_id=project.id, payload=project.terrain))
        # The API persists zone rows too; seed intentionally shows only generation.
        designs = generate_alternatives(project.id, terrain, requirements)
        from app.api.designs import store_design
        for design in designs:
            store_design(db, design, commit=False)
        db.commit()
    print(f"Created demo project {project.id} with {len(designs)} alternatives")


if __name__ == "__main__":
    main()
