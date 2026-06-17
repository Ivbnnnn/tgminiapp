import pytest

from app.main import app
from app.deps import get_info_api_client, get_calculation_service
from app.core.security import create_access_token


@pytest.fixture
def auth_headers():
    access_token = create_access_token(data={"sub": "1"})

    return {
        "Authorization": f"Bearer {access_token}",
    }


class FakeInfoAPIClient:
    async def search(self, model_name, relations, filters):
        return [
            {
                "id": 1,
                "model_name": model_name,
                "relations": relations,
                "filters": filters,
            }
        ]

    async def get_test_calculation_data(self):
        return {
            "lastname": "Иванов",
            "firstname": "Иван",
            "middlename": "Иванович",
            "insurance_companies": None,
            "license_plate": "А123ВС77",
            "vin": "XTA12345678901234",
            "body_number": None,
            "chassis_number": None,
            "license_serial": "1111",
            "license_number": "222222",
            "use_period": 12,
            "policy_start_date": "2026-05-25",
        }


class FakeCalculationService:
    async def make_offers(self, data, info_api, agent_id: int):
        return {
            "agent_id": agent_id,
            "status": "calculated",
            "offers": [
                {
                    "company_id": 1,
                    "company_name": "Test Insurance",
                    "price": 10000,
                }
            ],
        }

    async def choose_offer(self, user_id: int, company_id: int, calculation_id: int):
        return {
            "agent_id": user_id,
            "company_id": company_id,
            "calculation_id": calculation_id,
            "status": "waiting_for_payment",
        }

    async def pay_offer(self, user_id: int, calculation_id: int, info_api):
        return {
            "agent_id": user_id,
            "calculation_id": calculation_id,
            "status": "paid",
        }

    async def cancel_offers(self, user_id: int, company_id: int, calculation_id: int):
        return {
            "agent_id": user_id,
            "company_id": company_id,
            "calculation_id": calculation_id,
            "status": "canceled",
        }

    async def get_insurance_companies(self, info_api):
        return [
            {
                "id": 1,
                "name": "Test Insurance",
                "commission_percent": 10,
            }
        ]


@pytest.fixture(autouse=True)
def override_osago_dependencies():
    app.dependency_overrides[get_info_api_client] = lambda: FakeInfoAPIClient()
    app.dependency_overrides[get_calculation_service] = lambda: FakeCalculationService()

    yield

    app.dependency_overrides.pop(get_info_api_client, None)
    app.dependency_overrides.pop(get_calculation_service, None)


def calculation_payload() -> dict:
    return {
        "lastname": "Иванов",
        "firstname": "Иван",
        "middlename": "Иванович",
        "insurance_companies": ["Test Insurance"],
        "license_plate": "А123ВС77",
        "vin": "XTA12345678901234",
        "body_number": None,
        "chassis_number": None,
        "license_serial": "1111",
        "license_number": "222222",
        "use_period": 12,
        "policy_start_date": "2026-05-24",
    }


@pytest.mark.asyncio
async def test_search_success(client, auth_headers):
    response = await client.post(
        "/osago/search",
        headers=auth_headers,
        json={
            "model_name": "InsuranceCompany",
            "relations": [],
            "filters": {
                "name": "Test Insurance",
            },
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert isinstance(data, list)
    assert data[0]["model_name"] == "InsuranceCompany"
    assert data[0]["relations"] == []
    assert data[0]["filters"] == {
        "name": "Test Insurance",
    }


@pytest.mark.asyncio
async def test_get_test_data_success(client, auth_headers):
    response = await client.get(
        "/osago/test-data",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["lastname"] == "Иванов"
    assert data["firstname"] == "Иван"
    assert data["license_plate"] == "А123ВС77"
    assert data["license_serial"] == "1111"
    assert data["license_number"] == "222222"
    assert data["insurance_companies"] is None


@pytest.mark.asyncio
async def test_get_offers_success(client, auth_headers):
    response = await client.post(
        "/osago/get_offers",
        headers=auth_headers,
        json=calculation_payload(),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["agent_id"] == 1
    assert data["status"] == "calculated"
    assert len(data["offers"]) == 1
    assert data["offers"][0]["company_id"] == 1


@pytest.mark.asyncio
async def test_choose_offer_success(client, auth_headers):
    response = await client.post(
        "/osago/choose_offer",
        headers=auth_headers,
        json={
            "company_id": 1,
            "calculation_id": 10,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["agent_id"] == 1
    assert data["company_id"] == 1
    assert data["calculation_id"] == 10
    assert data["status"] == "waiting_for_payment"


@pytest.mark.asyncio
async def test_pay_offer_success(client, auth_headers):
    response = await client.post(
        "/osago/pay_offer",
        headers=auth_headers,
        json={
            "calculation_id": 10,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["agent_id"] == 1
    assert data["calculation_id"] == 10
    assert data["status"] == "paid"


@pytest.mark.asyncio
async def test_cancel_offer_success(client, auth_headers):
    response = await client.post(
        "/osago/cancel_offer",
        headers=auth_headers,
        json={
            "company_id": 1,
            "calculation_id": 10,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["agent_id"] == 1
    assert data["company_id"] == 1
    assert data["calculation_id"] == 10
    assert data["status"] == "canceled"


@pytest.mark.asyncio
async def test_get_companies_success(client, auth_headers):
    response = await client.get(
        "/osago/companies",
        headers=auth_headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert isinstance(data, list)
    assert data[0]["id"] == 1
    assert data[0]["name"] == "Test Insurance"


@pytest.mark.asyncio
async def test_osago_requires_auth(client):
    response = await client.post(
        "/osago/choose_offer",
        json={
            "company_id": 1,
            "calculation_id": 10,
        },
    )

    assert response.status_code == 401
