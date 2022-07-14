from datetime import datetime

from . import client, login


def test_get_passports_unauthorized() -> None:
    """Only authorized users allowed to read information about employees"""
    r = client.get("/api/v1/passports/")
    assert r.status_code != 200, "unattended access"


def test_get_passports_authorized() -> None:
    token = login()
    r = client.get("/api/v1/passports/", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.json()


def test_create_passport() -> None:
    passport = {
        "schema_id": "test_simple_unit_1",
        "uuid": "123456",
        "internal_id": "123456",
        "passport_short_url": "url",
        "biography": [],
        "components_internal_ids": None,
        "featured_in_int_id": "123456",
        "barcode": None,
        "model": "testing",
    }
    token = login()
    r = client.post("/api/v1/passports/", headers={"Authorization": f"Bearer {token}"}, json=passport)
    assert r.status_code == 200, r.json()


def test_check_new_passport() -> None:
    token = login()
    r = client.get("/api/v1/passports/123456", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("passport", None) is not None, r.json()
    assert r.json().get("passport", None)["model"] == "Testing simple unit"


new_stage = {
    "name": "testing",
    "employee_name": None,
    "parent_unit_uuid": "12345678",
    "session_start_time": str(datetime.now()),
    "session_end_time": str(datetime.now()),
    "video_hashes": None,
    "additional_info": {},
    "id": "12345678",
    "is_in_db": False,
    "creation_time": str(datetime.now()),
}


# def test_add_stage_to_nonexistent_passport() -> None:
#     token = login()
#     r = client.post(
#         "/api/v1/passports/nonexistent/add_stage", headers={"Authorization": f"Bearer {token}"}, json=new_stage
#     )
#     assert r.status_code != 200, f"Patched nonexistent passport. Wtf?. Resp: {r.json()}"


# def test_add_stage_to_passport() -> None:
#     token = login()
#     r = client.post("/api/v1/passports/123456/add_stage", headers={"Authorization": f"Bearer {token}"}, json=new_stage)
#     assert r.json()["status_code"] == 200, r.json()


# def test_check_added_stage() -> None:
#     token = login()
#     r = client.get("/api/v1/passports/123456", headers={"Authorization": f"Bearer {token}"})
#     assert r.json()["status_code"] == 200, r.json()
#     assert r.json()["passport"].get("biography", None) is not None, r.json()
#     assert r.json()["passport"].get("biography")[0].get("name", None) is not None, r.json()


def test_patch_passport() -> None:
    """
    Ignored fields: {"uuid", "internal_id", "is_in_db", "featured_in_int_id"}. Send anything, nothing will be changed
    """
    token = login()
    passport_patch = {
        "schema_id": "test_composite_unit_1",
        "uuid": "fake",
        "internal_id": "fake",
        "passport_short_url": "new_url",
        "biography": None,
        "components_units": {},
        "featured_in_int_id": "fake",
        "barcode": None,
        "model": "New Model",
    }
    r = client.patch("/api/v1/passports/123456", headers={"Authorization": f"Bearer {token}"}, json=passport_patch)
    assert r.json().get("status_code", None) == 200, r.json()


def test_get_patched_passport() -> None:
    token = login()
    r = client.get("/api/v1/passports/123456", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("status_code", None) == 200, f"Failed to proceed request. Resp: {r.json()}"
    assert r.json().get("passport", None) is not None, f"Patched passport not found. Resp: {r.json()}"
    assert r.json().get("passport").get("model") == "Testing composite unit", f"Failed to patch model. Resp: {r.json()}"
    assert (
        r.json().get("passport").get("internal_id") != "fake"
    ), f"Patched immutable field internal_id. Resp: {r.json()}"
    assert (
        r.json().get("passport").get("passport_short_url") == "new_url"
    ), f"Patched immutable field passport_short_url. Resp: {r.json()}"
    assert r.json().get("passport").get("biography") == [], f"Failed to patch biography. Resp: {r.json()}"


def test_get_filtered_passport() -> None:
    token = login()
    r = client.get("/api/v1/passports/?name=123456", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.json()


def test_remove_created_passport() -> None:
    token = login()
    r = client.delete("/api/v1/passports/123456", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("status_code", None) == 200, r.json()


def test_check_deleted_passport() -> None:
    token = login()
    r = client.get("/api/v1/passports/123456", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("passport", None) is None, r.json()


def test_get_nonexistent_passport() -> None:
    token = login()
    r = client.get("/api/v1/passports/nonexistent", headers={"Authorization": f"Bearer {token}"})
    assert r.json().get("passport", None) is None, r.json()
    assert r.json().get("status_code", None) == 404, r.json()
