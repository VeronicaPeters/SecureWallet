def test_transfer_between_customers(client, authenticated_clients):
    alice = authenticated_clients["alice"]
    bob = authenticated_clients["bob"]

    client.post(
        "/wallets/fund",
        json={"amount": "2000.00"},
        headers=alice["headers"],
    )

    response = client.post(
        "/transactions/transfer",
        json={
            "receiver_wallet_id": bob["user"]["wallet_id"],
            "amount": "500.00",
        },
        headers={
            **alice["headers"],
            "Idempotency-Key": "alice-transfer-001",
        },
    )

    assert response.status_code == 201
    assert response.json()["amount"] == "500.00"
    assert response.json()["status"] == "completed"


def test_insufficient_balance_rejected(client, authenticated_clients):
    alice = authenticated_clients["alice"]
    bob = authenticated_clients["bob"]

    response = client.post(
        "/transactions/transfer",
        json={
            "receiver_wallet_id": bob["user"]["wallet_id"],
            "amount": "500.00",
        },
        headers={
            **alice["headers"],
            "Idempotency-Key": "alice-transfer-002",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient wallet balance."


def test_self_transfer_rejected(client, authenticated_clients):
    alice = authenticated_clients["alice"]

    response = client.post(
        "/transactions/transfer",
        json={
            "receiver_wallet_id": alice["user"]["wallet_id"],
            "amount": "100.00",
        },
        headers={
            **alice["headers"],
            "Idempotency-Key": "alice-transfer-003",
        },
    )

    assert response.status_code == 400


def test_transaction_history_is_isolated(client, authenticated_clients):
    alice = authenticated_clients["alice"]
    charlie = authenticated_clients["charlie"]

    client.post(
        "/wallets/fund",
        json={"amount": "1000.00"},
        headers=alice["headers"],
    )

    alice_history = client.get(
        "/transactions/me", headers=alice["headers"]
    )
    charlie_history = client.get(
        "/transactions/me", headers=charlie["headers"]
    )

    assert alice_history.status_code == 200
    assert len(alice_history.json()) == 1
    assert charlie_history.json() == []


def test_pagination_validation(client, authenticated_clients):
    headers = authenticated_clients["alice"]["headers"]

    assert client.get(
        "/transactions/me?skip=-1", headers=headers
    ).status_code == 422

    assert client.get(
        "/transactions/me?limit=0", headers=headers
    ).status_code == 422

    assert client.get(
        "/transactions/me?limit=101", headers=headers
    ).status_code == 422

    assert client.get(
        "/transactions/me?skip=0&limit=2", headers=headers
    ).status_code == 200


def test_transfer_idempotency_prevents_duplicate_debit(
    client, authenticated_clients
):
    alice = authenticated_clients["alice"]
    bob = authenticated_clients["bob"]

    client.post(
        "/wallets/fund",
        json={"amount": "1000.00"},
        headers=alice["headers"],
    )

    request_headers = {
        **alice["headers"],
        "Idempotency-Key": "alice-idempotency-001",
    }

    payload = {
        "receiver_wallet_id": bob["user"]["wallet_id"],
        "amount": "250.00",
    }

    first_response = client.post(
        "/transactions/transfer",
        json=payload,
        headers=request_headers,
    )

    retry_response = client.post(
        "/transactions/transfer",
        json=payload,
        headers=request_headers,
    )

    assert first_response.status_code == 201
    assert retry_response.status_code == 201

    # Both responses must refer to the same transaction.
    assert first_response.json()["id"] == retry_response.json()["id"]
    assert first_response.json()["reference"] == retry_response.json()["reference"]

    alice_wallet = client.get(
        "/wallets/me", headers=alice["headers"]
    ).json()

    bob_wallet = client.get(
        "/wallets/me", headers=bob["headers"]
    ).json()

    assert alice_wallet["balance"] == "750.00"
    assert bob_wallet["balance"] == "250.00"


def test_idempotency_key_cannot_be_reused_for_different_transfer(
    client, authenticated_clients
):
    alice = authenticated_clients["alice"]
    bob = authenticated_clients["bob"]
    charlie = authenticated_clients["charlie"]

    client.post(
        "/wallets/fund",
        json={"amount": "1000.00"},
        headers=alice["headers"],
    )

    request_headers = {
        **alice["headers"],
        "Idempotency-Key": "alice-idempotency-002",
    }

    first_response = client.post(
        "/transactions/transfer",
        json={
            "receiver_wallet_id": bob["user"]["wallet_id"],
            "amount": "200.00",
        },
        headers=request_headers,
    )

    conflicting_response = client.post(
        "/transactions/transfer",
        json={
            "receiver_wallet_id": charlie["user"]["wallet_id"],
            "amount": "300.00",
        },
        headers=request_headers,
    )

    assert first_response.status_code == 201
    assert conflicting_response.status_code == 409

    alice_wallet = client.get(
        "/wallets/me", headers=alice["headers"]
    ).json()

    assert alice_wallet["balance"] == "800.00"


def test_transfer_requires_idempotency_key(client, authenticated_clients):
    alice = authenticated_clients["alice"]
    bob = authenticated_clients["bob"]

    response = client.post(
        "/transactions/transfer",
        json={
            "receiver_wallet_id": bob["user"]["wallet_id"],
            "amount": "100.00",
        },
        headers=alice["headers"],
    )

    assert response.status_code == 422
