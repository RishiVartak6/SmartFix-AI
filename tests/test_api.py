import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.database.database import init_db

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    await init_db()

@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["app"] == "SmartFix AI"
        assert data["status"] == "online"

@pytest.mark.asyncio
async def test_system_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/system/health")
        assert response.status_code == 200
        data = response.json()
        assert "health_status" in data
        assert "cpu_percent" in data
        assert "memory_percent" in data

@pytest.mark.asyncio
async def test_repairs_catalog_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/repairs")
        assert response.status_code == 200
        data = response.json()
        assert "catalog" in data
        assert len(data["catalog"]) >= 10

@pytest.mark.asyncio
async def test_diagnosis_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"mode": "full_scan", "user_query": "Testing network DNS diagnosis"}
        response = await client.post("/api/diagnosis/diagnose", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "diagnoses" in data
        assert len(data["diagnoses"]) >= 1
