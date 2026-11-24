def test_user_can_view_own_wallet(client, authenticated_clients):
    alice = authenticated_clients["alice"]
    response = client.get("/wallets/me", headers=alice["headers"])

    assert response.status_code == 200
    assert response.json()["user_id"] == alice["user"]["id"]
    assert response.json()["balance"] == "0.00"


def test_user_cannot_view_wallet_by_changing_user_id(client, authenticated_clients):
    alice = authenticated_clients["alice"]
    response = client.get(
        f"/wallets/me?user_id={authenticated_clients['bob']['user']['id']}",
        headers=alice["headers"],
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == alice["user"]["id"]


def test_wallet_funding(client, authenticated_clients):
    alice = authenticated_clients["alice"]
    response = client.post(
        "/wallets/fund",
        json={"amount": "1500.00"},
        headers=alice["headers"],
    )

    assert response.status_code == 200
    assert response.json()["balance"] == "1500.00"


def test_negative_funding_rejected(client, authenticated_clients):
    alice = authenticated_clients["alice"]
    response = client.post(
        "/wallets/fund",
        json={"amount": "-100.00"},
        headers=alice["headers"],
    )

    assert response.status_code == 422
