def test_successful_reversal(client, db_session):
    # 1. Process event first
    event_data = {
        "event_id": "EVT001",
        "user_id": "USER001",
        "event_type": "medicine_purchase",
        "amount": 2500,
        "timestamp": "2026-06-20T10:00:00Z"
    }
    client.post("/events", json=event_data)

    # 2. Reverse event
    response = client.post("/reverse/EVT001")
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["message"] == "Event reversed successfully"
    assert res_json["event_id"] == "EVT001"
    assert res_json["points_reversed"] == 55
    assert res_json["updated_balance"] == 0

    # 3. Check ledger history
    ledger_resp = client.get("/users/USER001/ledger")
    ledger_data = ledger_resp.json()
    assert len(ledger_data) == 2
    # newest first
    assert ledger_data[0]["entry_type"] == "REVERSAL"
    assert ledger_data[0]["points"] == -55
    assert ledger_data[1]["entry_type"] == "CREDIT"
    assert ledger_data[1]["points"] == 55

def test_reversal_resulting_in_negative_balance(client, db_session):
    # 1. Process event for 55 points
    event_data = {
        "event_id": "EVT002",
        "user_id": "USER002",
        "event_type": "medicine_purchase",
        "amount": 2500,
        "timestamp": "2026-06-20T10:00:00Z"
    }
    client.post("/events", json=event_data)

    # 2. Redeem 50 points (Free Delivery Coupon, cost 100? No, let's credit more points or redeem something.
    # Actually, Free Delivery Coupon costs 100. Let's first credit 50 points directly to make balance 105,
    # then redeem 100 points, leaving balance at 5. Then reverse the original 55 event, making balance -50)
    from app.services.ledger_service import LedgerService
    LedgerService.record_entry(db_session, user_id="USER002", entry_type="CREDIT", points=50)
    db_session.commit()

    # Balance is now 105. Redeem Free Delivery Coupon (cost 100)
    client.post("/redeem", json={"user_id": "USER002", "reward_id": 1})

    # Verify balance is 5
    balance_resp = client.get("/users/USER002/balance")
    assert balance_resp.json()["balance"] == 5

    # 3. Reverse EVT002 (55 points)
    reversal_resp = client.post("/reverse/EVT002")
    assert reversal_resp.status_code == 200
    assert reversal_resp.json()["updated_balance"] == -50

    # Verify balance endpoint returns -50
    balance_resp_final = client.get("/users/USER002/balance")
    assert balance_resp_final.json()["balance"] == -50
