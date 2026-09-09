import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import get_db, Base
from app.db import models  # noqa: F401


@pytest.fixture(scope="session")
def engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """Create a fresh database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = SessionLocal()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_patient_data():
    """Return a sample valid patient data dict."""
    return {
        "first_name": "Jane",
        "last_name": "Doe",
        "date_of_birth": "03/05/1990",
        "sex": "Female",
        "phone_number": "4155551234",
        "address_line_1": "100 Main Street",
        "city": "San Francisco",
        "state": "CA",
        "zip_code": "94105",
    }


@pytest.fixture
def created_patient(client, sample_patient_data):
    """Create a patient and return the response data."""
    response = client.post("/patients", json=sample_patient_data)
    assert response.status_code == 201
    return response.json()["data"]