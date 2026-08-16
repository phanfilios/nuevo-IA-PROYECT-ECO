# EcoPark AI

EcoPark AI is a functional MVP for generating **preliminary** ecological-park concepts from a rectangular terrain and explicit project requirements. It produces three deterministic alternatives, validates them geometrically, renders them in 2D, stores projects and exports validated results to DXF, GeoJSON and SVG.

> Important: EcoPark AI does not replace professional engineering, architecture, hydrology, environmental-impact, accessibility, regulatory, permitting or agronomic studies. Plant suggestions and designs are preliminary.

## Architecture

The application enforces this one-way pipeline:

`optional LLM → typed DesignSpecification → deterministic planner → Shapely geometry → validator → export`

The LLM layer has no geometry or exporter capability. It cannot write DXF, GeoJSON, SVG, database rows or files. Metrics, scores and constraints are backend calculations, not AI output.

## Run with Docker

1. Copy `.env.example` to `.env` and set only server-side settings as needed. Do not put an API key in the frontend.
2. Run `docker compose up --build`.
3. Open [http://localhost:3000](http://localhost:3000). The API documentation is at [http://localhost:8000/docs](http://localhost:8000/docs).

Docker starts Next.js, FastAPI and PostgreSQL. Projects, terrain snapshots, designs, zones and export events are persisted in PostgreSQL.

## Local development

Backend:

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
python -m pytest
```

Frontend:

```bash
cd frontend
npm install
npm run dev
npm run build
```

The local backend defaults to a SQLite database for convenience; Docker uses PostgreSQL through `DATABASE_URL`.

## MVP capabilities

- Typed terrain and requirements validation, including area and requested-land constraints.
- Alternative A (Biodiversity), B (Balanced) and C (Recreation).
- Shapely based polygons, areas, intersections, buffers, containment and distances.
- Conservation, water, path connectivity, accessibility, terrain and budget constraints.
- Backend-calculated metrics and configurable optimization weights.
- SVG 2D viewer with zone selection, dimensions, paths and legend.
- DXF layers: `ECO_BOUNDARY`, conservation, forest, meadow, water, recreation, education, path, bike path, building, entrance and label layers.
- GeoJSON, SVG and DXF download after validation; no direct AutoCAD automation.
- Environment configuration, CORS allow-list, payload limit, basic in-memory rate limiting, error logging and no client API keys.

## Current limitations

- The MVP accepts rectangular terrain only; irregular boundaries, topography/GIS and site obstacles are future work.
- The optional LLM provider seam is intentionally disabled by default. No provider client is implemented until a server-side provider and review policy are selected.
- Authentication data structures are prepared, but login/roles are intentionally deferred to Phase 2.
- The cost estimate is a transparent planning heuristic, not a quotation.
- Docker configuration is included; Docker must be installed on the host to run the compose verification.

See [architecture notes](docs/architecture.md), [API reference](docs/api.md), [design engine](docs/design-engine.md) and [CAD integration](docs/autocad-integration.md).
