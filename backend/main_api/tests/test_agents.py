import pytest

from app.main import app
from app.deps import (
    get_agent_service,
    get_commissions_service,
    get_payouts_service,
    get_info_api_client,
)
from app.core.security import create_access_token


@pytest.fixture
def auth_headers():
    access_token = create_access_token(data={"sub": "1"})

    return {
        "Authorization": f"Bearer {access_token}",
    }


class FakeAgentService:
    async def me(self, agent_id: int):
        return {
            "id": agent_id,
            "lastname": "ivan",
            "firstname": "isakov",
            "middlename": "andreevich",
            "phone": "79999999999",
            "email": "ivan@ivan.com",
            "passport_serial": "1234",
            "passport_number": "567890",
            "passport_issue_date": "2026-05-24T09:11:42.792000",
            "passport_issuer": "kto-to",
            "passport_code": "330",
            "birthdate": "2006-10-02",
            "status": "individual",
            "inn": "123",
            "ogrnip": "123",
            "is_verified": True,
        }

    async def update(self, agent_id: int, data):
        agent = await self.me(agent_id)

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            agent[key] = value

        return agent

    async def get_calculations(self, agent_id: int, info_api):
        return [
            {
                "id": 1,
                "agent_id": agent_id,
                "status": "calculated",
                "policy_price": 10000,
                "driver": {
                    "id": 1,
                    "firstname": "Иван",
                    "lastname": "Иванов",
                },
                "vehicle": {
                    "id": 1,
                    "brand": "Lada",
                    "model": "Vesta",
                },
            }
        ]


class FakeCommissionService:
    async def get_commissions(self, agent_id: int):
        return [
            {
                "id": 1,
                "agent_id": agent_id,
                "calculation_id": 1,
                "amount": 1000,
                "status": "accrued",
            }
        ]


class FakePayoutService:
    async def get_payouts(self, agent_id: int):
        return [
            {
                "id": 1,
                "agent_id": agent_id,
                "total_amount": 1000,
                "status": "pending",
            }
        ]

    async def create_payout(self, agent_id: int):
        return {
            "id": 2,
            "agent_id": agent_id,
            "total_amount": 1000,
            "status": "pending",
        }


class FakeInfoAPIClient:
    pass


@pytest.fixture(autouse=True)
def override_agents_dependencies():
    app.dependency_overrides[get_agent_service] = lambda: FakeAgentService()
    app.dependency_overrides[get_commissions_service] = lambda: FakeCommissionService()
    app.dependency_overrides[get_payouts_service] = lambda: FakePayoutService()
    app.dependency_overrides[get_info_api_client] = lambda: FakeInfoAPIClient()

    yield

    app.dependency_overrides.pop(get_agent_service, None)
    app.dependency_overrides.pop(get_commissions_service, None)
    app.dependency_overrides.pop(get_payouts_service, None)
    app.dependency_overrides.pop(get_info_api_client, None)


@pytest.mark.asyncio
async def test_me_success(client, auth_headers):
    response = await client.get(
        "/agents/me",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["email"] == "ivan@ivan.com"
    assert data["status"] == "individual"


@pytest.mark.asyncio
async def test_me_requires_auth(client):
    response = await client.get("/agents/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_agent_success(client, auth_headers):
    response = await client.patch(
        "/agents/",
        headers=auth_headers,
        json={
            "phone": "78888888888",
            "status": "self_employed",
            "inn": "123456789012",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["phone"] == "78888888888"
    assert data["status"] == "self_employed"
    assert data["inn"] == "123456789012"


@pytest.mark.asyncio
async def test_update_agent_requires_auth(client):
    response = await client.patch(
        "/agents/",
        json={
            "phone": "78888888888",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_calculations_success(client, auth_headers):
    response = await client.get(
        "/agents/calculations",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert data[0]["agent_id"] == 1
    assert data[0]["status"] == "calculated"


@pytest.mark.asyncio
async def test_get_calculations_requires_auth(client):
    response = await client.get("/agents/calculations")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_commissions_success(client, auth_headers):
    response = await client.get(
        "/agents/commissions",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert data[0]["agent_id"] == 1
    assert data[0]["amount"] == 1000


@pytest.mark.asyncio
async def test_get_commissions_requires_auth(client):
    response = await client.get("/agents/commissions")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_payouts_success(client, auth_headers):
    response = await client.get(
        "/agents/payouts",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert data[0]["agent_id"] == 1
    assert data[0]["status"] == "pending"


@pytest.mark.asyncio
async def test_get_payouts_requires_auth(client):
    response = await client.get("/agents/payouts")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_payout_success(client, auth_headers):
    response = await client.post(
        "/agents/payouts",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["agent_id"] == 1
    assert data["status"] == "pending"
    assert data["total_amount"] == 1000


@pytest.mark.asyncio
async def test_create_payout_requires_auth(client):
    response = await client.post("/agents/payouts")

    assert response.status_code == 401