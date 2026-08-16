# API

All mutation bodies are validated with Pydantic; unknown fields are rejected.

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Readiness probe |
| POST / GET | `/projects` | Create or list projects |
| GET / PATCH / DELETE | `/projects/{id}` | Read, edit inputs, or delete a project |
| POST | `/projects/{id}/designs/generate` | Generate one to three alternatives |
| GET | `/projects/{id}/designs` | List saved alternatives |
| GET | `/designs/{id}` | Read a saved design |
| POST | `/designs/{id}/regenerate` | Replan an alternative with changed requirements |
| POST | `/designs/{id}/validate` | Re-run deterministic validation |
| GET | `/designs/{id}/export/dxf` | Download valid DXF |
| GET | `/designs/{id}/export/geojson` | Download valid GeoJSON |
| GET | `/designs/{id}/export/svg` | Download valid SVG |

`POST /projects/{id}/designs/generate` accepts `{ "alternatives": 3, "weights": { "biodiversity": 0.25 } }`. Weights are normalized on the server. A DXF is unavailable (`422`) when validation fails.
