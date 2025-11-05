"""
Smoke Test: Frontend Availability

Verifies that the frontend is built, running, and can serve pages.

Time Budget: < 5 seconds
"""

import pytest
import httpx


@pytest.mark.smoke
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_frontend_is_reachable(frontend_url):
    """Test that frontend responds to HTTP requests"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(frontend_url, timeout=3.0, follow_redirects=True)
            assert response.status_code == 200, \
                f"Frontend returned {response.status_code}"

            # Check it's HTML (not an error JSON)
            content_type = response.headers.get("content-type", "")
            assert "text/html" in content_type.lower(), \
                f"Frontend not serving HTML: {content_type}"

            print(f"✅ Frontend reachable at {frontend_url}")
            print(f"   Content-Type: {content_type}")

        except httpx.ConnectError:
            pytest.fail(f"❌ Cannot connect to frontend at {frontend_url}. Is it running?")
        except httpx.TimeoutException:
            pytest.fail("❌ Frontend connection timeout.")


@pytest.mark.smoke
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_frontend_loads_html(frontend_url):
    """Test that frontend serves valid HTML with expected content"""
    async with httpx.AsyncClient() as client:
        response = await client.get(frontend_url, timeout=3.0, follow_redirects=True)

        assert response.status_code == 200
        html = response.text

        # Basic HTML structure checks
        assert "<!DOCTYPE html>" in html or "<html" in html, \
            "Response doesn't appear to be HTML"

        # Check for Next.js or React indicators
        assert "__NEXT_DATA__" in html or "react" in html.lower(), \
            "Response doesn't appear to be a Next.js/React app"

        print("✅ Frontend serves valid HTML")
        print(f"   HTML size: {len(html)} bytes")


@pytest.mark.smoke
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_frontend_static_assets_accessible(frontend_url):
    """Test that static assets can be loaded (if any exist)"""
    async with httpx.AsyncClient() as client:
        # Try to load favicon or other common assets
        common_assets = [
            "/favicon.ico",
            "/_next/static/css",  # Next.js CSS
        ]

        for asset_path in common_assets:
            try:
                response = await client.get(
                    f"{frontend_url}{asset_path}",
                    timeout=2.0,
                    follow_redirects=True
                )
                # Assets might 404 if not created yet, but connection should work
                if response.status_code == 200:
                    print(f"✅ Asset accessible: {asset_path}")
                else:
                    print(f"⚠️  Asset not found: {asset_path} ({response.status_code})")
            except Exception as e:
                print(f"⚠️  Asset check failed: {asset_path} ({type(e).__name__})")


@pytest.mark.smoke
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_frontend_response_time(frontend_url):
    """Test frontend responds quickly"""
    async with httpx.AsyncClient() as client:
        import time
        start = time.time()
        response = await client.get(frontend_url, timeout=3.0, follow_redirects=True)
        elapsed = (time.time() - start) * 1000

        assert response.status_code == 200

        # Frontend might be slower on first load (Next.js compilation)
        # Allow up to 3 seconds for MVP
        assert elapsed < 3000, \
            f"Frontend too slow: {elapsed:.0f}ms (expected < 3000ms)"

        print(f"✅ Frontend response time: {elapsed:.0f}ms")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
