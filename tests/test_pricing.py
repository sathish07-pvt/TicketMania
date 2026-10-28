import pytest
from services.pricing import calculate_convenience_fee, calculate_order_summary

def test_specification_pricing_table():
    """
    Test the exact convenience fee pricing table provided in Section 6 of the specifications.
    
    Number of tickets | Base fee | Discount | Final fee
    1                 | 20       | 5        | 15
    2                 | 40       | 10       | 30
    3                 | 60       | 5        | 55
    4                 | 80       | 10       | 70
    5                 | 100      | 5        | 95
    6                 | 120      | 10       | 110
    7                 | 140      | 5        | 135
    8                 | 160      | 10       | 150
    9                 | 180      | 5        | 175
    10                | 200      | 10       | 190
    """
    expected_table = [
        (1, 20.0, 5.0, 15.0),
        (2, 40.0, 10.0, 30.0),
        (3, 60.0, 5.0, 55.0),
        (4, 80.0, 10.0, 70.0),
        (5, 100.0, 5.0, 95.0),
        (6, 120.0, 10.0, 110.0),
        (7, 140.0, 5.0, 135.0),
        (8, 160.0, 10.0, 150.0),
        (9, 180.0, 5.0, 175.0),
        (10, 200.0, 10.0, 190.0),
    ]
    
    for ticket_count, expected_base, expected_discount, expected_final in expected_table:
        result = calculate_convenience_fee(ticket_count)
        assert result["ticket_count"] == ticket_count
        assert result["base_fee"] == expected_base, f"Failed base fee for {ticket_count} tickets"
        assert result["discount"] == expected_discount, f"Failed discount for {ticket_count} tickets"
        assert result["final_fee"] == expected_final, f"Failed final fee for {ticket_count} tickets"


def test_odd_even_discount_rules():
    """Verify that odd quantities get ₹5 discount and even quantities get ₹10 discount."""
    for n in [1, 3, 5, 7, 9, 11, 25]:
        res = calculate_convenience_fee(n)
        assert res["is_odd"] is True
        assert res["discount"] == 5.0
        assert res["final_fee"] == (20.0 * n) - 5.0

    for n in [2, 4, 6, 8, 10, 12, 30]:
        res = calculate_convenience_fee(n)
        assert res["is_odd"] is False
        assert res["discount"] == 10.0
        assert res["final_fee"] == (20.0 * n) - 10.0


def test_zero_and_invalid_inputs():
    """Verify handling of 0, negative, and non-integer values."""
    assert calculate_convenience_fee(0)["final_fee"] == 0.0
    assert calculate_convenience_fee(-5)["final_fee"] == 0.0
    assert calculate_convenience_fee("two")["final_fee"] == 0.0


def test_theatre_ticket_price_preservation():
    """
    Ensure the discount applies strictly to the convenience fee
    and does NOT reduce the original theatre ticket price.
    """
    seats = [
        {"seat_number": "A1", "tier": "VIP", "price": 220.0},
        {"seat_number": "A2", "tier": "VIP", "price": 220.0},
        {"seat_number": "C5", "tier": "PREMIUM", "price": 160.0},
    ]
    
    summary = calculate_order_summary(seats)
    expected_subtotal = 220.0 + 220.0 + 160.0  # 600.0
    assert summary["subtotal_ticket_price"] == expected_subtotal
    
    # 3 tickets -> odd discount ₹5, base fee ₹60, final fee ₹55
    assert summary["base_convenience_fee"] == 60.0
    assert summary["discount_amount"] == 5.0
    assert summary["final_convenience_fee"] == 55.0
    
    # Grand total should be exactly subtotal + final_convenience_fee (600 + 55 = 655)
    assert summary["grand_total"] == 655.0


def test_conventional_fee_savings_comparison():
    """
    Verify customer savings calculation against conventional benchmark (₹35/ticket).
    """
    res = calculate_convenience_fee(4)
    # Conventional: 4 * 35 = 140
    # Ticket Mania: (4 * 20) - 10 = 70
    # Savings: 140 - 70 = 70
    assert res["conventional_fee"] == 140.0
    assert res["final_fee"] == 70.0
    assert res["customer_savings"] == 70.0
