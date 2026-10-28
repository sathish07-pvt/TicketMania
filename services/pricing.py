"""
Ticket Mania - Convenience Fee and Pricing Engine

Core USP:
- Base convenience fee: ₹20 per ticket.
- Odd number of tickets (1, 3, 5, 7, 9, etc.): ₹5 discount on the total convenience fee.
- Even number of tickets (2, 4, 6, 8, 10, etc.): ₹10 discount on the total convenience fee.
- Discount applies to the convenience fee only (never reduces theatre ticket price).
- Applied once per booking.
"""

from typing import Dict, Any, List

BASE_FEE_PER_TICKET = 20.0
ODD_DISCOUNT = 5.0
EVEN_DISCOUNT = 10.0
CONVENTIONAL_FEE_PER_TICKET = 35.0  # Illustrative benchmark comparison


def calculate_convenience_fee(ticket_count: int) -> Dict[str, Any]:
    """
    Calculate the convenience fee and applicable Ticket Mania discount.
    
    Args:
        ticket_count: Number of tickets being booked (N >= 0)
        
    Returns:
        dict containing:
            - ticket_count: int
            - base_fee: float (20 * N)
            - discount: float (5 if N is odd else 10 for N > 0)
            - final_fee: float (base_fee - discount, min 0)
            - is_odd: bool
            - conventional_fee: float (35 * N)
            - customer_savings: float (conventional_fee - final_fee)
    """
    if not isinstance(ticket_count, int) or ticket_count <= 0:
        return {
            "ticket_count": 0,
            "base_fee": 0.0,
            "discount": 0.0,
            "final_fee": 0.0,
            "is_odd": False,
            "conventional_fee": 0.0,
            "customer_savings": 0.0,
            "discount_label": "No discount (0 tickets)"
        }
        
    base_fee = BASE_FEE_PER_TICKET * ticket_count
    is_odd = (ticket_count % 2 != 0)
    discount = ODD_DISCOUNT if is_odd else EVEN_DISCOUNT
    final_fee = max(0.0, base_fee - discount)
    
    # Illustrative comparison with standard platform fee of ₹35/ticket
    conventional_fee = CONVENTIONAL_FEE_PER_TICKET * ticket_count
    customer_savings = max(0.0, conventional_fee - final_fee)
    
    discount_label = f"₹{int(discount)} Ticket Mania {'Odd' if is_odd else 'Even'} Booking Discount"
    
    return {
        "ticket_count": ticket_count,
        "base_fee": round(base_fee, 2),
        "discount": round(discount, 2),
        "final_fee": round(final_fee, 2),
        "is_odd": is_odd,
        "conventional_fee": round(conventional_fee, 2),
        "customer_savings": round(customer_savings, 2),
        "discount_label": discount_label
    }


def calculate_order_summary(seats: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate complete order breakdown for selected seats.
    
    Args:
        seats: List of dicts representing seats, each with at least 'price' (float)
               and 'seat_number' (str).
               
    Returns:
        dict containing itemized tickets breakdown, subtotal, convenience fee,
        discount, final fee, grand total, and conventional comparison.
    """
    ticket_count = len(seats)
    subtotal_ticket_price = sum(float(s.get('price', 0.0)) for s in seats)
    
    fee_breakdown = calculate_convenience_fee(ticket_count)
    grand_total = subtotal_ticket_price + fee_breakdown["final_fee"]
    
    return {
        "ticket_count": ticket_count,
        "seats": seats,
        "subtotal_ticket_price": round(subtotal_ticket_price, 2),
        "base_convenience_fee": fee_breakdown["base_fee"],
        "discount_amount": fee_breakdown["discount"],
        "final_convenience_fee": fee_breakdown["final_fee"],
        "is_odd": fee_breakdown["is_odd"],
        "discount_label": fee_breakdown["discount_label"],
        "grand_total": round(grand_total, 2),
        "conventional_fee": fee_breakdown["conventional_fee"],
        "customer_savings": fee_breakdown["customer_savings"]
    }
