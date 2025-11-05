"""
Pytest Configuration for AutoCbot Tests
Shared fixtures and configuration
"""

import pytest
import asyncio
import os
from typing import Generator
from pathlib import Path

# Add backend to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def backend_url() -> str:
    """Backend API URL"""
    return os.getenv("TEST_BACKEND_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def frontend_url() -> str:
    """Frontend URL"""
    return os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")


@pytest.fixture(scope="session")
def test_symbols() -> list:
    """Test symbols for trading"""
    return ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT"]


@pytest.fixture
def timeout_short() -> float:
    """Short timeout for fast operations (ms)"""
    return 0.5


@pytest.fixture
def timeout_medium() -> float:
    """Medium timeout for API calls (seconds)"""
    return 3.0


@pytest.fixture
def timeout_long() -> float:
    """Long timeout for complex operations (seconds)"""
    return 10.0


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line("markers", "smoke: quick smoke tests")
    config.addinivalue_line("markers", "e2e: end-to-end integration tests")
    config.addinivalue_line("markers", "contract: API contract tests")
    config.addinivalue_line("markers", "integration: external integration tests")
    config.addinivalue_line("markers", "slow: tests that take > 5 seconds")
    config.addinivalue_line("markers", "websocket: WebSocket tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    # Auto-mark tests based on file location
    for item in items:
        if "smoke" in str(item.fspath):
            item.add_marker(pytest.mark.smoke)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "contract" in str(item.fspath):
            item.add_marker(pytest.mark.contract)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
