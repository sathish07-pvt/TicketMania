import urllib.request
import urllib.error
import json

base = 'http://127.0.0.1:5000'

def run_verifications():
    print("Testing Ticket Mania Endpoints...")
    
    # 1. Test Homepage
    resp = urllib.request.urlopen(base + '/')
    assert resp.status == 200
    html = resp.read().decode('utf-8')
    assert 'Ticket' in html and 'Tiruchirappalli (Trichy)' in html
    print('[OK] Homepage loaded with default Trichy location')

    # 2. Test Movies
    resp = urllib.request.urlopen(base + '/movies')
    assert resp.status == 200
    html = resp.read().decode('utf-8')
    assert 'Amaran' in html
    print('[OK] Movies page loaded')

    # 3. Test Theatres
    resp = urllib.request.urlopen(base + '/theatres')
    assert resp.status == 200
    html = resp.read().decode('utf-8')
    assert 'LA Cinema Maris Complex' in html
    print('[OK] Theatres page loaded with Trichy halls')

    # 4. Test Offers USP page
    resp = urllib.request.urlopen(base + '/offers')
    assert resp.status == 200
    html = resp.read().decode('utf-8')
    assert 'Standard Pricing & Discount Table' in html
    print('[OK] Offers USP page loaded')

    # 5. Test Seat Selection for show 1
    resp = urllib.request.urlopen(base + '/show/1/seats')
    assert resp.status == 200
    html = resp.read().decode('utf-8')
    assert 'Screen This Way' in html
    print('[OK] Seat selection layout loaded')

    # 6. Test API Price Calculation
    req = urllib.request.Request(
        base + '/api/calculate-price',
        data=json.dumps({'seats': [{'seat_number': 'B1', 'price': 220}, {'seat_number': 'B2', 'price': 220}]}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode('utf-8'))
    assert data['ticket_count'] == 2
    assert data['base_convenience_fee'] == 40.0
    assert data['discount_amount'] == 10.0
    assert data['final_convenience_fee'] == 30.0
    assert data['customer_savings'] == 40.0
    print('[OK] API Price Calculation: 2 tickets correctly calculates Rs 10 even discount (Base Rs 40, Final Rs 30, Savings Rs 40)')

    # 7. Test Simulated Payment API
    payment_payload = {
        'show_id': 1,
        'seats': [{'seat_number': 'A5', 'tier': 'VIP', 'price': 240.0}],
        'name': 'Ramesh Kumar',
        'email': 'ramesh@example.com',
        'phone': '9840123456',
        'payment_method': 'UPI',
        'simulate_failure': False
    }
    req = urllib.request.Request(
        base + '/api/process-payment',
        data=json.dumps(payment_payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    resp = urllib.request.urlopen(req)
    pay_data = json.loads(resp.read().decode('utf-8'))
    assert pay_data['success'] is True
    b_code = pay_data['booking_code']
    print(f'[OK] Simulated payment successful, booking code: {b_code}')

    # 8. Test Confirmation page for created booking
    resp = urllib.request.urlopen(base + f'/confirmation/{b_code}')
    assert resp.status == 200
    html = resp.read().decode('utf-8')
    assert b_code in html
    assert 'Booking Confirmed' in html
    print('[OK] Confirmation digital ticket page generated')

    # 9. Test Payment failure simulation toggle
    fail_payload = {
        'show_id': 1,
        'seats': [{'seat_number': 'A6', 'tier': 'VIP', 'price': 240.0}],
        'name': 'Ramesh Kumar',
        'email': 'ramesh@example.com',
        'phone': '9840123456',
        'payment_method': 'UPI',
        'simulate_failure': True
    }
    try:
        req = urllib.request.Request(
            base + '/api/process-payment',
            data=json.dumps(fail_payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req)
        assert False, 'Should fail'
    except urllib.error.HTTPError as e:
        err_body = json.loads(e.read().decode('utf-8'))
        assert err_body['simulated_failure'] is True
        print('[OK] Payment failure simulator correctly catches simulated bank timeout')

    print('\nALL INTEGRATION AND ROUTE CHECKS PASSED!')

if __name__ == '__main__':
    run_verifications()
