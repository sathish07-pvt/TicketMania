"""
Seed demonstration data for Ticket Mania.
Pre-populates default location (Tiruchirappalli / Trichy), regional cities,
real Trichy cinema halls, trending movies, showtimes, and demo user accounts.
"""

from datetime import datetime, date, timedelta
from app import create_app
from models import db, User, City, Theatre, Screen, Movie, Show, Booking, BookingSeat

def seed():
    app = create_app()
    with app.app_context():
        print("Recreating database tables...")
        db.drop_all()
        db.create_all()
        
        # 1. Seed Demo Users
        print("Seeding users...")
        admin = User(
            name="Ticket Mania Admin",
            email="admin@ticketmania.com",
            phone="9944001122",
            role="admin"
        )
        admin.set_password("admin123")
        
        demo_user = User(
            name="Sathish Kumar",
            email="demo@ticketmania.com",
            phone="9876543210",
            role="user"
        )
        demo_user.set_password("demo123")
        
        db.session.add_all([admin, demo_user])
        db.session.commit()
        
        # 2. Seed Cities
        print("Seeding cities...")
        trichy = City(
            name="Tiruchirappalli (Trichy)",
            state="Tamil Nadu",
            slug="trichy",
            is_default=True,
            latitude=10.7905,
            longitude=78.7047
        )
        chennai = City(
            name="Chennai",
            state="Tamil Nadu",
            slug="chennai",
            is_default=False,
            latitude=13.0827,
            longitude=80.2707
        )
        coimbatore = City(
            name="Coimbatore",
            state="Tamil Nadu",
            slug="coimbatore",
            is_default=False,
            latitude=11.0168,
            longitude=76.9558
        )
        madurai = City(
            name="Madurai",
            state="Tamil Nadu",
            slug="madurai",
            is_default=False,
            latitude=9.9252,
            longitude=78.1198
        )
        salem = City(
            name="Salem",
            state="Tamil Nadu",
            slug="salem",
            is_default=False,
            latitude=11.6643,
            longitude=78.1460
        )
        bengaluru = City(
            name="Bengaluru",
            state="Karnataka",
            slug="bengaluru",
            is_default=False,
            latitude=12.9716,
            longitude=77.5946
        )
        
        db.session.add_all([trichy, chennai, coimbatore, madurai, salem, bengaluru])
        db.session.commit()
        
        # 3. Seed Theatres in Trichy
        print("Seeding Trichy theatres...")
        theatres_data = [
            {
                "city_id": trichy.id,
                "name": "LA Cinema Maris Complex",
                "area": "Thillai Nagar / Fort Station",
                "address": "No. 1, Fort Station Road, Thillai Nagar, Tiruchirappalli - 620002",
                "distance_km": 1.8,
                "total_screens": 2,
                "amenities": "Dolby Atmos, 4K RGB Laser, VIP Recliner Lounge, Food Court, Covered Parking",
                "image_url": "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=800&auto=format&fit=crop&q=80",
                "screens": [
                    {"name": "Maris Dolby Atmos (Audi 1)", "type": "Dolby Atmos 4K"},
                    {"name": "Royal Laser 4K (Audi 2)", "type": "Barco 4K Laser"}
                ]
            },
            {
                "city_id": trichy.id,
                "name": "Mega Star Cinemas",
                "area": "Cantonment / Central Bus Stand",
                "address": "Opposite Central Bus Stand, Cantonment, Tiruchirappalli - 620001",
                "distance_km": 2.4,
                "total_screens": 2,
                "amenities": "Barco 4K Laser, Dolby Surround 7.1, Cafeteria, Multi-Level Parking",
                "image_url": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800&auto=format&fit=crop&q=80",
                "screens": [
                    {"name": "Mega Screen 1", "type": "4K Laser Dolby"},
                    {"name": "Star Screen 2", "type": "Dolby 7.1"}
                ]
            },
            {
                "city_id": trichy.id,
                "name": "Sona Mina Theatres",
                "area": "Karur Bypass Road",
                "address": "Karur Bypass Road, Annamalai Nagar, Tiruchirappalli - 620018",
                "distance_km": 3.1,
                "total_screens": 2,
                "amenities": "Dolby Atmos Sound, 4K Projection, Recliner Rows, Gourmet Snacks, Valet Parking",
                "image_url": "https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?w=800&auto=format&fit=crop&q=80",
                "screens": [
                    {"name": "Sona Atmos Screen", "type": "Dolby Atmos 4K"},
                    {"name": "Mina Digital Screen", "type": "Qube 4K"}
                ]
            },
            {
                "city_id": trichy.id,
                "name": "Sri Venkatesha / Rohini Silver Screens",
                "area": "K.K. Nagar",
                "address": "Kallukuzhi, Near Railway Overbridge, K.K. Nagar, Tiruchirappalli - 620021",
                "distance_km": 4.2,
                "total_screens": 1,
                "amenities": "Dolby 7.1 Sound, 2K Digital, Ample Two-Wheeler Parking, Snack Corner",
                "image_url": "https://images.unsplash.com/photo-1585647347483-22b66260dfff?w=800&auto=format&fit=crop&q=80",
                "screens": [
                    {"name": "Main Silver Screen", "type": "Dolby 7.1 2K"}
                ]
            },
            {
                "city_id": trichy.id,
                "name": "Cauvery Theatre",
                "area": "Srirangam / Tiruvanaikoil",
                "address": "Near Cauvery River Bridge, Srirangam Trunk Rd, Tiruchirappalli - 620005",
                "distance_km": 5.5,
                "total_screens": 1,
                "amenities": "Dolby Digital, Fully Air Conditioned, Traditional Popcorn & Tea Bar",
                "image_url": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=800&auto=format&fit=crop&q=80",
                "screens": [
                    {"name": "Cauvery Screen", "type": "Dolby Digital"}
                ]
            },
            {
                "city_id": trichy.id,
                "name": "Ramakrishna Theatre",
                "area": "Palakkarai",
                "address": "Palakkarai Main Road, Near Railway Junction, Tiruchirappalli - 620008",
                "distance_km": 2.9,
                "total_screens": 1,
                "amenities": "Digital Cinema, DTS Surround, Refreshment Counters",
                "image_url": "https://images.unsplash.com/photo-1518929458119-e5bf444c30f4?w=800&auto=format&fit=crop&q=80",
                "screens": [
                    {"name": "Screen 1", "type": "DTS Surround"}
                ]
            },
            # Chennai Theatres (Sample)
            {
                "city_id": chennai.id,
                "name": "SPI Cinemas - Sathyam",
                "area": "Royapettah, Chennai",
                "address": "No 8, Thiru-Vi-Ka Road, Royapettah, Chennai - 600014",
                "distance_km": 3.0,
                "total_screens": 2,
                "amenities": "Dolby Atmos, 4K Laser, Sathyam Popcorn, Valet Parking",
                "image_url": "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=800&auto=format&fit=crop&q=80",
                "screens": [
                    {"name": "Sathyam Main", "type": "Dolby Atmos 4K"},
                    {"name": "Santham", "type": "Dolby 7.1"}
                ]
            },
            # Coimbatore Theatres (Sample)
            {
                "city_id": coimbatore.id,
                "name": "Broadway Cinemas",
                "area": "Aerodrome Post, Coimbatore",
                "address": "Broadway Mega Cineverse, Coimbatore - 641014",
                "distance_km": 4.5,
                "total_screens": 2,
                "amenities": "EPIQ Premium Large Format, Dolby Atmos, Gold Lounge",
                "image_url": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800&auto=format&fit=crop&q=80",
                "screens": [
                    {"name": "EPIQ Audi", "type": "EPIQ Dolby Atmos"},
                    {"name": "Gold Class", "type": "Barco 4K"}
                ]
            }
        ]
        
        theatre_objs = []
        screen_objs = []
        for t_info in theatres_data:
            screens = t_info.pop("screens")
            t = Theatre(**t_info)
            db.session.add(t)
            db.session.flush()
            theatre_objs.append(t)
            
            for s_info in screens:
                scr = Screen(
                    theatre_id=t.id,
                    screen_name=s_info["name"],
                    screen_type=s_info["type"],
                    total_rows=10,
                    total_cols=14
                )
                db.session.add(scr)
                screen_objs.append(scr)
                
        db.session.commit()
        
        # 4. Seed Movies
        print("Seeding movies...")
        movies_data = [
            {
                "title": "Amaran",
                "slug": "amaran",
                "language": "Tamil",
                "genre": "Biographical, Action, Drama",
                "duration_mins": 169,
                "release_date": "31 Oct 2024",
                "rating": "UA",
                "user_rating": 9.4,
                "votes_count": 89400,
                "synopsis": "An extraordinary biographical war action drama depicting the life of Major Mukund Varadarajan AC, an officer in the Rajput Regiment who was posthumously awarded the Ashoka Chakra for his courageous leadership during a counter-terrorism operation in Kashmir.",
                "poster_url": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=800&auto=format&fit=crop&q=80",
                "backdrop_url": "https://images.unsplash.com/photo-1518676590629-3dcbd9c5a5c9?w=1400&auto=format&fit=crop&q=80",
                "trailer_url": "https://www.youtube.com/watch?v=hylixphslb8",
                "is_now_showing": True,
                "is_popular": True,
                "is_upcoming": False
            },
            {
                "title": "The Greatest of All Time (GOAT)",
                "slug": "goat",
                "language": "Tamil",
                "genre": "Sci-Fi, Action, Thriller",
                "duration_mins": 183,
                "release_date": "05 Sep 2024",
                "rating": "UA",
                "user_rating": 9.1,
                "votes_count": 142000,
                "synopsis": "Gandhi, a top elite hostage extraction and intelligence officer belonging to the Special Anti-Terrorist Squad (SATS), confronts a haunting past when an unforeseen enemy from former operations surfaces to dismantle his legacy.",
                "poster_url": "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?w=800&auto=format&fit=crop&q=80",
                "backdrop_url": "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=1400&auto=format&fit=crop&q=80",
                "trailer_url": "https://www.youtube.com/watch?v=JgD1JbNkjr4",
                "is_now_showing": True,
                "is_popular": True,
                "is_upcoming": False
            },
            {
                "title": "Vettaiyan",
                "slug": "vettaiyan",
                "language": "Tamil",
                "genre": "Action, Crime, Drama",
                "duration_mins": 163,
                "release_date": "10 Oct 2024",
                "rating": "UA",
                "user_rating": 8.8,
                "votes_count": 67300,
                "synopsis": "Superintendent of Police Athiyan, renowned across the state as a relentless encounter specialist, gets caught in a moral conflict involving educational corruption and justice outside the legal framework.",
                "poster_url": "https://images.unsplash.com/photo-1574267432553-4b4628081c31?w=800&auto=format&fit=crop&q=80",
                "backdrop_url": "https://images.unsplash.com/photo-1509281373149-e957c6296406?w=1400&auto=format&fit=crop&q=80",
                "trailer_url": "https://www.youtube.com/watch?v=6mXo4Xh6Pz4",
                "is_now_showing": True,
                "is_popular": True,
                "is_upcoming": False
            },
            {
                "title": "Gladiator II",
                "slug": "gladiator-ii",
                "language": "English",
                "genre": "Epic, Action, Historical",
                "duration_mins": 148,
                "release_date": "15 Nov 2024",
                "rating": "A",
                "user_rating": 9.2,
                "votes_count": 52100,
                "synopsis": "Decades after witnessing the martyrdom of revered hero Maximus, Lucius must enter the Colosseum after his home is conquered by the tyrannical Emperors who now lead Rome with an iron fist.",
                "poster_url": "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=800&auto=format&fit=crop&q=80",
                "backdrop_url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=1400&auto=format&fit=crop&q=80",
                "trailer_url": "https://www.youtube.com/watch?v=4rgYUipGJNo",
                "is_now_showing": True,
                "is_popular": False,
                "is_upcoming": False
            },
            {
                "title": "Devara: Part 1",
                "slug": "devara-part-1",
                "language": "Telugu",
                "genre": "Action, Drama, Thriller",
                "duration_mins": 178,
                "release_date": "27 Sep 2024",
                "rating": "UA",
                "user_rating": 8.7,
                "votes_count": 78900,
                "synopsis": "An epic sea-bound saga set across coastal lands, following an unflinching chieftain who vows to guard his people from ruthless smuggling cartels across treacherous waters.",
                "poster_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&auto=format&fit=crop&q=80",
                "backdrop_url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1400&auto=format&fit=crop&q=80",
                "trailer_url": "https://www.youtube.com/watch?v=Q4nF2lG1M_c",
                "is_now_showing": True,
                "is_popular": False,
                "is_upcoming": False
            },
            {
                "title": "Leo",
                "slug": "leo",
                "language": "Tamil",
                "genre": "Action, Thriller",
                "duration_mins": 164,
                "release_date": "19 Oct 2023",
                "rating": "A",
                "user_rating": 9.0,
                "votes_count": 189000,
                "synopsis": "Parthiban is a mild-mannered cafe owner in Theog, Himachal Pradesh, who becomes a local hero after thwarting an armed robbery, only to find himself pursued by drug kingpins who suspect he is their former enforcer Leo Das.",
                "poster_url": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=800&auto=format&fit=crop&q=80",
                "backdrop_url": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1400&auto=format&fit=crop&q=80",
                "trailer_url": "https://www.youtube.com/watch?v=Po3jVh2CAT8",
                "is_now_showing": True,
                "is_popular": True,
                "is_upcoming": False
            },
            {
                "title": "Viduthalai Part 2",
                "slug": "viduthalai-part-2",
                "language": "Tamil",
                "genre": "Crime, Period Drama",
                "duration_mins": 160,
                "release_date": "20 Dec 2024",
                "rating": "A",
                "user_rating": 9.5,
                "votes_count": 31000,
                "synopsis": "The explosive conclusion to Vetrimaaran's critically acclaimed saga, chronicling the rise of Vaathiyaar and the gripping clash of ideologies within the dense hills.",
                "poster_url": "https://images.unsplash.com/photo-1518929458119-e5bf444c30f4?w=800&auto=format&fit=crop&q=80",
                "backdrop_url": "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=1400&auto=format&fit=crop&q=80",
                "trailer_url": "https://www.youtube.com/watch?v=mocktrailer",
                "is_now_showing": False,
                "is_popular": False,
                "is_upcoming": True
            },
            {
                "title": "Good Bad Ugly",
                "slug": "good-bad-ugly",
                "language": "Tamil",
                "genre": "Action, Crime, Comedy",
                "duration_mins": 155,
                "release_date": "Pongal 2025",
                "rating": "UA",
                "user_rating": 9.3,
                "votes_count": 25000,
                "synopsis": "An adrenaline-fueled, stylistic retro action thriller packed with mass swagger and exhilarating confrontations.",
                "poster_url": "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?w=800&auto=format&fit=crop&q=80",
                "backdrop_url": "https://images.unsplash.com/photo-1509281373149-e957c6296406?w=1400&auto=format&fit=crop&q=80",
                "trailer_url": "https://www.youtube.com/watch?v=mocktrailer2",
                "is_now_showing": False,
                "is_popular": False,
                "is_upcoming": True
            }
        ]
        
        movie_objs = []
        for m_info in movies_data:
            m = Movie(**m_info)
            db.session.add(m)
            movie_objs.append(m)
            
        db.session.commit()
        
        # 5. Seed Shows
        print("Seeding showtimes...")
        today = date.today()
        dates = [today + timedelta(days=i) for i in range(4)] # Today, Tomorrow, +2, +3
        
        show_times_slots = [
            ("10:30 AM", "Morning", "2D"),
            ("02:15 PM", "Afternoon", "Dolby Atmos"),
            ("06:30 PM", "Evening", "Dolby Atmos 4K"),
            ("10:00 PM", "Night", "2D")
        ]
        
        # Assign now-showing movies to screens
        now_showing_movies = [m for m in movie_objs if m.is_now_showing]
        
        show_count = 0
        all_shows = []
        for s_date in dates:
            date_str = s_date.strftime("%Y-%m-%d")
            
            for t in theatre_objs:
                for scr in t.screens:
                    # Pick movies in rotation
                    for slot_idx, (stime, scat, sfmt) in enumerate(show_times_slots):
                        movie = now_showing_movies[(t.id + scr.id + slot_idx) % len(now_showing_movies)]
                        
                        # Price variations by screen/theatre quality
                        base_vip = 240.0 if "Atmos" in scr.screen_type else 200.0
                        base_premium = 180.0 if "Atmos" in scr.screen_type else 150.0
                        base_normal = 120.0 if "Atmos" in scr.screen_type else 90.0
                        
                        show = Show(
                            theatre_id=t.id,
                            screen_id=scr.id,
                            movie_id=movie.id,
                            show_date=date_str,
                            show_time=stime,
                            time_category=scat,
                            format=sfmt,
                            price_vip=base_vip,
                            price_premium=base_premium,
                            price_normal=base_normal
                        )
                        db.session.add(show)
                        all_shows.append(show)
                        show_count += 1
                        
        db.session.commit()
        print(f"Created {show_count} shows across theatres and dates.")
        
        # 6. Seed a sample booking for the demo user
        print("Seeding sample booking...")
        sample_show = all_shows[0]
        sample_booking = Booking(
            booking_code="TM-TRC-892147",
            user_id=demo_user.id,
            show_id=sample_show.id,
            customer_name="Sathish Kumar",
            customer_email="demo@ticketmania.com",
            customer_phone="9876543210",
            ticket_count=2,
            total_ticket_price=sample_show.price_premium * 2,
            base_convenience_fee=40.0,
            discount_amount=10.0,
            final_convenience_fee=30.0,
            total_amount=(sample_show.price_premium * 2) + 30.0,
            payment_status="SUCCESS",
            payment_method="UPI",
            payment_ref="UPI-DEMO-991823",
            booking_time=datetime.utcnow() - timedelta(hours=3),
            cancellation_status="NONE",
            refund_amount=0.0
        )
        db.session.add(sample_booking)
        db.session.flush()
        
        b_seat1 = BookingSeat(booking_id=sample_booking.id, seat_number="D6", tier="PREMIUM", price=sample_show.price_premium)
        b_seat2 = BookingSeat(booking_id=sample_booking.id, seat_number="D7", tier="PREMIUM", price=sample_show.price_premium)
        db.session.add_all([b_seat1, b_seat2])
        db.session.commit()
        
        print("Database successfully seeded with realistic Trichy & cinema prototype data!")

if __name__ == "__main__":
    seed()
