# Ticket Mania — Location-Based Movie Ticket Booking Platform

**Ticket Mania** is a modern, responsive movie ticket booking web application inspired by BookMyShow and District, featuring a customer-friendly convenience fee discount system, location-based theatre discovery defaulting to **Tiruchirappalli (Trichy), Tamil Nadu**, an interactive seat booking layout, simulated payment workflows, and an administrative control panel.

---

## 🌟 The Core USP: Transparent Convenience Fee Discount System

Unlike conventional movie ticketing platforms that charge high convenience fees (~₹35 per ticket), Ticket Mania offers a lower base fee of **₹20 per ticket** and applies automatic tiered discounts based on the total number of tickets in a single booking:

- **Odd number of tickets (1, 3, 5, 7, 9, etc.):** **₹5 flat discount** on the total convenience fee.
- **Even number of tickets (2, 4, 6, 8, 10, etc.):** **₹10 flat discount** on the total convenience fee.
- **The theatre's original ticket price is 100% untouched.** Discounts apply strictly to Ticket Mania's convenience fee.
- **Applied once per booking**, transparently itemized prior to payment.

### Pricing Formula
$$\text{Base Fee} = ₹20 \times N$$
$$\text{Discount} = \begin{cases} ₹5 & \text{if } N \text{ is odd} \\ ₹10 & \text{if } N \text{ is even} \end{cases}$$
$$\text{Total Convenience Fee} = (₹20 \times N) - \text{Discount}$$

### Official Pricing & Savings Table

| Number of Tickets | Base Fee (₹20 × N) | Ticket Mania Discount | Final Fee Payable | Standard Platform Fee (~₹35/tkt) | Customer Savings |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | ₹20 | ₹5 | **₹15** | ₹35 | **₹20** |
| **2** | ₹40 | ₹10 | **₹30** | ₹70 | **₹40** |
| **3** | ₹60 | ₹5 | **₹55** | ₹105 | **₹50** |
| **4** | ₹80 | ₹10 | **₹70** | ₹140 | **₹70** |
| **5** | ₹100 | ₹5 | **₹95** | ₹175 | **₹80** |
| **6** | ₹120 | ₹10 | **₹110** | ₹210 | **₹100** |
| **7** | ₹140 | ₹5 | **₹135** | ₹245 | **₹110** |
| **8** | ₹160 | ₹10 | **₹150** | ₹280 | **₹130** |
| **9** | ₹180 | ₹5 | **₹175** | ₹315 | **₹140** |
| **10** | ₹200 | ₹10 | **₹190** | ₹350 | **₹160** |

---

## 📍 Location-Based Theatre Discovery (Trichy Default)

- **Default Location:** Tiruchirappalli (Trichy), Tamil Nadu, India.
- **Authentic Demonstration Theatres in Trichy:**
  1. **LA Cinema Maris Complex** (Fort Station Rd / Thillai Nagar) — Maris Dolby Atmos & Royal 4K Laser.
  2. **Mega Star Cinemas** (Cantonment, Central Bus Stand) — Screen 1 & Screen 2.
  3. **Sona Mina Theatres** (Karur Bypass Road) — Sona Dolby Atmos & Mina Qube 4K.
  4. **Sri Venkatesha / Rohini Silver Screens** (K.K. Nagar).
  5. **Cauvery Theatre** (Srirangam / Tiruvanaikoil).
  6. **Ramakrishna Theatre** (Palakkarai).
- **Searchable Location Selector:** Switch between Trichy, Chennai, Coimbatore, Madurai, Salem, and Bengaluru.
- **Browser Geolocation:** Click *"Detect My Current Location"* to compute the nearest city via the Haversine formula, with a smooth fallback to Trichy if permission is denied.

---

## 🎟️ Key Features & Workflows

1. **Movie Catalog & Details:**
   - Filter by language (*Tamil, Telugu, English, Hindi*), status (*Now Showing, Coming Soon*), and genre.
   - Comprehensive detail page with backdrop, synopsis, censor rating, user reviews, trailer link, date picker, and showtimes grouped by cinema hall.

2. **Interactive Seating Layout:**
   - Curved cinematic screen indicator (*"Screen This Way"*).
   - Real-time seat statuses: Available, Selected (glowing crimson), Booked/Occupied (locked).
   - Tiered seating: VIP Recliner (Rows A–B), Premium Executive (Rows C–F), and Classic Normal (Rows G–J).
   - Floating summary drawer that updates live with ticket totals, convenience fees, and savings.
   - Real-time double-booking collision prevention.

3. **Transparent Checkout & Simulated Payment:**
   - Itemized bill breakdown with Ticket Mania discount badge and conventional platform savings comparison.
   - **Simulated Payment Options:**
     - **UPI:** Dynamic simulated QR code and mock UPI ID input.
     - **Debit / Credit Card:** Formatted 16-digit card input, expiry MM/YY, CVV.
     - **Net Banking:** Popular demo banks (HDFC, SBI, ICICI, Axis).
   - **Test Mode Toggle:** *"Simulate Payment Failure"* checkbox to verify error handling and retry mechanism without losing seat reservations.

4. **Digital Pass & Booking History:**
   - Unique alphanumeric booking code (e.g., `TM-TRC-892147`).
   - Digital perforated cinema boarding pass with movie metadata, seat numbers, simulated gate-scan QR code, and print/download button.
   - *"My Bookings"* page with full cancellation workflow (releases seats back to the hall and issues simulated refund).

5. **Administrative Dashboard (`/admin`):**
   - Secured with role-based authentication.
   - Metric cards: Total Bookings, Gross Revenue, Tickets Sold, Total Customer Savings on Fees.
   - Chart.js visual trend graphs.
   - Theatres CRUD, Movies Catalog Manager, Shows & Tier Pricing Scheduler.
   - **Live Seat Map Editor:** Click any seat to manually block or unblock it in real time.
   - Comprehensive audit log of all bookings with status filters.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.11+, Flask 3.0+
- **Database & ORM:** SQLite with Flask-SQLAlchemy 3.1+ (schema ready for MySQL / PostgreSQL migration)
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Visuals & Charts:** Chart.js, Google Fonts (*Plus Jakarta Sans*, *Inter*)
- **Automated Testing:** Pytest 8.2+

---

## 🚀 Setup & Execution Instructions

### 1. Clone or Open Workspace
```bash
cd "c:\Users\sathish\OneDrive\Desktop\Ticket Mania"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
Populate Trichy cinema complexes, trending movies, show schedules, and demo users:
```bash
python seed_data.py
```

### 4. Run Automated Unit Tests
Verify that all convenience fee calculations match the specification table and booking rules:
```bash
python -m pytest tests/ -v
```

### 5. Start the Web Server
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Pre-Seeded Demonstration Accounts

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Customer** | `demo@ticketmania.com` | `demo123` | Browsing, seat selection, booking history, cancellations |
| **Administrator** | `admin@ticketmania.com` | `admin123` | Full access to `/admin`, seat editor, pricing, and analytics |

---

## 📁 Project Directory Structure

```
Ticket Mania/
├── app.py                      # Application factory, routes, and error handlers
├── config.py                   # Configuration and pricing constants
├── models.py                   # SQLAlchemy models (User, City, Theatre, Screen, Movie, Show, Booking, BookingSeat)
├── seed_data.py                # Database population with Trichy & regional demo data
├── verify_integration.py       # Automated integration & endpoint test script
├── requirements.txt            # Python dependencies
├── services/
│   ├── __init__.py
│   ├── pricing.py              # Reusable convenience fee & order pricing engine
│   └── booking_service.py      # Seat reservation, double-booking prevention, cancellation
├── static/
│   ├── css/
│   │   ├── style.css           # Modern dark obsidian cinema theme, glassmorphism, responsive styles
│   │   └── seating.css         # Interactive cinema hall, seat layout, screen curve, legend
│   └── js/
│       ├── main.js             # City selector, geolocation, search, live fee calculator widget
│       ├── seating.js          # Dynamic seat selection, multi-seat rules, real-time fee updater
│       ├── payment.js          # Simulated UPI QR, card validator, mock success/failure toggles
│       └── admin.js            # Chart.js analytics, seat management, admin AJAX handlers
├── templates/
│   ├── base.html               # Master layout with navbar, sticky city picker, footer, modals
│   ├── index.html              # Homepage (Hero carousel, Now Showing, Trichy Theatres, Fee Calculator)
│   ├── movies.html             # All movies with language, genre, format filters
│   ├── movie_details.html      # Movie backdrop, synopsis, date selector, theatres with showtimes
│   ├── theatres.html           # Theatres directory with distance & amenities
│   ├── theatre_details.html    # Specific theatre info & current movie showtimes
│   ├── seat_selection.html     # Interactive screen layout with real-time price & discount breakdown
│   ├── checkout.html           # Transparent billing breakdown, Ticket Mania savings, payment simulator
│   ├── confirmation.html       # Digital cinema pass with simulated QR code, print/download
│   ├── my_bookings.html        # User booking history with details & cancellation
│   ├── offers.html             # Ticket Mania USP convenience fee savings breakdown & calculator
│   ├── auth/
│   │   ├── login.html          # User login with quick demo-fill buttons
│   │   └── register.html       # User registration
│   └── admin/
│       ├── dashboard.html      # Metrics, revenue, savings generated, Chart.js graphs
│       ├── theatres.html       # Manage theatres
│       ├── movies.html         # Manage movies
│       ├── shows.html          # Manage showtimes and ticket tier prices
│       ├── seat_editor.html    # Live seat map editor (block/unblock seats)
│       └── bookings.html       # Booking logs & demo refund triggers
└── tests/
    ├── __init__.py
    ├── test_pricing.py         # Pytest for convenience fee odd/even rules & price calculations
    └── test_booking.py         # Pytest for booking flow, seat double-booking prevention, cancellation
```

---

## ⚠️ Prototype Limitations & Roadmap to Production

1. **Simulation Disclaimer:** All cinema halls, show schedules, seat layouts, booking references, and payment gateways in this prototype are simulated for demonstration. Tickets are not valid for admission at physical cinema halls.
2. **Production Roadmap:**
   - **Exhibitor Integration:** Integrate with cinema Box Office ERP APIs (e.g., Vista, TicketNew/BookMyShow Partner APIs, Qube POS) for verified real-time seat status.
   - **Payment Gateway:** Replace the simulated payment sandbox with PCI-DSS compliant providers (e.g., Razorpay, Cashfree, or PayU).
   - **SMS & WhatsApp Dispatch:** Connect to Twilio or Gupshup for automated m-ticket dispatch with authentic digital barcode tokens.
   - **Geolocation & Maps:** Connect with Google Maps or Mapbox API to calculate live turn-by-turn driving distances from user GPS coordinates to cinema halls.
#   T i c k e t M a n i a  
 