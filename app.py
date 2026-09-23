import re
from datetime import datetime
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Fixed booking fee per transaction
BOOKING_FEE = 5.00

# Global ID counter for bookings
booking_counter = 1001

# In-Memory Event Catalog (Data-driven demo dataset covering all 8 categories)
events = [
    {
        "id": "EVT-101",
        "name": "Neon Pulse Music Festival",
        "category": "Music",
        "description": "Experience an unforgettable night of high-energy electronic music, stunning light shows, and world-class DJ performances live on the main stage.",
        "date": "2026-10-15",
        "time": "18:00",
        "venue": "Grand Horizon Amphitheater",
        "city": "Metropolis",
        "image": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=800&q=80",
        "featured": True,
        "booking_fee": BOOKING_FEE,
        "ticket_types": {
            "General": {"price": 49.00, "capacity": 200, "available": 145},
            "Premium": {"price": 89.00, "capacity": 100, "available": 60},
            "VIP": {"price": 149.00, "capacity": 40, "available": 12}
        }
    },
    {
        "id": "EVT-102",
        "name": "The Phantom Mirage",
        "category": "Theatre",
        "description": "A captivating theatrical masterpiece blending classic drama with modern storytelling and breathtaking stage scenery.",
        "date": "2026-10-20",
        "time": "19:30",
        "venue": "Royal Crown Playhouse",
        "city": "Riverdale",
        "image": "https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?auto=format&fit=crop&w=800&q=80",
        "featured": True,
        "booking_fee": BOOKING_FEE,
        "ticket_types": {
            "General": {"price": 35.00, "capacity": 120, "available": 80},
            "Premium": {"price": 65.00, "capacity": 60, "available": 35},
            "VIP": {"price": 110.00, "capacity": 25, "available": 8}
        }
    },
    {
        "id": "EVT-103",
        "name": "Stand-Up Comedy Gala",
        "category": "Comedy",
        "description": "Prepare for non-stop laughter with top comedy heavyweights and brilliant rising stars performing live.",
        "date": "2026-10-25",
        "time": "20:00",
        "venue": "Laughter Lounge Arena",
        "city": "Downtown",
        "image": "https://images.unsplash.com/photo-1585699324551-f6c309eedeca?auto=format&fit=crop&w=800&q=80",
        "featured": True,
        "booking_fee": BOOKING_FEE,
        "ticket_types": {
            "General": {"price": 25.00, "capacity": 150, "available": 100},
            "Premium": {"price": 45.00, "capacity": 75, "available": 40},
            "VIP": {"price": 80.00, "capacity": 30, "available": 15}
        }
    },
    {
        "id": "EVT-104",
        "name": "Urban Championship Derby",
        "category": "Sports",
        "description": "Witness high-stakes athletic prowess and thrilling head-to-head rivalry at the city's annual derby.",
        "date": "2026-11-02",
        "time": "15:00",
        "venue": "Summit Arena Stadium",
        "city": "Metropolis",
        "image": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=800&q=80",
        "featured": False,
        "booking_fee": BOOKING_FEE,
        "ticket_types": {
            "General": {"price": 40.00, "capacity": 300, "available": 210},
            "Premium": {"price": 75.00, "capacity": 150, "available": 90},
            "VIP": {"price": 130.00, "capacity": 50, "available": 20}
        }
    },
    {
        "id": "EVT-105",
        "name": "AI & Tech Innovation Summit",
        "category": "Business",
        "description": "Connect with industry leaders, founders, and engineers showcasing cutting-edge AI breakthroughs and tech trends.",
        "date": "2026-11-10",
        "time": "09:00",
        "venue": "Vanguard Convention Center",
        "city": "Tech Valley",
        "image": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=800&q=80",
        "featured": True,
        "booking_fee": BOOKING_FEE,
        "ticket_types": {
            "General": {"price": 99.00, "capacity": 250, "available": 180},
            "Premium": {"price": 199.00, "capacity": 100, "available": 45},
            "VIP": {"price": 349.00, "capacity": 40, "available": 10}
        }
    },
    {
        "id": "EVT-106",
        "name": "Creative UI/UX Workshop",
        "category": "Workshops",
        "description": "An interactive hands-on design masterclass focusing on user-centered principles, design systems, and rapid prototyping.",
        "date": "2026-11-14",
        "time": "10:00",
        "venue": "Design Studio Hub",
        "city": "Riverdale",
        "image": "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=800&q=80",
        "featured": False,
        "booking_fee": BOOKING_FEE,
        "ticket_types": {
            "General": {"price": 60.00, "capacity": 40, "available": 22},
            "Premium": {"price": 95.00, "capacity": 20, "available": 10},
            "VIP": {"price": 140.00, "capacity": 10, "available": 3}
        }
    },
    {
        "id": "EVT-107",
        "name": "Quantum Computing 101",
        "category": "Education",
        "description": "Explore the foundational principles of quantum mechanics, qubits, algorithms, and practical applications in physics.",
        "date": "2026-11-18",
        "time": "14:00",
        "venue": "Metropolis University Auditorium",
        "city": "Metropolis",
        "image": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=800&q=80",
        "featured": False,
        "booking_fee": BOOKING_FEE,
        "ticket_types": {
            "General": {"price": 20.00, "capacity": 100, "available": 75},
            "Premium": {"price": 40.00, "capacity": 50, "available": 30},
            "VIP": {"price": 75.00, "capacity": 15, "available": 5}
        }
    },
    {
        "id": "EVT-108",
        "name": "Autumn Cultural & Food Festival",
        "category": "Festivals",
        "description": "Celebrate food, art, and music from around the world with live cooking demos, artisan stalls, and family activities.",
        "date": "2026-11-22",
        "time": "11:00",
        "venue": "Riverside Heritage Park",
        "city": "Riverdale",
        "image": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=800&q=80",
        "featured": True,
        "booking_fee": BOOKING_FEE,
        "ticket_types": {
            "General": {"price": 15.00, "capacity": 500, "available": 380},
            "Premium": {"price": 30.00, "capacity": 200, "available": 140},
            "VIP": {"price": 60.00, "capacity": 50, "available": 25}
        }
    },
    {
        "id": "EVT-109",
        "name": "Symphony Under the Stars",
        "category": "Music",
        "description": "An enchanting evening of orchestral classics performed outdoors by the City Philharmonic Orchestra.",
        "date": "2026-12-01",
        "time": "19:00",
        "venue": "Botanical Gardens Pavilion",
        "city": "Downtown",
        "image": "https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=800&q=80",
        "featured": False,
        "booking_fee": BOOKING_FEE,
        "ticket_types": {
            "General": {"price": 45.00, "capacity": 180, "available": 110},
            "Premium": {"price": 85.00, "capacity": 70, "available": 42},
            "VIP": {"price": 135.00, "capacity": 25, "available": 10}
        }
    },
    {
        "id": "EVT-110",
        "name": "Indie Film Showcase",
        "category": "Theatre",
        "description": "Screening of short independent films followed by live director Q&A sessions and networking.",
        "date": "2026-12-05",
        "time": "17:30",
        "venue": "Cinema Lumiere",
        "city": "Tech Valley",
        "image": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=800&q=80",
        "featured": False,
        "booking_fee": BOOKING_FEE,
        "ticket_types": {
            "General": {"price": 18.00, "capacity": 90, "available": 45},
            "Premium": {"price": 32.00, "capacity": 40, "available": 20},
            "VIP": {"price": 55.00, "capacity": 15, "available": 6}
        }
    }
]

# In-Memory Booking Storage indexed by Booking ID for O(1) lookup
# Format: { "EVT-1001": booking_dict }
bookings_by_id = {}


# ==============================================================================
# REUSABLE HELPERS (Backend)
# ==============================================================================

def find_event(event_id):
    """Locate an event dictionary by event_id in O(n) time."""
    if not event_id:
        return None
    for ev in events:
        if ev["id"].upper() == str(event_id).strip().upper():
            return ev
    return None

def find_booking(booking_id):
    """Locate a booking dictionary by booking_id in O(1) average time."""
    if not booking_id:
        return None
    return bookings_by_id.get(str(booking_id).strip().upper())

def generate_booking_id():
    """Generate a unique sequential booking ID like EVT-1001."""
    global booking_counter
    bid = f"EVT-{booking_counter}"
    booking_counter += 1
    return bid

def calculate_total(ticket_price, quantity, booking_fee=BOOKING_FEE):
    """Calculate subtotal and total for a ticket order."""
    subtotal = round(float(ticket_price) * int(quantity), 2)
    fee = round(float(booking_fee), 2)
    total = round(subtotal + fee, 2)
    return {
        "unit_price": round(float(ticket_price), 2),
        "quantity": int(quantity),
        "subtotal": subtotal,
        "booking_fee": fee,
        "total": total
    }

def check_availability(event, ticket_type, quantity):
    """Check if the requested quantity for a ticket_type is available."""
    if not event or "ticket_types" not in event:
        return False, "Invalid event specified."
    
    if ticket_type not in event["ticket_types"]:
        return False, f"Ticket type '{ticket_type}' does not exist for this event."
    
    t_info = event["ticket_types"][ticket_type]
    try:
        qty = int(quantity)
        if qty <= 0:
            return False, "Ticket quantity must be at least 1."
    except (ValueError, TypeError):
        return False, "Invalid ticket quantity."

    if t_info["available"] < qty:
        return False, f"Only {t_info['available']} '{ticket_type}' tickets remaining."
    
    return True, "Available"

def validate_booking(data):
    """Validate incoming JSON booking payload with robust type checks."""
    if not isinstance(data, dict):
        return False, "Invalid JSON payload format."
    
    name = str(data.get("name") or "").strip()
    email = str(data.get("email") or "").strip()
    mobile = str(data.get("mobile") or "").strip()
    event_id = str(data.get("event_id") or "").strip()
    ticket_type = str(data.get("ticket_type") or "").strip()
    quantity = data.get("quantity")

    if not name or len(name) < 2:
        return False, "Full Name is required (at least 2 characters)."
    
    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not email or not re.match(email_regex, email):
        return False, "A valid Email address is required."
    
    mobile_regex = r"^\+?[0-9\s\-]{7,15}$"
    if not mobile or not re.match(mobile_regex, mobile):
        return False, "A valid Mobile number is required (7-15 digits)."
    
    if not event_id:
        return False, "Event ID is required."
    
    event = find_event(event_id)
    if not event:
        return False, "Event not found."
    
    if not ticket_type or ticket_type not in event["ticket_types"]:
        return False, f"Invalid ticket type '{ticket_type}'."
    
    if quantity is None or isinstance(quantity, bool):
        return False, "Quantity must be a valid integer."

    try:
        qty = int(quantity)
        if float(quantity) != qty:
            return False, "Quantity must be a whole integer."
        if qty <= 0:
            return False, "Quantity must be a positive integer."
    except (ValueError, TypeError):
        return False, "Quantity must be a valid integer."
    
    avail, msg = check_availability(event, ticket_type, qty)
    if not avail:
        return False, msg
    
    return True, "Validation successful"

def cancel_booking(booking_id):
    """Cancel a confirmed booking and restore ticket availability."""
    booking = find_booking(booking_id)
    if not booking:
        return False, "Booking ID not found."
    
    if booking["status"] == "Cancelled":
        return False, "Booking is already cancelled."
    
    if booking["status"] != "Confirmed":
        return False, f"Cannot cancel booking with status '{booking['status']}'."
    
    # Restore availability
    event = find_event(booking["event_id"])
    if event and booking["ticket_type"] in event["ticket_types"]:
        event["ticket_types"][booking["ticket_type"]]["available"] += booking["quantity"]
    
    booking["status"] = "Cancelled"
    booking["cancelled_at"] = datetime.now().isoformat()
    return True, "Booking cancelled successfully."

def success_response(data, status_code=200):
    return jsonify({"status": "success", "data": data}), status_code

def error_response(message, status_code=400):
    return jsonify({"status": "error", "message": message}), status_code


# ==============================================================================
# HTML ROUTES
# ==============================================================================

@app.route("/")
def page_home():
    return render_template("index.html")

@app.route("/events")
def page_events():
    return render_template("events.html")

@app.route("/events/<event_id>")
def page_event_detail(event_id):
    return render_template("event-details.html", event_id=event_id)

@app.route("/bookings")
def page_bookings():
    return render_template("bookings.html")

@app.route("/ticket/<booking_id>")
def page_ticket(booking_id):
    return render_template("ticket.html", booking_id=booking_id)


# ==============================================================================
# REST API ENDPOINTS
# ==============================================================================

@app.route("/api/events", methods=["GET"])
def api_get_events():
    """Retrieve list of all events."""
    return success_response(events)

@app.route("/api/events/<event_id>", methods=["GET"])
def api_get_event_by_id(event_id):
    """Retrieve details for a single event."""
    event = find_event(event_id)
    if not event:
        return error_response("Event not found.", 404)
    return success_response(event)

@app.route("/api/events/search", methods=["GET"])
def api_search_events():
    """Search and filter events by q, category, date, max_price, available_only."""
    query = request.args.get("q", "").strip().lower()
    category = request.args.get("category", "").strip()
    date_str = request.args.get("date", "").strip()
    max_price_str = request.args.get("max_price", "").strip()
    available_only = request.args.get("available_only", "false").lower() == "true"

    filtered = events

    if query:
        filtered = [
            e for e in filtered
            if query in e["name"].lower()
            or query in e["venue"].lower()
            or query in e["city"].lower()
            or query in e["category"].lower()
            or query in e["description"].lower()
        ]

    if category and category.lower() != "all":
        filtered = [e for e in filtered if e["category"].lower() == category.lower()]

    if date_str:
        filtered = [e for e in filtered if e["date"] == date_str]

    if max_price_str:
        try:
            max_p = float(max_price_str)
            filtered = [
                e for e in filtered
                if any(t["price"] <= max_p for t in e["ticket_types"].values())
            ]
        except ValueError:
            pass

    if available_only:
        filtered = [
            e for e in filtered
            if any(t["available"] > 0 for t in e["ticket_types"].values())
        ]

    return success_response(filtered)

@app.route("/api/bookings", methods=["POST"])
def api_create_booking():
    """Create a new booking."""
    data = request.get_json(silent=True)
    if data is None:
        return error_response("Missing or malformed JSON body.", 400)
    
    valid, msg = validate_booking(data)
    if not valid:
        return error_response(msg, 400)
    
    event = find_event(data["event_id"])
    ticket_type = str(data["ticket_type"]).strip()
    quantity = int(data["quantity"])
    
    # Calculate pricing
    ticket_info = event["ticket_types"][ticket_type]
    price_details = calculate_total(ticket_info["price"], quantity, event.get("booking_fee", BOOKING_FEE))
    
    # Reduce available ticket count
    ticket_info["available"] -= quantity
    
    # Create booking record
    b_id = generate_booking_id()
    booking_record = {
        "booking_id": b_id,
        "created_at": datetime.now().isoformat(),
        "customer": {
            "name": str(data["name"]).strip(),
            "email": str(data["email"]).strip(),
            "mobile": str(data["mobile"]).strip()
        },
        "event_id": event["id"],
        "event_name": event["name"],
        "event_category": event["category"],
        "event_date": event["date"],
        "event_time": event["time"],
        "event_venue": event["venue"],
        "event_city": event["city"],
        "event_image": event["image"],
        "ticket_type": ticket_type,
        "quantity": quantity,
        "pricing": price_details,
        "status": "Confirmed"
    }
    
    bookings_by_id[b_id] = booking_record
    
    return success_response(booking_record, 201)

@app.route("/api/bookings", methods=["GET"])
def api_get_all_bookings():
    """Retrieve all bookings."""
    b_list = list(bookings_by_id.values())
    b_list.sort(key=lambda x: x["created_at"], reverse=True)
    return success_response(b_list)

@app.route("/api/bookings/<booking_id>", methods=["GET"])
def api_get_booking_by_id(booking_id):
    """Retrieve details for a single booking."""
    booking = find_booking(booking_id)
    if not booking:
        return error_response("Booking ID not found.", 404)
    return success_response(booking)

@app.route("/api/bookings/<booking_id>/cancel", methods=["PATCH"])
def api_cancel_booking(booking_id):
    """Cancel a booking by ID."""
    ok, msg = cancel_booking(booking_id)
    if not ok:
        return error_response(msg, 400)
    
    booking = find_booking(booking_id)
    return success_response(booking)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
