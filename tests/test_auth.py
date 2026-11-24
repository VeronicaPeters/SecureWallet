def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecureWallet-NewUser-2026!",
            "full_name": "New User",
        },
    )
    assert response.status_code == 201
    assert response.json()["role"] == "customer"
    assert "hashed_password" not in response.json()


def test_duplicate_registration_rejected(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "SecureWallet-Duplicate-2026!",
        "full_name": "Duplicate User",
    }
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 409


def test_login_returns_access_token(client, registered_users):
    response = client.post(
        "/auth/login",
        json={
            "email": "alice@example.com",
            "password": "SecureWallet-Alice-2026!",
        },
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_invalid_password_rejected(client, registered_users):
    response = client.post(
        "/auth/login",
        json={
            "email": "alice@example.com",
            "password": "Wrong-Password-2026!",
        },
    )
    assert response.status_code == 401


def test_protected_endpoint_requires_authentication(client):
    assert client.get("/auth/me").status_code == 401



def test_login_rate_limit(client, registered_users):
    responses = []

    for _ in range(6):
        responses.append(
            client.post(
                "/auth/login",
                json={
                    "email": "alice@example.com",
                    "password": "Wrong-Password-2026!",
                },
            )
        )

    assert [response.status_code for response in responses[:5]] == [401] * 5
    assert responses[5].status_code == 429


def test_registration_rate_limit(client):
    responses = []

    for index in range(6):
        responses.append(
            client.post(
                "/auth/register",
                json={
                    "email": f"ratelimit{index}@example.com",
                    "password": "SecureWallet-RateLimit-2026!",
                    "full_name": f"Rate Limit {index}",
                },
            )
        )

    assert [response.status_code for response in responses[:5]] == [201] * 5
    assert responses[5].status_code == 429
