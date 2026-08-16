from fastapi.testclient import TestClient

from app.main import app


PAYLOAD = {
    "name": "Parque del Río",
    "description": "MVP API test",
    "terrain": {"width_m": 100, "length_m": 100, "climate": "temperate", "soil_type": "loam"},
    "requirements": {"conservation_percentage": 35, "recreation_percentage": 20, "education_percentage": 8},
}


def test_full_api_project_design_validate_regenerate_export_flow():
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        created = client.post("/projects", json=PAYLOAD)
        assert created.status_code == 201, created.text
        project_id = created.json()["id"]
        assert client.get("/projects").status_code == 200
        revised = {**PAYLOAD, "terrain": {**PAYLOAD["terrain"], "width_m": 110}}
        patched = client.patch(f"/projects/{project_id}", json=revised)
        assert patched.status_code == 200
        assert patched.json()["terrain"]["width_m"] == 110
        generated = client.post(f"/projects/{project_id}/designs/generate", json={"alternatives": 3})
        assert generated.status_code == 200, generated.text
        designs = generated.json()
        assert len(designs) == 3
        design_id = designs[0]["id"]
        assert client.get(f"/projects/{project_id}/designs").status_code == 200
        assert client.post(f"/designs/{design_id}/validate").json()["validation"]["valid"]
        assert client.post(f"/designs/{design_id}/regenerate", json={}).status_code == 200
        assert client.get(f"/designs/{design_id}/export/geojson").headers["content-type"].startswith("application/geo+json")
        assert client.get(f"/designs/{design_id}/export/dxf").headers["content-type"].startswith("application/dxf")
        assert client.delete(f"/projects/{project_id}").status_code == 204


def test_api_rejects_invalid_terrain_area_and_unknown_fields():
    invalid = {
        **PAYLOAD,
        "terrain": {"width_m": 100, "length_m": 100, "total_area_m2": 500, "unexpected": True},
    }
    with TestClient(app) as client:
        response = client.post("/projects", json=invalid)
    assert response.status_code == 422
