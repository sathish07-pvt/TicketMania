"""
Booking Service for Ticket Mania

Manages seat reservations, double-booking prevention, 
booking confirmation, and simulated cancellations.
"""

import random
import string
from datetime import datetime
from typing import List, Dict, Any, Tuple
from models import db, Booking, BookingSeat, Show
from services.pricing import calculate_order_summary


def generate_booking_code(city_slug: str = "TRC") -> str:
    """Generate a readable unique demo booking reference code like TM-TRC-489271."""
    prefix = (city_slug[:3] if city_slug else "TRC").upper()
    digits = ''.join(random.choices(string.digits, k=6))
    return f"TM-{prefix}-{digits}"


def get_booked_seats_for_show(show_id: int) -> List[str]:
    """
    Returns list of seat numbers currently booked and active for the given show.
    Excludes cancelled bookings.
    """
    active_bookings = Booking.query.filter(
        Booking.show_id == show_id,
        Booking.payment_status == 'SUCCESS',
        Booking.cancellation_status != 'CANCELLED'
    ).all()
    
    booked_seats = []
    for b in active_bookings:
        for s in b.seats:
            booked_seats.append(s.seat_number)
            
    return booked_seats


def create_booking(
    show_id: int,
    seats_data: List[Dict[str, Any]],
    customer_info: Dict[str, str],
    payment_method: str = "UPI",
    user_id: int = None
) -> Tuple[bool, Any]:
    """
    Attempt to create a booking for the specified show and seats.
    Prevents double booking by validating that none of the requested seats are already booked.
    
    Args:
        show_id: ID of the Show
        seats_data: List of dicts: [{"seat_number": "A5", "tier": "VIP", "price": 220.0}, ...]
        customer_info: {"name": str, "email": str, "phone": str}
        payment_method: "UPI", "CARD", or "NETBANKING"
        user_id: Optional logged in User ID
        
    Returns:
        (success: bool, booking_or_error: Booking | str)
    """
    if not seats_data:
        return False, "No seats selected."
        
    show = db.session.get(Show, show_id)
    if not show:
        return False, "Show not found."
        
    # Check for duplicate seat selections within the request itself
    requested_seat_numbers = [s["seat_number"] for s in seats_data]
    if len(requested_seat_numbers) != len(set(requested_seat_numbers)):
        return False, "Duplicate seat numbers in selection."
        
    # Check against already booked active seats in database
    already_booked = get_booked_seats_for_show(show_id)
    conflicts = set(requested_seat_numbers).intersection(set(already_booked))
    if conflicts:
        return False, f"Seats already booked by another user: {', '.join(sorted(conflicts))}"
        
    # Calculate pricing
    summary = calculate_order_summary(seats_data)
    
    city_slug = show.theatre.city.slug if show.theatre and show.theatre.city else "TRC"
    booking_code = generate_booking_code(city_slug)
    
    # Ensure uniqueness of booking code
    while Booking.query.filter_by(booking_code=booking_code).first() is not None:
        booking_code = generate_booking_code(city_slug)
        
    booking = Booking(
        booking_code=booking_code,
        user_id=user_id,
        show_id=show_id,
        customer_name=customer_info.get("name", "Demo Guest"),
        customer_email=customer_info.get("email", "guest@ticketmania.com"),
        customer_phone=customer_info.get("phone", "9876543210"),
        ticket_count=summary["ticket_count"],
        total_ticket_price=summary["subtotal_ticket_price"],
        base_convenience_fee=summary["base_convenience_fee"],
        discount_amount=summary["discount_amount"],
        final_convenience_fee=summary["final_convenience_fee"],
        total_amount=summary["grand_total"],
        payment_status="SUCCESS",
        payment_method=payment_method,
        payment_ref=f"PAY-{random.randint(100000, 999999)}",
        booking_time=datetime.utcnow(),
        cancellation_status="NONE",
        refund_amount=0.0
    )
    
    db.session.add(booking)
    db.session.flush() # obtain booking.id
    
    for s in seats_data:
        seat_record = BookingSeat(
            booking_id=booking.id,
            seat_number=s["seat_number"],
            tier=s.get("tier", "PREMIUM"),
            price=float(s.get("price", 150.0))
        )
        db.session.add(seat_record)
        
    db.session.commit()
    return True, booking


def cancel_booking(booking_id: int, user_id: int = None) -> Tuple[bool, str, float]:
    """
    Cancel an existing booking and calculate demo refund.
    Demo refund policy: 100% refund of base ticket price; 
    convenience fee is retained per simulated terms.
    
    Returns:
        (success: bool, message: str, refund_amount: float)
    """
    query = Booking.query.filter_by(id=booking_id)
    if user_id:
        query = query.filter_by(user_id=user_id)
    booking = query.first()
    
    if not booking:
        return False, "Booking not found or access denied.", 0.0
        
    if booking.cancellation_status == "CANCELLED":
        return False, "This booking has already been cancelled.", 0.0
        
    if booking.payment_status != "SUCCESS":
        return False, "Only successful bookings can be cancelled.", 0.0
        
    # Simulated refund rule: 100% of ticket price refunded
    refund_amount = booking.total_ticket_price
    
    booking.cancellation_status = "CANCELLED"
    booking.refund_amount = refund_amount
    db.session.commit()
    
    return True, f"Booking {booking.booking_code} cancelled successfully. ₹{refund_amount:.2f} refunded.", refund_amount
