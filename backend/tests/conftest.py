import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from db.mongo import get_db

async def override_get_db():
    class MockCollection:
        async def find_one(self, *args, **kwargs):
            return {"_id": "123", "email": "admin@demo.com", "role": "admin", "hashed_password": "mock", "is_active": True}
    class MockDB:
        def __init__(self):
            self.users = MockCollection()
            self.token_blacklist = MockCollection()
    return MockDB()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
