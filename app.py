import os
import math
from datetime import datetime, date, timedelta
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for, 
    flash, session, jsonify, abort
)
from config import Config
from models import db, User, City, Theatre, Screen, Movie, Show, Booking, BookingSeat
from services.pricing import (
    calculate_convenience_fee, calculate_order_summary,
    BASE_FEE_PER_TICKET, ODD_DISCOUNT, EVEN_DISCOUNT, CONVENTIONAL_FEE_PER_TICKET
)
from services.booking_service import (
    create_booking, cancel_booking, get_booked_seats_for_show
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    
    # Haversine distance calculator for geolocation
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0 # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    # Context Processors
    @app.context_processor
    def inject_global_data():
        current_city_slug = session.get('city_slug', 'trichy')
        current_city = City.query.filter_by(slug=current_city_slug).first()
        if not current_city:
            current_city = City.query.filter_by(is_default=True).first()
            if current_city:
                session['city_slug'] = current_city.slug
                
        all_cities = City.query.order_by(City.name).all()
        
        current_user = None
        if 'user_id' in session:
            current_user = db.session.get(User, session['user_id'])
            
        return {
            'current_city': current_city,
            'all_cities': all_cities,
            'current_user': current_user,
            'now_date': date.today().strftime('%Y-%m-%d'),
            'current_year': datetime.now().year,
            'calculate_fee': calculate_convenience_fee,
            'base_fee': BASE_FEE_PER_TICKET,
            'odd_discount': ODD_DISCOUNT,
            'even_discount': EVEN_DISCOUNT,
            'conventional_fee': CONVENTIONAL_FEE_PER_TICKET
        }

    # Template filters
    @app.template_filter('currency')
    def currency_filter(value):
        try:
            return f"₹{float(value):,.2f}".replace('.00', '')
        except (ValueError, TypeError):
            return "₹0"

    # Admin check decorator
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please log in with admin credentials.", "warning")
                return redirect(url_for('login', next=request.url))
            user = db.session.get(User, session['user_id'])
            if not user or not user.is_admin:
                flash("Access denied. Admin privileges required.", "danger")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function

    # -------------------------------------------------------------
    # Location & Search Routes
    # -------------------------------------------------------------
    @app.route('/set-city/<slug>')
    def set_city(slug):
        city = City.query.filter_by(slug=slug).first()
        if city:
            session['city_slug'] = city.slug
            flash(f"Location changed to {city.name}", "info")
        else:
            flash("Selected city is not available.", "warning")
            
        next_url = request.args.get('next')
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect(url_for('index'))

    @app.route('/api/detect-city', methods=['POST'])
    def detect_city():
        """Match browser coordinates to nearest available city."""
        data = request.get_json() or {}
        user_lat = data.get('latitude')
        user_lng = data.get('longitude')
        
        if user_lat is None or user_lng is None:
            return jsonify({'success': False, 'message': 'Coordinates not provided'}), 400
            
        cities = City.query.filter(City.latitude.isnot(None), City.longitude.isnot(None)).all()
        if not cities:
            return jsonify({'success': False, 'message': 'No geolocation data configured'}), 404
            
        closest_city = None
        min_dist = float('inf')
        for c in cities:
            dist = haversine(user_lat, user_lng, c.latitude, c.longitude)
            if dist < min_dist:
                min_dist = dist
                closest_city = c
                
        if closest_city:
            session['city_slug'] = closest_city.slug
            return jsonify({
                'success': True,
                'city_name': closest_city.name,
                'city_slug': closest_city.slug,
                'distance_km': round(min_dist, 1)
            })
            
        return jsonify({'success': False, 'message': 'Could not determine city'}), 500

    # -------------------------------------------------------------
    # Core User Facing Routes
    # -------------------------------------------------------------
    @app.route('/')
    def index():
        city_slug = session.get('city_slug', 'trichy')
        city = City.query.filter_by(slug=city_slug).first() or City.query.filter_by(is_default=True).first()
        
        # Movies in selected city with active shows
        theatres = Theatre.query.filter_by(city_id=city.id, is_active=True).all() if city else []
        theatre_ids = [t.id for t in theatres]
        
        today_str = date.today().strftime('%Y-%m-%d')
        running_shows = Show.query.filter(Show.theatre_id.in_(theatre_ids), Show.show_date == today_str).all() if theatre_ids else []
        running_movie_ids = list(set([s.movie_id for s in running_shows]))
        
        now_showing_movies = Movie.query.filter(Movie.is_now_showing == True).all()
        popular_movies = [m for m in now_showing_movies if m.is_popular]
        upcoming_movies = Movie.query.filter_by(is_upcoming=True).all()
        tamil_movies = [m for m in now_showing_movies if m.language.lower() == 'tamil']
        regional_movies = [m for m in now_showing_movies if m.language.lower() != 'tamil']
        
        # Top 3 featured movies for hero carousel
        featured_movies = now_showing_movies[:3]
        
        return render_template(
            'index.html',
            city=city,
            theatres=theatres,
            now_showing_movies=now_showing_movies,
            popular_movies=popular_movies,
            upcoming_movies=upcoming_movies,
            tamil_movies=tamil_movies,
            regional_movies=regional_movies,
            featured_movies=featured_movies,
            running_shows=running_shows
        )

    @app.route('/movies')
    def movies():
        query = request.args.get('q', '').strip()
        language = request.args.get('language', '')
        genre = request.args.get('genre', '')
        status = request.args.get('status', 'now_showing')
        
        movies_query = Movie.query
        
        if status == 'upcoming':
            movies_query = movies_query.filter_by(is_upcoming=True)
        else:
            movies_query = movies_query.filter_by(is_now_showing=True)
            
        if query:
            movies_query = movies_query.filter(Movie.title.ilike(f'%{query}%'))
            
        if language:
            movies_query = movies_query.filter(Movie.language.ilike(f'%{language}%'))
            
        if genre:
            movies_query = movies_query.filter(Movie.genre.ilike(f'%{genre}%'))
            
        movies_list = movies_query.all()
        
        return render_template(
            'movies.html',
            movies=movies_list,
            search_query=query,
            selected_language=language,
            selected_genre=genre,
            selected_status=status
        )

    @app.route('/movie/<slug>')
    def movie_details(slug):
        movie = Movie.query.filter_by(slug=slug).first_or_404()
        
        city_slug = session.get('city_slug', 'trichy')
        city = City.query.filter_by(slug=city_slug).first() or City.query.filter_by(is_default=True).first()
        
        # Date filter
        selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
        
        # Available dates: next 4 days
        dates_list = []
        for i in range(4):
            d = date.today() + timedelta(days=i)
            dates_list.append({
                'date_str': d.strftime('%Y-%m-%d'),
                'day_name': 'Today' if i == 0 else ('Tomorrow' if i == 1 else d.strftime('%a')),
                'display': d.strftime('%d %b')
            })
            
        # Theatres in this city showing this movie on selected_date
        theatres = Theatre.query.filter_by(city_id=city.id, is_active=True).all()
        theatre_shows = {}
        for t in theatres:
            shows = Show.query.filter_by(
                theatre_id=t.id, 
                movie_id=movie.id, 
                show_date=selected_date
            ).order_by(Show.show_time).all()
            if shows:
                theatre_shows[t] = shows
                
        return render_template(
            'movie_details.html',
            movie=movie,
            city=city,
            selected_date=selected_date,
            dates_list=dates_list,
            theatre_shows=theatre_shows
        )

    @app.route('/theatres')
    def theatres():
        city_slug = session.get('city_slug', 'trichy')
        city = City.query.filter_by(slug=city_slug).first() or City.query.filter_by(is_default=True).first()
        
        query = request.args.get('q', '').strip()
        theatres_query = Theatre.query.filter_by(city_id=city.id, is_active=True)
        if query:
            theatres_query = theatres_query.filter(
                (Theatre.name.ilike(f'%{query}%')) | (Theatre.area.ilike(f'%{query}%'))
            )
        theatres_list = theatres_query.order_by(Theatre.distance_km).all()
        
        # Collect currently playing movie titles for each theatre
        today_str = date.today().strftime('%Y-%m-%d')
        theatre_movies = {}
        for t in theatres_list:
            shows = Show.query.filter_by(theatre_id=t.id, show_date=today_str).all()
            movie_ids = list(set([s.movie_id for s in shows]))
            theatre_movies[t.id] = Movie.query.filter(Movie.id.in_(movie_ids)).all() if movie_ids else []
            
        return render_template(
            'theatres.html',
            city=city,
            theatres=theatres_list,
            theatre_movies=theatre_movies,
            search_query=query
        )

    @app.route('/theatre/<int:theatre_id>')
    def theatre_details(theatre_id):
        theatre = Theatre.query.get_or_404(theatre_id)
        selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
        
        dates_list = []
        for i in range(4):
            d = date.today() + timedelta(days=i)
            dates_list.append({
                'date_str': d.strftime('%Y-%m-%d'),
                'day_name': 'Today' if i == 0 else ('Tomorrow' if i == 1 else d.strftime('%a')),
                'display': d.strftime('%d %b')
            })
            
        shows = Show.query.filter_by(theatre_id=theatre.id, show_date=selected_date).order_by(Show.show_time).all()
        
        # Group by movie
        movie_shows = {}
        for s in shows:
            if s.movie not in movie_shows:
                movie_shows[s.movie] = []
            movie_shows[s.movie].append(s)
            
        return render_template(
            'theatre_details.html',
            theatre=theatre,
            selected_date=selected_date,
            dates_list=dates_list,
            movie_shows=movie_shows
        )

    # -------------------------------------------------------------
    # Seat Selection & Booking Workflow
    # -------------------------------------------------------------
    @app.route('/show/<int:show_id>/seats')
    def seat_selection(show_id):
        show = db.session.get(Show, show_id)
        if not show:
            abort(404)
            
        booked_seats = get_booked_seats_for_show(show.id)
        
        # Layout definition: Rows A through J
        # Rows A-B: VIP (e.g. ₹220)
        # Rows C-F: PREMIUM (e.g. ₹160)
        # Rows G-J: NORMAL (e.g. ₹100)
        rows_config = [
            {'row': 'A', 'tier': 'VIP', 'price': show.price_vip},
            {'row': 'B', 'tier': 'VIP', 'price': show.price_vip},
            {'row': 'C', 'tier': 'PREMIUM', 'price': show.price_premium},
            {'row': 'D', 'tier': 'PREMIUM', 'price': show.price_premium},
            {'row': 'E', 'tier': 'PREMIUM', 'price': show.price_premium},
            {'row': 'F', 'tier': 'PREMIUM', 'price': show.price_premium},
            {'row': 'G', 'tier': 'NORMAL', 'price': show.price_normal},
            {'row': 'H', 'tier': 'NORMAL', 'price': show.price_normal},
            {'row': 'I', 'tier': 'NORMAL', 'price': show.price_normal},
            {'row': 'J', 'tier': 'NORMAL', 'price': show.price_normal},
        ]
        
        return render_template(
            'seat_selection.html',
            show=show,
            booked_seats=booked_seats,
            rows_config=rows_config,
            total_cols=show.screen.total_cols
        )

    @app.route('/api/calculate-price', methods=['POST'])
    def api_calculate_price():
        """AJAX endpoint for instant real-time fee and discount updates."""
        data = request.get_json() or {}
        seats = data.get('seats', [])
        summary = calculate_order_summary(seats)
        return jsonify(summary)

    @app.route('/checkout', methods=['GET', 'POST'])
    def checkout():
        if request.method == 'POST':
            # Seat selection form submitted
            show_id = request.form.get('show_id', type=int)
            seats_json_str = request.form.get('seats_data')
            if not show_id or not seats_json_str:
                flash("Please select at least one seat to proceed.", "warning")
                return redirect(url_for('index'))
                
            import json
            try:
                seats_data = json.loads(seats_json_str)
            except Exception:
                flash("Invalid seat selection data.", "danger")
                return redirect(url_for('index'))
                
            session['checkout_show_id'] = show_id
            session['checkout_seats'] = seats_data
            return redirect(url_for('checkout'))
            
        show_id = session.get('checkout_show_id')
        seats_data = session.get('checkout_seats', [])
        
        if not show_id or not seats_data:
            flash("No active booking session found.", "info")
            return redirect(url_for('index'))
            
        show = db.session.get(Show, show_id)
        if not show:
            flash("Selected show is no longer available.", "danger")
            return redirect(url_for('index'))
            
        summary = calculate_order_summary(seats_data)
        
        # Verify seats haven't been taken in the meantime
        booked = get_booked_seats_for_show(show.id)
        selected_numbers = [s['seat_number'] for s in seats_data]
        conflicts = set(selected_numbers).intersection(set(booked))
        if conflicts:
            flash(f"Seats {', '.join(conflicts)} were just booked by someone else! Please select alternative seats.", "danger")
            return redirect(url_for('seat_selection', show_id=show.id))
            
        current_user = None
        if 'user_id' in session:
            current_user = db.session.get(User, session['user_id'])
            
        return render_template(
            'checkout.html',
            show=show,
            seats=seats_data,
            summary=summary,
            current_user=current_user
        )

    @app.route('/api/process-payment', methods=['POST'])
    def process_payment():
        """Simulated payment processing API with success/failure options."""
        data = request.get_json() or {}
        show_id = data.get('show_id')
        seats_data = data.get('seats', [])
        payment_method = data.get('payment_method', 'UPI')
        simulate_failure = data.get('simulate_failure', False)
        
        customer_info = {
            'name': data.get('name', 'Demo Guest').strip(),
            'email': data.get('email', 'guest@ticketmania.com').strip(),
            'phone': data.get('phone', '9876543210').strip()
        }
        
        # Basic validation
        if not customer_info['name'] or not customer_info['email']:
            return jsonify({'success': False, 'message': 'Please provide your full name and valid email address.'}), 400
            
        if simulate_failure:
            return jsonify({
                'success': False, 
                'simulated_failure': True,
                'message': 'Simulated Payment Rejection: Bank gateway timed out or mock payment was declined. You can retry safely.'
            }), 400
            
        user_id = session.get('user_id')
        
        success, result = create_booking(
            show_id=show_id,
            seats_data=seats_data,
            customer_info=customer_info,
            payment_method=payment_method,
            user_id=user_id
        )
        
        if not success:
            return jsonify({'success': False, 'message': str(result)}), 400
            
        # Clear checkout session data
        session.pop('checkout_show_id', None)
        session.pop('checkout_seats', None)
        
        return jsonify({
            'success': True,
            'booking_code': result.booking_code,
            'redirect_url': url_for('confirmation', booking_code=result.booking_code)
        })

    @app.route('/confirmation/<booking_code>')
    def confirmation(booking_code):
        booking = Booking.query.filter_by(booking_code=booking_code).first_or_404()
        return render_template('confirmation.html', booking=booking)

    # -------------------------------------------------------------
    # User Profile & Booking History
    # -------------------------------------------------------------
    @app.route('/my-bookings')
    def my_bookings():
        user_id = session.get('user_id')
        if user_id:
            bookings_list = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_time.desc()).all()
        else:
            # If guest, fetch latest created bookings from session or demo user
            demo_user = User.query.filter_by(email="demo@ticketmania.com").first()
            bookings_list = Booking.query.filter_by(user_id=demo_user.id).order_by(Booking.booking_time.desc()).all() if demo_user else []
            
        return render_template('my_bookings.html', bookings=bookings_list)

    @app.route('/api/cancel-booking/<int:booking_id>', methods=['POST'])
    def api_cancel_booking():
        user_id = session.get('user_id')
        success, message, refund = cancel_booking(booking_id, user_id=user_id if user_id else None)
        return jsonify({
            'success': success,
            'message': message,
            'refund_amount': refund
        })

    # -------------------------------------------------------------
    # USP / Offers Page
    # -------------------------------------------------------------
    @app.route('/offers')
    def offers():
        return render_template('offers.html')

    # -------------------------------------------------------------
    # Authentication Routes
    # -------------------------------------------------------------
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_role'] = user.role
                flash(f"Welcome back, {user.name}!", "success")
                
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                if user.is_admin:
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('index'))
            else:
                flash("Invalid email or password. You may use demo@ticketmania.com / demo123", "danger")
                
        return render_template('auth/login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            password = request.form.get('password', '').strip()
            
            if not name or not email or not password:
                flash("Please fill in all required fields.", "warning")
                return redirect(url_for('register'))
                
            if User.query.filter_by(email=email).first():
                flash("An account with this email already exists. Please log in.", "info")
                return redirect(url_for('login'))
                
            user = User(name=name, email=email, phone=phone, role='user')
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            flash("Registration successful! Welcome to Ticket Mania.", "success")
            return redirect(url_for('index'))
            
        return render_template('auth/register.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash("You have been logged out safely.", "info")
        return redirect(url_for('index'))

    # -------------------------------------------------------------
    # Admin Dashboard & Management Routes
    # -------------------------------------------------------------
    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        total_bookings = Booking.query.filter_by(payment_status='SUCCESS').count()
        total_revenue = db.session.query(db.func.sum(Booking.total_amount)).filter_by(payment_status='SUCCESS').scalar() or 0.0
        total_tickets = db.session.query(db.func.sum(Booking.ticket_count)).filter_by(payment_status='SUCCESS').scalar() or 0
        total_discount_given = db.session.query(db.func.sum(Booking.discount_amount)).filter_by(payment_status='SUCCESS').scalar() or 0.0
        
        theatres_count = Theatre.query.count()
        movies_count = Movie.query.count()
        recent_bookings = Booking.query.order_by(Booking.booking_time.desc()).limit(8).all()
        
        return render_template(
            'admin/dashboard.html',
            total_bookings=total_bookings,
            total_revenue=total_revenue,
            total_tickets=total_tickets,
            total_discount_given=total_discount_given,
            theatres_count=theatres_count,
            movies_count=movies_count,
            recent_bookings=recent_bookings
        )

    @app.route('/admin/theatres', methods=['GET', 'POST'])
    @admin_required
    def admin_theatres():
        if request.method == 'POST':
            name = request.form.get('name')
            city_id = request.form.get('city_id', type=int)
            area = request.form.get('area')
            address = request.form.get('address')
            amenities = request.form.get('amenities', 'Dolby Atmos, 4K Laser')
            distance_km = request.form.get('distance_km', type=float, default=2.0)
            
            theatre = Theatre(
                name=name,
                city_id=city_id,
                area=area,
                address=address,
                amenities=amenities,
                distance_km=distance_km,
                total_screens=1
            )
            db.session.add(theatre)
            db.session.flush()
            
            # Create default screen
            scr = Screen(theatre_id=theatre.id, screen_name="Screen 1", screen_type="Dolby Atmos 4K")
            db.session.add(scr)
            db.session.commit()
            flash(f"Theatre '{name}' added successfully.", "success")
            return redirect(url_for('admin_theatres'))
            
        theatres_list = Theatre.query.order_by(Theatre.city_id, Theatre.name).all()
        cities = City.query.order_by(City.name).all()
        return render_template('admin/theatres.html', theatres=theatres_list, cities=cities)

    @app.route('/admin/movies', methods=['GET', 'POST'])
    @admin_required
    def admin_movies():
        if request.method == 'POST':
            title = request.form.get('title')
            slug = request.form.get('slug') or title.lower().replace(' ', '-')
            language = request.form.get('language')
            genre = request.form.get('genre')
            duration_mins = request.form.get('duration_mins', type=int, default=150)
            synopsis = request.form.get('synopsis')
            poster_url = request.form.get('poster_url')
            backdrop_url = request.form.get('backdrop_url')
            is_now_showing = 'is_now_showing' in request.form
            
            movie = Movie(
                title=title,
                slug=slug,
                language=language,
                genre=genre,
                duration_mins=duration_mins,
                synopsis=synopsis,
                poster_url=poster_url,
                backdrop_url=backdrop_url,
                is_now_showing=is_now_showing
            )
            db.session.add(movie)
            db.session.commit()
            flash(f"Movie '{title}' added successfully.", "success")
            return redirect(url_for('admin_movies'))
            
        movies_list = Movie.query.order_by(Movie.title).all()
        return render_template('admin/movies.html', movies=movies_list)

    @app.route('/admin/shows', methods=['GET', 'POST'])
    @admin_required
    def admin_shows():
        if request.method == 'POST':
            theatre_id = request.form.get('theatre_id', type=int)
            screen_id = request.form.get('screen_id', type=int)
            movie_id = request.form.get('movie_id', type=int)
            show_date = request.form.get('show_date')
            show_time = request.form.get('show_time')
            fmt = request.form.get('format', '2D')
            price_vip = request.form.get('price_vip', type=float, default=220.0)
            price_premium = request.form.get('price_premium', type=float, default=160.0)
            price_normal = request.form.get('price_normal', type=float, default=100.0)
            
            show = Show(
                theatre_id=theatre_id,
                screen_id=screen_id,
                movie_id=movie_id,
                show_date=show_date,
                show_time=show_time,
                format=fmt,
                price_vip=price_vip,
                price_premium=price_premium,
                price_normal=price_normal
            )
            db.session.add(show)
            db.session.commit()
            flash("Show scheduled successfully.", "success")
            return redirect(url_for('admin_shows'))
            
        shows_list = Show.query.order_by(Show.show_date.desc(), Show.show_time).limit(50).all()
        theatres = Theatre.query.filter_by(is_active=True).all()
        movies = Movie.query.filter_by(is_now_showing=True).all()
        screens = Screen.query.all()
        return render_template('admin/shows.html', shows=shows_list, theatres=theatres, movies=movies, screens=screens)

    @app.route('/admin/seat-editor/<int:show_id>')
    @admin_required
    def admin_seat_editor(show_id):
        show = db.session.get(Show, show_id)
        if not show:
            abort(404)
        booked_seats = get_booked_seats_for_show(show.id)
        return render_template('admin/seat_editor.html', show=show, booked_seats=booked_seats)

    @app.route('/admin/api/toggle-seat', methods=['POST'])
    @admin_required
    def admin_toggle_seat():
        """Admin API to manually block or unblock a demo seat."""
        data = request.get_json() or {}
        show_id = data.get('show_id')
        seat_number = data.get('seat_number')
        
        # Check if already booked
        active_seat = BookingSeat.query.join(Booking).filter(
            Booking.show_id == show_id,
            Booking.cancellation_status != 'CANCELLED',
            BookingSeat.seat_number == seat_number
        ).first()
        
        if active_seat:
            # Unblock by marking booking cancelled
            active_seat.booking.cancellation_status = 'CANCELLED'
            db.session.commit()
            return jsonify({'success': True, 'action': 'unblocked', 'seat_number': seat_number})
        else:
            # Block by creating admin reserved dummy booking
            show = db.session.get(Show, show_id)
            dummy_booking = Booking(
                booking_code=f"ADMIN-BLOCK-{seat_number}",
                user_id=session.get('user_id'),
                show_id=show_id,
                customer_name="Admin Reserved",
                customer_email="admin@ticketmania.com",
                customer_phone="0000000000",
                ticket_count=1,
                total_ticket_price=show.price_premium,
                base_convenience_fee=20.0,
                discount_amount=5.0,
                final_convenience_fee=15.0,
                total_amount=show.price_premium + 15.0,
                payment_status='SUCCESS',
                payment_method='ADMIN_BLOCK'
            )
            db.session.add(dummy_booking)
            db.session.flush()
            bseat = BookingSeat(booking_id=dummy_booking.id, seat_number=seat_number, tier="PREMIUM", price=show.price_premium)
            db.session.add(bseat)
            db.session.commit()
            return jsonify({'success': True, 'action': 'blocked', 'seat_number': seat_number})

    @app.route('/admin/bookings')
    @admin_required
    def admin_bookings():
        bookings_list = Booking.query.order_by(Booking.booking_time.desc()).all()
        return render_template('admin/bookings.html', bookings=bookings_list)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
