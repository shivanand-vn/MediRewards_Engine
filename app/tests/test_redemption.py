from app.services.ledger_service import LedgerService

def test_successful_redemption(client, db_session):
    # 1. Earn points first (direct credit of 300 points)
    LedgerService.record_entry(db_session, user_id="USER001", entry_type="CREDIT", points=300)
    db_session.commit()

    # Verify balance is 300
    balance_resp = client.get("/users/USER001/balance")
    assert balance_resp.json()["balance"] == 300

    # 2. Redeem Free Delivery Coupon (ID 1, cost 100)
    redeem_data = {"user_id": "USER001", "reward_id": 1}
    response = client.post("/redeem", json=redeem_data)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["reward_name"] == "Free Delivery Coupon"
    assert res_json["points_spent"] == 100
    assert res_json["updated_balance"] == 200

    # 3. Verify ledger shows debit
    ledger_resp = client.get("/users/USER001/ledger")
    ledger_data = ledger_resp.json()
    assert len(ledger_data) == 2
    # descending order, so debit is first
    assert ledger_data[0]["entry_type"] == "DEBIT"
    assert ledger_data[0]["points"] == -100
    assert ledger_data[0]["reference_id"] == str(res_json["redemption_id"])

def test_insufficient_balance(client, db_session):
    # 1. Earn small points (direct credit of 50 points)
    LedgerService.record_entry(db_session, user_id="USER002", entry_type="CREDIT", points=50)
    db_session.commit()

    # 2. Try to redeem Free Delivery Coupon (costs 100)
    redeem_data = {"user_id": "USER002", "reward_id": 1}
    response = client.post("/redeem", json=redeem_data)
    assert response.status_code == 400
    assert response.json() == {"error": "Insufficient balance"}

def test_reward_not_found(client, db_session):
    # Try to redeem non-existent reward ID
    redeem_data = {"user_id": "USER003", "reward_id": 999}
    response = client.post("/redeem", json=redeem_data)
    assert response.status_code == 404
    assert response.json() == {"error": "Reward not found"}
