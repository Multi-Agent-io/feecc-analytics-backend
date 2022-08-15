from . import client, login


def test_get_schemas_unauthorized():
    """Only authorized users allowed to read information about employees"""
    r = client.get("/api/v1/schemas/")
    assert r.status_code != 200, "unattended access"


def test_get_schemas_authorized():
    token = login()
    r = client.get("/api/v1/schemas/", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.json()


def test_create_schema():
    schema = {
        "schema_id": "123456",
        "unit_name": "testing",
        "production_stages": [{"name": "string", "stage_id": "1"}],
        "required_components_schema_ids": ["string"],
        "parent_schema_id": "123456",
        "schema_type": "testing1",
    }
    token = login()
    r = client.post("/api/v1/schemas/", headers={"Authorization": f"Bearer {token}"}, json=schema)
    assert r.status_code == 200, r.json()


def test_check_new_schema():
    token = login()
    r = client.get("/api/v1/schemas/123456", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("prod_schema", None) is not None, r.json()
    assert r.json().get("prod_schema", None)["unit_name"] == "testing"


def test_patch_schema():
    token = login()
    schema_patch = {
        "schema_id": "broken",
        "unit_name": "new shiny thing",
        "production_stages": None,
        "required_components_schema_ids": None,
        "parent_schema_id": "123456",
        "schema_type": "schema_type",
    }
    r = client.patch("/api/v1/schemas/123456", headers={"Authorization": f"Bearer {token}"}, json=schema_patch)
    assert r.json().get("status_code", None) == 200, r.json()


def test_get_patched_schema():
    token = login()
    r = client.get("/api/v1/schemas/123456", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("status_code", None) == 200, r.json()
    assert r.json().get("prod_schema", {}).get("schema_id", None) == "123456", "You can't change schema_id!"
    assert r.json().get("prod_schema", {}).get("unit_name", None) != "testing", f"Name wasn't changed {r.json()}"


def test_remove_created_schema():
    token = login()
    r = client.delete("/api/v1/schemas/123456", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("status_code", None) == 200


def test_check_deleted_schema():
    token = login()
    r = client.get("/api/v1/schemas/123456", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("prod_schema", None) is None, r.json()
    assert r.json().get("status_code") == 404, r.json()


def test_get_nonexistent_schema():
    token = login()
    r = client.get("/api/v1/schemas/nonexistent", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("prod_schema", None) is None, r.json()
    assert r.json().get("status_code", None) == 404, r.json()
