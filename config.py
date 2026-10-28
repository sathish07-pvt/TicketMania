import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ticket-mania-super-secret-key-2025')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(BASE_DIR, 'ticket_mania.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEFAULT_CITY = "Tiruchirappalli (Trichy)"
    DEFAULT_CITY_SLUG = "trichy"
    
    # Ticket Mania USP Pricing Constants
    BASE_CONVENIENCE_FEE_PER_TICKET = 20.0
    ODD_TICKET_DISCOUNT = 5.0
    EVEN_TICKET_DISCOUNT = 10.0
    INDUSTRY_STANDARD_CONVENIENCE_FEE = 35.0  # For illustrative comparison
