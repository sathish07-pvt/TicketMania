from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    bookings = db.relationship('Booking', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    @property
    def is_admin(self):
        return self.role == 'admin'


class City(db.Model):
    __tablename__ = 'cities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), default='Tamil Nadu')
    slug = db.Column(db.String(100), unique=True, nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    theatres = db.relationship('Theatre', backref='city', lazy=True)


class Theatre(db.Model):
    __tablename__ = 'theatres'
    
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    area = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    distance_km = db.Column(db.Float, default=2.5)
    total_screens = db.Column(db.Integer, default=2)
    amenities = db.Column(db.String(255), default="Dolby Atmos, 4K Laser, Food Court, Parking, Recliners")
    image_url = db.Column(db.String(255), default="/static/images/theatres/theatre_default.jpg")
    is_active = db.Column(db.Boolean, default=True)
    
    screens = db.relationship('Screen', backref='theatre', cascade='all, delete-orphan', lazy=True)
    shows = db.relationship('Show', backref='theatre', cascade='all, delete-orphan', lazy=True)


class Screen(db.Model):
    __tablename__ = 'screens'
    
    id = db.Column(db.Integer, primary_key=True)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatres.id'), nullable=False)
    screen_name = db.Column(db.String(50), nullable=False)  # e.g., "Screen 1 - Maris Atmos"
    screen_type = db.Column(db.String(50), default="Dolby Atmos 4K")
    total_rows = db.Column(db.Integer, default=10)  # Rows A through J
    total_cols = db.Column(db.Integer, default=14)  # 1 through 14
    
    shows = db.relationship('Show', backref='screen', cascade='all, delete-orphan', lazy=True)


class Movie(db.Model):
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    language = db.Column(db.String(50), default="Tamil")  # Tamil, Telugu, Hindi, English, etc.
    genre = db.Column(db.String(100), default="Action, Thriller")
    duration_mins = db.Column(db.Integer, default=155)
    release_date = db.Column(db.String(50), default="2025")
    rating = db.Column(db.String(10), default="UA")
    user_rating = db.Column(db.Float, default=9.2)
    votes_count = db.Column(db.Integer, default=14200)
    synopsis = db.Column(db.Text, nullable=False)
    poster_url = db.Column(db.String(255), nullable=False)
    backdrop_url = db.Column(db.String(255), nullable=True)
    trailer_url = db.Column(db.String(255), nullable=True)
    is_now_showing = db.Column(db.Boolean, default=True)
    is_popular = db.Column(db.Boolean, default=False)
    is_upcoming = db.Column(db.Boolean, default=False)
    
    shows = db.relationship('Show', backref='movie', cascade='all, delete-orphan', lazy=True)
    
    @property
    def duration_formatted(self):
        hrs = self.duration_mins // 60
        mins = self.duration_mins % 60
        return f"{hrs}h {mins}m"


class Show(db.Model):
    __tablename__ = 'shows'
    
    id = db.Column(db.Integer, primary_key=True)
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatres.id'), nullable=False)
    screen_id = db.Column(db.Integer, db.ForeignKey('screens.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    show_date = db.Column(db.String(20), nullable=False)  # YYYY-MM-DD
    show_time = db.Column(db.String(20), nullable=False)  # e.g., "10:30 AM", "02:15 PM"
    time_category = db.Column(db.String(20), default="Evening") # Morning, Afternoon, Evening, Night
    format = db.Column(db.String(20), default="2D")  # 2D, 3D, IMAX 2D, Dolby Atmos
    
    # Tier prices
    price_vip = db.Column(db.Float, default=220.0)      # Rows A-B (Recliner/VIP)
    price_premium = db.Column(db.Float, default=160.0)  # Rows C-F (Executive)
    price_normal = db.Column(db.Float, default=100.0)   # Rows G-J (Classic)
    
    bookings = db.relationship('Booking', backref='show', cascade='all, delete-orphan', lazy=True)


class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    show_id = db.Column(db.Integer, db.ForeignKey('shows.id'), nullable=False)
    
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    
    ticket_count = db.Column(db.Integer, nullable=False)
    total_ticket_price = db.Column(db.Float, nullable=False)  # Base tickets sum
    base_convenience_fee = db.Column(db.Float, nullable=False) # ₹20 * N
    discount_amount = db.Column(db.Float, nullable=False)      # ₹5 for odd, ₹10 for even
    final_convenience_fee = db.Column(db.Float, nullable=False)# (₹20 * N) - discount
    total_amount = db.Column(db.Float, nullable=False)         # total_ticket_price + final_convenience_fee
    
    payment_status = db.Column(db.String(20), default='SUCCESS') # SUCCESS, PENDING, FAILED, CANCELLED
    payment_method = db.Column(db.String(30), default='UPI')     # UPI, CARD, NETBANKING
    payment_ref = db.Column(db.String(50), nullable=True)
    
    booking_time = db.Column(db.DateTime, default=datetime.utcnow)
    cancellation_status = db.Column(db.String(20), default='NONE') # NONE, CANCELLED
    refund_amount = db.Column(db.Float, default=0.0)
    
    seats = db.relationship('BookingSeat', backref='booking', cascade='all, delete-orphan', lazy=True)


class BookingSeat(db.Model):
    __tablename__ = 'booking_seats'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)  # e.g., "A5", "C12"
    tier = db.Column(db.String(20), default='PREMIUM')       # VIP, PREMIUM, NORMAL
    price = db.Column(db.Float, nullable=False)
