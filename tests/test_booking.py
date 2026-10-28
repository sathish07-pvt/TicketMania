import pytest
from flask import Flask
from models import db, User, City, Theatre, Screen, Movie, Show, Booking, BookingSeat
from services.booking_service import create_booking, cancel_booking, get_booked_seats_for_show

@pytest.fixture
def test_app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Seed test city, theatre, screen, movie, show
        city = City(name="Tiruchirappalli (Trichy)", slug="trichy", is_default=True)
        db.session.add(city)
        db.session.commit()
        
        theatre = Theatre(
            city_id=city.id,
            name="LA Cinema Maris Complex",
            area="Thillai Nagar",
            address="Fort Station Rd, Trichy"
        )
        db.session.add(theatre)
        db.session.commit()
        
        screen = Screen(theatre_id=theatre.id, screen_name="Screen 1 Atmos", total_rows=10, total_cols=14)
        db.session.add(screen)
        db.session.commit()
        
        movie = Movie(
            title="The Greatest of All Time",
            slug="goat-tamil",
            language="Tamil",
            genre="Action, Sci-Fi",
            duration_mins=183,
            synopsis="A high-octane spy action thriller.",
            poster_url="/static/images/movies/goat.jpg"
        )
        db.session.add(movie)
        db.session.commit()
        
        show = Show(
            theatre_id=theatre.id,
            screen_id=screen.id,
            movie_id=movie.id,
            show_date="2025-05-15",
            show_time="06:30 PM",
            price_vip=220.0,
            price_premium=160.0,
            price_normal=100.0
        )
        db.session.add(show)
        db.session.commit()
        
        yield app
        db.session.remove()
        db.drop_all()


def test_successful_booking_and_odd_discount(test_app):
    with test_app.app_context():
        show = Show.query.first()
        seats_data = [
            {"seat_number": "A1", "tier": "VIP", "price": 220.0},
            {"seat_number": "A2", "tier": "VIP", "price": 220.0},
            {"seat_number": "A3", "tier": "VIP", "price": 220.0},
        ]
        customer_info = {"name": "Sathish", "email": "sathish@example.com", "phone": "9876543210"}
        
        success, booking = create_booking(show.id, seats_data, customer_info, payment_method="UPI")
        assert success is True
        assert booking.ticket_count == 3
        assert booking.total_ticket_price == 660.0
        assert booking.base_convenience_fee == 60.0
        # 3 tickets is odd -> ₹5 discount
        assert booking.discount_amount == 5.0
        assert booking.final_convenience_fee == 55.0
        assert booking.total_amount == 660.0 + 55.0  # 715.0
        assert len(booking.seats) == 3


def test_double_booking_prevention(test_app):
    with test_app.app_context():
        show = Show.query.first()
        seats_user_1 = [{"seat_number": "B4", "tier": "PREMIUM", "price": 160.0}]
        seats_user_2 = [{"seat_number": "B4", "tier": "PREMIUM", "price": 160.0}]
        
        # User 1 books B4
        success1, b1 = create_booking(show.id, seats_user_1, {"name": "User 1", "email": "u1@test.com", "phone": "111"})
        assert success1 is True
        
        # User 2 attempts to book the same B4 seat
        success2, err = create_booking(show.id, seats_user_2, {"name": "User 2", "email": "u2@test.com", "phone": "222"})
        assert success2 is False
        assert "Seats already booked" in err


def test_booking_cancellation_and_seat_release(test_app):
    with test_app.app_context():
        show = Show.query.first()
        seats = [{"seat_number": "C8", "tier": "PREMIUM", "price": 160.0}]
        success, booking = create_booking(show.id, seats, {"name": "User", "email": "u@test.com", "phone": "123"})
        assert success is True
        
        # Check seat is currently booked
        assert "C8" in get_booked_seats_for_show(show.id)
        
        # Cancel booking
        canc_ok, msg, refund = cancel_booking(booking.id)
        assert canc_ok is True
        assert refund == 160.0
        
        # Verify seat C8 is now released back to available pool
        assert "C8" not in get_booked_seats_for_show(show.id)
