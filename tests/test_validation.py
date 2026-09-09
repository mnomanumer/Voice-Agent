import pytest


def test_invalid_phone_too_short(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "123", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "10001"
    })
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_invalid_phone_letters(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "abcdefghij", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "10001"
    })
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_invalid_phone_too_long(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "12345678901234", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "10001"
    })
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_valid_phone_with_formatting(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "(415) 555-1234", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "10001"
    })
    assert response.status_code == 201
    assert response.json()["data"]["phone_number"] == "4155551234"


def test_valid_phone_with_country_code(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "+1 415 555 1234", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "10001"
    })
    assert response.status_code == 201
    assert response.json()["data"]["phone_number"] == "4155551234"


def test_future_dob(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "User", "date_of_birth": "01/01/2099",
        "sex": "Male", "phone_number": "1234567890", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "10001"
    })
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_invalid_dob_format(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "User", "date_of_birth": "not-a-date",
        "sex": "Male", "phone_number": "1234567890", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "10001"
    })
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_invalid_state(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "1234567890", "address_line_1": "123 St",
        "city": "NYC", "state": "XX", "zip_code": "10001"
    })
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_valid_state_lowercase(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "1234567890", "address_line_1": "123 St",
        "city": "NYC", "state": "ca", "zip_code": "10001"
    })
    assert response.status_code == 201
    assert response.json()["data"]["state"] == "CA"


def test_invalid_zip_short(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "1234567890", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "123"
    })
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_invalid_zip_format(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "1234567890", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "ABCDE"
    })
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_valid_zip_plus_four(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "1234567890", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "94105-1234"
    })
    assert response.status_code == 201


def test_invalid_sex(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Unknown", "phone_number": "1234567890", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "10001"
    })
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_valid_sex_options(client):
    for sex in ["Male", "Female", "Other", "Decline to Answer"]:
        response = client.post("/patients", json={
            "first_name": "Test", "last_name": f"User{sex}", "date_of_birth": "01/01/1990",
            "sex": sex, "phone_number": "1234567890", "address_line_1": "123 St",
            "city": "NYC", "state": "NY", "zip_code": "10001"
        })
        assert response.status_code == 201, f"Failed for sex: {sex}"


def test_empty_first_name(client):
    response = client.post("/patients", json={
        "first_name": "", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "1234567890", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "10001"
    })
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_long_first_name(client):
    response = client.post("/patients", json={
        "first_name": "A" * 51, "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "1234567890", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "10001"
    })
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_name_with_special_chars(client):
    response = client.post("/patients", json={
        "first_name": "Jane<script>", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "1234567890", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "10001"
    })
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_valid_name_with_hyphen(client):
    response = client.post("/patients", json={
        "first_name": "Mary-Jane", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "1234567890", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "10001"
    })
    assert response.status_code == 201


def test_valid_name_with_apostrophe(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "O'Brien", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "1234567890", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "10001"
    })
    assert response.status_code == 201


def test_invalid_email(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "1234567890", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "10001", "email": "not-an-email"
    })
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_valid_email(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "1234567890", "address_line_1": "123 St",
        "city": "NYC", "state": "NY", "zip_code": "10001", "email": "jane@example.com"
    })
    assert response.status_code == 201


def test_empty_address(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "1234567890", "address_line_1": "",
        "city": "NYC", "state": "NY", "zip_code": "10001"
    })
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_empty_city(client):
    response = client.post("/patients", json={
        "first_name": "Test", "last_name": "User", "date_of_birth": "01/01/1990",
        "sex": "Male", "phone_number": "1234567890", "address_line_1": "123 St",
        "city": "", "state": "NY", "zip_code": "10001"
    })
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"