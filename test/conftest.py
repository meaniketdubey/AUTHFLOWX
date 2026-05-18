import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base, get_db


# Separate test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_authflowx.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Create tables
Base.metadata.create_all(bind=engine)


# Dependency override
def override_get_db():

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():

    Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)

    yield TestClient(app)

    Base.metadata.drop_all(bind=engine)