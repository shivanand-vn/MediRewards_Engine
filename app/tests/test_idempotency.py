from app.models.ledger import LedgerEntry

def test_event_idempotency(client, db_session):
    event_data = {
        "event_id": "EVT001",
        "user_id": "USER001",
        "event_type": "medicine_purchase",
        "amount": 2500,
        "timestamp": "2026-06-20T10:00:00Z"
    }

    # 1. Post event for the first time
    response = client.post("/events", json=event_data)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["event_id"] == "EVT001"
    assert res_json["points_awarded"] == 55  # 10 base + 20 high-value + 25 weekend

    # 2. Post same event again (idempotent call)
    response_dup = client.post("/events", json=event_data)
    assert response_dup.status_code == 200
    assert response_dup.json() == {"message": "Event already processed"}

    # 3. Check database to ensure only one ledger entry was created
    entries = db_session.query(LedgerEntry).filter(LedgerEntry.event_id == "EVT001").all()
    assert len(entries) == 1
    assert entries[0].entry_type == "CREDIT"
    assert entries[0].points == 55

    # 4. Check user balance
    balance_response = client.get("/users/USER001/balance")
    assert balance_response.status_code == 200
    assert balance_response.json() == {"user_id": "USER001", "balance": 55}
