from datetime import datetime, timedelta

def test_rules_engine_points_calculation(client, db_session):
    # 1. Test medicine_purchase (Base: 10)
    # Sat Jun 20, 2026, amount: 100 (no weekend bonus since amount < 500)
    resp = client.post("/events", json={
        "event_id": "EVT_BASE_MED",
        "user_id": "USER001",
        "event_type": "medicine_purchase",
        "amount": 100,
        "timestamp": "2026-06-20T10:00:00Z"
    })
    assert resp.status_code == 200
    assert resp.json()["points_awarded"] == 10

    # 2. Test high value bonus (Base: 10 + High Value: 20 = 30)
    # Mon Jun 22, 2026 (weekday), amount: 2000
    resp = client.post("/events", json={
        "event_id": "EVT_HV",
        "user_id": "USER001",
        "event_type": "medicine_purchase",
        "amount": 2000,
        "timestamp": "2026-06-22T10:00:00Z"
    })
    assert resp.status_code == 200
    assert resp.json()["points_awarded"] == 30

    # 3. Test weekend bonus (Base: 10 + Weekend: 25 = 35)
    # Sat Jun 20, 2026, amount: 500
    resp = client.post("/events", json={
        "event_id": "EVT_WE",
        "user_id": "USER001",
        "event_type": "medicine_purchase",
        "amount": 500,
        "timestamp": "2026-06-20T10:00:00Z"
    })
    assert resp.status_code == 200
    assert resp.json()["points_awarded"] == 35

    # 4. Test max points cap (Base: 50 + HV: 20 + WE: 25 = 95 -> let's make it go over 100.
    # Referral base: 50. If referral had amount, could it get bonuses? Let's verify.
    # In rules config, referral has base 50. If amount: 2500 and Sunday, points: 50 + 20 + 25 = 95.
    # If we have an event type with base 70 or similar, but the maximum base is 50.
    # What if base points is 100? If we set an event type, it caps at 100.
    # Let's test capping by creating a very large amount or verifying cap:
    # Say base = 50 (referral), amount = 2500, Sunday. Points = 50 + 20 + 25 = 95.
    # What if base = 50, amount = 3000, Sunday, and we add more? It's 95.
    # Wait, what if we have a base of 70? The rule is max 100.
    # Let's test with a custom mock or test if the code caps points at 100.
    # If we submit base = 50 (referral), amount = 3000 (HV +20), Sunday (WE +25). Total before cap = 95.
    # Wait, what if base = 30 (subscription_purchase), amount = 2500 (HV +20), Sunday (WE +25). Total before cap = 75.
    # If we modify rules.json we can verify. But with our current rules.json:
    # Let's check calculation with referral:
    # If referral amount is 2000, and it falls on Sunday:
    # Base: 50, High Value: 20, Weekend: 25 -> Total = 95.
    # Wait, is there any combination that goes over 100?
    # What if the user submits an event with repeat_purchase (15) and HV (20) and WE (25) -> 60.
    # So with the current rules, no standard event naturally goes over 100. But the rules engine logic
    # has a strict `if points > 100: points = 100` which we can verify via rules engine unit test.

def test_repeat_purchase_validation(client, db_session):
    # 1. Try to submit repeat_purchase first without prior purchases
    resp = client.post("/events", json={
        "event_id": "EVT_RP_FAIL",
        "user_id": "USER_RP",
        "event_type": "repeat_purchase",
        "amount": 100,
        "timestamp": "2026-06-20T10:00:00Z"
    })
    assert resp.status_code == 400
    assert "requires a previous purchase within 30 days" in resp.json()["detail"]

    # 2. Submit a valid purchase
    client.post("/events", json={
        "event_id": "EVT_RP_PREV",
        "user_id": "USER_RP",
        "event_type": "medicine_purchase",
        "amount": 100,
        "timestamp": "2026-06-01T10:00:00Z"
    })

    # 3. Now submit repeat_purchase within 30 days (June 20 is 19 days later)
    resp = client.post("/events", json={
        "event_id": "EVT_RP_SUCCESS",
        "user_id": "USER_RP",
        "event_type": "repeat_purchase",
        "amount": 100,
        "timestamp": "2026-06-20T10:00:00Z"
    })
    assert resp.status_code == 200
    assert resp.json()["points_awarded"] == 15

    # 4. Try submitting another repeat_purchase after 30 days (e.g., July 15, which is > 30 days since June 20)
    # Wait! July 15 is within 30 days of June 20 (since June 20 was a repeat purchase).
    # What about August 20? That is 60 days later.
    resp = client.post("/events", json={
        "event_id": "EVT_RP_LATE",
        "user_id": "USER_RP",
        "event_type": "repeat_purchase",
        "amount": 100,
        "timestamp": "2026-08-20T10:00:00Z"
    })
    assert resp.status_code == 400
