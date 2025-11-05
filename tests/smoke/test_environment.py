"""
Smoke Test: Environment & Dependencies

Verifies that the environment is correctly configured and all
required dependencies are available.

Time Budget: < 5 seconds
"""

import pytest
import os
import sys
from pathlib import Path


@pytest.mark.smoke
def test_python_version():
    """Test Python version is 3.11+"""
    major, minor = sys.version_info[:2]
    assert major == 3 and minor >= 11, \
        f"Python 3.11+ required, got {major}.{minor}"

    print(f"✅ Python version: {major}.{minor}.{sys.version_info.micro}")


@pytest.mark.smoke
def test_backend_directory_exists():
    """Test backend directory structure exists"""
    backend_dir = Path(__file__).parent.parent.parent / "backend"
    assert backend_dir.exists(), "Backend directory not found"

    required_files = [
        backend_dir / "main.py",
        backend_dir / "requirements.txt",
    ]

    for file_path in required_files:
        assert file_path.exists(), f"Required file missing: {file_path.name}"

    print(f"✅ Backend directory structure valid")


@pytest.mark.smoke
def test_frontend_directory_exists():
    """Test frontend directory structure exists"""
    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    assert frontend_dir.exists(), "Frontend directory not found"

    required_files = [
        frontend_dir / "package.json",
        frontend_dir / "next.config.js",
    ]

    for file_path in required_files:
        assert file_path.exists(), f"Required file missing: {file_path.name}"

    print(f"✅ Frontend directory structure valid")


@pytest.mark.smoke
def test_docker_compose_exists():
    """Test docker-compose.yml exists"""
    root_dir = Path(__file__).parent.parent.parent
    docker_compose = root_dir / "docker-compose.yml"

    assert docker_compose.exists(), "docker-compose.yml not found"

    print(f"✅ Docker Compose configuration exists")


@pytest.mark.smoke
def test_env_file_exists():
    """Test .env file exists (or .env.example as fallback)"""
    root_dir = Path(__file__).parent.parent.parent
    env_file = root_dir / ".env"
    env_example = root_dir / ".env.example"

    if env_file.exists():
        print(f"✅ .env file exists")
    elif env_example.exists():
        print(f"⚠️  .env not found, but .env.example exists (run: cp .env.example .env)")
    else:
        pytest.fail("Neither .env nor .env.example found")


@pytest.mark.smoke
def test_backend_imports():
    """Test critical backend imports work"""
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
        import uvicorn
        import aiohttp
        print("✅ Backend core dependencies importable")
    except ImportError as e:
        pytest.fail(f"Backend import failed: {e}")


@pytest.mark.smoke
def test_test_dependencies():
    """Test that test dependencies are installed"""
    try:
        import pytest
        import httpx
        import asyncio
        print("✅ Test dependencies installed")
    except ImportError as e:
        pytest.fail(f"Test dependency missing: {e}")


@pytest.mark.smoke
def test_backend_services_importable():
    """Test that backend services can be imported"""
    # Add backend to path
    backend_path = Path(__file__).parent.parent.parent / "backend"
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))

    try:
        from services.market_data import MarketDataService
        from services.sentiment import SentimentService
        from services.signal_generator import SignalGeneratorService
        print("✅ Backend services importable")
    except ImportError as e:
        pytest.fail(f"Backend service import failed: {e}\nMake sure backend dependencies are installed.")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
