# EcoPark AI – Engineering Rules

## Architecture and safety

- The LLM is advisory only. It may create a typed `DesignSpecification`, never coordinates, geometry, database records, DXF/SVG/GeoJSON, or executable code.
- The planner creates all layout geometry through the geometry package; the validator must run before an export is made available.
- Geometry uses Shapely and must be validated for bounds, overlap and area constraints. Do not duplicate geometric arithmetic in the AI or frontend.
- Metrics, scores and validation results are calculated by the backend only.
- Never place secrets in source control or expose server API keys to the client.

## Quality gates

- Validate all external input with Pydantic schemas.
- Add tests for every new planner, geometry, validator and export behaviour.
- Run `pytest` after backend changes and `npm run lint`/`npm run build` after frontend changes where the environment supports them.
- The user-facing disclaimer that outputs are preliminary is required in the UI and generated design summaries.
