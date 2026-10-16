import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app


# every test gets a new empty sqlite database in memory,
# so the tests never touch the real postgres
@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, autoflush=False)

    def get_test_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    # use the test db instead of the real one
    app.dependency_overrides[get_db] = get_test_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
