import pytest
from uuid import uuid4


def test_create_patient_valid(client, sample_patient_data):
    response = client.post("/patients", json=sample_patient_data)
    assert response.status_code == 201
    data = response.json()
    assert "data" in data
    assert "patient_id" in data["data"]
    assert data["error"] is None


def test_create_patient_returns_envelope(client, sample_patient_data):
    response = client.post("/patients", json=sample_patient_data)
    data = response.json()
    assert "data" in data
    assert "error" in data
    assert data["error"] is None


def test_get_patients_empty(client):
    response = client.get("/patients")
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []
    assert data["error"] is None


def test_get_patients_after_create(client, sample_patient_data):
    client.post("/patients", json=sample_patient_data)
    response = client.get("/patients")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["first_name"] == "Jane"
    assert data["data"][0]["last_name"] == "Doe"


def test_get_patient_by_id(client, created_patient):
    patient_id = created_patient["patient_id"]
    response = client.get(f"/patients/{patient_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["patient_id"] == patient_id


def test_get_patient_not_found(client):
    fake_id = str(uuid4())
    response = client.get(f"/patients/{fake_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "PATIENT_NOT_FOUND"


def test_update_patient_partial(client, created_patient):
    patient_id = created_patient["patient_id"]
    response = client.put(f"/patients/{patient_id}", json={"last_name": "Smith"})
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["last_name"] == "Smith"
    assert data["data"]["first_name"] == "Jane"  # unchanged


def test_update_patient_not_found(client):
    fake_id = str(uuid4())
    response = client.put(f"/patients/{fake_id}", json={"last_name": "Smith"})
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "PATIENT_NOT_FOUND"


def test_delete_patient_soft(client, created_patient):
    patient_id = created_patient["patient_id"]
    response = client.delete(f"/patients/{patient_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["deleted_at"] is not None
    
    # Verify GET returns 404
    response = client.get(f"/patients/{patient_id}")
    assert response.status_code == 404


def test_deleted_patient_hidden_from_list(client, created_patient):
    patient_id = created_patient["patient_id"]
    client.delete(f"/patients/{patient_id}")
    response = client.get("/patients")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 0


def test_filter_by_last_name(client):
    # Create two patients with different last names
    client.post("/patients", json={
        "first_name": "Jane", "last_name": "Doe", "date_of_birth": "03/05/1990",
        "sex": "Female", "phone_number": "4155551234", "address_line_1": "100 Main St",
        "city": "San Francisco", "state": "CA", "zip_code": "94105"
    })
    client.post("/patients", json={
        "first_name": "John", "last_name": "Smith", "date_of_birth": "01/15/1985",
        "sex": "Male", "phone_number": "2125550199", "address_line_1": "200 Park Ave",
        "city": "New York", "state": "NY", "zip_code": "10001"
    })
    
    response = client.get("/patients?last_name=Doe")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["last_name"] == "Doe"


def test_filter_by_phone_number(client):
    client.post("/patients", json={
        "first_name": "Jane", "last_name": "Doe", "date_of_birth": "03/05/1990",
        "sex": "Female", "phone_number": "4155551234", "address_line_1": "100 Main St",
        "city": "San Francisco", "state": "CA", "zip_code": "94105"
    })
    
    response = client.get("/patients?phone_number=4155551234")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["phone_number"] == "4155551234"


def test_filter_by_date_of_birth(client):
    client.post("/patients", json={
        "first_name": "Jane", "last_name": "Doe", "date_of_birth": "03/05/1990",
        "sex": "Female", "phone_number": "4155551234", "address_line_1": "100 Main St",
        "city": "San Francisco", "state": "CA", "zip_code": "94105"
    })
    
    response = client.get("/patients?date_of_birth=1990-03-05")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["date_of_birth"] == "1990-03-05"


def test_create_patient_duplicate_phone(client, sample_patient_data):
    # Create first patient
    client.post("/patients", json=sample_patient_data)
    # Create second with same phone - should succeed (no unique constraint on phone)
    response = client.post("/patients", json={
        **sample_patient_data,
        "first_name": "John",
        "last_name": "Doe"
    })
    assert response.status_code == 201