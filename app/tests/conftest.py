import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app, seed_rewards
from app.models.event import Event
from app.models.ledger import LedgerEntry
from app.models.reward import Reward
from app.models.redemption import Redemption

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Creates tables and seeds rewards using a single persistent connection.
    """
    connection = engine.connect()
    
    # Session for the test code (main thread)
    db = TestingSessionLocal(bind=connection)
    
    # Create tables
    Base.metadata.create_all(bind=connection)
    
    # Seed default rewards
    seed_rewards(db)
    
    try:
        yield db
    finally:
        db.close()
        connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """
    Overrides get_db to create a new session bound to the same connection per request.
    This ensures thread-safety while sharing the database state.
    """
    connection = db_session.get_bind()
    
    def override_get_db():
        db = TestingSessionLocal(bind=connection)
        try:
            yield db
        finally:
            db.close()
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
