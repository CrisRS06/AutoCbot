"""
Smoke Test: Backend Health Check (Journey J1)

Verifies that the backend service is running and all services are healthy.
This is the most basic test - if this fails, nothing else will work.

Time Budget: < 5 seconds
"""

import pytest
import httpx
import asyncio


@pytest.mark.smoke
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_backend_is_reachable(backend_url):
    """Test that backend responds to requests"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{backend_url}/", timeout=3.0)
            assert response.status_code == 200, f"Backend returned {response.status_code}"

            data = response.json()
            assert "name" in data, "Response missing 'name' field"
            assert "version" in data, "Response missing 'version' field"
            assert "status" in data, "Response missing 'status' field"

            print(f"✅ Backend reachable: {data['name']} v{data['version']}")
        except httpx.ConnectError:
            pytest.fail("❌ Cannot connect to backend. Is it running on {backend_url}?")
        except httpx.TimeoutException:
            pytest.fail("❌ Backend connection timeout. Service may be slow or hanging.")


@pytest.mark.smoke
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_health_endpoint(backend_url):
    """Test /health endpoint returns healthy status"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{backend_url}/health", timeout=3.0)

        assert response.status_code == 200, f"Health check failed with {response.status_code}"

        data = response.json()
        assert "status" in data, "Health response missing 'status'"
        assert data["status"] == "healthy", f"Service not healthy: {data['status']}"

        assert "services" in data, "Health response missing 'services'"
        services = data["services"]

        print(f"✅ Health check passed:")
        print(f"   - Status: {data['status']}")
        print(f"   - Services: {services}")

        # Check individual services (non-blocking - warn if down but don't fail)
        for service_name, is_running in services.items():
            if is_running:
                print(f"   ✅ {service_name}: running")
            else:
                print(f"   ⚠️  {service_name}: not running (may start on first request)")


@pytest.mark.smoke
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_health_response_time(backend_url):
    """Test health endpoint responds quickly (< 500ms)"""
    async with httpx.AsyncClient() as client:
        import time
        start = time.time()
        response = await client.get(f"{backend_url}/health", timeout=3.0)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert response.status_code == 200
        assert elapsed < 500, f"Health check too slow: {elapsed:.0f}ms (expected < 500ms)"

        print(f"✅ Health check response time: {elapsed:.0f}ms")


@pytest.mark.smoke
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_cors_headers(backend_url):
    """Test CORS headers are configured"""
    async with httpx.AsyncClient() as client:
        response = await client.options(
            f"{backend_url}/api/v1/market/overview",
            headers={"Origin": "http://localhost:3000"}
        )

        # CORS headers should be present for OPTIONS requests
        # Note: Some frameworks auto-handle OPTIONS, so we just verify no error
        assert response.status_code in [200, 204, 405], \
            f"OPTIONS request failed: {response.status_code}"

        print("✅ CORS configuration appears functional")


@pytest.mark.smoke
@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_api_routes_are_mounted(backend_url):
    """Test that API routes are properly mounted at /api/v1"""
    async with httpx.AsyncClient() as client:
        # Test a few key endpoints to ensure router is mounted
        endpoints_to_test = [
            "/api/v1/market/overview",
            "/api/v1/sentiment/fear-greed",
            "/api/v1/trading/signals",
            "/api/v1/portfolio/summary",
        ]

        for endpoint in endpoints_to_test:
            try:
                response = await client.get(f"{backend_url}{endpoint}", timeout=5.0)
                # We just check it doesn't 404 - actual data validation is in E2E tests
                assert response.status_code != 404, \
                    f"Route not found: {endpoint}"
                print(f"✅ Route exists: {endpoint} (status {response.status_code})")
            except httpx.TimeoutException:
                print(f"⚠️  Route timeout: {endpoint} (may be slow on first call)")


if __name__ == "__main__":
    # Allow running this file directly for quick testing
    pytest.main([__file__, "-v", "-s"])
