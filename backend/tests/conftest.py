"""
Pytest configuration and fixtures for AutoCbot backend tests
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from database.base import Base
from database.session import get_db
from main import app


@pytest.fixture(scope="function")
def test_db():
    """
    Create a fresh test database for each test
    Uses in-memory SQLite for speed
    """
    # Create in-memory test database
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """
    FastAPI test client with test database
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_strategy_params():
    """Sample strategy parameters for testing"""
    return {
        "symbols": ["BTC/USDT", "ETH/USDT"],
        "timeframe": "1h",
        "indicators": {
            "sma_period": 50,
            "rsi_period": 14,
            "rsi_overbought": 70,
            "rsi_oversold": 30
        },
        "risk_management": {
            "position_size": 0.1,
            "stop_loss": 0.02,
            "take_profit": 0.05
        }
    }
