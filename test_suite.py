import json
import time
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:5000"

def make_request(url, method="GET", data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    
    encoded_data = None
    if data is not None:
        encoded_data = json.dumps(data).encode("utf-8")
        
    try:
        with urllib.request.urlopen(req, data=encoded_data) as response:
            res_body = response.read().decode("utf-8")
            return response.status, json.loads(res_body) if res_body else {}
    except urllib.error.HTTPError as e:
        res_body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(res_body)
        except Exception:
            return e.code, {"error": res_body}

def run_tests():
    print("==================================================")
    print("      EVENTRA EXHAUSTIVE TEST SUITE RUNNER        ")
    print("==================================================")

    time.sleep(1)
    passed = 0
    failed = 0

    def assert_test(condition, name, details=""):
        nonlocal passed, failed
        if condition:
            print(f"[PASS] {name}")
            passed += 1
        else:
            print(f"[FAIL] {name} - {details}")
            failed += 1

    # ----------------------------------------------------
    # 1. HTML ROUTES & BACKEND ACCESSIBILITY
    # ----------------------------------------------------
    for route in ["/", "/events", "/bookings"]:
        try:
            with urllib.request.urlopen(f"{BASE_URL}{route}") as res:
                assert_test(res.status == 200, f"HTML Route Check: {route}")
        except Exception as e:
            assert_test(False, f"HTML Route Check: {route}", str(e))

    # ----------------------------------------------------
    # 2. AUDIT ALL 10 PREDEFINED EVENTS & 8 CATEGORIES
    # ----------------------------------------------------
    status, res = make_request(f"{BASE_URL}/api/events")
    events = res.get("data", [])
    assert_test(status == 200 and len(events) == 10, "API: Retrieve all 10 predefined events")

    required_categories = {"Music", "Theatre", "Comedy", "Sports", "Workshops", "Business", "Education", "Festivals"}
    found_categories = set(e["category"] for e in events)
    assert_test(required_categories.issubset(found_categories), "API Data Audit: All 8 required categories represented")

    for index, ev in enumerate(events, 1):
        has_fields = all(k in ev for k in ["id", "name", "category", "description", "date", "time", "venue", "city", "image", "ticket_types"])
        has_tickets = all(t in ev["ticket_types"] for t in ["General", "Premium", "VIP"])
        assert_test(has_fields and has_tickets, f"Event Audit {index}: {ev['id']} ({ev['name']}) fields & ticket tiers valid")

    # ----------------------------------------------------
    # 3. SEARCH & FILTERING VERIFICATION
    # ----------------------------------------------------
    status, search_res = make_request(f"{BASE_URL}/api/events/search?q=Metropolis")
    assert_test(status == 200 and len(search_res.get("data", [])) >= 2, "Search API: Search by city 'Metropolis'")

    status, cat_res = make_request(f"{BASE_URL}/api/events/search?category=Workshops")
    assert_test(status == 200 and len(cat_res.get("data", [])) == 1 and cat_res["data"][0]["category"] == "Workshops", "Filter API: Category 'Workshops'")

    status, price_res = make_request(f"{BASE_URL}/api/events/search?max_price=20")
    assert_test(status == 200 and len(price_res.get("data", [])) > 0, "Filter API: Max Price <= $20 filter")

    # ----------------------------------------------------
    # 4. GOOD INPUT TESTS (Test Users 1 to 5)
    # ----------------------------------------------------
    test_users = [
        {"name": "Test User 1", "email": "testuser1@example.com", "mobile": "+1 555-0101", "event_id": "EVT-101", "ticket_type": "General", "qty": 2},
        {"name": "Test User 2", "email": "testuser2@example.com", "mobile": "+1 555-0102", "event_id": "EVT-102", "ticket_type": "Premium", "qty": 1},
        {"name": "Test User 3", "email": "testuser3@example.com", "mobile": "+1 555-0103", "event_id": "EVT-103", "ticket_type": "VIP", "qty": 3},
        {"name": "Test User 4", "email": "testuser4@example.com", "mobile": "+1 555-0104", "event_id": "EVT-105", "ticket_type": "General", "qty": 1},
        {"name": "Test User 5", "email": "testuser5@example.com", "mobile": "+1 555-0105", "event_id": "EVT-108", "ticket_type": "VIP", "qty": 2}
    ]

    created_bookings = []
    for tu in test_users:
        payload = {
            "name": tu["name"],
            "email": tu["email"],
            "mobile": tu["mobile"],
            "event_id": tu["event_id"],
            "ticket_type": tu["ticket_type"],
            "quantity": tu["qty"]
        }
        st, r = make_request(f"{BASE_URL}/api/bookings", method="POST", data=payload)
        b_data = r.get("data", {})
        b_id = b_data.get("booking_id")
        if b_data and b_id:
            created_bookings.append(b_data)
        assert_test(st == 201 and b_id is not None and b_id.startswith("EVT-"), f"Valid Booking Creation ({tu['name']} -> {b_id})")

    # ----------------------------------------------------
    # 5. MATHEMATICAL PRICE CALCULATION VERIFICATION
    # ----------------------------------------------------
    if len(created_bookings) >= 3:
        b1_pricing = created_bookings[0]["pricing"]
        assert_test(b1_pricing["subtotal"] == 98.00 and b1_pricing["total"] == 103.00, "Math Check: Qty 2 General Ticket ($49.00 x 2 + $5 = $103.00)")

        b3_pricing = created_bookings[2]["pricing"]
        assert_test(b3_pricing["subtotal"] == 240.00 and b3_pricing["total"] == 245.00, "Math Check: Qty 3 VIP Ticket ($80.00 x 3 + $5 = $245.00)")

    # ----------------------------------------------------
    # 6. BAD INPUT VALIDATION TESTS
    # ----------------------------------------------------
    bad_payloads = [
        ({"name": "", "email": "a@b.com", "mobile": "12345678", "event_id": "EVT-101", "ticket_type": "General", "quantity": 1}, "Empty Name"),
        ({"name": "   ", "email": "a@b.com", "mobile": "12345678", "event_id": "EVT-101", "ticket_type": "General", "quantity": 1}, "Whitespace Name"),
        ({"name": "John", "email": "invalid-email", "mobile": "12345678", "event_id": "EVT-101", "ticket_type": "General", "quantity": 1}, "Malformed Email"),
        ({"name": "John", "email": "john@domain", "mobile": "12345678", "event_id": "EVT-101", "ticket_type": "General", "quantity": 1}, "Email Missing TLD"),
        ({"name": "John", "email": "j@b.com", "mobile": "123", "event_id": "EVT-101", "ticket_type": "General", "quantity": 1}, "Too Short Mobile"),
        ({"name": "John", "email": "j@b.com", "mobile": "12345678", "event_id": "INVALID-EVT", "ticket_type": "General", "quantity": 1}, "Non-existent Event ID"),
        ({"name": "John", "email": "j@b.com", "mobile": "12345678", "event_id": "EVT-101", "ticket_type": "SuperVIP", "quantity": 1}, "Invalid Ticket Type"),
        ({"name": "John", "email": "j@b.com", "mobile": "12345678", "event_id": "EVT-101", "ticket_type": "General", "quantity": 0}, "Zero Quantity"),
        ({"name": "John", "email": "j@b.com", "mobile": "12345678", "event_id": "EVT-101", "ticket_type": "General", "quantity": -2}, "Negative Quantity"),
        ({"name": "John", "email": "j@b.com", "mobile": "12345678", "event_id": "EVT-101", "ticket_type": "General", "quantity": 2.5}, "Float Quantity"),
        ({"name": "John", "email": "j@b.com", "mobile": "12345678", "event_id": "EVT-101", "ticket_type": "General", "quantity": "abc"}, "Text Quantity")
    ]

    for bad_data, label in bad_payloads:
        st, r = make_request(f"{BASE_URL}/api/bookings", method="POST", data=bad_data)
        assert_test(st == 400 and r.get("status") == "error", f"Validation Rejection: {label}")

    # ----------------------------------------------------
    # 7. OVERBOOKING & BOUNDARY TESTING
    # ----------------------------------------------------
    # Fetch current available VIP tickets for EVT-107
    st, ev_res = make_request(f"{BASE_URL}/api/events/EVT-107")
    avail_vip = ev_res["data"]["ticket_types"]["VIP"]["available"]
    
    if avail_vip > 0:
        boundary_payload = {
            "name": "Boundary Tester",
            "email": "boundary@example.com",
            "mobile": "+1 555-9999",
            "event_id": "EVT-107",
            "ticket_type": "VIP",
            "quantity": avail_vip
        }
        st, r_b = make_request(f"{BASE_URL}/api/bookings", method="POST", data=boundary_payload)
        assert_test(st == 201, f"Boundary Test: Booked remaining VIP stock ({avail_vip} tickets)")

    # Attempt to book 1 additional VIP ticket when stock is 0
    overbook_payload = {
        "name": "Overbook Tester",
        "email": "overbook@example.com",
        "mobile": "+1 555-8888",
        "event_id": "EVT-107",
        "ticket_type": "VIP",
        "quantity": 1
    }
    st, r_ob = make_request(f"{BASE_URL}/api/bookings", method="POST", data=overbook_payload)
    assert_test(st == 400 and "remaining" in r_ob.get("message", "").lower(), "Overbooking Test: Rejected booking when stock reached 0")

    # ----------------------------------------------------
    # 8. BOOKING DASHBOARD & DIGITAL TICKET LOOKUP
    # ----------------------------------------------------
    if created_bookings:
        first_b_id = created_bookings[0]["booking_id"]
        st, ticket_res = make_request(f"{BASE_URL}/api/bookings/{first_b_id}")
        assert_test(st == 200 and ticket_res.get("data", {}).get("booking_id") == first_b_id, f"Digital Ticket API: Retrieve {first_b_id}")

        st, dashboard_res = make_request(f"{BASE_URL}/api/bookings")
        all_b = dashboard_res.get("data", [])
        assert_test(st == 200 and len(all_b) >= 5, f"Dashboard API: Retrieve all active runtime bookings ({len(all_b)} bookings found)")

        # ----------------------------------------------------
        # 9. CANCELLATION FLOW & STOCK RESTORATION
        # ----------------------------------------------------
        st, ev101_before = make_request(f"{BASE_URL}/api/events/EVT-101")
        stock_before = ev101_before["data"]["ticket_types"]["General"]["available"]

        st, cancel_res = make_request(f"{BASE_URL}/api/bookings/{first_b_id}/cancel", method="PATCH")
        assert_test(st == 200 and cancel_res.get("data", {}).get("status") == "Cancelled", f"Cancellation API: Successfully cancelled {first_b_id}")

        st, ev101_after = make_request(f"{BASE_URL}/api/events/EVT-101")
        stock_after = ev101_after["data"]["ticket_types"]["General"]["available"]
        assert_test(stock_after == stock_before + 2, f"Stock Restoration Check: EVT-101 General stock restored from {stock_before} to {stock_after}")

        st, double_cancel = make_request(f"{BASE_URL}/api/bookings/{first_b_id}/cancel", method="PATCH")
        assert_test(st == 400 and "already cancelled" in double_cancel.get("message", "").lower(), "Double Cancel Test: Second cancellation rejected")

    print("==================================================")
    print(f"TOTAL TEST RESULTS: {passed} PASSED, {failed} FAILED")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
