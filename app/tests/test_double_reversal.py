from app.models.ledger import LedgerEntry

def test_double_reversal_protection(client, db_session):
    # 1. Process event
    event_data = {
        "event_id": "EVT001",
        "user_id": "USER001",
        "event_type": "medicine_purchase",
        "amount": 2500,
        "timestamp": "2026-06-20T10:00:00Z"
    }
    # 1. Process event
    resp_evt = client.post("/events", json=event_data)
    assert resp_evt.status_code == 200
 
    # 2. Reverse once
    resp1 = client.post("/reverse/EVT001")
    assert resp1.status_code == 200
 
    # 3. Try to reverse again
    resp2 = client.post("/reverse/EVT001")
    assert resp2.status_code == 400
    assert "already been reversed" in resp2.json()["error"]
 
    # 4. Check ledger history to verify only 1 REVERSAL entry exists
    ledger_resp = client.get("/users/USER001/ledger")
    assert ledger_resp.status_code == 200
    ledger_data = ledger_resp.json()
    reversal_entries = [entry for entry in ledger_data if entry["entry_type"] == "REVERSAL"]
    assert len(reversal_entries) == 1
