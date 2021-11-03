import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_utils import create_database, drop_database, database_exists

from app import file_storage as fs
from core.config import TEST_DATABASE_URL
from db.models import Base
from main import app, get_db

engine = create_engine(TEST_DATABASE_URL)


def mock_get_db():
    """
    Override of get_db in app
    """
    SessionLocal = sessionmaker(bind=engine)
    test_db = SessionLocal()

    try:
        yield test_db
    finally:
        test_db.close()


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """
    Creates a clean database before every test and drops it afterwards
    """
    if database_exists(TEST_DATABASE_URL):
        drop_database(TEST_DATABASE_URL)
    create_database(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    app.dependency_overrides[get_db] = mock_get_db
    yield
    drop_database(TEST_DATABASE_URL)


@pytest.fixture(scope="session", autouse=True)
def clear_file_storage():
    """
    Deletes all files in files storage after tests
    """
    yield
    fs.clear()


@pytest.fixture
def test_db_session():
    """
    Creates session before each test and terminates it afterwards
    """
    SessionLocal = sessionmaker(bind=engine)
    session: Session = SessionLocal()
    yield session
    for tbl in reversed(Base.metadata.sorted_tables):
        engine.execute(tbl.delete())
    session.close()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
