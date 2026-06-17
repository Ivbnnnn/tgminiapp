import pytest


def agent_payload(
    email: str = "ivan@ivan.com",
    password: str = "ivan",
    status: str = "individual",
) -> dict:
    return {
        "lastname": "ivan",
        "firstname": "isakov",
        "middlename": "andreevich",
        "phone": "79999999999",
        "email": email,
        "passport_serial": "1234",
        "passport_number": "567890",
        "passport_issue_date": "2020-05-24T09:11:42.792Z",
        "passport_issuer": "kto-to",
        "passport_code": "330-001",
        "birthdate": "1990-10-02",
        "status": status,
        "inn": "123456789012" if status != "individual" else "",
        "ogrnip": "123456789012345" if status == "ip" else "",
        "is_verified": True,
        "password": password,
    }


@pytest.mark.asyncio
async def test_signup_success(client):
    response = await client.post(
        "/auth/signup",
        json=agent_payload(),
    )

    assert response.status_code == 201

    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

    assert response.cookies.get("access_token")
    assert response.cookies.get("refresh_token")


@pytest.mark.asyncio
async def test_signup_duplicate_email(client):
    payload = agent_payload(email="duplicate@ivan.com")

    first_response = await client.post("/auth/signup", json=payload)
    second_response = await client.post("/auth/signup", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code in {400, 409}


@pytest.mark.asyncio
async def test_signup_invalid_email(client):
    payload = agent_payload(email="bad-email")

    response = await client.post(
        "/auth/signup",
        json=payload,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client):
    payload = agent_payload(
        email="login@ivan.com",
        password="ivan",
    )

    signup_response = await client.post(
        "/auth/signup",
        json=payload,
    )

    assert signup_response.status_code == 201

    response = await client.post(
        "/auth/login",
        json={
            "email": "login@ivan.com",
            "password": "ivan",
        },
    )

    assert response.status_code == 200

    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

    assert response.cookies.get("access_token")
    assert response.cookies.get("refresh_token")


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    payload = agent_payload(
        email="wrong-password@ivan.com",
        password="ivan",
    )

    signup_response = await client.post(
        "/auth/signup",
        json=payload,
    )

    assert signup_response.status_code == 201

    response = await client.post(
        "/auth/login",
        json={
            "email": "wrong-password@ivan.com",
            "password": "wrong",
        },
    )

    assert response.status_code in {400, 401}


@pytest.mark.asyncio
async def test_login_unknown_email(client):
    response = await client.post(
        "/auth/login",
        json={
            "email": "unknown@ivan.com",
            "password": "ivan",
        },
    )

    assert response.status_code in {400, 401, 404}

@pytest.mark.asyncio
async def test_refresh_success(client):
    payload = agent_payload(
        email="refresh@ivan.com",
        password="ivan",
    )

    signup_response = await client.post(
        "/auth/signup",
        json=payload,
    )

    assert signup_response.status_code == 201

    refresh_token = signup_response.cookies.get("refresh_token")
    assert refresh_token is not None

    client.cookies.set("refresh_token", refresh_token)

    response = await client.post("/auth/refresh")

    assert response.status_code == 200
    assert "access_token" in response.cookies
    assert response.cookies.get("access_token")


@pytest.mark.asyncio
async def test_refresh_without_cookie(client):
    response = await client.post("/auth/refresh")

    assert response.status_code == 422
