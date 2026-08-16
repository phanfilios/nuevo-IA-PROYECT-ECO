# Architecture

EcoPark AI separates presentation, orchestration, planning, geometry, validation, exports and persistence.

```text
Next.js client
    │ typed JSON
FastAPI routes ── SQLAlchemy ── PostgreSQL
    │
AI adapter (optional, coordinate-free DesignSpecification)
    │
Planning modules (zoning, paths, vegetation)
    │
Shapely geometry primitives
    │
Constraints and scoring
    │
DXF / GeoJSON / SVG exporters
```

The client does not calculate scores or geometry. `ai_service.py` contains only a constrained, typed handoff. It cannot call planners, exporters or persistence. The planner is deterministic and the exporter refuses invalid designs.

Database tables are `users`, `projects`, `terrain_inputs`, `designs`, `zones`, `plant_species` and `exports`. Project and design payloads are stored as versionable JSON snapshots; normalized terrain and zone tables are also retained for future queries.
